void setup() {
  Serial.begin(9600);
  setupPIR();
  setupEnvSensors();
}

void loop() {
  int motion = readPIR();
  float temp = readTemperature();
  float humidity = readHumidity();
  int light = readLight();

  Serial.print("MOTION:");    Serial.print(motion);
  Serial.print(",TEMP:");     Serial.print(temp, 1);
  Serial.print(",HUMIDITY:"); Serial.print(humidity, 1);
  Serial.print(",LIGHT:");    Serial.print(light);
  Serial.println();
  delay(2000);
}