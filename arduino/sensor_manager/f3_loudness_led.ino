// ============================================
// FEATURE 3 - Loudness Sensor + LED Bar
// ============================================
// Components: Loudness (Sound) Sensor
//             LED Bar
// Purpose:    Read ambient noise level continuously.
//             Display noise level visually on LED bar.
//             The raw loudness value is sent to the Pi,
//             which decides whether to trigger the camera
//             for cry detection.
// ============================================

#include <Grove_LED_Bar.h>

const int LOUDNESS_PIN = A1;       // Analog pin for loudness sensor

// Thresholds for LED bar display 
const int NOISE_LOW = 100;         // Below this = quiet (green)
const int NOISE_MED = 250;         // Below this = moderate (amber)
const int NOISE_HIGH = 500;        // Above this = loud (red)

Grove_LED_Bar ledBar(9, 8, 1);

void setupLoudness() {
  pinMode(LOUDNESS_PIN, INPUT);

  ledBar.begin();
  ledBar.setLevel(0); // All LEDs off at startup
}

int readLoudness() {
  // Take 5 separate peak-to-peak measurements
  // and average them to smooth out random spikes
  int readings[5];

  for (int r = 0; r < 5; r++) {
    int minVal = 1023;
    int maxVal = 0;

    // Sample the sound wave over 200ms
    // tracking the highest and lowest points
    for (int i = 0; i < 200; i++) {
      int val = analogRead(LOUDNESS_PIN);
      if (val > maxVal) maxVal = val;
      if (val < minVal) minVal = val;
      delay(1);
    }

    // Peak-to-peak range = loudness for this window
    readings[r] = maxVal - minVal;
  }

  // Sort the 5 readings so we can drop outliers
  for (int i = 0; i < 4; i++) {
    for (int j = i + 1; j < 5; j++) {
      if (readings[j] < readings[i]) {
        int temp = readings[i];
        readings[i] = readings[j];
        readings[j] = temp;
      }
    }
  }

  // Drop the lowest and highest readings (outliers)
  // Average the middle 3 for a stable result
  int sum = readings[1] + readings[2] + readings[3];
  return sum / 3;
}

// Alert mode: 0 = show noise, 1 = low, 2 = high
int currentAlertLevel = 0;
unsigned long lastAlertFlash = 0;
bool alertFlashState = false;

void setLEDAlert(int level) {
  currentAlertLevel = level;
}

void updateLEDBar(int loudness) {
  if (currentAlertLevel == 0) {
    // No alert, show normal noise level
    loudness = constrain(loudness, 0, NOISE_HIGH);
    int level = map(loudness, 0, NOISE_HIGH, 0, 10);
    ledBar.setLevel(level);
  }
  else if (currentAlertLevel == 1) {
    // LOW alert: steady 10 LEDs
    ledBar.setLevel(10);
  }
  else if (currentAlertLevel == 2) {
    // HIGH alert: flash all LEDs
    unsigned long now = millis();
    if (now - lastAlertFlash >= 500) {
      lastAlertFlash = now;
      alertFlashState = !alertFlashState;
      if (alertFlashState) {
        ledBar.setLevel(10);
      } else {
        ledBar.setLevel(0);
      }
    }
  }
}