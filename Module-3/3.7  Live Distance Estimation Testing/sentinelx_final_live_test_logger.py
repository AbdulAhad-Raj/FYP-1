
import os
import re
import time
import joblib
import serial
import numpy as np
import pandas as pd

from pathlib import Path
from datetime import datetime

# ==================================================
# SENTINEL-X FINAL LIVE DISTANCE TEST
# ==================================================

FOLDER = Path(__file__).parent

MODEL_FILE = FOLDER / "sentinel_x_random_forest.pkl"

SERIAL_PORT = "COM6"
BAUD_RATE = 115200

# Actual distances measured using measuring tape
ACTUAL_DISTANCES = {
    "TAG-01": 1.0,
    "TAG-02": 2.0,
    "TAG-03": 3.0,
    "TAG-04": 4.0
}

OUTPUT_FILE = FOLDER / (
    "sentinelx_final_live_test_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
    + ".csv"
)

print("=" * 55)
print("SENTINEL-X FINAL LIVE DISTANCE TEST")
print("=" * 55)

# --------------------------------------------------
# 1. LOAD TRAINED MODEL BUNDLE
# --------------------------------------------------

if not MODEL_FILE.exists():
    raise FileNotFoundError(
        f"Model not found: {MODEL_FILE}"
    )

bundle = joblib.load(MODEL_FILE)

if not isinstance(bundle, dict):
    raise TypeError(
        "Unexpected model file format. "
        "Expected a dictionary saved by the training script."
    )

model = bundle["model"]
feature_columns = bundle["feature_columns"]

print("\nMODEL LOADED SUCCESSFULLY")
print("Model type:", type(model).__name__)
print("Training readings:", bundle["training_readings"])
print("Testing readings:", bundle["testing_readings"])
print("Input features:", feature_columns)

# --------------------------------------------------
# 2. NORMALIZE TAG IDENTIFIERS
# --------------------------------------------------

def normalize_tag(value):

    value = value.strip().upper()

    match = re.search(
        r"(?:SX[_-]?)?TAG[_-]?0?([1-4])",
        value
    )

    if match:
        return "TAG-0" + match.group(1)

    return None


# --------------------------------------------------
# 3. PREPARE INPUT EXACTLY LIKE TRAINING
# --------------------------------------------------

def prepare_model_input(tag_id, rssi):

    row = {}

    for column in feature_columns:

        if column == "RSSI_dBm":

            row[column] = float(rssi)

        elif column.startswith("Tag_ID_"):

            encoded_tag = column.replace(
                "Tag_ID_", "", 1
            )

            row[column] = (
                1 if encoded_tag == tag_id else 0
            )

        else:

            raise ValueError(
                "Unknown model feature: " + column
            )

    if "RSSI_dBm" not in feature_columns:
        raise ValueError(
            "RSSI_dBm feature is missing from the model."
        )

    return pd.DataFrame(
        [[row[column] for column in feature_columns]],
        columns=feature_columns
    )


# --------------------------------------------------
# 4. PREPARE CSV
# --------------------------------------------------

columns = [
    "Timestamp",
    "Anchor_ID",
    "Tag_ID",
    "RSSI_dBm",
    "WiFi_Channel",
    "BSSID",
    "Elapsed_ms",
    "Actual_Distance_m",
    "Predicted_Distance_m",
    "Absolute_Error_m",
    "Within_0.5m",
    "Within_1m"
]

records = []

# --------------------------------------------------
# 5. CONNECT TO ANC-01
# --------------------------------------------------

print("\nCONNECTING TO ESP32 ANCHOR...")
print("Serial port:", SERIAL_PORT)

