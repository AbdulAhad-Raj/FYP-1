Sentinel-X — Module 1: IoT Hardware & ESP32 Setup
Detailed Phase Summary
1. Overview of the phas
Module 1 of the Sentinel-X project focuses on preparing the hardware and software environment required for the indoor positioning and cybersecurity system. The main objective is to establish communication between the computer and ESP32 development boards, verify that the boards can execute custom firmware, and prepare the foundation for Wi-Fi signal-strength measurements.

The initial phase introduces the ESP32 hardware architecture, Arduino IDE, ESP32 board support, serial communication, and the project folder structure. It follows a step-by-step engineering approach in which each component must be configured, tested, and verified before proceeding to the next stage.

Important status note: The instructions and code for the initial setup have been defined, but the conversation does not confirm which steps you have physically completed. Therefore, the summary below documents the work planned and the expected results without claiming that unverified hardware tests have passed.
2. Project hardware architecture
The initial Sentinel-X design uses five ESP32 development boards. One board acts as a tracking tag, while the remaining four act as anchor nodes.
Device	Assigned role	Device ID	Main responsibility
ESP32 1	Tracking tag	TAG-01	Transmits identifiable Wi-Fi signals
ESP32 2	Anchor node	ANCHOR-01	Detects the tag and measures RSSI
ESP32 3	Anchor node	ANCHOR-02	Detects the tag and measures RSSI
ESP32 4	Anchor node	ANCHOR-03	Detects the tag and measures RSSI
ESP32 5	Anchor node	ANCHOR-04	Detects the tag and measures RSSI

TAG-01 — Tracking Tag

Broadcasts an identifiable Wi-Fi signal

Wireless signal detection

ANCHOR-01

Scans and records RSSI


ANCHOR-02

Scans and records RSSI


ANCHOR-03

Scans and records RSSI


ANCHOR-04

Scans and records RSSI



Future data collection and ML pipeline

RSSI dataset → preprocessing → positioning model

Planned architecture. The anchor-to-tag detection and machine-learning pipeline still require implementation and testing.
How the architecture works
1. The tracking tag transmits a recognizable Wi-Fi signal.
2. Each anchor scans for that signal and identifies the tracking tag.
3. The anchors record the received signal strength, known as RSSI.
4. The measurements are collected and organized into a dataset.
5. Later modules will use the RSSI measurements to estimate the indoor location of the tag using machine learning.
RSSI stands for Received Signal Strength Indicator. It is commonly reported in dBm. Values closer to zero generally indicate a stronger signal; for example, −40 dBm is stronger than −75 dBm.

RSSI is affected by walls, distance, interference, device orientation, and reflections. Therefore, it cannot provide a consistently accurate distance measurement on its own. Calibration, fingerprinting, and filtering will be important in later phases.
3. Software environment preparation
The planned software environment consists of the following components.
Component	Purpose
Arduino IDE 2	Write, compile, and upload firmware
ESP32 board package	Add ESP32 board definitions and compilation support
USB data cable	Connect an ESP32 to the computer
USB-to-serial driver, if needed	Allow Windows to communicate with the development board
Serial Monitor	Display diagnostic messages and sensor/network measurements

Arduino IDE installation
The first setup task is to install Arduino IDE for Windows using the official Arduino software page.

Installation procedure:
1. Open the official Arduino download page.
2. Download the Windows version of Arduino IDE.
3. Run the installer and complete the installation.
4. Launch Arduino IDE.
5. Confirm that the application opens successfully.
Official resource: Arduino IDE download
ESP32 board support installation
Arduino IDE requires the ESP32 board package to compile and upload programs for ESP32 devices.

The configured board package URL is:
https://espressif.github.io/arduino-esp32/package_esp32_index.json


The installation procedure is:
1. Open Arduino IDE.
2. Navigate to File → Preferences.
3. Add the URL to Additional Boards Manager URLs.
4. Open Tools → Board → Boards Manager.
5. Search for esp32.
6. Select the package published by Espressif Systems.
7. Install the package and wait for completion.
Official resource: Espressif ESP32 Arduino installation guide

This package enables the IDE to recognize supported ESP32 board targets and compile the firmware using the appropriate tools and libraries.
4. First ESP32 connection and communication test
The initial hardware test uses only one ESP32 board. The other four boards are not configured until the first board has passed the initial checks.

The planned connection procedure is:
1. Connect the ESP32 to the computer using a USB data cable.
2. Allow Windows to detect the device.
3. Open Arduino IDE.
4. Select Tools → Board and choose the appropriate ESP32 board profile, initially ESP32 Dev Module if suitable for the hardware.
5. Open Tools → Port.
6. Select the COM port associated with the connected board.
If no COM port appears, possible causes include a power-only USB cable, a missing USB-to-serial driver, a faulty USB port, or a board connection issue.

The selected board profile and COM port must match the actual hardware before uploading firmware.
5. First firmware program: ESP32 initialization
The first program is designed to verify the basic development workflow without introducing Wi-Fi or machine-learning complexity.

