
#include <WiFi.h>

// ==========================================
// SENTINEL-X MODULE 4.4
// ==========================================

// Router credentials
const char* WIFI_SSID = "SultanAsgher";
const char* WIFI_PASSWORD = "Sultan@123";

// Sensor identification
const char* SENSOR_ID = "SENSOR-04";
const char* SENSOR_LOCATION = "West";

void setup() {

  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("========================================");
  Serial.println("       SENTINEL-X SENSOR 04");
  Serial.println("========================================");

  Serial.print("Sensor ID: ");
  Serial.println(SENSOR_ID);

  Serial.print("Location: ");
  Serial.println(SENSOR_LOCATION);

  Serial.println();
  Serial.println("Connecting to Wi-Fi router...");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 40) {

    delay(500);
    Serial.print(".");
    attempts++;

  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println();
    Serial.println("WI-FI CONNECTION SUCCESSFUL");

    Serial.print("Connected SSID: ");
    Serial.println(WiFi.SSID());

    Serial.print("Sensor IP Address: ");
    Serial.println(WiFi.localIP());

    Serial.print("Sensor MAC Address: ");
    Serial.println(WiFi.macAddress());

    Serial.print("Connected Wi-Fi Channel: ");
    Serial.println(WiFi.channel());

    Serial.print("Router Signal Strength: ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");

    Serial.println();
    Serial.println("SENSOR 04 IS CONNECTED");
    Serial.println("========================================");

  } else {

    Serial.println();
    Serial.println("WI-FI CONNECTION FAILED");
    Serial.println("Check router credentials and signal.");

  }
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) {

    Serial.print("SENSOR-04 ONLINE | IP: ");
    Serial.print(WiFi.localIP());

    Serial.print(" | Router RSSI: ");
    Serial.print(WiFi.RSSI());

    Serial.println(" dBm");

  } else {

    Serial.println("Wi-Fi disconnected. Reconnecting...");
    WiFi.reconnect();

  }

  delay(5000);
}
