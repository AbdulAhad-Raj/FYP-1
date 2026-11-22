
import sqlite3
from pathlib import Path

# Existing Module 4.7 database
DATABASE_FILE = (
    Path("..")
    / "4.7 Database and Historical Tracking"
    / "sentinelx_tracking.db"
)

def create_position_table():

    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Existing database not found: {DATABASE_FILE}"
        )

    connection = sqlite3.connect(DATABASE_FILE)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset_positions (
            position_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            asset_id TEXT,
            mac_address TEXT NOT NULL,
            x_m REAL NOT NULL,
            y_m REAL NOT NULL,
            sensor_01_rssi REAL NOT NULL,
            sensor_02_rssi REAL NOT NULL,
            sensor_03_rssi REAL NOT NULL,
            sensor_04_rssi REAL NOT NULL,
            model_name TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_asset_positions_mac_timestamp
        ON asset_positions(mac_address, timestamp)
    """)

    connection.commit()

    print("=" * 60)
    print("SENTINEL-X LIVE POSITION DATABASE SETUP")
    print("=" * 60)

    print("Database:", DATABASE_FILE)
    print("Table: asset_positions")

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        AND name='asset_positions'
    """)

    print("Table created:", cursor.fetchone() is not None)

    cursor.execute("PRAGMA table_info(asset_positions)")

    print("\nTABLE STRUCTURE")
    for column in cursor.fetchall():
        print(column)

    connection.close()

    print("\nDATABASE SETUP COMPLETED SUCCESSFULLY.")

if __name__ == "__main__":
    create_position_table()
