SENTINEL-X
MODULE 4: INTELLIGENT ASSET TRACKING

1. Objective
Develop an intelligent asset tracking system
using ESP32 Wi-Fi tags, RSSI measurements,
and the trained Random Forest distance model.

2. Hardware
- ANC-01: ESP32 Anchor
- TAG-01: ESP32 Tracking Tag
- TAG-02: ESP32 Tracking Tag
- TAG-03: ESP32 Tracking Tag
- TAG-04: ESP32 Tracking Tag

3. Software
- Python
- Pandas
- NumPy
- Scikit-learn
- Joblib
- Existing trained Random Forest model

4. Main Functions
- Asset identification
- Live tag detection
- RSSI collection
- Distance estimation
- Proximity classification
- Detection status monitoring
- Last detected time
- Asset tracking records
- Live monitoring dashboard

5. Tracking Architecture
ESP32 Tags -> ANC-01 -> Python Tracking Engine
-> Random Forest Model -> Asset Tracking System
-> Monitoring Dashboard

6. Tracking Method
Distance-based proximity tracking using
one ESP32 anchor and four ESP32 tracking tags.
