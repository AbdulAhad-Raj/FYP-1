SENTINEL-X
Module 4.1 —  System Architecture

Project Title: Sentinel-X: Secure AI-Powered Wi-Fi Indoor Positioning and Intelligent Asset Tracking System

1. System Overview

The Sentinel-X system will use Wi-Fi signal observations from multiple ESP32 sensor nodes to estimate the indoor locations of registered Wi-Fi-enabled devices, such as laptops, desktop computers and smartphones.

The system will not require an individual ESP32 tracking tag to be physically attached to every asset.

Registered devices will connect to an authorized common Wi-Fi network. The system will use available network connection information and observations from four ESP32 sensor nodes to identify active devices and estimate their indoor positions.

2. Hardware Architecture

The planned hardware consists of:

- Four ESP32-WROOM-32 sensor nodes.
- One existing Wi-Fi router or authorized Wi-Fi access point.
- One central gateway or computer-based backend.
- Multiple Wi-Fi-enabled devices to be tracked.
- A computer running the Sentinel-X backend and dashboard.

The four ESP32 sensors will be installed at known positions around the laboratory:

- Sensor 01 — North
- Sensor 02 — South
- Sensor 03 — East
- Sensor 04 — West

The role of the fifth ESP32 board will be finalized after the communication and gateway design is tested.

3. Wi-Fi Device Detection

The system will identify registered devices using available and authorized network connection information.

Router client information or connection events will be used as the preferred source for detecting device connections and disconnections when accessible.

ESP32 sensors will collect observable Wi-Fi frame information and RSSI measurements. The system will evaluate whether device identifiers can be consistently observed.

MAC randomization, device sleep behaviour, network restrictions and incomplete packet reception will be considered during implementation.

4. Four-Sensor RSSI Collection

Each ESP32 sensor will collect available Wi-Fi signal observations from tracked devices.

Each observation should contain relevant fields such as:

- Timestamp
- Sensor ID
- Device identifier, when observable
- RSSI in dBm
- Wi-Fi channel
- Other available frame information

The sensor observations will be transferred to a central processing system.

The system will account for the possibility that not every sensor observes every transmission.

5. Indoor Positioning

A new multi-sensor positioning model will be developed for Sentinel-X.

The model will use RSSI observations from the four sensor locations as positioning features.

Known laboratory reference positions will be used to collect calibration data and train and evaluate the positioning model.

The intended output will include estimated indoor coordinates or laboratory areas.

The system may also calculate approximate direction and displacement, such as movement towards the east or south.

Positioning accuracy and confidence will be evaluated experimentally.

6. Asset Registration

Registered assets will be stored in an asset registry.

Each asset will have a unique system identifier and an associated observable network identity where available.

The registry will support device identification, tracking status and dashboard selection.

7. Tracking Database

The backend will store:

- Registered asset information
- Device detection events
- Sensor RSSI observations
- Estimated device coordinates
- Position timestamps
- Online/offline status
- Historical estimated positions

This information will support movement history and path visualization.

8. Live Monitoring Dashboard

The Sentinel-X dashboard will provide a visual interface for monitoring registered assets.

Planned dashboard features include:

- Laboratory floor plan
- Manually mapped walls, doors, furniture and obstacles
- Registered asset selection
- Current estimated device positions
- Online/offline status
- Estimated coordinates and direction
- Historical movement paths
- Last detected timestamps
- Positioning confidence or uncertainty information

The dashboard will update device markers as new position estimates become available.

9. Portability and Deployment

The system will be developed and tested in the home environment before deployment in the university laboratory.

Separate configuration and positioning calibration profiles will be maintained for different environments.

University deployment will require authorized network access and verification of Wi-Fi compatibility, network restrictions and sensor communication.

The positioning model will be tested and recalibrated using measurements from the deployment environment when necessary.

10. Security and Privacy

The system will operate only on networks and devices for which permission has been obtained.

Device identifiers and tracking records will be handled securely.

Network credentials will be stored separately from public source code, and access to the dashboard and tracking database will be controlled.

11. Implementation Sequence

The revised Module 4 implementation will follow these stages:

1. Revised System Architecture
2. Wi-Fi Device Detection and Identification
3. Four-Sensor RSSI Data Collection
4. Asset Registration and Device Mapping
5. Indoor Positioning Model and Calibration
6. Tracking Database and Movement History
7. Live Monitoring Dashboard
8. Complete System Testing and Evaluation
