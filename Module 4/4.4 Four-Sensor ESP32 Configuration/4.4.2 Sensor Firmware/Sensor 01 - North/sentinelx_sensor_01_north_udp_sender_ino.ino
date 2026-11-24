
#include <WiFi.h>
#include <WiFiUdp.h>

// ==========================================
// SENTINEL-X SENSOR 01 - NORTH
// UDP DATA SENDER
// ==========================================

const char* WIFI_SSID = "SultanAsgher";
const char* WIFI_PASSWORD = "Sultan@123";

const char* SENSOR_ID = "SENSOR-01";
const char* SENSOR_LOCATION = "NORTH";

// ANC-01 central gateway
IPAddress gatewayIP(192, 168, 1, 27);

const unsigned int gatewayPort = 4210;
const unsigned int localPort = 4211;

WiFiUDP udp;

unsigned long packetNumber = 0;

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("SENTINEL-X UDP SENSOR");
  Serial.println("================================");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  Serial.println("Connecting to FiberHome router...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 40) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println("SENSOR CONNECTED!");

    Serial.print("Sensor ID: ");
    Serial.println(SENSOR_ID);

    Serial.print("Location: ");
    Serial.println(SENSOR_LOCATION);

    Serial.print("Sensor IP: ");
    Serial.println(WiFi.localIP());

    Serial.print("Gateway IP: ");
    Serial.println(gatewayIP);

    Serial.print("Gateway Port: ");
    Serial.println(gatewayPort);

    udp.begin(localPort);

    Serial.println("UDP SENDER READY!");

  } else {
    Serial.println("WIFI CONNECTION FAILED!");
  }
}

void loop() {

  if (WiFi.status() == WL_CONNECTED) {

    packetNumber++;

    char message[200];

    snprintf(
      message,
      sizeof(message),
      "SENSOR_ID=%s,LOCATION=%s,PACKET=%lu,STATUS=ONLINE",
      SENSOR_ID,
      SENSOR_LOCATION,
      packetNumber
    );

    udp.beginPacket(gatewayIP, gatewayPort);
    udp.write((const uint8_t*)message, strlen(message));

    int result = udp.endPacket();

    if (result == 1) {
      Serial.print("MESSAGE SENT: ");
      Serial.println(message);
    } else {
      Serial.println("MESSAGE SEND FAILED!");
    }

  } else {
    Serial.println("SENSOR DISCONNECTED!");
  }

  delay(5000);
}
