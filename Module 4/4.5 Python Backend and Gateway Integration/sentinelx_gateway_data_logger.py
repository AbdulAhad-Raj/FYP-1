
import serial
import csv
import re
import time
from pathlib import Path
from datetime import datetime

print("=" * 65)
print("SENTINEL-X MODULE 4.5")
print("CENTRAL GATEWAY TO PYTHON DATA LOGGER")
print("=" * 65)

PORT = "COM6"
BAUD_RATE = 115200

OUTPUT_FILE = Path(__file__).parent / "sentinelx_four_sensor_observations.csv"

columns = [
    "Timestamp",
    "Sender_IP",
    "Sender_Port",
    "Sensor_ID",
    "Location",
    "MAC",
    "RSSI_dBm",
    "Channel",
    "Frame_Type",
    "Raw_Message"
]

def parse_message(message):
    result = {}

    for item in message.split(","):
        if "=" in item:
            key, value = item.split("=", 1)
            result[key.strip()] = value.strip()

    return result


print(f"\nConnecting to ANC-01 on {PORT}...")

try:
    connection = serial.Serial(PORT, BAUD_RATE, timeout=1)
    time.sleep(2)

    print("GATEWAY CONNECTED!")
    print("Waiting for sensor observations...\n")

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as file:

        writer = csv.DictWriter(file, fieldnames=columns)

        if file.tell() == 0:
            writer.writeheader()

        sender_ip = ""
        sender_port = ""

        while True:
            line = connection.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if line.startswith("Sender IP:"):
                sender_ip = line.split(":", 1)[1].strip()

            elif line.startswith("Sender Port:"):
                sender_port = line.split(":", 1)[1].strip()

            elif line.startswith("Message:"):
                message = line.split(":", 1)[1].strip()
                data = parse_message(message)

                if "SENSOR_ID" not in data:
                    continue

                record = {
                    "Timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "Sender_IP": sender_ip,
                    "Sender_Port": sender_port,
                    "Sensor_ID": data.get("SENSOR_ID", ""),
                    "Location": data.get("LOCATION", ""),
                    "MAC": data.get("MAC", ""),
                    "RSSI_dBm": data.get("RSSI", ""),
                    "Channel": data.get("CHANNEL", ""),
                    "Frame_Type": data.get("FRAME_TYPE", ""),
                    "Raw_Message": message
                }

                writer.writerow(record)
                file.flush()

                print(
                    f"RECEIVED: {record['Sensor_ID']} | "
                    f"{record['Location']} | "
                    f"{record['MAC']} | "
                    f"RSSI: {record['RSSI_dBm']} dBm"
                )

except serial.SerialException as error:
    print("\nSERIAL CONNECTION ERROR:", error)
    print("Check COM6 and close Arduino Serial Monitor.")

except KeyboardInterrupt:
    print("\nDATA COLLECTION STOPPED BY USER.")

finally:
    try:
        connection.close()
    except:
        pass

    print("\nLogger stopped.")
    print("Output:", OUTPUT_FILE)
