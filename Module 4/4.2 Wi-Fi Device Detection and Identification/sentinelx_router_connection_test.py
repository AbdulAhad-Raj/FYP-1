
import requests
import time

router = "http://192.168.1.1"

session = requests.Session()

headers = {
    "Accept": "application/json, text/javascript, */*",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/157.0.0.0 Safari/537.36"
}

try:
    # Step 1: Open the router's main page
    page = session.get(
        router + "/index_main_CM",
        timeout=10
    )

    print("MAIN PAGE STATUS:", page.status_code)
    print("MAIN PAGE LENGTH:", len(page.text))
    print("SESSION COOKIE NAMES:", list(session.cookies.keys()))

    # Step 2: Request the connected-device information
    headers["Referer"] = router + "/index_main_CM"

    response = session.get(
        router + "/cgi-bin/statslan_CM.cgi",
        headers=headers,
        params={"_": str(int(time.time() * 1000))},
        timeout=10
    )

    print("\nDEVICE REQUEST STATUS:", response.status_code)
    print("CONTENT TYPE:", response.headers.get("Content-Type"))
    print("RESPONSE LENGTH:", len(response.text))
    print("RAW RESPONSE:", repr(response.text))

    if response.text.strip():
        print("\nRESPONSE CONTENT:")
        print(response.text)

except requests.RequestException as error:
    print("REQUEST ERROR:", error)
