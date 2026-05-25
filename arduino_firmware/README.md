# ESP8266 Raw Wi-Fi Packet Sniffer

A lightweight, high-performance Wi-Fi promiscuous mode sniffer designed for the ESP8266 microcontroller. This script configures the hardware radio to intercept raw 802.11 frames on a specified channel and streams them over a serial connection using a structured hexadecimal format, making it ideal for integration with Python scripts or other host-side data parsers.

**Note: This firmware is intended for educational and research purposes only. Ensure you have proper authorization to capture Wi-Fi traffic in your environment.**


---

## Features

* **Promiscuous Mode**: Bypasses standard Wi-Fi filtering to capture all over-the-air 802.11 packets on the channel.
* **Hardware Interrupt Driven**: Packet capturing is handled asynchronously via low-level callbacks, minimizing overhead.
* **Structured Serial Output**: Pre-formats packets with a `PKT:[length]:[payload]` prefix for trivial parsing on the host device.
* **Hex-Padded Output**: Automatically pads single-digit hex values to ensure a clean, predictable byte stream.

<br>

## Hardware Requirements

* **Microcontroller**: Any ESP8266-based development board (NodeMCU, Wemos D1 Mini, ESP-01, etc.).
* **Data Cable**: Micro-USB (or USB-C depending on your board) capable of data transfer.


<br>

## ⚙️ How It Works

1.  **Radio Disconnection**: The script disconnects the ESP8266 from any active Wi-Fi networks and sets the operating mode to `STATION_MODE` to unlock the radio.
2.  **Channel Locking**: The radio is statically locked onto **Channel 6** (2.4 GHz).
3.  **Promiscuous Injection**: The SDK's promiscuous engine is enabled, injecting a custom callback function (`sniffer_callback`) into the RX radio stack.
4.  **Serial Streaming**: For every intercepted frame, the script prints the first 50 bytes of the payload in hexadecimal format directly to the Serial interface at **115200 baud**.

<br>

## 📊 Data Output Format

The serial output is structured to be easily parsed by regular expressions or string splitting in a host script (e.g., Python):

`PKT:<packet_length>:<hex_payload>`

### Example Output:
```text
🛰️ Hardware Sniffer Initialized.
PKT:128:80000000ffffffffffff00259c218bb000259c218bb0a0c1
PKT:64:4000000000259c218bb0ffffffffffffa0c1
````

📌 Note: To prevent serial buffer congestion, the script is currently capped to stream up to the first 50 bytes of each packet payload. You can adjust this limit in the std::min((int)length, 50) line inside the sketch.
<br>

## 🔍 Elastic SIEM Integration & Real-Time Parsing

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

---

### 🛠️ Runtime Field Implementations (Painless)

To analyze this data in Kibana, navigate to **Stack Management** -> **Data Views** -> Select your index -> **Runtime Fields**, and add the following metrics:

#### 1. Extracting the Frame Type (`wifi.frame_type`)
Identify exactly what the target device is doing on the airwaves.
* **Type:** `keyword`

```painless
if (doc['raw_message.keyword'].size() > 0) {
  String msg = doc['raw_message.keyword'].value;
  if (msg.startsWith("PKT:")) {
    String[] parts = msg.splitOnToken(':');
    if (parts.length >= 3 && parts[2].length() >= 4) {
      String frameControl = parts[2].substring(0, 4);
      
      if (frameControl.equals("4000")) {
        emit("Probe Request (Device Searching for Wi-Fi)");
      } else if (frameControl.equals("8000")) {
        emit("Beacon Frame (Router Broadcasting SSID)");
      } else if (frameControl.equals("a000")) {
        emit("Disassociation (Device Disconnecting)");
      } else {
        emit("Other Data/Control Frame (" + frameControl + ")");
      }
    }
  }
}

<br>

## Installation & Setup:
1. Open the Arduino IDE.
2. Ensure you have the ESP8266 Board Package installed (via Tools > Board > Boards Manager...).
3. Copy the script into a new sketch.
4. Select your specific ESP8266 board and correct COM port from the Tools menu.
5. Set the Serial Monitor baud rate to 115200.
6. Upload the sketch, using the "Upload" button in the Arduino IDE.
7. Open the Serial Monitor to start viewing captured Wi-Fi packets in real-time.

<br>

## Configuration Changes:
If you want to monitor a different Wi-Fi channel, locate the following line in void setup() and change the integer (1-13 depending on your region):

```C++
// Change 6 to your desired target channel (e.g., 1 or 11)
wifi_set_channel(6); 
```

<br>

## Important Considerations
***No Wi-Fi Connectivity:*** While this script is running, the ESP8266 cannot connect to a Wi-Fi network or host an Access Point because the radio chipset is completely dedicated to listening.

***2.4 GHz Limitation:*** The ESP8266 hardware only supports 2.4 GHz frequencies (802.11 b/g/n). It cannot sniff 5 GHz or 6 GHz bands.