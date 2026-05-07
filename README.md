# Infant Support System (ISS)

A privacy-preserving IoT monitoring prototype for hospital nurseries. ISS combines Arduino sensors, Raspberry Pi camera processing, Node-RED orchestration, local actuators, and a Flask cloud dashboard so nurses can monitor infant state, environment conditions, care interactions, and alerts from a single web interface.

This is a proof-of-concept coursework prototype, not a certified medical device.

## Project Features

The feature numbers match the poster, CodeCast, and source code evidence.

1. **Infant State Monitor** - Uses the Raspberry Pi camera, dlib HOG face detection, dlib facial landmarks, eye aspect ratio, mouth aspect ratio, and loudness readings to classify the infant as sleeping, awake, crying, face not visible, or absent.
2. **Smart Motion Detection** - Combines PIR inactivity from Arduino with visual verification on the Raspberry Pi. Node-RED triggers a CNN presence check and a short histogram-equalised motion check only when extra verification is needed.
3. **RFID Nurse Logging System** - Reads nurse RFID tags on Arduino, sends them through Node-RED, signs the request with HMAC-SHA256, and stores check-in events against nurse records in the backend database.
4. **Infant Priority Alert System** - Uses state, crying duration, movement, care timers, temperature, and sound context to generate low/high priority alerts. Node-RED sends buzzer and LED bar commands back to Arduino and logs alert events in the cloud API.
5. **Cloud Web App** - Flask backend and browser dashboard hosted locally or on OpenShift. Nurses can log in, view live status, inspect telemetry history, review alerts, update check-in actions, and temporarily check the infant out of the crib for care tasks.

## System Architecture

Data flow:

1. Arduino reads PIR motion, DHT temperature/humidity, light, loudness, and RFID data.
2. Arduino sends JSON over USB serial to the Raspberry Pi/Node-RED flow every second.
3. Node-RED parses sensor data, publishes MQTT messages for the camera and LCD services, evaluates state/alert logic, and sends HMAC-signed HTTP requests to Flask.
4. `raspberry_pi/camera_monitor.py` receives loudness and motion-trigger messages over MQTT, processes camera frames locally, and publishes camera state back to MQTT.
5. Node-RED combines sensor and camera state, sends actuator commands back to Arduino, and posts telemetry, check-ins, and alerts to the Flask API.
6. Flask stores data in MySQL on OpenShift, or SQLite for local development when MySQL variables are not configured.
7. The web dashboard polls Flask API routes using JWT authentication.

## Repository Structure

```text
infant-support-system/
  README.md
  arduino/
    sensor_manager/
      sensor_manager.ino        Main Arduino sketch and serial JSON protocol
      f1_pir_presence.ino       PIR motion sensing
      f2_env_lcd.ino            DHT temperature/humidity and light sensing
      f3_loudness_led.ino       Loudness sensing and LED bar alert display
      f4_rfid_buzzer.ino        RFID nurse tag input and buzzer control
      README.md                 Arduino-specific notes and pin table
  raspberry_pi/
    camera_monitor.py           Camera, dlib face/landmark, crying, and motion processing
    lcd_display.py              MQTT-driven Grove RGB LCD display process
    flows.json                  Node-RED flow for serial parsing, MQTT, alert logic, and API calls
    packages.txt                Raspberry Pi package notes
    mmod_human_face_detector.dat
    shape_predictor_68_face_landmarks.dat
  web_app/
    app.py                      Flask entry point, JWT setup, blueprint registration
    database.py                 SQLAlchemy database configuration and seed data
    extensions.py               Bcrypt, JWT, and HMAC helpers
    Dockerfile                  Gunicorn container for OpenShift-style deployment
    requirements.txt            Python web dependencies
    backend/
      models.py                 Nurse, telemetry, alert, check-in, and crib checkout models
      frontend_route.py         JWT-protected web/dashboard API routes
      pi_route.py               HMAC-protected Raspberry Pi ingestion routes
      README.md                 Detailed API documentation
    front-end/
      index.html                Login page
      dashboard.html            Live monitoring dashboard
      history.html              Telemetry history page
      alerts.html               Alert history page
      checkins.html             Nurse check-in history page
      css/style.css             Dashboard styling
      js/*.js                   API, auth, dashboard, history, alerts, and check-in logic
```

