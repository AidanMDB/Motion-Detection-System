# Motion-Detection-System
Software for Embbeded Systems project

Uses an ESP32 microcontroller and MPU-6050 accelerometer and gyroscope to detect when the device is moved and send notificaitons to phone



Connections
MPU SDA -> GPIO22
MPU SCL -> GPIO14
MPU GND -> GND
MPU VIN -> 3V

NeoPixel and Pin 13 for red LED

IFTTT
If (web request) Then (notification)
If "activate motion sensor on" Then "POST val=1"
If "activate motion sensor off" Then "POST val=0"

Thingspeak
Channel called 'Google Assistant Data'
field1 - sensor_state

Youtube
https://youtube.com/shorts/h7zCffbNo9w?feature=share 
