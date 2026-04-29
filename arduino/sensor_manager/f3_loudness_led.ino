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

const int LOUDNESS_PIN = A1;       // Analog pin for loudness sensor

// Thresholds for LED bar display 
const int NOISE_LOW = 100;         // Below this = quiet (green)
const int NOISE_MED = 250;         // Below this = moderate (amber)
const int NOISE_HIGH = 400;        // Above this = loud (red)

void setupLoudness() {
  pinMode(LOUDNESS_PIN, INPUT);

  // TODO: Initialise LED bar

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

void updateLEDBar(int loudness) {
  // TODO: Map the loudness value to the number of LEDs lit

  // Colour logic:
  // loudness < NOISE_LOW  -> green LEDs only
  // loudness < NOISE_MED  -> amber LEDs
  // loudness >= NOISE_MED -> red LEDs
}
