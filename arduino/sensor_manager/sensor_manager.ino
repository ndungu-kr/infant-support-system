void setup() {
  Serial.begin(9600);
  setupPIR();
  setupEnvSensors();
  setupLoudness();
  setupRFID();
}

void loop() {
  checkRFIDTap();

  int motion = readPIR();
  float temp = readTemperature();
  float humidity = readHumidity();
  int light = readLight();
  int loudness = readLoudness();
  String rfid = readRFID();

  Serial.print("MOTION:");    Serial.print(motion);
  Serial.print(",TEMP:");     Serial.print(temp, 1);
  Serial.print(",HUMIDITY:"); Serial.print(humidity, 1);
  Serial.print(",LIGHT:");    Serial.print(light);
  Serial.print(",LOUDNESS:"); Serial.print(loudness);
  Serial.print(",RFID:");     Serial.print(rfid);
  Serial.println();
  delay(2000);
}