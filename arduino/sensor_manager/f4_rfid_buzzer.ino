// ============================================
// FEATURE 4 - RFID Nurse Check-in + Buzzer
// ============================================
// Components: RFID Reader
//             Buzzer
// Purpose:    Detect when a nurse taps their RFID tag
//             to log a check-in. The buzzer is controlled
//             by commands from the Pi (escalation alerts).
// ============================================

// TODO: Add Buzzer pin 
const int BUZZER_PIN = 4;

// Buzzer alert levels
const int BUZZ_NONE = 0; // No alert - buzzer off
const int BUZZ_LOW = 1; // Low alert - periodic buzz
const int BUZZ_HIGH = 2; // High alert - rapid buzz

// Buzzer timing (milliseconds)
// low alert turn on and off feels like one beep per second
const int LOW_ON_MS = 200; // Low alert: buzz on duration 
const int LOW_OFF_MS = 800; // Low alert: buzz off duration 
// high alert turn on and off feels like rapid alternating beeps
const int HIGH_ON_MS = 200; // High alert: buzz on duration
const int HIGH_OFF_MS = 200; // High alert: buzz off duration

// Buzzer state - controlled by Pi via serial commands
int buzzLevel = BUZZ_NONE; // current alert level
bool buzzOn = false; // is buzzer currently buzzing
unsigned long lastToggle = 0; //millis() of last on/off toggle

//RFID state
String lastRFID = "NONE";
bool rfidReady = false;

void setupRFID() {
  Serial1.begin(9600);
}

void setupBuzzer(){
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN,LOW); //Buzzer off at startup
}

void checkRFIDTap() {
  if (Serial1.available()) {
    lastRFID = "";
    delay(100);  // wait for full tag to arrive
    while (Serial1.available()) {
      char c = Serial1.read();
      if (c >= 32) {  // ignore control characters
        lastRFID += c;
      }
    }
    lastRFID.trim();
    if (lastRFID.length() > 0) {
      rfidReady = true;
    }
  }
}

// Returns the tag ID if one was scanned, otherwise "NONE"
// Resets after reading so the same tap is only sent once
String readRFID() {
  if (rfidReady) {
    rfidReady = false;
    String tag = lastRFID;
    lastRFID = "NONE";
    return tag;
  }
  return "NONE";
}
// BUZZER ----------------------------------------------------
// TODO: Called every loop() cycle to handle buzzer timing
void updateBuzzer() {
  if (buzzLevel == BUZZ_NONE){
    digitalWrite(BUZZER_PIN, LOW);  // Ensure buzzer is off
    return;
  }

  unsigned long now = millis();
  int onMs = (buzzLevel == BUZZ_LOW) ? LOW_ON_MS : HIGH_ON_MS;
  int offMs = (buzzLevel == BUZZ_LOW) ? LOW_OFF_MS : HIGH_OFF_MS;
  unsigned long elapsed = now - lastToggle;

  if(buzzOn && elapsed >= (unsigned long)onMs){
    // On duration expired - turn off
    buzzOn = false;
    lastToggle = now;
    digitalWrite(BUZZER_PIN, LOW);
  } else if (!buzzOn && elapsed >= (unsigned long)offMs){
    // Off duration expired - turn on
    buzzOn = true;
    lastToggle = now;
    digitalWrite(BUZZER_PIN, HIGH);
  }
}

// TODO: Call this when the Pi sends a command to trigger the buzzer
void triggerBuzzer(int level) {
  buzzLevel = level;
  lastToggle = millis();

  if(level == BUZZ_NONE){
    buzzOn = false;
    digitalWrite(BUZZER_PIN, LOW);
  }else {
    buzzOn = true;
    digitalWrite(BUZZER_PIN,HIGH);
  }
}

// Stop buzzer immediately when the RFID is tapped
void stopBuzzer(){
  triggerBuzzer(BUZZ_NONE);
}




