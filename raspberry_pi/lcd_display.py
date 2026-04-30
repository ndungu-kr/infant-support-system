import sys
import time
import json
import smbus
import paho.mqtt.client as mqtt

# Config-------------------
DISPLAY_TEXT_ADDR = 0x3E
DISPLAY_RGB_ADDR = 0x30
I2C_BUS = 1

bus = smbus.SMBus(I2C_BUS)

# MQTT config
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "infant/env"

# FUNCTIONS---------------------

def initRGB():
    bus.write_byte_data(0x30, 0x00, 0x07)  # reset the chip
    time.sleep(0.01)
    bus.write_byte_data(0x30, 0x04, 0x15)  # set all LEDs always on

def setRGB(r, g, b):
    bus.write_byte_data(0x30, 0x06, r)
    bus.write_byte_data(0x30, 0x07, g)
    bus.write_byte_data(0x30, 0x08, b)
 
# send command to display (no need for external use)    
def textCommand(cmd):
    bus.write_byte_data(DISPLAY_TEXT_ADDR,0x80,cmd)
 
# set display text \n for second line(or auto wrap)     
def setText(text):
    textCommand(0x01) # clear display
    time.sleep(.05)
    textCommand(0x08 | 0x04) # display on, no cursor
    textCommand(0x28) # 2 lines
    time.sleep(.05)
    count = 0
    row = 0
    for c in text:
        if c == '\n' or count == 16:
            count = 0
            row += 1
            if row == 2:
                break
            textCommand(0xc0)
            if c == '\n':
                continue
        count += 1
        bus.write_byte_data(DISPLAY_TEXT_ADDR,0x40,ord(c))
 
# MQTT CALLBACKS------------------------------

def on_connect(client, userdata, flags, rc):
	client.subscribe(MQTT_TOPIC)
	setRGB(0,0,255)  #blue when connected, waiting for data
	setText("WAITING FOR\nDATA...")
	
def on_message(client, userdata, msg):
	try:
		data = json.loads(msg.payload.decode("utf-8"))
	except json.JSONDecodeError:
		return
	
	temp = data.get("temperature","--")
	humidity = data.get("humidity", "--")
	
	setRGB(0, 255, 0) #Green when data received
	setText(f"Temp: {temp}C\nHumidity: {humidity}%")
	
# Main ------------------------------

if __name__ == "__main__":
    initRGB()
	setRGB(255,255,0) #Yellow at startup before connecting
	setText("CONNECTING...\n")
	
	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_message = on_message
	
	client.connect(MQTT_BROKER, MQTT_PORT)
	client.loop_forever()
	
