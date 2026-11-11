
import serial
import pickle
import pandas as pd
import time

# ==========================================
# SENTINEL-X MODULE 3.5
# LIVE RSSI-BASED DISTANCE ESTIMATION
# ==========================================

SERIAL_PORT = "COM6"
BAUD_RATE = 115200

MODEL_FILE = "sentinel_x_session1_random_forest.pkl"

print("=" * 60)
print("SENTINEL-X LIVE DISTANCE ESTIMATION")
print("=" * 60)

# 1. Load trained Random Forest model
print("\nLoading trained Random Forest model...")

try:
    with open(MODEL_FILE, "rb") as file:
        model_bundle = pickle.load(file)

    model = model_bundle["model"]
    feature_columns = model_bundle["feature_columns"]

    print("Model loaded successfully.")

except Exception as error:
    print("MODEL LOADING ERROR:", error)
    raise SystemExit

# 2. Connect to ESP32 anchor
print("\nConnecting to ANC-01...")
print("Serial port:", SERIAL_PORT)

try:
    esp32 = serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=2
    )

    time.sleep(2)
    esp32.reset_input_buffer()

    print("ANC-01 connected successfully.")

except Exception as error:
    print("SERIAL CONNECTION ERROR:", error)
    print("Check COM port and close Arduino Serial Monitor.")
    raise SystemExit

# 3. Keep track of latest estimates
latest_distances = {}

print("\nWaiting for live RSSI readings...")
print("Press CTRL+C to stop.")
print("-" * 60)

try:
    while True:

        raw_line = esp32.readline().decode(
            "utf-8", errors="ignore"
        ).strip()

        if not raw_line:
            continue

        # Display incoming serial data
        parts = raw_line.split(",")

        # Expected format:
        # ANC-01,TAG-01,-67,6,BSSID,12500

        if len(parts) != 6:
            continue

        anchor_id = parts[0].strip()
        tag_id = parts[1].strip()

        try:
            rssi = float(parts[2].strip())
            channel = int(parts[3].strip())
            bssid = parts[4].strip()
            elapsed_ms = int(parts[5].strip())

        except ValueError:
            continue

        # Accept only known tags
        if anchor_id != "ANC-01":
            continue

        if tag_id not in [
            "TAG-01",
            "TAG-02",
            "TAG-03",
            "TAG-04"
        ]:
            continue

        # Basic RSSI validity check
        if not (-100 <= rssi <= 0):
            continue

        # 4. Prepare model input
        input_data = {
            "RSSI_dBm": rssi,
            "Tag_ID_TAG-01": int(tag_id == "TAG-01"),
            "Tag_ID_TAG-02": int(tag_id == "TAG-02"),
            "Tag_ID_TAG-03": int(tag_id == "TAG-03"),
            "Tag_ID_TAG-04": int(tag_id == "TAG-04")
        }

        X_live = pd.DataFrame(
            [input_data]
        ).reindex(
            columns=feature_columns,
            fill_value=0
        )

        # 5. Predict distance
        estimated_distance = model.predict(X_live)[0]

        # 6. Store latest estimate
        latest_distances[tag_id] = estimated_distance

        # 7. Display result
        print(
            f"Tag: {tag_id} | "
            f"RSSI: {rssi:.0f} dBm | "
            f"Channel: {channel} | "
            f"Estimated Distance: {estimated_distance:.2f} m"
        )

except KeyboardInterrupt:
    print("\n\nStopping live estimation...")

finally:
    esp32.close()
    print("Serial connection closed.")
    print("SENTINEL-X LIVE ESTIMATION STOPPED.")
