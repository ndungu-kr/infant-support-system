const int LOUDNESS_PIN = A1;

void setupLoudness() {
  pinMode(LOUDNESS_PIN, INPUT);
}

int readLoudness() {
  long total = 0;
  for (int i = 0; i < 5; i++) {
    total += analogRead(LOUDNESS_PIN);
    delay(1);
  }
  return total / 5;
}