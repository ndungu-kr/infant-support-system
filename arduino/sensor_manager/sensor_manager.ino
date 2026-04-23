// ============================================
// INFANT SUPPORT SYSTEM - Main Sensor Manager
// ============================================
// This is the main file. It calls functions from
// all the other .ino files in this folder.
// Arduino merges them all together automatically.
//
// DATA FORMAT sent over Serial to Raspberry Pi:
// MOTION:0,TEMP:24.6,HUMIDITY:58.0,LIGHT:120,LOUDNESS:65,RFID:NONE
//
// When RFID is tapped, RFID field shows the tag ID instead of NONE.
// ============================================

// How often we read sensors and send data (in milliseconds)
const unsigned long SEND_INTERVAL = 1000; // 1 second

unsigned long lastSendTime = 0;

void setup() {
  // Start serial communication with Raspberry Pi
  Serial.begin(9600);

  // Call each feature's setup function
  setupPIR();           // Feature 1 - f1_pir_presence.ino
  setupEnvSensors();    // Feature 2 - f2_env_lcd.ino
  setupLoudness();      // Feature 3 - f3_loudness_led.ino
  setupRFID();          // Feature 4 - f4_rfid_buzzer.ino

  Serial.println("STATUS:READY");
}

void loop() {
  unsigned long now = millis();

  // Read sensors and send data at a regular interval
  if (now - lastSendTime >= SEND_INTERVAL) {
    lastSendTime = now;

    // --- Read all sensors ---
    int motion       = readPIR();           // 1 = motion detected, 0 = no motion
    float temp       = readTemperature();   // degrees Celsius
    float humidity   = readHumidity();      // percentage
    int light        = readLight();         // raw analog value (0-1023)
    int loudness     = readLoudness();      // raw analog value (0-1023)
    String rfid      = readRFID();          // tag ID string or "NONE"

    // --- Update actuators based on readings ---
    updateLCD(temp, humidity);              // Feature 2 - show on LCD
    updateLEDBar(loudness);                 // Feature 3 - show noise level

    // --- Send data to Raspberry Pi over Serial ---
    Serial.print("MOTION:");    Serial.print(motion);
    Serial.print(",TEMP:");     Serial.print(temp, 1);
    Serial.print(",HUMIDITY:"); Serial.print(humidity, 1);
    Serial.print(",LIGHT:");    Serial.print(light);
    Serial.print(",LOUDNESS:"); Serial.print(loudness);
    Serial.print(",RFID:");     Serial.print(rfid);
    Serial.println();  // newline marks end of message
  }

  // Check RFID continuously (taps can happen anytime)
  checkRFIDTap();       // Feature 4 - runs every loop, not just every second

  // Check buzzer escalation
  updateBuzzer();       // Feature 4 - handles buzzer timing
}