## Prerequisites

Hardware:

- Arduino-compatible board with PIR sensor, DHT11, light sensor, loudness sensor, RFID reader, Grove LED Bar, and buzzer.
- Raspberry Pi with camera module, I2C enabled for the LCD, and USB serial connection to Arduino.
- Grove RGB LCD or compatible I2C LCD.

Software:

- Arduino IDE.
- Python 3.11 for the Flask web app, matching `web_app/Dockerfile`.
- Raspberry Pi OS with Python 3, Mosquitto MQTT broker, Node-RED, OpenCV, dlib, Picamera2, NumPy, paho-mqtt, and smbus.
- MySQL for production/OpenShift deployment. SQLite is used automatically for local development if MySQL environment variables are missing.

## Configuration

Create `web_app/.env` for local Flask development:

```env
JWT_SECRET=replace-with-a-long-random-value
HMAC_SECRET=replace-with-the-same-secret-used-by-node-red
MYSQL_SERVICE_HOST=localhost
MYSQL_DATABASE=infant_support
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
```

If the MySQL variables are omitted, the backend falls back to `sqlite:///local.db`.

Node-RED also needs the same `HMAC_SECRET` so the Pi routes can verify telemetry, alert, and check-in payloads. In production, store secrets in environment variables or platform secrets rather than hardcoding real values into exported flows.

## Setup and Running

### 1. Arduino Sensor Manager

1. Open `arduino/sensor_manager/sensor_manager.ino` in Arduino IDE.
2. Install these Arduino libraries through **Sketch > Include Library > Manage Libraries**:
   - DHT sensor library
   - Grove LED Bar
   - Arduino_JSON
3. Confirm pins in the `.ino` files match the wiring:
   - PIR: D2
   - DHT: D3
   - Light sensor: A0
   - Loudness sensor: A1
   - LED bar: D8/D9
   - Buzzer: D4
   - RFID reader: UART/Serial1
4. Upload the sketch.
5. Open Serial Monitor at 9600 baud. Expected output is JSON similar to:

```json
{"motion":1,"temp":"24.6","humidity":"58","light":120,"loudness":65,"rfid":"NONE"}
```

### 2. Raspberry Pi Services

Install core packages:

```bash
sudo apt update
sudo apt install -y python3-opencv python3-picamera2 python3-smbus i2c-tools mosquitto mosquitto-clients
pip install numpy dlib paho-mqtt
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

Import `raspberry_pi/flows.json` into Node-RED, then check these flow settings:

- Serial port to Arduino, usually `/dev/ttyACM0`.
- MQTT broker, usually `localhost:1883`.
- Flask/OpenShift API URLs in the HTTP request nodes.
- `HMAC_SECRET` environment value.

Run the camera monitor:

```bash
cd raspberry_pi
python3 camera_monitor.py
```

Run the LCD display process in another terminal:

```bash
cd raspberry_pi
python3 lcd_display.py
```

Expected MQTT topics:

- `infant/camera/input` - Node-RED sends loudness and CNN trigger requests to the camera process.
- `infant/camera` - Camera process publishes presence, state, crying, and camera motion.
- `infant/env` - Node-RED sends temperature and humidity to the LCD process.

### 3. Flask Web App

Local development:

```bash
cd web_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app listens on:

```text
http://localhost:8080
```

Seeded demo nurse accounts are created automatically when the database is empty:

```text
user1 / abcd1234
user2 / abcd1234
user3 / abcd1234
```

Container/OpenShift-style run:

```bash
cd web_app
docker build -t infant-support-system .
docker run -p 8080:8080 --env-file .env infant-support-system
```

## Main API Routes

Frontend routes use JWT Bearer tokens:

- `POST /api/login`
- `POST /api/logout`
- `GET /api/status`
- `GET /api/summary`
- `GET /api/history?start=YYYY-MM-DD&end=YYYY-MM-DD`
- `GET /api/alert?start=YYYY-MM-DD&end=YYYY-MM-DD`
- `GET /api/checkins?start=YYYY-MM-DD&end=YYYY-MM-DD`
- `POST /api/checkin/update`
- `GET /api/crib-status`
- `POST /api/crib-checkout`
- `POST /api/crib-return`

