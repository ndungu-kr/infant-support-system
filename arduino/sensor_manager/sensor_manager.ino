void setup() {
  Serial.begin(9600);
  setupPIR();
  setupEnvSensors();
  setupLoudness();
}

void loop() {
  int motion = readPIR();
  float temp = readTemperature();
  float humidity = readHumidity();
  int light = readLight();
  int loudness = readLoudness();

  Serial.print("MOTION:");    Serial.print(motion);
  Serial.print(",TEMP:");     Serial.print(temp, 1);
  Serial.print(",HUMIDITY:"); Serial.print(humidity, 1);
  Serial.print(",LIGHT:");    Serial.print(light);
  Serial.print(",LOUDNESS:"); Serial.print(loudness);
  Serial.println();
  delay(2000);
}
