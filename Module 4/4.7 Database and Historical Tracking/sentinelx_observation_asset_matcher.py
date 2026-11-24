
import pandas as pd
from pathlib import Path

BASE = Path(__file__).parent

OBSERVATIONS = BASE / "sentinelx_four_sensor_observations.csv"

REGISTRY = (
    BASE.parent
    / "4.3 Asset Registration and Device Mapping"
    / "sentinelx_asset_registry.csv"
)

OUTPUT = BASE / "sentinelx_observation_asset_matching_results.csv"

# ESP32 infrastructure MAC addresses
INFRASTRUCTURE = {
    "8C:94:DF:6C:2A:38": "SENSOR-01 NORTH",
    "8C:94:DF:6C:B1:0C": "SENSOR-02 SOUTH",
    "8C:94:DF:6D:99:5C": "SENSOR-03 EAST",
    "8C:94:DF:6C:9A:94": "SENSOR-04 WEST",
    "8C:94:DF:6C:A5:18": "ANC-01 GATEWAY",

    # Original ESP32 tag SoftAP MAC addresses
    "8C:94:DF:6C:2A:39": "TAG-01",
    "8C:94:DF:6C:B1:0D": "TAG-02",
    "8C:94:DF:6D:99:5D": "TAG-03",
    "8C:94:DF:6C:9A:95": "TAG-04",
}

print("=" * 60)
print("SENTINEL-X MODULE 4.6")
print("MULTI-SENSOR ASSET IDENTIFICATION")
print("=" * 60)

observations = pd.read_csv(OBSERVATIONS)
registry = pd.read_csv(REGISTRY)

# Normalize MAC addresses
observations["MAC_Normalized"] = (
    observations["MAC"].fillna("")
    .astype(str).str.strip().str.upper()
)

registry["MAC_Normalized"] = (
    registry["Registered_MAC"].fillna("")
    .astype(str).str.strip().str.upper()
)

# Match against registered assets
registered = registry[
    registry["MAC_Normalized"].ne("")
].copy()

result = observations.merge(
    registered[
        ["MAC_Normalized", "Asset_ID", "Asset_Name", "Is_Active"]
    ],
    on="MAC_Normalized",
    how="left"
)

# First classify all observations as UNKNOWN
result["Asset_Status"] = "UNKNOWN"
result["Asset_ID"] = result["Asset_ID"].fillna("UNKNOWN")
result["Asset_Name"] = result["Asset_Name"].fillna("Unknown Device")

# Identify registered devices
is_registered = result["Asset_ID"].ne("UNKNOWN")

result.loc[is_registered, "Asset_Status"] = "REGISTERED"

# Identify ESP32 infrastructure
is_infrastructure = result["MAC_Normalized"].isin(
    INFRASTRUCTURE.keys()
)

result.loc[is_infrastructure, "Asset_Status"] = "INFRASTRUCTURE"
result.loc[is_infrastructure, "Asset_ID"] = (
    result.loc[is_infrastructure, "MAC_Normalized"]
    .map(INFRASTRUCTURE)
)
result.loc[is_infrastructure, "Asset_Name"] = (
    result.loc[is_infrastructure, "MAC_Normalized"]
    .map(INFRASTRUCTURE)
)

# Save classified observations
result.to_csv(OUTPUT, index=False)

# Display classification totals
print("\nTOTAL OBSERVATIONS:", len(result))

for status in ["REGISTERED", "UNKNOWN", "INFRASTRUCTURE"]:
    count = (result["Asset_Status"] == status).sum()
    print(f"{status} OBSERVATIONS: {count}")

print("\nDEVICE IDENTIFICATION SUMMARY:")

summary = result.groupby(
    ["MAC_Normalized", "Asset_ID", "Asset_Name", "Asset_Status"]
).size().reset_index(name="Observation_Count")

print(summary.to_string(index=False))

print("\nOUTPUT SAVED:", OUTPUT)
print("\nTHREE-WAY ASSET CLASSIFICATION COMPLETED.")
