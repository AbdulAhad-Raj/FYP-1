
import serial
import csv
import os
import time
from datetime import datetime

# -------------------------------
# SENTINEL-X EXPANDED DATA LOGGER
# -------------------------------

PORT = "COM6"
BAUD_RATE = 115200

OUTPUT_FILE = "sentinel_x_calibration_expanded.csv"

# Select experiment details
tag_id = input("Enter Tag ID (TAG-01 to TAG-04): ").strip().upper()
distance = input("Enter measured distance in metres: ").strip()
session = input("Enter session number (1, 2, etc.): ").strip()

if tag_id not in ["TAG-01", "TAG-02", "TAG-03", "TAG-04"]:
    raise SystemExit("Invalid tag ID.")

try:
    distance = float(distance)
    session = int(session)
except ValueError:
    raise SystemExit("Distance or session number is invalid.")

if distance not in [1, 2, 3, 4, 5] or session < 1:
    raise SystemExit("Use a distance from 1 to 5 and session >= 1.")

# Create CSV with header if it doesn't exist
file_exists = os.path.exists(OUTPUT_FILE)

with open(OUTPUT_FILE, "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists or os.path.getsize(OUTPUT_FILE) == 0:
        writer.writerow([
            "Timestamp",
            "Distance_m",
            "Tag_ID",
            "RSSI_dBm",
            "Session_ID"
        ])

    print("\nConnecting to ESP32...")
    print("Port:", PORT)
    print("Press CTRL+C after collecting 50 readings.")

    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=2)
        time.sleep(2)

        count = 0

        while count < 50:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if not line:
                continue

            # Expected ANC-01 CSV:
            # ANCHOR_ID,TAG_ID,RSSI_DBM,CHANNEL,BSSID,ELAPSED_MS
            parts = line.split(",")

            if len(parts) != 6:
                continue

            anchor_id = parts[0].strip()
            detected_tag = parts[1].strip()

            try:
                rssi = int(parts[2].strip())
            except ValueError:
                continue

            if anchor_id != "ANC-01" or detected_tag != tag_id:
                continue

            timestamp = datetime.now().isoformat(
                timespec="seconds"
            )

            writer.writerow([
                timestamp,
                distance,
                tag_id,
                rssi,
                session
            ])

            file.flush()
            count += 1

            print(
                f"{count}/50 | {tag_id} | "
                f"{distance} m | RSSI: {rssi} dBm"
            )

        ser.close()

        print("\nCollection completed successfully.")
        print("Saved in:", OUTPUT_FILE)

    except KeyboardInterrupt:
        print("\nCollection stopped by user.")
        if "ser" in locals() and ser.is_open:
            ser.close()

    except serial.SerialException as error:
        print("\nSerial connection error:", error)
        print("Check COM port and close Arduino Serial Monitor.")
        if "ser" in locals() and ser.is_open:
            ser.close()
