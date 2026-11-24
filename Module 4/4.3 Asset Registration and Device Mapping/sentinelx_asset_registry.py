import csv
import re
from pathlib import Path

print("=" * 65)
print("SENTINEL-X MODULE 4.3")
print("ASSET REGISTRATION AND DEVICE MAPPING")
print("=" * 65)

# --------------------------------------------------
# 1. DEFINE FILE LOCATIONS
# --------------------------------------------------

MODULE_FOLDER = Path(__file__).resolve().parent
PROJECT_FOLDER = MODULE_FOLDER.parent

ROUTER_FILE = (
    PROJECT_FOLDER
    / "4.2 Wi-Fi Device Detection and Identification"
    / "sentinelx_router_devices.csv"
)

REGISTRY_FILE = MODULE_FOLDER / "sentinelx_asset_registry.csv"

OUTPUT_FILE = MODULE_FOLDER / "sentinelx_asset_matching_results.csv"


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def normalize_header(header):
    """Make column names easier to compare."""
    return re.sub(r"[^a-z0-9]", "", header.lower())


def find_column(fieldnames, possible_names):
    """Find a CSV column using alternative column names."""
    available = {
        normalize_header(name): name
        for name in fieldnames
        if name
    }

    for name in possible_names:
        match = available.get(normalize_header(name))
        if match:
            return match

    return None


def normalize_mac(mac):
    """Normalize MAC addresses for consistent matching."""
    return re.sub(r"[^a-fA-F0-9]", "", str(mac)).lower()


def is_active(value):
    return str(value).strip().lower() in ("true", "1", "yes", "active")


# --------------------------------------------------
# 3. CHECK REQUIRED FILES
# --------------------------------------------------

if not ROUTER_FILE.exists():
    raise FileNotFoundError(
        f"Router device file not found:\n{ROUTER_FILE}"
    )

if not REGISTRY_FILE.exists():
    raise FileNotFoundError(
        f"Asset registry file not found:\n{REGISTRY_FILE}"
    )


# --------------------------------------------------
# 4. READ THE ASSET REGISTRY
# --------------------------------------------------

with open(REGISTRY_FILE, "r", newline="", encoding="utf-8-sig") as file:
    registry_reader = csv.DictReader(file)

    if not registry_reader.fieldnames:
        raise ValueError("The asset registry CSV is empty.")

    registry_columns = registry_reader.fieldnames

    required_registry_columns = [
        "Asset_ID",
        "Asset_Name",
        "Registered_MAC",
        "Registered_Hostname",
        "Is_Active"
    ]

    missing = [
        column for column in required_registry_columns
        if column not in registry_columns
    ]

    if missing:
        raise ValueError(
            "Missing registry columns: " + ", ".join(missing)
        )

    registry = list(registry_reader)


# Build lookup tables for active assets.
assets_by_mac = {}
assets_by_hostname = {}

for asset in registry:

    if not is_active(asset.get("Is_Active", "")):
        continue

    mac = normalize_mac(asset.get("Registered_MAC", ""))
    hostname = asset.get("Registered_Hostname", "").strip().lower()

    if mac:
        assets_by_mac[mac] = asset

    if hostname:
        assets_by_hostname[hostname] = asset


# --------------------------------------------------
# 5. READ DEVICES DETECTED BY THE ROUTER
# --------------------------------------------------

with open(ROUTER_FILE, "r", newline="", encoding="utf-8-sig") as file:
    router_reader = csv.DictReader(file)

    if not router_reader.fieldnames:
        raise ValueError("The router devices CSV is empty.")

    router_columns = router_reader.fieldnames

    mac_column = find_column(
        router_columns,
        ["MAC", "MAC Address", "MAC_Address"]
    )

    hostname_column = find_column(
        router_columns,
        ["Hostname", "Host Name", "Device Name", "Name"]
    )

    ip_column = find_column(
        router_columns,
        ["IP", "IP Address", "IP_Address"]
    )

    type_column = find_column(
        router_columns,
        ["Type", "Device Type", "Device_Type"]
    )

    rssi_column = find_column(
        router_columns,
        ["Router RSSI", "Router_RSSI", "RSSI", "Signal Strength"]
    )

    if not mac_column and not hostname_column:
        raise ValueError(
            "Could not find a MAC or hostname column in the router CSV.\n"
            f"Available columns: {router_columns}"
        )

    detected_devices = list(router_reader)


