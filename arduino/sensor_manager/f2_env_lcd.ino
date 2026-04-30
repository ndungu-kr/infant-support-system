// ============================================
// FEATURE 2 - Environmental Monitoring + LCD
// ============================================
// Components: Temperature/Humidity Sensor (DHT11 or DHT22)
//             Light Sensor
// Purpose:    Read environment data and send all readings to the Pi for analytics.
// ============================================

#include <DHT.h>

const int DHT_PIN = 3;             // Digital pin for DHT sensor
const int LIGHT_PIN = A0;          // Analog pin for light sensor
DHT dht(DHT_PIN, DHT11); 

void setupEnvSensors() {
  pinMode(LIGHT_PIN, INPUT);

  // Initialise DHT sensor
  dht.begin();

}

float readTemperature() {
  float temp = dht.readTemperature();
  if (isnan(temp)) return -1;
  return temp;
}

float readHumidity() {
  float humidity = dht.readHumidity();
  if (isnan(humidity)) return -1;
  return humidity;
}

int readLight() {
  return analogRead(LIGHT_PIN);
}
