// ============================================
// INFANT SUPPORT SYSTEM - Main Sensor Manager
// ============================================
// This is the main file. It calls functions from
// all the other .ino files in this folder.
// Arduino merges them all together automatically.
// 
//It also read JSON commands that sent from Pi over USB serial
//
// DATA FORMAT sent over Serial to Raspberry Pi:
// MOTION:0,TEMP:24.6,HUMIDITY:58.0,LIGHT:120,LOUDNESS:65,RFID:NONE
//
// When RFID is tapped, RFID field shows the tag ID instead of NONE.
// ============================================

#include <Arduino_JSON.h>

// Serial input buffer for reading Pi commands
String inputBuffer = "";

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
  setupBuzzer();

  Serial.println("STATUS:READY");
}

void loop() {
  unsigned long now = millis();

  // read commands from Pi every cycle - buzz commands can arrive anytime
  readPiCommands();

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
    updateLEDBar(loudness);                 // Feature 3 - show noise level
    
    // --- If RFID tapped, stop buzzer immediately ---
    if (rfid != "NONE"){
      stopBuzzer();
    }

    // --- Send all sensor data to Pi as JSON ---
    JSONVar doc;
    doc["motion"]   = motion;
    doc["temp"]     = String(temp, 1); // sending as string then parsing on node red
    doc["humidity"] = String(humidity, 0); // because json library doesnt handle floats well
    doc["light"]    = light;
    doc["loudness"] = loudness;
    doc["rfid"]     = rfid;

    Serial.println(JSON.stringify(doc));
    Serial.println();  // newline marks end of message
  }

  // Check RFID continuously (taps can happen anytime)
  checkRFIDTap();       // Feature 4 - runs every loop, not just every second

  // Check buzzer escalation
  updateBuzzer();       // Feature 4 - handles buzzer timing
}

// Serial command reading ------------------------------------

// Read JSON commands from Pi over USB serial
void readPiCommands(){
  while (Serial.available()){
    char c = Serial.read();
    if (c == '\n'){
      inputBuffer.trim();
      if(inputBuffer.length()>0){
        parsePiCommand(inputBuffer);
      }
      inputBuffer = "";
    } else{
      inputBuffer += c;
    }
  }
}

void parsePiCommand(String cmd){
  JSONVar doc = JSON.parse(cmd);

  if (JSON.typeof(doc) == "undefined") {
    return; //malforned JSON
  }

  // Buzz command
  if (doc.hasOwnProperty("buzz")){
    int buzz = constrain((int)doc["buzz"], 0, 2);
    triggerBuzzer(buzz);
  }

  // LED bar alert mode command
  if (doc.hasOwnProperty("led")) {
    int led = constrain((int)doc["led"], 0, 3);
    setLEDAlert(led);
  }
}
