
import pandas as pd
import numpy as np
from pathlib import Path

# ==========================================
# SENTINEL-X MODULE 4.8
# FINAL DATASET VALIDATION
# ==========================================

folder = Path(__file__).parent

input_file = folder / "05_final_coordinate_labelled_calibration_dataset.csv"

df = pd.read_csv(input_file)

rssi_columns = [
    "RSSI_SENSOR_01_dBm",
    "RSSI_SENSOR_02_dBm",
    "RSSI_SENSOR_03_dBm",
    "RSSI_SENSOR_04_dBm"
]

positions = ["CENTRE", "NORTH", "SOUTH", "EAST", "WEST"]

expected_coordinates = {
    "CENTRE": (0.00, 0.00),
    "NORTH": (0.00, 0.23),
    "SOUTH": (0.00, -0.23),
    "EAST": (0.23, 0.00),
    "WEST": (-0.23, 0.00)
}

print("=" * 70)
print("SENTINEL-X FINAL CALIBRATION DATASET VALIDATION")
print("=" * 70)

# 1. Dataset dimensions
print("\n1. DATASET SIZE")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# 2. MAC validation
print("\n2. DEVICE VALIDATION")

print("Unique MAC addresses:")
print(df["MAC"].value_counts().to_string())

# 3. Position distribution
print("\n3. POSITION DISTRIBUTION")

counts = df["Ground_Truth_Position"].value_counts()

for position in positions:
    print(position, ":", counts.get(position, 0))

# 4. Coordinate validation
print("\n4. COORDINATE VALIDATION")

coordinate_errors = []

for position, expected in expected_coordinates.items():

    subset = df[
        df["Ground_Truth_Position"] == position
    ]

    if subset.empty:
        coordinate_errors.append(
            f"{position}: no fingerprints"
        )
        continue

    correct_x = np.isclose(subset["X_m"], expected[0])
    correct_y = np.isclose(subset["Y_m"], expected[1])

    if not (correct_x & correct_y).all():
        coordinate_errors.append(
            f"{position}: incorrect coordinates"
        )

    print(
        position,
        "Expected:", expected,
        "Actual:",
        (subset["X_m"].iloc[0], subset["Y_m"].iloc[0])
    )

print("Coordinate errors:", coordinate_errors)

# 5. RSSI completeness and range
print("\n5. RSSI VALIDATION")

print("Missing RSSI values:")
print(df[rssi_columns].isna().sum())

for column in rssi_columns:
    values = pd.to_numeric(df[column], errors="coerce")

    print(
        column,
        "| Min:", values.min(),
        "| Max:", values.max(),
        "| Mean:", round(values.mean(), 2),
        "| Std:", round(values.std(), 2)
    )

# 6. RSSI patterns by position
print("\n6. RSSI AVERAGES BY POSITION")

print(
    df.groupby("Ground_Truth_Position")[rssi_columns]
    .mean()
    .reindex(positions)
    .round(2)
    .to_string()
)

# 7. Duplicate checks
print("\n7. DUPLICATE CHECKS")

print("Exact duplicate rows:", df.duplicated().sum())

if "Timestamp" in df.columns:
    print(
        "Duplicate timestamps:",
        df.duplicated(
            subset=["Ground_Truth_Position", "Timestamp"]
        ).sum()
    )

# 8. Timestamp inspection
print("\n8. TIMESTAMP INSPECTION")

if "Timestamp" in df.columns:

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"], errors="coerce"
    )

    print("Invalid timestamps:", df["Timestamp"].isna().sum())
    print("First:", df["Timestamp"].min())
    print("Last:", df["Timestamp"].max())

    print("\nFingerprint counts by position and minute:")

    df["Capture_Minute"] = df["Timestamp"].dt.floor("min")

    print(
        df.groupby(
            ["Ground_Truth_Position", "Capture_Minute"]
        ).size().to_string()
    )

# 9. Feature variation
print("\n9. FEATURE VARIATION")

for column in rssi_columns:
    print(
        column,
        "Unique values:",
        df[column].nunique()
    )

# 10. Final checks
print("\n10. FINAL CHECKS")

checks = {
    "220 or more fingerprints": len(df) >= 220,
    "Only target NOTE10 MAC":
        df["MAC"].nunique() == 1
        and df["MAC"].iloc[0] == "B2:BF:3F:73:01:38",
    "All five positions present":
        set(df["Ground_Truth_Position"]) == set(positions),
    "No missing coordinates":
        not df[["X_m", "Y_m"]].isna().any().any(),
    "No missing RSSI":
        not df[rssi_columns].isna().any().any(),
    "All coordinates correct":
        len(coordinate_errors) == 0
}

for name, result in checks.items():
    print(("PASS" if result else "FAIL"), "-", name)

print("\n" + "=" * 70)
print("FINAL VALIDATION FINISHED")
print("No source dataset was modified.")
print("No KNN model was trained.")
print("=" * 70)