# --------------------------------------------------
# 6. MATCH DETECTED DEVICES WITH REGISTERED ASSETS
# --------------------------------------------------

results = []

for device in detected_devices:

    detected_mac = (
        device.get(mac_column, "").strip()
        if mac_column else ""
    )

    detected_hostname = (
        device.get(hostname_column, "").strip()
        if hostname_column else ""
    )

    detected_ip = (
        device.get(ip_column, "").strip()
        if ip_column else ""
    )

    detected_type = (
        device.get(type_column, "").strip()
        if type_column else ""
    )

    detected_rssi = (
        device.get(rssi_column, "").strip()
        if rssi_column else ""
    )

    mac_key = normalize_mac(detected_mac)
    hostname_key = detected_hostname.lower()

    matched_asset = None
    match_method = "NONE"

    # MAC address is the primary identity.
    if mac_key and mac_key in assets_by_mac:
        matched_asset = assets_by_mac[mac_key]
        match_method = "MAC_ADDRESS"

    # Use hostname only when the router record has no MAC.
    elif not mac_key and hostname_key:
        if hostname_key in assets_by_hostname:
            matched_asset = assets_by_hostname[hostname_key]
            match_method = "HOSTNAME_ONLY"

    if matched_asset:
        detection_status = "REGISTERED"
        asset_id = matched_asset.get("Asset_ID", "")
        asset_name = matched_asset.get("Asset_Name", "")
        asset_category = matched_asset.get("Asset_Category", "")
    else:
        detection_status = "UNKNOWN"
        asset_id = ""
        asset_name = ""
        asset_category = ""

    results.append({
        "Detection_Status": detection_status,
        "Asset_ID": asset_id,
        "Asset_Name": asset_name,
        "Asset_Category": asset_category,
        "Detected_Hostname": detected_hostname,
        "Detected_MAC": detected_mac,
        "Detected_IP": detected_ip,
        "Device_Type": detected_type,
        "Router_RSSI": detected_rssi,
        "Match_Method": match_method
    })


# --------------------------------------------------
# 7. SAVE MATCHING RESULTS
# --------------------------------------------------

output_columns = [
    "Detection_Status",
    "Asset_ID",
    "Asset_Name",
    "Asset_Category",
    "Detected_Hostname",
    "Detected_MAC",
    "Detected_IP",
    "Device_Type",
    "Router_RSSI",
    "Match_Method"
]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=output_columns)
    writer.writeheader()
    writer.writerows(results)


# --------------------------------------------------
# 8. DISPLAY SUMMARY
# --------------------------------------------------

registered_count = sum(
    row["Detection_Status"] == "REGISTERED"
    for row in results
)

unknown_count = sum(
    row["Detection_Status"] == "UNKNOWN"
    for row in results
)

print("\nROUTER DEVICES DETECTED:", len(results))
print("REGISTERED ASSETS FOUND:", registered_count)
print("UNKNOWN DEVICES FOUND:", unknown_count)

print("\nDEVICE MATCHING RESULTS")
print("-" * 65)

for row in results:
    print(
        f'{row["Detection_Status"]:<12} | '
        f'{row["Detected_Hostname"]:<22} | '
        f'{row["Asset_ID"] or "Not registered"}'
    )

print("\nSUCCESS: MATCHING RESULTS SAVED")
print("File:", OUTPUT_FILE)

print("\nMODULE 4.3 MATCHING TEST FINISHED")