
import pandas as pd
from pathlib import Path

# ==========================================
# SENTINEL-X MODULE 4.8
# FOUR-FILE DATASET INSPECTION
# READ-ONLY VALIDATION
# ==========================================

FOLDER = Path(__file__).parent

TARGET_MAC = "B2:BF:3F:73:01:38"

FILES = {
    "01 RAW OBSERVATIONS":
        "01_consolidated_raw_observations.csv",

    "02 SYNCHRONIZED FINGERPRINTS":
        "02_synchronized_four_sensor_fingerprints.csv",

    "03 DATA QUALITY REPORT":
        "03_sensor_coverage_data_quality_report.csv",

    "04 COORDINATE-LABELLED DATASET":
        "04_coordinate_labelled_calibration_dataset.csv"
}

EXPECTED_SENSORS = [
    "SENSOR-01",
    "SENSOR-02",
    "SENSOR-03",
    "SENSOR-04"
]

EXPECTED_POSITIONS = [
    "CENTRE",
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST"
]

def section(title):
    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)

def find_column(df, possible_names):
    lookup = {
        str(column).strip().lower(): column
        for column in df.columns
    }

    for name in possible_names:
        if name.lower() in lookup:
            return lookup[name.lower()]

    return None

def inspect_file(title, filename):
    section(title)

    path = FOLDER / filename

    if not path.exists():
        print("FILE NOT FOUND:", filename)
        print("Check the filename and extension.")
        return

    try:
        df = pd.read_csv(path)
    except Exception as error:
        print("Could not read file:", error)
        return

    print("Filename:", filename)
    print("Total rows:", len(df))
    print("Total columns:", len(df.columns))

    print("\nCOLUMN NAMES:")
    print(list(df.columns))

    print("\nMISSING VALUES:")
    missing = df.isnull().sum()
    print(missing[missing > 0].to_string()
          if missing.sum() else "No missing values detected.")

    # MAC inspection
    mac_col = find_column(
        df, ["MAC", "BSSID", "Device_MAC", "Registered_MAC"]
    )

    if mac_col:
        mac_values = (
            df[mac_col].astype(str).str.strip().str.upper()
        )

        target = df[mac_values == TARGET_MAC]

        print("\nNOTE 10 MAC COLUMN:", mac_col)
        print("NOTE 10 matching rows:", len(target))
        print("Unique MAC addresses:", mac_values.nunique())

    else:
        print("\nMAC COLUMN NOT FOUND.")

    # Sensor inspection
    sensor_col = find_column(
        df, ["Sensor_ID", "SensorID", "Sensor"]
    )

    if sensor_col:
        print("\nSENSOR COUNTS:")
        print(df[sensor_col].value_counts(dropna=False).to_string())

        actual = set(df[sensor_col].dropna().astype(str).str.strip())
        print("Missing expected sensor IDs:",
              sorted(set(EXPECTED_SENSORS) - actual))

    # Sensor location inspection
    location_col = find_column(
        df, ["Location", "Sensor_Location"]
    )

    if location_col:
        print("\nSENSOR LOCATION COUNTS:")
        print(df[location_col].value_counts(dropna=False).to_string())

    # Position label inspection
    position_col = find_column(
        df, ["Position", "Ground_Truth_Position",
             "Phone_Position", "Position_Label"]
    )

    if position_col:
        print("\nPHONE POSITION COUNTS:")
        print(df[position_col].value_counts(dropna=False).to_string())

        actual_positions = set(
            df[position_col].dropna().astype(str).str.strip().str.upper()
        )

        print("Missing expected position labels:",
              sorted(set(EXPECTED_POSITIONS) - actual_positions))
    else:
        print("\nPHONE POSITION LABEL COLUMN NOT FOUND.")

    # Timestamp inspection
    timestamp_col = find_column(
        df, ["Timestamp", "Datetime", "Time"]
    )

    if timestamp_col:
        timestamps = pd.to_datetime(
            df[timestamp_col], errors="coerce"
        )

        print("\nTIMESTAMP INSPECTION:")
        print("Valid timestamps:", timestamps.notna().sum())
        print("Invalid timestamps:", timestamps.isna().sum())
        print("First timestamp:", timestamps.min())
        print("Last timestamp:", timestamps.max())

    else:
        print("\nTIMESTAMP COLUMN NOT FOUND.")

    # RSSI inspection
    rssi_col = find_column(
        df, ["RSSI_dBm", "RSSI", "Signal_Strength"]
    )

    if rssi_col:
        rssi = pd.to_numeric(df[rssi_col], errors="coerce")

        print("\nRSSI INSPECTION:")
        print("Valid numeric RSSI:", rssi.notna().sum())
        print("Minimum RSSI:", rssi.min())
        print("Maximum RSSI:", rssi.max())
        print("Average RSSI:", rssi.mean())

        invalid_rssi = (
            rssi.notna() & ((rssi > 0) | (rssi < -100))
        ).sum()

        print("RSSI outside -100 to 0 dBm:", invalid_rssi)

    # Coordinate inspection
    x_col = find_column(df, ["X_m", "X", "Coordinate_X"])
    y_col = find_column(df, ["Y_m", "Y", "Coordinate_Y"])

    if x_col and y_col:
        print("\nCOORDINATE INSPECTION:")
        print("X coordinate column:", x_col)
        print("Y coordinate column:", y_col)
        print("Missing X:", df[x_col].isna().sum())
        print("Missing Y:", df[y_col].isna().sum())

        print("\nCOORDINATE COMBINATIONS:")
        print(
            df.groupby([x_col, y_col], dropna=False)
            .size()
            .to_string()
        )
    else:
        print("\nX/Y COORDINATE COLUMNS NOT BOTH FOUND.")

    # Duplicate inspection
    print("\nDUPLICATE ROWS:", df.duplicated().sum())

    print("\nFIRST FIVE ROWS:")
    print(df.head().to_string(index=False))

    print("\nINSPECTION FINISHED FOR:", filename)


# ==========================================
# RUN ALL FOUR INSPECTIONS
# ==========================================

print("SENTINEL-X MODULE 4.8 DATASET INSPECTION")
print("READ-ONLY MODE - ORIGINAL FILES WILL NOT BE MODIFIED")

for title, filename in FILES.items():
    inspect_file(title, filename)

section("ALL FOUR FILES INSPECTED")

print("No files were modified.")
print("No machine-learning model was trained.")
print("KNN training remains pending validation.")
