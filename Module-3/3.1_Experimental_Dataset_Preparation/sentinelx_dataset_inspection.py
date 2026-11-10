
import pandas as pd
import os

# Calibration dataset
file_name = "sentinel_x_calibration.csv"

print("SENTINEL-X MODULE 3")
print("Dataset Inspection")
print("-" * 40)

if not os.path.exists(file_name):
    print("ERROR: Calibration CSV file not found.")
    print("Place this script in the folder containing the CSV file.")
    raise SystemExit

# Load dataset
df = pd.read_csv(file_name)

# Required columns
required_columns = ["Distance_m", "Tag_ID", "RSSI_dBm"]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    print("ERROR: Missing columns:", missing)
    raise SystemExit

# Convert measurement columns to numeric
df["Distance_m"] = pd.to_numeric(
    df["Distance_m"], errors="coerce"
)

df["RSSI_dBm"] = pd.to_numeric(
    df["RSSI_dBm"], errors="coerce"
)

# Remove incomplete or invalid records
df = df.dropna(subset=required_columns)

# Display dataset information
print("\nTotal valid readings:", len(df))

print("\nTags found:")
print(df["Tag_ID"].unique())

print("\nDistances found (metres):")
print(sorted(df["Distance_m"].unique()))

print("\nReadings per tag and distance:")
print(
    df.groupby(["Tag_ID", "Distance_m"])
      .size()
      .to_string()
)

print("\nRSSI statistical summary:")
print(df["RSSI_dBm"].describe())

# Save cleaned dataset
df.to_csv("sentinel_x_clean_dataset.csv", index=False)

print("\nClean dataset saved successfully:")
print("sentinel_x_clean_dataset.csv")
