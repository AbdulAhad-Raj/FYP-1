
import serial
import csv
import os
from datetime import datetime

# ==========================================
# SENTINEL-X MODULE 2.2
# PYTHON SERIAL DATA LOGGER
# ==========================================

# Change this to your actual ANC-01 COM port
SERIAL_PORT = "COM6"

# Communication speed must match Arduino
BAUD_RATE = 115200

# CSV output file
CSV_FILE = "sentinel_x_rssi.csv"

# ==========================================
# CREATE CSV FILE
# ==========================================

file_exists = os.path.exists(CSV_FILE)

csv_file = open(
    CSV_FILE,
    mode="a",
    newline="",
    encoding="utf-8"
)

csv_writer = csv.writer(csv_file)

# Write headings only when creating a new file
if not file_exists or os.path.getsize(CSV_FILE) == 0:

    csv_writer.writerow([
        "Timestamp",
        "Anchor_ID",
        "Tag_ID",
        "RSSI_dBm",
        "Channel",
        "BSSID",
        "Elapsed_ms"
    ])

    csv_file.flush()

# ==========================================
# CONNECT TO ESP32
# ==========================================

try:

    print("======================================")
    print("       SENTINEL-X DATA LOGGER")
    print("======================================")

    print("Connecting to:", SERIAL_PORT)

    esp32 = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=1
    )

    print("Connected successfully!")
    print("Waiting for RSSI measurements...")
    print("Press CTRL+C to stop logging.")
    print("--------------------------------------")

    # ======================================
    # READ SERIAL DATA
    # ======================================

    while True:

        line = esp32.readline().decode(
            "utf-8",
            errors="replace"
        ).strip()

        if not line:
            continue

        # Ignore the Arduino CSV header
        if line.startswith("ANCHOR_ID"):
            continue

        # Ignore scan errors and non-data messages
        if line.startswith("SCAN_ERROR"):
            print("Warning: ESP32 scan error")
            continue

        # Split the incoming CSV-style record
        values = line.split(",")

        # Each measurement must contain 6 fields
        if len(values) != 6:
            continue

        anchor_id = values[0]
        tag_id = values[1]

        try:
            rssi = int(values[2])
            channel = int(values[3])
            bssid = values[4]
            elapsed_ms = int(values[5])

        except ValueError:
            continue

        # Validate the incoming tag and anchor
        if anchor_id != "ANC-01":
            continue

        if tag_id not in [
            "TAG-01",
            "TAG-02",
            "TAG-03",
            "TAG-04"
        ]:
            continue

        # Host computer timestamp
        timestamp = datetime.now().astimezone().isoformat(
            timespec="milliseconds"
        )

        # Write measurement into CSV
        csv_writer.writerow([
            timestamp,
            anchor_id,
            tag_id,
            rssi,
            channel,
            bssid,
            elapsed_ms
        ])

        # Save data immediately
        csv_file.flush()

        print(
            f"{timestamp} | {tag_id} | "
            f"RSSI: {rssi} dBm | Channel: {channel}"
        )

except KeyboardInterrupt:

    print("\nData collection stopped by user.")

except serial.SerialException as error:

    print("\nSerial connection error:", error)

except Exception as error:

    print("\nUnexpected error:", error)

finally:

    # Close serial connection if it was opened
    if "esp32" in locals() and esp32.is_open:
        esp32.close()

    csv_file.close()

    print("CSV file saved.")
    print("Sentinel-X logger closed.")
