*************Configurtion of the Anchor node***************

#include <WiFi.h>

const char* DEVICE_NAME = "Sentinel-X-Anchor-01";

void setup() {
  Serial.begin(115200);
  delay(1000);

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(500);

  Serial.println();
  Serial.println("================================");
  Serial.println("       SENTINEL-X TEST");
  Serial.println("================================");

  Serial.print("Device name: ");
  Serial.println(DEVICE_NAME);

  Serial.print("ESP32 MAC address: ");
  Serial.println(WiFi.macAddress());

  Serial.println("Wi-Fi scanner initialized.");
}

void loop() {
  Serial.println();
  Serial.println("Scanning nearby Wi-Fi networks...");

  int count = WiFi.scanNetworks(false, true);

  if (count < 0) {
    Serial.println("Scan failed. Retrying shortly.");
  } else if (count == 0) {
    Serial.println("No networks found.");
  } else {
    Serial.printf("Networks found: %d\n", count);
    Serial.println("SSID | RSSI (dBm) | Channel | Encryption");

    for (int i = 0; i < count; i++) {
      Serial.printf(
        "%s | %d | %d | %s\n",
        WiFi.SSID(i).c_str(),
        WiFi.RSSI(i),
        WiFi.channel(i),
        WiFi.encryptionType(i) == WIFI_AUTH_OPEN
          ? "Open"
          : "Secured"
      );
    }
  }

  WiFi.scanDelete();
  delay(3000);
