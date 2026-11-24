
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent

files = [
    "01_consolidated_raw_observations",
    "02_synchronized_four_sensor_fingerprints",
    "03_sensor_coverage_data_quality_report",
    "04_coordinate_labelled_calibration_dataset"
]

for filename in files:
    path = folder / filename

    print("\n" + "=" * 60)
    print("FILE:", filename)

    if not path.exists():
        print("FILE NOT FOUND - check the filename.")
        continue

    df = pd.read_csv(path)

    print("Total rows:", len(df))
    print("Columns:", list(df.columns))

    if "Sensor_ID" in df.columns:
        print("Sensor IDs:")
        print(df["Sensor_ID"].value_counts(dropna=False))

    if "Location" in df.columns:
        print("Sensor locations:")
        print(df["Location"].value_counts(dropna=False))

    if "MAC" in df.columns:
        target = df[
            df["MAC"].astype(str).str.strip().str.upper()
            == "B2:BF:3F:73:01:38"
        ]
        print("NOTE 10 observations:", len(target))

    if "Timestamp" in df.columns:
        timestamps = pd.to_datetime(
            df["Timestamp"], errors="coerce"
        )
        print("Valid timestamps:", timestamps.notna().sum())
        print("First timestamp:", timestamps.min())
        print("Last timestamp:", timestamps.max())

    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))

print("\nINSPECTION COMPLETE")
