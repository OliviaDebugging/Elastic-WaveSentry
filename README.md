# 🛰️ Arduino Wi-Fi Packet Sniffer & Elastic Cloud SIEM Pipeline 

An end-to-end cyber-security data engineering project that intercepts ambient 802.11 Wi-Fi management frames using an ESP8266 microcontroller, pipes the raw hex payloads across a local USB serial bus, and streams them in real-time into an Elastic Cloud cluster for analysis via Kibana.

---

## 🏗️ System Architecture

1. **Edge Hardware Layer:** An ESP8266 (NodeMCU) board unlocks its radio antenna into low-level promiscuous mode, capturing raw ambient packet frame sizes and hex payloads.
2. **Local Transport Bridge Layer:** A Python 3 script runs a non-blocking loop listening to the active USB Serial interface (`/dev/cu.usbserial-210`), parsing structural packets (`PKT:<len>:<hex>`).
3. **Cloud Ingestion Layer:** The parsed data is structured into a normalized JSON document format containing explicit `@timestamp` metrics, device signatures, and payload metrics, then securely ingested via the `elasticsearch` native SDK using an API Key directly into an Elastic Cloud Index cluster (`logs-wifi`).

---

## 📁 Workspace Directory Hierarchy

This project follows the next structure:

```text
▼ ARDUINO WI-FI SNIFFER 
  ├── .gitignore               # Root Git exclusion file - excludes .venv, .env, and other sensitive files
  ├── .venv/                   # Python Local Virtual Environment -  Contains all installed dependencies including elasticsearch and python-dotenv
  ├── .vscode                  # VS Code Workspace Settings - Includes Python Interpreter Path for VS Code to .venv and other editor configurations
  ├── README.md                # This Markdown Documentation File
  ├── arduino_firmware/
  │   └── arduino_firmware.ino # Arduino Promiscuous Sniffer Firmware C++ Code - Compiled and Flashed to ESP8266 with Arduino IDE
  └── arduino_wifi_sensor/
      ├── .env                 # Local Environment Credentials Configuration File 
      └── sniffer_bridge.py    # Python Serial-to-Elastic Ingestion Engine - Reads from USB Serial, Parses Packets, and Ingests to Elastic Cloud