try:

    with serial.Serial(
        SERIAL_PORT,
        BAUD_RATE,
        timeout=2
    ) as ser:

        time.sleep(2)
        ser.reset_input_buffer()

        print("\nSERIAL CONNECTION SUCCESSFUL")
        print("\nLIVE DATA COLLECTION STARTED")
        print("-" * 55)

        print("TAG-01 actual distance: 1 metre")
        print("TAG-02 actual distance: 2 metres")
        print("TAG-03 actual distance: 3 metres")
        print("TAG-04 actual distance: 4 metres")

        print("\nPress CTRL+C to stop collection.")
        print("-" * 55)

        while True:

            raw_line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not raw_line:
                continue

            parts = [
                item.strip()
                for item in raw_line.split(",")
            ]

            # Expected anchor output:
            # ANCHOR_ID,TAG_ID,RSSI_DBM,
            # CHANNEL,BSSID,ELAPSED_MS

            if len(parts) != 6:
                continue

            anchor_id = parts[0]
            tag_id = normalize_tag(parts[1])

            if tag_id not in ACTUAL_DISTANCES:
                continue

            try:

                rssi = float(parts[2])
                channel = parts[3]
                bssid = parts[4]
                elapsed_ms = parts[5]

                actual_distance = ACTUAL_DISTANCES[tag_id]

                # Prepare the same features used in training
                model_input = prepare_model_input(
                    tag_id,
                    rssi
                )

                # Live distance prediction
                predicted_distance = float(
                    model.predict(model_input)[0]
                )

                error = abs(
                    actual_distance - predicted_distance
                )

                record = {
                    "Timestamp": datetime.now().isoformat(
                        timespec="seconds"
                    ),
                    "Anchor_ID": anchor_id,
                    "Tag_ID": tag_id,
                    "RSSI_dBm": rssi,
                    "WiFi_Channel": channel,
                    "BSSID": bssid,
                    "Elapsed_ms": elapsed_ms,
                    "Actual_Distance_m": actual_distance,
                    "Predicted_Distance_m": round(
                        predicted_distance, 4
                    ),
                    "Absolute_Error_m": round(error, 4),
                    "Within_0.5m": error <= 0.5,
                    "Within_1m": error <= 1.0
                }

                records.append(record)

                print(
                    f"{tag_id} | "
                    f"RSSI: {rssi:.1f} dBm | "
                    f"Actual: {actual_distance:.1f} m | "
                    f"Predicted: {predicted_distance:.3f} m | "
                    f"Error: {error:.3f} m"
                )

                # Save after every valid reading
                pd.DataFrame(
                    records,
                    columns=columns
                ).to_csv(
                    OUTPUT_FILE,
                    index=False
                )

            except (ValueError, TypeError) as error:

                print("Reading skipped:", error)

except KeyboardInterrupt:

    print("\n\nLIVE COLLECTION STOPPED.")

except serial.SerialException as error:

    print("\nSERIAL CONNECTION ERROR:", error)

finally:

    # --------------------------------------------------
    # 6. FINAL EVALUATION
    # --------------------------------------------------

    if records:

        df = pd.DataFrame(
            records,
            columns=columns
        )

        df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print("\n" + "=" * 55)
        print("FINAL LIVE TEST SUMMARY")
        print("=" * 55)

        print("Total readings:", len(df))

        print("\nREADINGS PER TAG")

        print(
            df["Tag_ID"]
            .value_counts()
            .sort_index()
        )

        print("\nTAG-WISE PERFORMANCE")

        for tag in sorted(ACTUAL_DISTANCES):

            tag_data = df[df["Tag_ID"] == tag]

            if len(tag_data) == 0:
                print(tag, ": No readings")
                continue

            tag_mae = tag_data[
                "Absolute_Error_m"
            ].mean()

            print(
                f"{tag}: "
                f"Readings={len(tag_data)}, "
                f"MAE={tag_mae:.3f} m"
            )

        errors = df["Absolute_Error_m"]

        mae = errors.mean()
        rmse = np.sqrt(np.mean(errors ** 2))

        print("\nOVERALL PERFORMANCE")

        print(f"MAE: {mae:.3f} m")
        print(f"RMSE: {rmse:.3f} m")

        print(
            "Within 0.5m:",
            f"{(errors <= 0.5).mean() * 100:.2f}%"
        )

        print(
            "Within 1m:",
            f"{(errors <= 1.0).mean() * 100:.2f}%"
        )

        print("\nSAVED CSV:")
        print(OUTPUT_FILE)

        print("\nFINAL LIVE TEST DATA SAVED SUCCESSFULLY.")

    else:

        print("\nNo valid readings were collected.")
        print("No final evaluation was generated.")

    print("=" * 55)
