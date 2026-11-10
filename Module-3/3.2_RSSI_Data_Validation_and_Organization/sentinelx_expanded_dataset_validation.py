
import pandas as pd
import os

FILE = "sentinel_x_calibration_expanded.csv"

print("SENTINEL-X")
print("EXPANDED DATASET VALIDATION")
print("-" * 45)

if not os.path.exists(FILE):
    raise SystemExit("ERROR: Expanded calibration CSV not found.")

df = pd.read_csv(FILE)

required = [
    "Distance_m",
    "Tag_ID",
    "RSSI_dBm",
    "Session_ID"
]

missing = [col for col in required if col not in df.columns]

if missing:
    raise SystemExit(f"Missing columns: {missing}")

# Validate data types
df["Distance_m"] = pd.to_numeric(
    df["Distance_m"], errors="coerce"
)
df["RSSI_dBm"] = pd.to_numeric(
    df["RSSI_dBm"], errors="coerce"
)
df["Session_ID"] = pd.to_numeric(
    df["Session_ID"], errors="coerce"
)

df = df.dropna(subset=required)

# Keep only expected tags and distances
valid_tags = ["TAG-01", "TAG-02", "TAG-03", "TAG-04"]
valid_distances = [1, 2, 3, 4, 5]

df = df[
    df["Tag_ID"].isin(valid_tags)
    & df["Distance_m"].isin(valid_distances)
    & (df["RSSI_dBm"] < 0)
    & (df["Session_ID"] >= 1)
].copy()

print("\nTotal valid readings:", len(df))

print("\nReadings per tag and distance:")
counts = (
    df.groupby(["Tag_ID", "Distance_m"])
      .size()
      .unstack(fill_value=0)
      .reindex(index=valid_tags, columns=valid_distances, fill_value=0)
)

print(counts.to_string())

print("\nTotal readings per tag:")
print(df.groupby("Tag_ID").size().to_string())

print("\nReadings per session:")
print(df.groupby("Session_ID").size().to_string())

print("\nRSSI statistics:")
print(df["RSSI_dBm"].describe())

print("\nMissing values:")
print(df[required].isnull().sum().to_string())

# Save validated dataset
df.to_csv("sentinel_x_validated_dataset.csv", index=False)

print("\nValidated dataset saved:")
print("sentinel_x_validated_dataset.csv")

if (counts == 0).any().any():
    print("\nWARNING: Some tag-distance combinations have no readings.")
elif (counts < 30).any().any():
    print("\nWARNING: Some combinations have fewer than 30 readings.")
else:
    print("\nAll tag-distance combinations have at least 30 readings.")

print("\nValidation completed.")
