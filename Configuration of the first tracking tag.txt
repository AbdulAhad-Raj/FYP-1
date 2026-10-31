************************Configuration of the first tracking tag*********************



#include <WiFi.h>

// Sentinel-X Tracking Tag Configuration
const char* TAG_ID = "TAG-01";
const char* TAG_SSID = "SX_TAG_01";
const char* TAG_PASSWORD = "SentinelTag26";

// Wi-Fi configuration
const int WIFI_CHANNEL = 6;
const int MAX_CONNECTIONS = 4;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("   SENTINEL-X TRACKING TAG");
  Serial.println("================================");

  Serial.print("Device ID: ");
  Serial.println(TAG_ID);

  // Start ESP32 in Access Point mode
  WiFi.mode(WIFI_AP);

  // Start the tracking tag's Wi-Fi network
  bool started = WiFi.softAP(
    TAG_SSID,
    TAG_PASSWORD,
    WIFI_CHANNEL,
    false,
    MAX_CONNECTIONS
  );

  if (started) {
    Serial.println("Tracking tag started successfully!");

    Serial.print("Tag SSID: ");
    Serial.println(TAG_SSID);

    Serial.print("Tag MAC address: ");
    Serial.println(WiFi.softAPmacAddress());

    Serial.print("Wi-Fi channel: ");
    Serial.println(WIFI_CHANNEL);

    Serial.print("Tag IP address: ");
    Serial.println(WiFi.softAPIP());

    Serial.println("Broadcasting Wi-Fi signal...");
  } else {
    Serial.println("ERROR: Failed to start tracking tag.");
  }
}

void loop() {
  delay(5000);

  Serial.println("TAG-01 is broadcasting...");
}

