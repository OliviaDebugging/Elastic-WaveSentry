#include <ESP8266WiFi.h>
#include <algorithm> // Adds the missing standard algorithm libraries

extern "C" {
  #include "user_interface.h"
}

// This callback function triggers every single time a radio frame hits the antenna
void sniffer_callback(uint8_t *buffer, uint16_t length) {
  if (length > 12) {
    // 1. Send the structural prefix our Python script is hunting for
    Serial.print("PKT:");
    Serial.print(length);
    Serial.print(":");
    
    // 2. Stream the raw packet payload out as Hexadecimal characters
    // Fixed: Using std::min explicitly to resolve compiler scope errors
    for (int i = 0; i < std::min((int)length, 50); i++) {
      if (buffer[i] < 0x10) Serial.print("0"); // Pad single digits with a leading zero
      Serial.print(buffer[i], HEX);
    }
    
    // 3. Print a newline character to signal Python that the frame is complete
    Serial.println(); 
  }
}

void setup() {
  // Initialize the USB Serial connection at 115200 baud to match Python
  Serial.begin(115200);
  delay(500);
  Serial.println("\n🛰️ Hardware Sniffer Initialized.");

  // Disconnect from your home network to free up the internal radio chipset
  WiFi.disconnect();
  wifi_set_opmode(STATION_MODE);
  
  // Statically set the listener channel to Channel 6 (Standard 2.4GHz baseline)
  wifi_set_channel(6); 

  // Initialize and enable the promiscuous network driver engine
  wifi_promiscuous_enable(0);
  wifi_set_promiscuous_rx_cb(sniffer_callback);
  wifi_promiscuous_enable(1);
}

void loop() {
  // Sniffing happens instantly in the background via hardware interrupts
  delay(10); 
}