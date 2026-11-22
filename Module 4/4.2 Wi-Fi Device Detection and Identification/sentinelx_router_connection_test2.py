
import requests
import json
import csv
import time
from datetime import datetime

print("=" * 60)
print("SENTINEL-X MODULE 4.2")
print("ROUTER DEVICE DETECTION")
print("=" * 60)

ROUTER_URL = "http://192.168.1.1/cgi-bin/statslan_CM.cgi"

# Reproduce the headers from the successful cURL request
headers = {
    "Accept": "application/json, text/javascript, */*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Referer": "http://192.168.1.1/index_main_CM",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/157.0.0.0 Safari/537.36"
    ),
    "X-Requested-With": "XMLHttpRequest"
}

try:
    params = {"_": str(int(time.time() * 1000))}

    response = requests.get(
        ROUTER_URL,
        headers=headers,
        params=params,
        timeout=15
    )

    print("\nHTTP STATUS:", response.status_code)
    print("CONTENT TYPE:", response.headers.get("Content-Type"))
    print("RESPONSE LENGTH:", len(response.content))

    response.raise_for_status()

    if not response.content.strip():
        raise ValueError("Router returned an empty response.")

    data = response.json()

    if not data.get("RETURN", {}).get("success"):
        raise ValueError("Router reported an unsuccessful request.")

    stats = data["STATSLAN"]

    def get_values(field):
        return stats.get(field, "").split("&")

    ips = get_values("statslan_IPstr")
    hosts = get_values("statslan_Hoststr")
    macs = get_values("statslan_MACstr")
    types = get_values("statslan_DEVICEstr")
    modes = get_values("statslan_MODEstr")
    ports = get_values("statslan_PORT")
    leases = get_values("statslan_LeaseTimestr")
    signals = get_values("statslan_ReceivedSignalstr")
    rates = get_values("statslan_NegotiationRatestr")

    devices = []

    for i, ip in enumerate(ips):
        if not ip or ip == "NULL":
            continue

        def value_at(values):
            if i < len(values) and values[i] not in ("", "NULL"):
                return values[i]
            return ""

        device = {
            "Timestamp": datetime.now().isoformat(timespec="seconds"),
            "IP_Address": ip,
            "Hostname": value_at(hosts),
            "MAC_Address": value_at(macs),
            "Device_Type": value_at(types),
            "Mode": value_at(modes),
            "Port": value_at(ports),
            "Lease_Time": value_at(leases),
            "Router_RSSI_dBm": value_at(signals),
            "Negotiation_Rate": value_at(rates)
        }

        devices.append(device)

    if not devices:
        raise ValueError("No populated device records were returned.")

    print("\nCONNECTED DEVICES FOUND:", len(devices))
    print("-" * 60)

    for device in devices:
        print("Hostname:", device["Hostname"] or "Not provided")
        print("IP:", device["IP_Address"])
        print("MAC:", device["MAC_Address"])
        print("Type:", device["Device_Type"])
        print("Router RSSI:", device["Router_RSSI_dBm"], "dBm")
        print("-" * 60)

    filename = "sentinelx_router_devices.csv"

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=devices[0].keys()
        )
        writer.writeheader()
        writer.writerows(devices)

    print("\nSUCCESS: DEVICE DATA SAVED")
    print("File:", filename)

except requests.RequestException as error:
    print("\nNETWORK ERROR:", error)

except (ValueError, KeyError, json.JSONDecodeError) as error:
    print("\nDATA PROCESSING ERROR:", error)

except Exception as error:
    print("\nUNEXPECTED ERROR:", error)

print("\nTEST FINISHED")
