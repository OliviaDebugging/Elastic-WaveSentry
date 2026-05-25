# ESP8266 Wi-Fi Promiscuous Mode Sniffer Firmware

A lightweight, high-performance Wi-Fi promiscuous mode sniffer designed for the ESP8266 microcontroller. This script configures the hardware radio to intercept raw 802.11 frames on a specified channel and streams them over a serial connection using a structured hexadecimal format, making it ideal for integration with Python scripts or other host-side data parsers.

**Note: This firmware is intended for educational and research purposes only. Ensure you have proper authorization to capture Wi-Fi traffic in your environment.**
<br>

## Features

* **Promiscuous Mode**: Bypasses standard Wi-Fi filtering to capture all over-the-air 802.11 packets on the channel.
* **Hardware Interrupt Driven**: Packet capturing is handled asynchronously via low-level callbacks, minimizing overhead.
* **Structured Serial Output**: Pre-formats packets with a `PKT:[length]:[payload]` prefix for trivial parsing on the host device.
* **Hex-Padded Output**: Automatically pads single-digit hex values to ensure a clean, predictable byte stream.


## Hardware Requirements

* **Microcontroller**: Any ESP8266-based development board (NodeMCU, Wemos D1 Mini, ESP-01, etc.).
* **Data Cable**: Micro-USB (or USB-C depending on your board) capable of data transfer.
* **Power Source**: USB power from your computer or a compatible power adapter.


## ⚙️ How It Works

1.  **Radio Disconnection**: The script disconnects the ESP8266 from any active Wi-Fi networks and sets the operating mode to `STATION_MODE` to unlock the radio.
2.  **Promiscuous Injection**: The SDK's promiscuous engine is enabled, injecting a custom callback function (`sniffer_callback`) into the RX radio stack.
3.  **Channel Locking**: The radio is statically locked onto **Channel 6** (2.4 GHz).
4.  **Serial Streaming**: For every intercepted frame, the script prints the first 50 bytes of the payload in hexadecimal format directly to the Serial interface at **115200 baud**.


## Installation & Setup
1. Open the Arduino IDE.
2. Ensure you have the ESP8266 Board Package installed (via Tools > Board > Boards Manager...).
3. Copy the script into a new sketch.
4. Select your specific ESP8266 board and correct COM port from the Tools menu.
5. Set the Serial Monitor baud rate to 115200.
6. Upload the sketch, using the "Upload" button in the Arduino IDE.
7. Open the Serial Monitor to start viewing captured Wi-Fi packets in real-time.


### Configuration Changes:
If you want to monitor a different Wi-Fi channel, locate the following line in void setup() and change the integer (1-13 depending on your region):

```C++
// Change 6 to your desired target channel (e.g., 1 or 11)
wifi_set_channel(6); 
``` 

## Important Considerations
***No Wi-Fi Connectivity:*** While this script is running, the ESP8266 cannot connect to a Wi-Fi network or host an Access Point because the radio chipset is completely dedicated to listening.

***2.4 GHz Limitation:*** The ESP8266 hardware only supports 2.4 GHz frequencies (802.11 b/g/n). It cannot sniff 5 GHz or 6 GHz bands.

**Legal & Ethical Use:** Always ensure you have explicit permission to capture Wi-Fi traffic in your environment. Unauthorized interception of wireless communications may violate local laws and regulations.

## 📊 Data Output Format

The serial output is structured to be easily parsed by regular expressions or string splitting in a host script (e.g., Python):

`PKT:<packet_length>:<hex_payload>`

Where:
- `<packet_length>` is the total length of the captured packet in bytes.
- `<hex_payload>` is the raw packet data represented as a continuous hexadecimal string (with leading zeros padded for single-digit values).


### Example Output:
```text
🛰️ Hardware Sniffer Initialized.
PKT:128:80000000ffffffffffff00259c218bb000259c218bb0a0c1
PKT:64:4000000000259c218bb0ffffffffffffa0c1
```

📌 Note: To prevent serial buffer congestion, the script is currently capped to stream up to the first 50 bytes of each packet payload. You can adjust this limit in the std::min((int)length, 50) line inside the sketch.
 
<br>

## Elastic SIEM Integration & Real-Time Parsing

The hex payload streamed from the ESP8266 contains standard **IEEE 802.11 MAC Layer Headers**. When you forward this data from your Python bridge into Elasticsearch (into a field named `raw_message`), you can parse it dynamically at query-time using **Runtime Fields** (Painless scripting) without re-indexing your data.

### 802.11 Header Structure Map
The first 50 bytes streamed by the firmware expose the structural backbone of the intercepted packet:

