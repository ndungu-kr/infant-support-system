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
const int NOISE_HIGH = 500;        // Above this = loud (red)

void setupLoudness() {
  pinMode(LOUDNESS_PIN, INPUT);

  // TODO: Initialise LED bar

}

int readLoudness() {
  // Read multiple (5) samples and average for a smoother value
  // TODO: Find out why values are wierd, its acting properly sometimes but seems random at other times
  long total = 0;
  const int SAMPLES = 5;
  for (int i = 0; i < SAMPLES; i++) {
    total += analogRead(LOUDNESS_PIN);
    delay(1);  // tiny delay between reads
  }
  return total / SAMPLES;
}

void updateLEDBar(int loudness) {
  // TODO: Map the loudness value to the number of LEDs lit

  // Colour logic:
  // loudness < NOISE_LOW  -> green LEDs only
  // loudness < NOISE_MED  -> amber LEDs
  // loudness >= NOISE_MED -> red LEDs
}
