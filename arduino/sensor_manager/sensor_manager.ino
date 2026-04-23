void setup() {
  Serial.begin(9600);
  setupPIR();
  setupEnvSensors();
}

void loop() {
  int motion = readPIR();
  float temp = readTemperature();
  float humidity = readHumidity();

  Serial.print("MOTION:");    Serial.print(motion);
  Serial.print(",TEMP:");     Serial.print(temp, 1);
  Serial.print(",HUMIDITY:"); Serial.print(humidity, 1);
  Serial.println();
  delay(2000);
}
