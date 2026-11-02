
import pandas as pd
import numpy as np
import os

# -----------------------------------------
# SENTINEL-X MODULE 2.3
# RSSI DATA PREPROCESSING
# -----------------------------------------

INPUT_FILE = "../FYP-1 Module 2 RSSI collection/sentinel_x_rssi.csv"

OUTPUT_FILE = "sentinel_x_cleaned.csv"

print("=" * 45)
print("       SENTINEL-X DATA PREPROCESSING")
print("=" * 45)

# 1. Check whether input file exists
if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"Input CSV not found: {INPUT_FILE}"
    )

# 2. Load raw RSSI data
data = pd.read_csv(INPUT_FILE)

print("\nOriginal records:", len(data))

# 3. Check required columns
required_columns = [
    "Timestamp",
    "Anchor_ID",
    "Tag_ID",
    "RSSI_dBm",
    "Channel",
    "BSSID",
    "Elapsed_ms"
]

missing_columns = [
    column for column in required_columns
    if column not in data.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# 4. Remove duplicate records
data = data.drop_duplicates()

# 5. Convert numerical columns
data["RSSI_dBm"] = pd.to_numeric(
    data["RSSI_dBm"], errors="coerce"
)

data["Channel"] = pd.to_numeric(
    data["Channel"], errors="coerce"
)

data["Elapsed_ms"] = pd.to_numeric(
    data["Elapsed_ms"], errors="coerce"
)

# 6. Remove records with missing essential values
data = data.dropna(
    subset=[
        "Timestamp",
        "Anchor_ID",
        "Tag_ID",
        "RSSI_dBm",
        "Channel",
        "BSSID",
        "Elapsed_ms"
    ]
)

# 7. Keep only the expected anchor and tags
valid_tags = [
    "TAG-01",
    "TAG-02",
    "TAG-03",
    "TAG-04"
]

data = data[
    (data["Anchor_ID"] == "ANC-01") &
    (data["Tag_ID"].isin(valid_tags))
]

# 8. Filter unrealistic RSSI readings
data = data[
    (data["RSSI_dBm"] >= -100) &
    (data["RSSI_dBm"] <= 0)
]

# 9. Sort measurements by tag and time
data["Timestamp"] = pd.to_datetime(
    data["Timestamp"], errors="coerce"
)

data = data.dropna(subset=["Timestamp"])

data = data.sort_values(
    by=["Tag_ID", "Timestamp"]
)

# 10. Apply moving average filtering
data["RSSI_Filtered"] = (
    data.groupby("Tag_ID")["RSSI_dBm"]
    .transform(
        lambda values: values.rolling(
            window=5,
            min_periods=1
        ).mean()
    )
)

# 11. Save cleaned data
data.to_csv(OUTPUT_FILE, index=False)

print("\nPreprocessing completed successfully!")
print("Cleaned records:", len(data))
print("Output file:", OUTPUT_FILE)

print("\nRecords per tag:")
print(data["Tag_ID"].value_counts().sort_index())

print("\nSample cleaned data:")
print(
    data[
        ["Tag_ID", "RSSI_dBm", "RSSI_Filtered"]
    ].head(10).to_string(index=False)
)