The firmware initializes serial communication at 115200 baud and repeatedly prints a status message.
void setup() {
  Serial.begin(115200);

  Serial.println();
  Serial.println("==========================");
  Serial.println("SENTINEL-X PROJECT");
  Serial.println("ESP32 INITIALIZATION");
  Serial.println("==========================");
}

void loop() {
  Serial.println("ESP32 is working successfully!");

  delay(2000);
}


Explanation of the program
- setup() executes once after the ESP32 starts or resets.
- Serial.begin(115200) initializes serial communication at 115200 bits per second.
- Serial.println() displays text in the Serial Monitor.
- loop() runs repeatedly after setup() finishes.
- delay(2000) pauses execution for approximately two seconds between messages.
Firmware upload procedure
1. Create a new sketch in Arduino IDE.
2. Replace the default code with the program above.
3. Save it as esp32_test.ino.
4. Click Verify to compile the code.
5. Resolve any compilation errors.
6. Click Upload to transfer the compiled firmware to the ESP32.
7. Open Tools → Serial Monitor.
8. Set the baud rate to 115200.
Expected output
==========================
SENTINEL-X PROJECT
ESP32 INITIALIZATION
==========================
ESP32 is working successfully!
ESP32 is working successfully!
ESP32 is working successfully!


The status message should continue appearing approximately every two seconds.

Verification criterion: If the program compiles, uploads successfully, and the expected messages appear repeatedly in the Serial Monitor, the initial firmware test has passed. This verifies the basic programming and serial communication workflow; it does not yet verify Wi-Fi operation or wireless tag detection.
6. Project folder structure
A standard folder structure has been defined to keep firmware, experimental data, software modules, and documentation organized.
Sentinel-X/
│
├── firmware/
│   ├── esp32_test/
│   │   └── esp32_test.ino
│   ├── wifi_connection_test/
│   ├── tracking_tag/
│   └── anchor_node/
│
├── data/
│   └── raw/
│
├── backend/
├── ml/
├── frontend/
│
└── documentation/
    ├── hardware_setup.md
    └── test_results.csv


Each directory has a specific purpose:
- firmware/esp32_test/ stores the initial ESP32 test program.
- firmware/wifi_connection_test/ will contain the Wi-Fi connectivity test.
- firmware/tracking_tag/ will contain the tracking tag firmware.
- firmware/anchor_node/ will contain the anchor scanning firmware.
- data/raw/ will store original RSSI measurements.
- backend/ is reserved for future data processing and communication services.
- ml/ is reserved for positioning and anomaly-detection models.
- frontend/ is reserved for the future monitoring dashboard.
- documentation/ stores hardware configuration details and test results.
The folder structure is a project organization plan. Its presence on the computer still needs to be verified separately.
7. Work completed in the planning and design phase
The following elements have been specified for Module 1.
Hardware roles defined

One tracking tag and four anchor nodes have been assigned device IDs.



Software requirements identified

Arduino IDE, ESP32 board support, USB connectivity, and Serial Monitor.



Initial firmware prepared

A basic program is ready to test compilation, uploading, and serial output.



Project structure designed

Directories for firmware, data, backend, ML, frontend, and documentation have been planned.



These are confirmed design and preparation outcomes. The physical installation, board detection, firmware upload, and serial output remain unverified unless you have completed them and confirmed the results.
8. Remaining practical work in Module 1
The module will progress in the following order:
1. Confirm the first ESP32 test. Verify that the board is detected, the firmware uploads, and the Serial Monitor displays the expected messages.
2. Test Wi-Fi connectivity. Configure the ESP32 to connect to the existing Wi-Fi network and print its connection status and assigned IP address. Keep network credentials private.
3. Configure TAG-01. Develop firmware that transmits an identifiable Wi-Fi signal, using a defined identifier such as a device-specific SSID or other suitable discovery mechanism.
4. Configure the four anchor nodes. Scan for the tag and record its identifier, RSSI, anchor ID, and timestamp where supported.
5. Validate detection. Confirm that the anchors can detect the tag and produce repeatable measurements. Test changes in signal strength at different locations.
6. Save test results. Record the configuration, observed output, errors, fixes, and RSSI samples in the project documentation.
One technical distinction is important: simply connecting every board to the same Wi-Fi network does not automatically make every board detect the tag. The tracking tag and anchor firmware must implement a compatible discovery and measurement method. The precise method will depend on the ESP32 model and the Wi-Fi scanning capabilities supported by its firmware.
9. Final phase summary
Module 1 establishes the foundation for the Sentinel-X indoor positioning project. Its design defines the roles of the five ESP32 boards, identifies the required development software, prepares an initial firmware test, and establishes a consistent project directory structure.

The immediate engineering milestone is to confirm that one ESP32 can be programmed reliably through Arduino IDE. Once that test is successful, the work can proceed to Wi-Fi connectivity, tracking tag configuration, anchor scanning, RSSI collection, and dataset preparation.

The output of this phase will ultimately be a verified hardware setup with identifiable wireless devices and reproducible RSSI measurements. Those measurements will support later positioning work involving fingerprinting, Kalman filtering, machine learning, and cybersecurity monitoring.
