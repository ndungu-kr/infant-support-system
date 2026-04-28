# Raspberry Pi 

## Camera sensor
###  feature : detect if infant is moving, if infant havent move for x second, send alert
### feature : detect infant presence by checking if the head is on camera
### feature : detect infant facial feature (eyes and mouth) to determine if the infant is sleeping, awake, or crying 
### (for crying, the infant needs to open their mouth and the noise detector needs to exceed the noise threshold to be consider crying)

## Libraries needed
```
    run these command via terminal/
    
    sudo apt update
    pip install numpy
    sudo apt install python3-opencv
    pip install dlib
    sudo apt install mosquitto mosquitto-clients -y
    sudo systemctl enable mosquitto   # auto-start on boot
    sudo systemctl start mosquitto # only for the first time
    sudo systemctl status mosquitto # verify its running

```