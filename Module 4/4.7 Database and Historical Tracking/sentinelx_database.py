
import sqlite3
import pandas as pd
from pathlib import Path

# ============================================================
# SENTINEL-X MODULE 4.7
# DATABASE AND HISTORICAL TRACKING
# ============================================================

BASE = Path(__file__).parent

SOURCE_FILE = (
    BASE.parent
    / "4.6 Asset identification"
    / "sentinelx_observation_asset_matching_results.csv"
)

DATABASE_FILE = BASE / "sentinelx_tracking.db"

print("=" * 65)
print("SENTINEL-X MODULE 4.7")
print("DATABASE AND HISTORICAL TRACKING")
print("=" * 65)

# ------------------------------------------------------------
# 1. CHECK SOURCE FILE
# ------------------------------------------------------------

if not SOURCE_FILE.exists():
    raise FileNotFoundError(
        f"Source CSV not found:\n{SOURCE_FILE}"
    )

data = pd.read_csv(SOURCE_FILE)

print("\nSOURCE FILE LOADED")
print("TOTAL SOURCE RECORDS:", len(data))

# Ensure expected columns exist
required_columns = [
    "Timestamp",
    "Sensor_ID",
    "Location",
    "MAC_Normalized",
    "RSSI_dBm",
    "Asset_ID",
    "Asset_Name",
    "Asset_Status"
]

missing = [
    column for column in required_columns
    if column not in data.columns
]

if missing:
    raise ValueError(
        f"Missing required CSV columns: {missing}"
    )

# Normalize values
for column in [
    "Sensor_ID",
    "Location",
    "MAC_Normalized",
    "Asset_ID",
    "Asset_Name",
    "Asset_Status"
]:
    data[column] = data[column].fillna("").astype(str).str.strip()

data["MAC_Normalized"] = data["MAC_Normalized"].str.upper()
data["Asset_Status"] = data["Asset_Status"].str.upper()

data["RSSI_dBm"] = pd.to_numeric(
    data["RSSI_dBm"], errors="coerce"
)

# ------------------------------------------------------------
# 2. CONNECT TO SQLITE DATABASE
# ------------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)
cursor = connection.cursor()

# Enable foreign key support
cursor.execute("PRAGMA foreign_keys = ON")

# ------------------------------------------------------------
# 3. CREATE DATABASE TABLES
# ------------------------------------------------------------

cursor.executescript("""
DROP TABLE IF EXISTS observations;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS assets;

CREATE TABLE assets (
    asset_id TEXT PRIMARY KEY,
    asset_name TEXT,
    registered_mac TEXT,
    asset_status TEXT
);

CREATE TABLE devices (
    mac_address TEXT PRIMARY KEY,
    asset_id TEXT,
    asset_name TEXT,
    device_class TEXT,
    first_seen TEXT,
    last_seen TEXT,
    observation_count INTEGER
);

CREATE TABLE observations (
    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    sender_ip TEXT,
    sender_port TEXT,
    sensor_id TEXT,
    location TEXT,
    mac_address TEXT,
    rssi_dbm REAL,
    channel TEXT,
    frame_type TEXT,
    asset_id TEXT,
    asset_name TEXT,
    asset_status TEXT,
    raw_message TEXT
);

CREATE INDEX idx_observations_mac
ON observations(mac_address);

CREATE INDEX idx_observations_timestamp
ON observations(timestamp);

CREATE INDEX idx_observations_sensor
ON observations(sensor_id);

CREATE INDEX idx_observations_status
ON observations(asset_status);
""")

# ------------------------------------------------------------
# 4. INSERT REGISTERED ASSETS
# ------------------------------------------------------------

registered_data = data[
    data["Asset_Status"] == "REGISTERED"
].copy()

assets = registered_data[
    ["Asset_ID", "Asset_Name", "MAC_Normalized"]
].drop_duplicates(subset=["Asset_ID"])

