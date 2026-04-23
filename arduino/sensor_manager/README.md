# Arduino - Sensor Manager

## How the sensor_manager is structured

```
sensor_manager/
  sensor_manager.ino     <-- Main file (setup + loop + serial output)
  f1_pir_presence.ino    <-- Feature 1: PIR motion sensor
  f2_env_lcd.ino         <-- Feature 2: Temp/Humidity/Light/LCD
  f3_loudness_led.ino    <-- Feature 3: Loudness sensor/LED bar
  f4_rfid_buzzer.ino     <-- Feature 4: RFID reader/Buzzer
```

## How multi-file Arduino sketches work

Arduino automatically merges all `.ino` files in the same folder into one
program when it compiles. This means:

- Any function written in any `.ino` file can be called from any other file
- No imports or includes needed between `.ino` files

## Data format sent to Raspberry Pi

Every second, the Arduino sends one line over Serial (9600 baud):

```
MOTION:1,TEMP:24.6,HUMIDITY:58.0,LIGHT:120,LOUDNESS:65,RFID:NONE
```

| Field      | Type   | Source         | Notes                              |
|------------|--------|----------------|------------------------------------|
| MOTION     | 0 or 1 | PIR sensor     | 1 = motion detected                |
| TEMP       | float  | DHT sensor     | Degrees Celsius, 1 decimal place   |
| HUMIDITY   | float  | DHT sensor     | Percentage, 1 decimal place        |
| LIGHT      | int    | Light sensor   | Raw analog 0-1023                  |
| LOUDNESS   | int    | Sound sensor   | Raw analog 0-1023 (averaged)       |
| RFID       | string | RFID reader    | Tag ID when tapped, otherwise NONE |

## Pin assignments


| Component              | Pin  | File               |
|------------------------|------|--------------------|
| PIR Motion Sensor      | D2   | f1_pir_presence    |
| Temp/Humidity (DHT)    | D3   | f2_env_lcd         |
| Light Sensor           | A0   | f2_env_lcd         |
| Loudness Sensor        | A1   | f3_loudness_led    |
| LED Bar                | TBD  | f3_loudness_led    |
| Buzzer                 | TBD  | f4_rfid_buzzer     |
| RFID Reader            | D6   | f4_rfid_buzzer     |
| LCD Display            | TBD  | f2_env_lcd         |


## Libraries needed

Install these via Arduino IDE (Sketch > Include Library > Manage Libraries):

- DHT sensor library (for temperature/humidity)
- SoftwareSerial 

## How to test without the full system

You can upload this sketch and open Serial Monitor (9600 baud) to see
the data output. 