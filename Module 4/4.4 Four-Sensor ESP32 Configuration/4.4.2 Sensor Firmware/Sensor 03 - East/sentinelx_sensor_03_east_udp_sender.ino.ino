
#include <WiFi.h>
#include <WiFiUdp.h>

// Router credentials
const char* WIFI_SSID = "SultanAsgher";
const char* WIFI_PASSWORD = "Sultan@123";

// Central gateway details
const char* GATEWAY_IP = "192.168.1.27";
const unsigned int GATEWAY_PORT = 4210;

// Sensor identity
const char* SENSOR_ID = "SENSOR-03";
const char* SENSOR_LOCATION = "EAST";

// UDP configuration
const unsigned int LOCAL_PORT = 4213;

WiFiUDP udp;

unsigned long lastSendTime = 0;
unsigned long packetNumber = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("SENTINEL-X SENSOR 03");
  Serial.println("LOCATION: EAST");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to router");

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

  Serial.println("UDP SENDER READY!");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Router disconnected. Reconnecting...");
    WiFi.reconnect();
    delay(1000);
    return;
  }

  if (millis() - lastSendTime >= 5000) {
    lastSendTime = millis();
    packetNumber++;

    char message[150];

    snprintf(
      message,
      sizeof(message),
      "SENSOR_ID=%s,LOCATION=%s,PACKET=%lu,STATUS=ONLINE",
      SENSOR_ID,
      SENSOR_LOCATION,
      packetNumber
    );

    udp.beginPacket(GATEWAY_IP, GATEWAY_PORT);
    udp.print(message);
    int result = udp.endPacket();

    Serial.print("Packet ");
    Serial.print(packetNumber);
    Serial.print(": ");

    if (result == 1) {
      Serial.println("MESSAGE SENT");
    } else {
      Serial.println("SEND FAILED");
    }
  }
}
