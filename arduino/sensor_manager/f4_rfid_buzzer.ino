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


String lastRFID = "NONE";
bool rfidReady = false;

// TODO: Buzzer state (controlled by Pi via serial commands)


void setupRFID() {
  Serial1.begin(9600);
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

// TODO: Called every loop() cycle to handle buzzer timing
void updateBuzzer() {

}

// TODO: Call this when the Pi sends a command to trigger the buzzer
void triggerBuzzer() {

}
