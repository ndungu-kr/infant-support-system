#include <DHT.h>

const int DHT_PIN = 3;
const int LIGHT_PIN = A0;
DHT dht(DHT_PIN, DHT11);  // Change DHT11 to DHT22 if that's your model

void setupEnvSensors() {
  dht.begin();
}

float readTemperature() {
  float t = dht.readTemperature();
  if (isnan(t)) return -1;
  return t;
}

float readHumidity() {
  float h = dht.readHumidity();
  if (isnan(h)) return -1;
  return h;
}