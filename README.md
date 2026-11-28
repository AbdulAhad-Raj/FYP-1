
**Sentinel-X – Summary of the Four Completed Modules**
We have developed Sentinel-X through four major modules, progressing from basic Wi-Fi device detection to an intelligent indoor asset-tracking system with a live dashboard.
**Module 1: Wi-Fi Device Detection**
- Configured ESP32-WROOM-32 boards as anchor nodes and tracking tags.
- Implemented Wi-Fi scanning and RSSI-based device detection.
- Successfully detected all four tracking tags using the anchor nodes.
- Verified device MAC addresses, RSSI values, and Wi-Fi channels.
**Achievement:** Established successful wireless communication and device detection between ESP32 boards.

**Module 2: RSSI Data Collection and Preprocessing**
- Developed a Python-based RSSI data logger.
- Collected readings from four tracking tags at physical distances of 1–5 metres.
- Created structured CSV datasets.
- Used Pandas and NumPy for data inspection and preprocessing.
**Achievement:** Prepared a dataset of 2,000 RSSI readings for machine-learning development.

**Module 3: Machine Learning-Based Distance Estimation**
- Developed a Random Forest regression model.
- Used RSSI values and Tag IDs as input features.
- Trained and evaluated the model using training and testing datasets.
**- Achieved:**
  - MAE: 0.730 metres
  - RMSE: 0.929 metres
  - R²: 0.560
  - Predictions within 1 metre: 72.20%.
**Achievement:** Developed a working machine-learning model capable of estimating the approximate distance of tracking tags using Wi-Fi signal strength.

**Module 4: Intelligent Asset Tracking System**
This was our largest module, consisting of several integrated components.
- Designed the four-sensor architecture with North, South, East, and West ESP32 sensor nodes.
- Connected the sensor nodes to the existing Wi-Fi network.
- Implemented UDP communication with the central gateway.
- Registered the target mobile device as Asset_001.
- Developed observation collection, asset matching, and SQLite database storage.
- Generated 220 complete RSSI fingerprints for five indoor positions.
- Developed a KNN-based positioning model.
- Implemented Isolation Forest-based anomaly detection.
- Integrated the live positioning engine and successfully processed 60 fingerprints, saving 60 position records.
- Developed a Flask-based web dashboard displaying asset information, positioning, sensor monitoring, and position history.
**Achievement:** Successfully integrated the hardware, wireless communication, machine-learning models, database, and web dashboard into a functional indoor asset-tracking prototype.
