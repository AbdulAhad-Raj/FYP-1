
import pandas as pd
import os

print("SENTINEL-X MODULE 3")
print("Feature Preparation")
print("-" * 40)

file_name = "sentinel_x_clean_dataset.csv"

if not os.path.exists(file_name):
    print("ERROR: Clean dataset not found.")
    raise SystemExit

df = pd.read_csv(file_name)

required = ["Distance_m", "Tag_ID", "RSSI_dBm"]

if not all(col in df.columns for col in required):
    print("ERROR: Required columns are missing.")
    raise SystemExit

# Keep only required columns
df = df[required].copy()

# One-hot encode tag identity
df = pd.get_dummies(
    df,
    columns=["Tag_ID"],
    dtype=int
)

# Separate input features and target
feature_columns = [
    col for col in df.columns
    if col != "Distance_m"
]

X = df[feature_columns]
y = df["Distance_m"]

# Combine features and target for inspection
prepared = X.copy()
prepared["Distance_m"] = y

prepared.to_csv(
    "sentinel_x_prepared_dataset.csv",
    index=False
)

print("\nInput features:")
print(feature_columns)

print("\nPrepared dataset preview:")
print(prepared.head(10).to_string(index=False))

print("\nTotal records:", len(prepared))
print("\nPrepared dataset saved successfully:")
print("sentinel_x_prepared_dataset.csv")