| Byte Offset | Size | Purpose | Description |
| :--- | :--- | :--- | :--- |
| **Bytes 0–1** | 2 Bytes | Frame Control | Dictates the type of packet (e.g., `4000` = Probe Request, `8000` = Beacon). |
| **Bytes 2–3** | 2 Bytes | Duration/ID | Channel allocation time window. |
| **Bytes 4–9** | 6 Bytes | **Address 1 (Receiver)** | The target MAC address receiving this over-the-air packet. |
| **Bytes 10–15**| 6 Bytes | **Address 2 (Transmitter)**| The MAC address of the device broadcasting (**Your Target Device**). |
| **Bytes 16–21**| 6 Bytes | **Address 3 (Filtering)** | Source or BSSID (Access Point MAC) depending on frame type. |

> 💡 **Byte to Hex Conversion Note:** Because 1 byte equals 2 hexadecimal characters, Byte 10 starts exactly at character index **20** of the raw payload string (ignoring the `PKT:[len]:` prefix).

<hr>


### 🛠️ Elastic Runtime Field Implementations (Painless Script): Advanced Multi-Pattern Vendor & Privacy Detection

Because different 802.11 frame types (e.g., heavy Management Beacons vs. short Control Frames) utilize entirely different header lengths, a static character offset will result in parsing garbage data. 

To overcome this, the Elastic Data View uses an adaptive runtime field script that evaluates the payload length dynamically. It also intercepts modern mobile security protocols by identifying **Locally Administered Addresses (LAA)** used for MAC randomization.

### Production Painless Script (`packet.oui`)
* **Type:** `keyword`
* **Target Field Parsed:** `packet.payload_hex.keyword`

```painless
if (doc.containsKey('packet.payload_hex.keyword') && !doc['packet.payload_hex.keyword'].empty) {
    String hex = doc['packet.payload_hex.keyword'].value;
    String oui = "";
    
    // Pattern A: Long Management, Beacon, and Data Frames (Standard 24-byte MAC headers)
    if (hex.length() >= 50) {
        oui = hex.substring(44, 50).toLowerCase();
    } 
    // Pattern B: Short Control and Link Synchronization Frames (Stripped control headers)
    else if (hex.length() >= 38 && hex.length() < 50) {
        oui = hex.substring(32, 38).toLowerCase();
    }

    if (!oui.equals("")) {
        // --- Enterprise Networking & Core Infrastructure ---
        if (oui.equals("00259c") || oui.equals("001ee5")) { emit("Cisco Systems"); }
        else if (oui.equals("24a074") || oui.equals("30aea4")) { emit("Espressif Inc."); }
        else if (oui.equals("001422") || oui.equals("a4438c")) { emit("Intel Corporation"); }
        
        // --- Consumer Electronics & Mobile Device Signatures ---
        else if (oui.equals("001c43") || oui.equals("3c286d")) { emit("Apple Inc."); }
        else if (oui.equals("f4f5d8") || oui.equals("bcd074")) { emit("Google LLC"); }
        else if (oui.equals("0000f0") || oui.equals("f87b8c")) { emit("Samsung Electronics"); }
        
        // --- Cyber Security Layer: Catch Randomized Privacy Profiles ---
        // Inspects the locally administered bit (b1 of the first byte). 
        // If the second hex character is 2, 6, a, or e, it is a randomized virtual MAC.
        else if (oui.substring(1,2).equals("2") || oui.substring(1,2).equals("6") || 
                 oui.substring(1,2).equals("a") || oui.substring(1,2).equals("e")) {
            emit("Randomized Privacy Address");
        } 
        
        // --- Global Fallback Catch for Manual Analysis ---
        else { 
            emit("Other Identity (" + oui + ")");
        }
    } else {
        emit("Malformed / Short Packet");
    }
} else {
    emit("No Payload Data");
}
```
### Explanation of the Painless Script Logic:
1. **Dynamic Length Evaluation**: The script first checks the length of the `packet.payload_hex.keyword` field to determine which parsing pattern to apply:
   - **Pattern A**: For packets with a hex string length of 50 or more characters, it assumes a standard 24-byte MAC header and extracts the OUI from bytes 16–21 (characters 44–49).
   - **Pattern B**: For shorter packets (38–49 characters), it assumes a stripped control frame and extracts the OUI from bytes 10–15 (characters 32–37).   
2. **Vendor Mapping**: The script contains a mapping of known OUIs to major manufacturers, allowing for immediate identification of devices from brands like Apple, Google, Samsung, Cisco, Intel, and Espressif.
3. **Privacy Detection**: By inspecting the locally administered bit in the OUI, the script can identify randomized MAC addresses, which are commonly used by modern mobile devices to enhance privacy.
4. **Fallback Handling**: If the OUI does not match any known patterns, it emits a generic "Other Identity" label along with the extracted OUI for manual analysis. It also handles cases where the packet is too short or malformed, ensuring that all documents receive a meaningful classification.  

## Conclusion
This ESP8266 firmware, combined with Elastic SIEM's powerful runtime field capabilities, provides a robust and flexible solution for real-time Wi-Fi packet analysis. By leveraging dynamic parsing logic and comprehensive vendor mapping, security analysts can gain immediate insights into the devices present in their wireless environment, while also identifying potential privacy threats from randomized MAC addresses.
