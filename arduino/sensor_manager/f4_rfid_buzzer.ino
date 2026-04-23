#include <SoftwareSerial.h>

const int RFID_RX = 6;
const int RFID_TX = 7;

SoftwareSerial rfidSerial(RFID_RX, RFID_TX);

String lastRFID = "NONE";
bool rfidReady = false;

void setupRFID() {
  rfidSerial.begin(9600);
}

void checkRFIDTap() {
  if (rfidSerial.available()) {
    lastRFID = "";
    delay(100);  // wait for full tag to arrive
    while (rfidSerial.available()) {
      char c = rfidSerial.read();
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

String readRFID() {
  if (rfidReady) {
    rfidReady = false;
    String tag = lastRFID;
    lastRFID = "NONE";
    return tag;
  }
  return "NONE";
}