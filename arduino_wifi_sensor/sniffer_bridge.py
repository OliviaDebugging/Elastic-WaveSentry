import os
import sys
import serial
import datetime
from dotenv import load_dotenv  
from elasticsearch import Elasticsearch  

load_dotenv()  # This automatically loads the hidden .env file

# 1. Connect to Elastic Cloud using API Key
ELASTIC_CLOUD_ID = os.getenv("ELASTIC_CLOUD_ID")
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")  # Swapped password for API Key

# Safety check to make sure variables aren't empty
if not ELASTIC_CLOUD_ID or not ELASTIC_API_KEY:
    print("❌ Error: Missing ELASTIC_CLOUD_ID or ELASTIC_API_KEY in your .env file!")
    sys.exit(1)

es = Elasticsearch(
    cloud_id=ELASTIC_CLOUD_ID, # Fixed: matched with your variable name
    api_key=ELASTIC_API_KEY  
)

# 2. Connect to the Arduino USB Port
ARDUINO_USB_PORT = os.getenv("ARDUINO_USB_PORT")
if not ARDUINO_USB_PORT:
    print("❌ Error: ARDUINO_USB_PORT is not set in your .env file!")
    sys.exit(1)

ser = serial.Serial(ARDUINO_USB_PORT, 115200, timeout=1)

print("🚀 Scanning the airwaves... Press Ctrl+C to stop.")

# 3. Read USB and push to Kibana
while True:
    try:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        
        # 🔴 DIAGNOSTIC PRINT: Let's see exactly what the Arduino is saying over USB
        print(f"Raw USB Data: '{line}'")
        
        if line.startswith("PKT:"):
            parts = line.split(":")
            if len(parts) >= 3:
                pkt_len = parts[1]
                raw_hex = parts[2]
                
                # Format the data cleanly for Kibana mapping
                log_document = {
                    "@timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "packet": {
                        "length": int(pkt_len),
                        "payload_hex": raw_hex[:100] # Cap the length to keep database light
                    },
                    "sensor": {
                        "device": "arduino_esp8266",
                        "interface": "ambient_wifi"
                    }
                }
                
                # Push data directly into an index named logs-wifi
                es.index(index="logs-wifi", document=log_document)
                print(f"Captured packet size {pkt_len} bytes -> Sent to Elastic.")
    except KeyboardInterrupt:
        print("\nStopping scan.")
        break
    except Exception as e:
        print(f"Error parsing data: {e}")