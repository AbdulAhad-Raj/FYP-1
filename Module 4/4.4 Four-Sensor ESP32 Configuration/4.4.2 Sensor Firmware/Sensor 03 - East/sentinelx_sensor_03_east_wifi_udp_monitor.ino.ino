
#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_wifi.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// ========================================
// SENTINEL-X SENSOR 03
// WIFI MONITOR + UDP TRANSMISSION
// ========================================

// Router credentials
const char* WIFI_SSID = "SultanAsgher";
const char* WIFI_PASSWORD = "Sultan@123";

// Central gateway
const char* GATEWAY_IP = "192.168.1.27";
const unsigned int GATEWAY_PORT = 4210;

// Sensor identity
const char* SENSOR_ID = "SENSOR-03";
const char* SENSOR_LOCATION = "EAST";

// Local UDP port
const unsigned int LOCAL_PORT = 4211;
WiFiUDP udp;
// Observation structure
struct WiFiObservation {
  char mac[18];
  int rssi;
  int channel;
  char frameType[5];
};

QueueHandle_t observationQueue;

volatile unsigned long totalFrames = 0;

// Duplicate reporting control
struct SeenDevice {
  char mac[18];
  unsigned long lastSent;
  bool valid;
};

SeenDevice seenDevices[30];
int nextSlot = 0;

// ========================================
// PROMISCUOUS MODE CALLBACK
// ========================================

void wifiCallback(
  void *buffer,
  wifi_promiscuous_pkt_type_t type
) {
  if (type != WIFI_PKT_MGMT && type != WIFI_PKT_DATA) {
    return;
  }

  wifi_promiscuous_pkt_t *packet =
    (wifi_promiscuous_pkt_t *)buffer;

  if (packet->rx_ctrl.sig_len < 16) {
    return;
  }

  const uint8_t *mac = packet->payload + 10;

  WiFiObservation observation;

  snprintf(
    observation.mac,
    sizeof(observation.mac),
    "%02X:%02X:%02X:%02X:%02X:%02X",
    mac[0], mac[1], mac[2],
    mac[3], mac[4], mac[5]
  );

  observation.rssi = packet->rx_ctrl.rssi;
  observation.channel = packet->rx_ctrl.channel;

  if (type == WIFI_PKT_MGMT) {
    strcpy(observation.frameType, "MGMT");
  } else {
    strcpy(observation.frameType, "DATA");
  }

  totalFrames++;

  xQueueSend(observationQueue, &observation, 0);
}

// ========================================
// DUPLICATE CONTROL
// ========================================

bool shouldForward(const char* mac) {

  unsigned long now = millis();

  for (int i = 0; i < 30; i++) {

    if (
      seenDevices[i].valid &&
      strcmp(seenDevices[i].mac, mac) == 0
    ) {

      if (now - seenDevices[i].lastSent < 1000) {
        return false;
      }

      seenDevices[i].lastSent = now;
      return true;
    }
  }

  strncpy(
    seenDevices[nextSlot].mac,
    mac,
    sizeof(seenDevices[nextSlot].mac) - 1
  );

  seenDevices[nextSlot].mac[17] = '\0';
  seenDevices[nextSlot].lastSent = now;
  seenDevices[nextSlot].valid = true;

  nextSlot = (nextSlot + 1) % 30;

  return true;
}

// ========================================
// SETUP
// ========================================

void setup() {

  Serial.begin(115200);
  delay(1500);

  Serial.println();
  Serial.println("================================");
  Serial.println("SENTINEL-X SENSOR 03");
  Serial.println("WIFI MONITOR + UDP");
  Serial.println("================================");

  observationQueue = xQueueCreate(
    50,
    sizeof(WiFiObservation)
  );

  if (observationQueue == NULL) {
    Serial.println("QUEUE CREATION FAILED!");
    return;
  }

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  Serial.println("Connecting to router...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("ROUTER CONNECTED!");

  Serial.print("Sensor IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Gateway IP: ");
  Serial.println(GATEWAY_IP);

  Serial.print("Router Channel: ");
  Serial.println(WiFi.channel());

  if (!udp.begin(LOCAL_PORT)) {
    Serial.println("UDP INITIALIZATION FAILED!");
    return;
  }

  Serial.println("UDP INITIALIZED!");

  wifi_promiscuous_filter_t filter = {};

  filter.filter_mask =
    WIFI_PROMIS_FILTER_MASK_MGMT |
    WIFI_PROMIS_FILTER_MASK_DATA;

  esp_wifi_set_promiscuous_filter(&filter);

  esp_wifi_set_promiscuous_rx_cb(&wifiCallback);

  if (esp_wifi_set_promiscuous(true) == ESP_OK) {
    Serial.println("PROMISCUOUS MODE ENABLED!");
  } else {
    Serial.println("PROMISCUOUS MODE FAILED!");
    return;
  }

  Serial.println("WIFI MONITORING STARTED!");
  Serial.println("UDP TRANSMISSION STARTED!");
}

// ========================================
// MAIN LOOP
// ========================================

void loop() {

  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("ROUTER CONNECTION LOST!");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  WiFiObservation observation;

  while (
    xQueueReceive(
      observationQueue,
      &observation,
      0
    ) == pdTRUE
  ) {

    if (!shouldForward(observation.mac)) {
      continue;
    }

    char message[200];

    snprintf(
      message,
      sizeof(message),
      "SENSOR_ID=%s,LOCATION=%s,MAC=%s,RSSI=%d,CHANNEL=%d,FRAME_TYPE=%s",
      SENSOR_ID,
      SENSOR_LOCATION,
      observation.mac,
      observation.rssi,
      observation.channel,
      observation.frameType
    );

    udp.beginPacket(GATEWAY_IP, GATEWAY_PORT);
    udp.print(message);

    int result = udp.endPacket();

    if (result == 1) {
      Serial.print("OBSERVATION SENT: ");
      Serial.println(message);
    } else {
      Serial.println("UDP SEND FAILED!");
    }
  }

  delay(5);
}
