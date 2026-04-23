// ============================================
// FEATURE 1 - PIR Presence Detection
// ============================================
// Component: PIR Motion Sensor
// Purpose:   Detect whether someone (nurse/infant movement)
//            is near the crib. Sends 1 or 0 to the Pi.
//            The Pi decides what "presence" means over time.
// ============================================

// TODO: Set this to the actual pin your PIR sensor is connected to
const int PIR_PIN = 2;

void setupPIR() {
  pinMode(PIR_PIN, INPUT);
}

// Returns 1 if motion is detected, 0 if not
int readPIR() {
  return digitalRead(PIR_PIN);
}
