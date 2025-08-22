#include <WiFi.h>
#include "DHT.h"
#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include <ArduinoJson.h>
#include <HTTPClient.h>

#define MOISTURE_SENSOR_PIN 33
#define TEMP_HUMIDITY_SENSOR_PIN 23
#define DHTTYPE DHT22
#define AWS_IOT_PUBLISH_TOPIC_MOISTURE_TEMP "home/environment/indoors/moisture_temp_sensor_1"

const char WIFI_SSID[] = "";
const char WIFI_PASSWORD[] = "";
const char AWS_IOT_ENDPOINT[] = "";
static const char AWS_CERT_CA[] PROGMEM = R"EOF()EOF";
static const char AWS_CERT_CRT[] PROGMEM = R"EOF()EOF";
static const char AWS_CERT_PRIVATE[] PROGMEM = R"EOF()EOF";

WiFiClientSecure net = WiFiClientSecure();
MQTTClient client = MQTTClient(256);

DHT dht(TEMP_HUMIDITY_SENSOR_PIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  delay(1000);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(100);
  }
  connectToAWSIoT();
  dht.begin();
}

void connectToAWSIoT() {
  net.setCACert(AWS_CERT_CA);
  net.setCertificate(AWS_CERT_CRT);
  net.setPrivateKey(AWS_CERT_PRIVATE);
  client.begin(AWS_IOT_ENDPOINT, 8883, net);
  while (!client.connect(THINGNAME)) {
    delay(100);
    Serial.println(".");
  }
  Serial.println("AWS IoT Connected");
  if (!client.connected()) {
    Serial.println("AWS IoT Timeout!");
    return;
  }
}

void publishMessage(float h, float t, float m) {
  StaticJsonDocument<200> doc;
  doc["address"] = WiFi.macAddress();
  doc["humidity"] = h;
  doc["temperature"] = t;
  doc["moisture"] = m;
  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);  // print to client
  client.publish(AWS_IOT_PUBLISH_TOPIC_MOISTURE_TEMP, jsonBuffer);
}

void loop() {
  delay(3000);
  // The DHT22 returns at most one measurement every 2s
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  int m = analogRead(MOISTURE_SENSOR_PIN);
  if (isnan(h) || isnan(t)) {
    Serial.println(F("Failed reception"));
    return;
    // Returns an error if the ESP32 does not receive any measurements
  }
  publishMessage(h, t, m);
}