
#include <WiFi.h>
#include "esp_wifi.h"

#define SENSOR_ID "SENSOR-01"
#define SENSOR_LOCATION "NORTH"
#define MONITOR_CHANNEL 12

volatile unsigned long totalFrames = 0;
volatile unsigned long lastReportTime = 0;

void wifiPromiscuousCallback(
  void *buffer,
  wifi_promiscuous_pkt_type_t type
) {
  if (type != WIFI_PKT_MGMT && type != WIFI_PKT_DATA) {
    return;
  }

  wifi_promiscuous_pkt_t *packet =
    (wifi_promiscuous_pkt_t *)buffer;

  const uint8_t *mac =
    packet->payload + 10;

  int rssi = packet->rx_ctrl.rssi;
  int channel = packet->rx_ctrl.channel;

  char macAddress[18];

  snprintf(
    macAddress,
    sizeof(macAddress),
    "%02X:%02X:%02X:%02X:%02X:%02X",
    mac[0], mac[1], mac[2],
    mac[3], mac[4], mac[5]
  );

  totalFrames++;

  Serial.printf(
    "SENSOR=%s,LOCATION=%s,MAC=%s,RSSI=%d,CHANNEL=%d\n",
    SENSOR_ID,
    SENSOR_LOCATION,
    macAddress,
    rssi,
    channel
  );
}

void setup() {
  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("================================");
  Serial.println("SENTINEL-X WIFI MONITOR");
  Serial.println("================================");

  WiFi.mode(WIFI_STA);
  WiFi.disconnect();

  esp_wifi_set_promiscuous(false);

  esp_err_t result = esp_wifi_set_channel(
    MONITOR_CHANNEL,
    WIFI_SECOND_CHAN_NONE
  );

  if (result != ESP_OK) {
    Serial.println("CHANNEL CONFIGURATION FAILED");
    return;
  }

  Serial.print("Sensor ID: ");
  Serial.println(SENSOR_ID);

  Serial.print("Location: ");
  Serial.println(SENSOR_LOCATION);

  Serial.print("Monitoring Channel: ");
  Serial.println(MONITOR_CHANNEL);

  esp_wifi_set_promiscuous_rx_cb(
    &wifiPromiscuousCallback
  );

  result = esp_wifi_set_promiscuous(true);

  if (result == ESP_OK) {
    Serial.println("PROMISCUOUS MODE ENABLED");
    Serial.println("MONITORING STARTED");
  } else {
    Serial.println("PROMISCUOUS MODE FAILED");
  }
}

void loop() {
  delay(10000);

  Serial.println("--------------------------------");
  Serial.print("Total frames observed: ");
  Serial.println(totalFrames);
  Serial.println("Monitoring continues...");
}