for _, row in assets.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO assets
        (asset_id, asset_name, registered_mac, asset_status)
        VALUES (?, ?, ?, ?)
    """, (
        row["Asset_ID"],
        row["Asset_Name"],
        row["MAC_Normalized"],
        "REGISTERED"
    ))

# ------------------------------------------------------------
# 5. INSERT DEVICE SUMMARY
# ------------------------------------------------------------

device_summary = data.groupby(
    "MAC_Normalized", dropna=False
).agg(
    asset_id=("Asset_ID", "first"),
    asset_name=("Asset_Name", "first"),
    device_class=("Asset_Status", "first"),
    first_seen=("Timestamp", "min"),
    last_seen=("Timestamp", "max"),
    observation_count=("MAC_Normalized", "size")
).reset_index()

for _, row in device_summary.iterrows():
    if not row["MAC_Normalized"]:
        continue

    cursor.execute("""
        INSERT OR REPLACE INTO devices
        (mac_address, asset_id, asset_name, device_class,
         first_seen, last_seen, observation_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        row["MAC_Normalized"],
        row["asset_id"],
        row["asset_name"],
        row["device_class"],
        str(row["first_seen"]),
        str(row["last_seen"]),
        int(row["observation_count"])
    ))

# ------------------------------------------------------------
# 6. INSERT ALL SENSOR OBSERVATIONS
# ------------------------------------------------------------

def get_value(row, column):
    value = row.get(column, None)

    if pd.isna(value):
        return None

    return str(value) if column != "RSSI_dBm" else float(value)


observation_records = []

for _, row in data.iterrows():
    observation_records.append((
        get_value(row, "Timestamp"),
        get_value(row, "Sender_IP"),
        get_value(row, "Sender_Port"),
        get_value(row, "Sensor_ID"),
        get_value(row, "Location"),
        get_value(row, "MAC_Normalized"),
        get_value(row, "RSSI_dBm"),
        get_value(row, "Channel"),
        get_value(row, "Frame_Type"),
        get_value(row, "Asset_ID"),
        get_value(row, "Asset_Name"),
        get_value(row, "Asset_Status"),
        get_value(row, "Raw_Message")
    ))

cursor.executemany("""
    INSERT INTO observations (
        timestamp,
        sender_ip,
        sender_port,
        sensor_id,
        location,
        mac_address,
        rssi_dbm,
        channel,
        frame_type,
        asset_id,
        asset_name,
        asset_status,
        raw_message
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", observation_records)

# ------------------------------------------------------------
# 7. COMMIT DATABASE
# ------------------------------------------------------------

connection.commit()

# ------------------------------------------------------------
# 8. VERIFY DATABASE CONTENTS
# ------------------------------------------------------------

print("\n" + "=" * 65)
print("DATABASE VERIFICATION")
print("=" * 65)

for table in ["assets", "devices", "observations"]:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table.upper()} RECORDS: {count}")

print("\nCLASSIFICATION SUMMARY:")

cursor.execute("""
    SELECT asset_status, COUNT(*)
    FROM observations
    GROUP BY asset_status
    ORDER BY asset_status
""")

for status, count in cursor.fetchall():
    print(f"{status}: {count}")

print("\nSENSOR OBSERVATION SUMMARY:")

cursor.execute("""
    SELECT sensor_id, location, COUNT(*)
    FROM observations
    GROUP BY sensor_id, location
    ORDER BY sensor_id
""")

for sensor, location, count in cursor.fetchall():
    print(f"{sensor} | {location} | {count} observations")

# Verify total
cursor.execute("SELECT COUNT(*) FROM observations")
database_total = cursor.fetchone()[0]

print("\nSOURCE RECORDS:", len(data))
print("DATABASE OBSERVATIONS:", database_total)

if database_total == len(data):
    print("\nDATABASE VALIDATION: SUCCESS")
else:
    print("\nDATABASE VALIDATION: FAILED")

connection.close()

print("\nDATABASE LOCATION:")
print(DATABASE_FILE)

print("\nMODULE 4.7 DATABASE CREATION COMPLETED.")
