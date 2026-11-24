
#include <WiFi.h>
#include <WiFiUdp.h>

// ==========================================
// SENTINEL-X CENTRAL GATEWAY
// UDP RECEIVER - ANC-01
// STATIC IP CONFIGURATION
// ==========================================

// Router credentials
const char* WIFI_SSID = "SultanAsgher";
const char* WIFI_PASSWORD = "Sultan@123";

// ==========================================
// STATIC IP CONFIGURATION - ANC-01
// ==========================================

IPAddress local_IP(192, 168, 1, 27);
IPAddress gateway(192, 168, 1, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(192, 168, 1, 1);
IPAddress secondaryDNS(8, 8, 8, 8);

// ==========================================
// GATEWAY SETTINGS
// ==========================================

const char* GATEWAY_ID = "ANC-01";
const unsigned int UDP_PORT = 4210;

WiFiUDP udp;

char incomingPacket[512];

// ==========================================
// SETUP
// ==========================================

void setup() {

  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("SENTINEL-X UDP GATEWAY");
  Serial.println("================================");

  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);

  // Apply static IP BEFORE connecting
  Serial.println("Configuring static IP...");

  if (!WiFi.config(
        local_IP,
        gateway,
        subnet,
        primaryDNS,
        secondaryDNS
      )) {

    Serial.println("STATIC IP CONFIGURATION FAILED!");

  } else {

    Serial.println("STATIC IP CONFIGURATION SUCCESSFUL!");

  }

  Serial.println("Connecting to router...");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");

  }

  Serial.println();
  Serial.println("GATEWAY CONNECTED!");

  Serial.print("Gateway ID: ");
  Serial.println(GATEWAY_ID);

  Serial.print("Gateway IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Gateway MAC: ");
  Serial.println(WiFi.macAddress());

  Serial.print("Subnet Mask: ");
  Serial.println(WiFi.subnetMask());

  Serial.print("Router Gateway: ");
  Serial.println(WiFi.gatewayIP());

  Serial.print("UDP Listening Port: ");
  Serial.println(UDP_PORT);

  // Start UDP receiver
  if (udp.begin(UDP_PORT)) {

    Serial.println("UDP RECEIVER READY!");

  } else {

    Serial.println("UDP RECEIVER FAILED TO START!");

  }

  Serial.println("Waiting for sensor messages...");
}

// ==========================================
// MAIN LOOP
// ==========================================

void loop() {

  int packetSize = udp.parsePacket();

  if (packetSize) {

    int len = udp.read(
      incomingPacket,
      sizeof(incomingPacket) - 1
    );

    if (len > 0) {

      incomingPacket[len] = '\0';

    }

    Serial.println();
    Serial.println("========== MESSAGE RECEIVED ==========");

    Serial.print("Sender IP: ");
    Serial.println(udp.remoteIP());

    Serial.print("Sender Port: ");
    Serial.println(udp.remotePort());

    Serial.print("Message: ");
    Serial.println(incomingPacket);

    Serial.println("======================================");

  }
}
