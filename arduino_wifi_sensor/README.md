# Arduino Wi-Fi Sniffer Bridge to Elastic Cloud 

A lightweight Python script that reads raw packet data broadcasted by an Arduino (or ESP8266/ESP32) via a USB Serial interface and streams it in real-time into **Elastic Cloud (Elasticsearch)** for storage, visualization, and analysis in **Kibana**. This bridge serves as a critical component in the **Elastic WaveSentry** project, enabling seamless integration between low-level wireless packet capture and high-level SIEM analytics.

## 📌 Features
- **Environment Driven:** Uses a `.env` file to securely handle sensitive Elastic Cloud credentials and configuration parameters.
- **Serial Data Monitoring:** Connects to the designated Arduino USB port at a `115200` baud rate.
- **Real-Time Data Normalization:** Parses specific packet data markers (`PKT:`) and formats fields into a structured, Elastic Common Schema (ECS) compatible layout.
- **Kibana-Ready:** Embeds ISO-compliant `@timestamp` fields and pushes documents directly into a structured `logs-wifi` data index.
- **Error Handling:** Implements robust exception handling for serial communication issues and Elastic API errors, ensuring continuous operation and clear logging of any faults.


## 🛠️ Prerequisites

Before executing the script, ensure you have the following ready:

1. **Python 3.8+** installed on your system.
2. **An Elastic Cloud Deployment**: You will need an active Elastic Cloud instance. If you don't have one, you can sign up for a free trial at [elastic.co](https://www.elastic.co/).
3. **An Arduino/ESP8266 Device**: Flashed with software designed to sniff wireless networks and output formatted strings via Serial connection in the following format:
   
   ```text
   PKT:<packet_length>:<hex_payload>
    ```

    Where `<packet_length>` is the total length of the captured packet in bytes, and `<hex_payload>` is the raw packet data represented as a continuous hexadecimal string. 


## 🚀 Installation & Setup
**1. Clone or Download the Project:** Ensure the Python script (e.g., sniffer_bridge.py) is located in your desired working directory.

**2. Install Dependencies:** Install the required external libraries using pip:

```Bash
pip install pyserial python-dotenv elasticsearch
```

**3. Configure the Environment Variables:** Create a file named .env in the exact same directory as your Python script. Populate it with your connection details:

```env
# Elastic Cloud Configuration
ELASTIC_CLOUD_ID="your-deployment-name:dXMtY2VudHJhbDEuZ2N...=="
ELASTIC_API_KEY="VjF...your_api_key_here...=="

# Serial/USB Hardware Configuration
# Windows Example: COM3, COM4
# Linux/macOS Example: /dev/ttyUSB0 or /dev/cu.usbserial-1410
ARDUINO_USB_PORT="/dev/ttyUSB0"
```

> **⚠️ Security Warning:** Never commit your .env file to a public version control system like GitHub. Add .env to your .gitignore file.
<br> 

> **TIP: How to Generate Your Elastic API Key**
> 
> To securely authenticate your script with Elastic Cloud without embedding username/password credentials:
> 1. Log in to your Kibana Dashboard.
> 2. Navigate to **Management** → **Stack Management** → **API Keys**.
> 3. Click **Create API key**.
> 4. Give your key a name (e.g., arduino-sniffer-key) and click **Create**.
> 5. Copy the generated API Key value and paste it into your ```.env``` file.


## Running the Script
Once your Arduino is plugged into the USB port and your .env configuration is finalized, execute the python script ```sniffer_bridge.py```

```Bash
Expected Console Output
Plaintext
🚀 Scanning the airwaves... Press Ctrl+C to stop.
Raw USB Data: 'Initializing Wi-Fi Sniffer...'
Raw USB Data: 'PKT:64:2f9a3c4d5e6f...'
Captured packet size 64 bytes -> Sent to Elastic.

To safely terminate the data collection stream, press Ctrl + C inside your terminal session.
```


## 📊 Elastic Data Schema Mapping
Data sent by this bridge is pushed automatically to the index named logs-wifi. Each document is indexed using the following standardized JSON structure:

```JSON
{
  "@timestamp": "2026-05-25T11:32:00.123456Z",
  "packet": {
    "length": 64,
    "payload_hex": "2f9a3c4d5e6f..."
  },
  "sensor": {
    "device": "arduino_esp8266",
    "interface": "ambient_wifi"
  }
}
```
Where:
- `@timestamp`: The exact time the packet was processed by the Python script, formatted in ISO 8601 with millisecond precision.
- `packet.length`: The total length of the captured packet in bytes, extracted from the raw data string.
- `packet.payload_hex`: The raw packet data represented as a continuous hexadecimal string, directly taken from the Serial output.
- `sensor.device`: A static identifier for the type of hardware used (e.g., "arduino_esp8266").
- `sensor.interface`: A static label indicating the method of data collection (e.g., "ambient_wifi").       

## 🛠️ Troubleshooting Tips
**Error: Missing Credentials:** Verify that the .env file name starts with a dot (.) and resides in the exact same directory where you are running the python script.

**Serial Exception (Port Busy):** Ensure that you do not have the Arduino IDE Serial Monitor open at the same time, as only one application can communicate with the USB interface at once.

**Elastic Authentication Faults:** Ensure your Elastic API key has the necessary indices management permissions (create_index, write) to auto-create or interact with the logs-wifi index pattern.