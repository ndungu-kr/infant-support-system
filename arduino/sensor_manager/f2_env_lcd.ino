// ============================================
// FEATURE 2 - Environmental Monitoring + LCD
// ============================================
// Components: Temperature/Humidity Sensor (DHT11 or DHT22)
//             Light Sensor
//             LCD Backlight Display
// Purpose:    Read environment data, show temp/humidity on LCD,
//             send all readings to the Pi for analytics.
// ============================================

#include <DHT.h>

const int DHT_PIN = 3;             // Digital pin for DHT sensor
const int LIGHT_PIN = A0;          // Analog pin for light sensor
DHT dht(DHT_PIN, DHT11); 

// TODO: Add LCD library include and setup


void setupEnvSensors() {
  pinMode(LIGHT_PIN, INPUT);

  // Initialise DHT sensor
  dht.begin();

  // TODO: Initialise LCD

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

void updateLCD(float temp, float humidity) {
  // TODO: Display temperature and humidity on the LCD

}
