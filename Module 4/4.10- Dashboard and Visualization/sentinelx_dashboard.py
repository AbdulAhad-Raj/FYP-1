
from flask import Flask, jsonify, render_template
import sqlite3
from pathlib import Path

# ============================================================
# SENTINEL-X DASHBOARD BACKEND
# ============================================================

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent

DATABASE_FILE = (
    BASE_DIR.parent
    / "4.7 Database and Historical Tracking"
    / "sentinelx_tracking.db"
)

# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_database_connection():
    if not DATABASE_FILE.exists():
        raise FileNotFoundError(
            f"Sentinel-X database not found: {DATABASE_FILE}"
        )

    connection = sqlite3.connect(str(DATABASE_FILE))
    connection.row_factory = sqlite3.Row
    return connection


# ============================================================
# DASHBOARD HOME PAGE
# ============================================================

@app.route("/")
def dashboard():
    return render_template("index.html")


# ============================================================
# DATABASE STATUS AND SUMMARY
# ============================================================

@app.route("/api/summary")
def get_summary():

    connection = get_database_connection()

    try:
        position_count = connection.execute(
            "SELECT COUNT(*) FROM asset_positions"
        ).fetchone()[0]

        asset_count = connection.execute(
            "SELECT COUNT(*) FROM assets"
        ).fetchone()[0]

        latest_position = connection.execute("""
            SELECT
                timestamp,
                asset_id,
                mac_address,
                x_m,
                y_m,
                sensor_01_rssi,
                sensor_02_rssi,
                sensor_03_rssi,
                sensor_04_rssi
            FROM asset_positions
            ORDER BY position_id DESC
            LIMIT 1
        """).fetchone()

        return jsonify({
            "status": "success",
            "total_positions": position_count,
            "total_assets": asset_count,
            "latest_position": (
                dict(latest_position)
                if latest_position else None
            )
        })

    finally:
        connection.close()


# ============================================================
# POSITION HISTORY
# ============================================================

@app.route("/api/positions")
def get_positions():

    connection = get_database_connection()

    try:
        rows = connection.execute("""
            SELECT
                position_id,
                timestamp,
                asset_id,
                mac_address,
                x_m,
                y_m,
                sensor_01_rssi,
                sensor_02_rssi,
                sensor_03_rssi,
                sensor_04_rssi
            FROM asset_positions
            ORDER BY position_id DESC
            LIMIT 100
        """).fetchall()

        return jsonify({
            "status": "success",
            "positions": [dict(row) for row in rows]
        })

    finally:
        connection.close()


# ============================================================
# REGISTERED ASSETS
# ============================================================

@app.route("/api/assets")
def get_assets():

    connection = get_database_connection()

    try:
        rows = connection.execute("""
            SELECT
                asset_id,
                asset_name,
                registered_mac,
                asset_status
            FROM assets
        """).fetchall()

        return jsonify({
            "status": "success",
            "assets": [dict(row) for row in rows]
        })

    finally:
        connection.close()


# ============================================================
# SENSOR RSSI INFORMATION
# ============================================================

@app.route("/api/sensors")
def get_sensors():

    connection = get_database_connection()

    try:
        latest = connection.execute("""
            SELECT
                sensor_01_rssi,
                sensor_02_rssi,
                sensor_03_rssi,
                sensor_04_rssi,
                timestamp
            FROM asset_positions
            ORDER BY position_id DESC
            LIMIT 1
        """).fetchone()

        if latest is None:
            return jsonify({
                "status": "success",
                "sensors": []
            })

        sensors = [
            {
                "sensor_id": "SENSOR-01",
                "location": "North",
                "rssi": latest["sensor_01_rssi"]
            },
            {
                "sensor_id": "SENSOR-02",
                "location": "South",
                "rssi": latest["sensor_02_rssi"]
            },
            {
                "sensor_id": "SENSOR-03",
                "location": "East",
                "rssi": latest["sensor_03_rssi"]
            },
            {
                "sensor_id": "SENSOR-04",
                "location": "West",
                "rssi": latest["sensor_04_rssi"]
            }
        ]

        return jsonify({
            "status": "success",
            "timestamp": latest["timestamp"],
            "sensors": sensors
        })

    finally:
        connection.close()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("SENTINEL-X ASSET TRACKING DASHBOARD")
    print("=" * 60)

    print("Database:", DATABASE_FILE)
    print("Database exists:", DATABASE_FILE.exists())

    print("Starting Flask server...")
    print("Dashboard: http://127.0.0.1:5000")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