Pi ingestion routes use HMAC-SHA256 signatures:

- `POST /api/telemetry`
- `POST /api/checkin`
- `POST /api/alert`
- `GET /api/pi-crib-status`

See `web_app/backend/README.md` for request/response examples.

## Third-Party Software and Frameworks

Versions are not pinned in this repository except for the Python base image in the Dockerfile. The web container uses Python 3.11.

| Component | Used for | Official documentation |
| --- | --- | --- |
| Flask | Web server, static frontend, API routes | https://flask.palletsprojects.com/ |
| Flask-SQLAlchemy / SQLAlchemy | Database models and queries | https://flask-sqlalchemy.palletsprojects.com/ |
| PyMySQL | MySQL driver for SQLAlchemy | https://pymysql.readthedocs.io/ |
| Flask-JWT-Extended | Nurse login sessions and protected dashboard APIs | https://flask-jwt-extended.readthedocs.io/ |
| Flask-Bcrypt | Password hashing for nurse accounts | https://flask-bcrypt.readthedocs.io/ |
| python-dotenv / dotenv | Local environment variable loading | https://pypi.org/project/python-dotenv/ |
| Gunicorn | Production WSGI server in Docker/OpenShift | https://gunicorn.org/ |
| Node-RED | Raspberry Pi orchestration, serial parsing, alert rules, API requests | https://nodered.org/docs/ |
| Mosquitto MQTT | Local message broker between Node-RED, camera, and LCD services | https://mosquitto.org/documentation/ |
| paho-mqtt | Python MQTT client in Raspberry Pi scripts | https://eclipse.dev/paho/ |
| OpenCV | Frame preprocessing and motion analysis | https://docs.opencv.org/ |
| dlib | HOG/CNN face detection and 68-point landmark model | http://dlib.net/ |
| NumPy | Aspect-ratio and motion calculations | https://numpy.org/doc/ |
| Picamera2 | Raspberry Pi camera capture | https://datasheets.raspberrypi.com/camera/picamera2-manual.pdf |
| Arduino_JSON | JSON command parsing and sensor output on Arduino | https://github.com/arduino-libraries/Arduino_JSON |
| DHT sensor library | Temperature/humidity sensor readings | https://github.com/adafruit/DHT-sensor-library |
| Grove LED Bar library | LED bar level/alert display | https://github.com/Seeed-Studio/Grove_LED_Bar |

## Code Documentation

- Arduino files are split by feature and include comments explaining sensor purpose, pin usage, and serial protocol.
- `raspberry_pi/camera_monitor.py` documents the camera thresholds, MQTT topics, CNN/HOG scheduling, and motion detection approach.
- `web_app/backend/README.md` documents backend routes, authentication, HMAC signing, payload formats, and error responses.
- Flask route files include comments for authentication, history, check-ins, alert, telemetry, and crib checkout behaviour.

## Troubleshooting

**Dashboard shows System Offline**

- Confirm Node-RED is running and posting telemetry to `/api/telemetry`.
- Check that the Flask backend is reachable from the Raspberry Pi.
- Confirm the latest telemetry timestamp is less than 60 seconds old.

**Pi routes return 401 Unauthorized**

- Ensure Node-RED and Flask use the same `HMAC_SECRET`.
- Sign the payload before adding the `signature` field.
- Sort JSON keys and use compact JSON formatting when calculating HMAC.

**Login fails**

- Use one of the seeded accounts above, or check the `nurse` table.
- Ensure `JWT_SECRET` is set before starting Flask.

**Camera monitor does not start**

- Confirm the dlib model files are in `raspberry_pi/`.
- Install `python3-picamera2`, OpenCV, dlib, NumPy, and paho-mqtt.
- Set `DEBUG_SHOW_CAMERA = False` in `camera_monitor.py` when running headless over SSH.

**No Arduino data in Node-RED**

- Check Arduino Serial Monitor first for JSON output.
- Confirm Node-RED serial port is `/dev/ttyACM0` or the correct device for the Arduino.
- Confirm the Arduino sketch is running at 9600 baud.

**LCD does not update**

- Enable I2C on Raspberry Pi.
- Check the LCD addresses in `lcd_display.py` (`0x3E` for text and `0x30` for RGB).
- Confirm Node-RED publishes to `infant/env`.
