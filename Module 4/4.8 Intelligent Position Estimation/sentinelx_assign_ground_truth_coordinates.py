
import pandas as pd
from pathlib import Path

# ==========================================
# SENTINEL-X MODULE 4.8
# GROUND-TRUTH COORDINATE ASSIGNMENT
# ==========================================

folder = Path(__file__).parent

input_file = folder / "04_coordinate_labelled_calibration_dataset.csv"

output_file = folder / "05_final_coordinate_labelled_calibration_dataset.csv"

TARGET_MAC = "B2:BF:3F:73:01:38"

# Confirmed phone coordinates in metres
POSITION_COORDINATES = {
    "CENTRE": (0.00, 0.00),
    "NORTH":  (0.00, 0.23),
    "SOUTH":  (0.00, -0.23),
    "EAST":   (0.23, 0.00),
    "WEST":   (-0.23, 0.00)
}

RSSI_COLUMNS = [
    "RSSI_SENSOR_01_dBm",
    "RSSI_SENSOR_02_dBm",
    "RSSI_SENSOR_03_dBm",
    "RSSI_SENSOR_04_dBm"
]

# ==========================================
# LOAD EXISTING DATASET
# ==========================================

print("=" * 65)
print("SENTINEL-X GROUND-TRUTH COORDINATE ASSIGNMENT")
print("=" * 65)

if not input_file.exists():
    raise FileNotFoundError(
        f"Input file not found: {input_file}"
    )

df = pd.read_csv(input_file)

print("Input rows:", len(df))

# ==========================================
# VERIFY REQUIRED COLUMNS
# ==========================================

required_columns = [
    "Ground_Truth_Position",
    "MAC",
    *RSSI_COLUMNS
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns missing: {missing_columns}"
    )

# ==========================================
# VERIFY TARGET DEVICE
# ==========================================

df["MAC"] = (
    df["MAC"].astype(str).str.strip().str.upper()
)

wrong_mac_rows = df[df["MAC"] != TARGET_MAC]

if len(wrong_mac_rows) > 0:
    raise ValueError(
        f"Found {len(wrong_mac_rows)} rows with an unexpected MAC. "
        "Review the dataset before continuing."
    )

print("Target MAC verified:", TARGET_MAC)

# ==========================================
# NORMALIZE POSITION LABELS
# ==========================================

df["Ground_Truth_Position"] = (
    df["Ground_Truth_Position"]
    .astype(str)
    .str.strip()
    .str.upper()
)

unknown_positions = sorted(
    set(df["Ground_Truth_Position"].unique())
    - set(POSITION_COORDINATES.keys())
)

if unknown_positions:
    raise ValueError(
        f"Unexpected position labels: {unknown_positions}"
    )

# ==========================================
# ASSIGN X AND Y COORDINATES
# ==========================================

df["X_m"] = df["Ground_Truth_Position"].map(
    lambda position: POSITION_COORDINATES[position][0]
)

df["Y_m"] = df["Ground_Truth_Position"].map(
    lambda position: POSITION_COORDINATES[position][1]
)

df["Coordinate_Status"] = "ASSIGNED_FROM_MEASURED_GEOMETRY"

# ==========================================
# CHECK RSSI COMPLETENESS
# ==========================================

missing_rssi = df[RSSI_COLUMNS].isna().sum()

print("\nMissing RSSI readings:")
print(missing_rssi.to_string())

if df[RSSI_COLUMNS].isna().any().any():
    raise ValueError(
        "Some fingerprints have missing RSSI readings. "
        "Do not use this dataset for KNN until reviewed."
    )

# ==========================================
# POSITION AND COORDINATE SUMMARY
# ==========================================

print("\nGround-truth position counts:")

print(
    df["Ground_Truth_Position"]
    .value_counts()
    .reindex(POSITION_COORDINATES.keys(), fill_value=0)
    .to_string()
)

print("\nCoordinate summary:")

summary = (
    df.groupby(
        ["Ground_Truth_Position", "X_m", "Y_m"]
    )
    .size()
    .reset_index(name="Fingerprint_Count")
)

print(summary.to_string(index=False))

# ==========================================
# FINAL VALIDATION
# ==========================================

if df[["X_m", "Y_m"]].isna().any().any():
    raise ValueError("Coordinate assignment is incomplete.")

if df.duplicated().sum() > 0:
    print("\nWARNING: Duplicate rows remain:",
          df.duplicated().sum())

# ==========================================
# SAVE AS A NEW FILE
# ==========================================

df.to_csv(output_file, index=False)

print("\n" + "=" * 65)
print("COORDINATE ASSIGNMENT COMPLETED")
print("=" * 65)

print("Output file:", output_file.name)
print("Total fingerprints:", len(df))
print("Missing coordinates:",
      df[["X_m", "Y_m"]].isna().sum().sum())

print("\nOriginal input file was not modified.")
print("KNN has NOT been trained.")
