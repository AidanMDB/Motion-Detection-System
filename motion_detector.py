from machine import I2C, Pin
from MPU import MPU
from machine import Timer
import time
import urequests
import machine
import network
import neopixel


# Network Configuration
ssid = "Aidan D-B iPhone"
password = "HunterMasterRace"
IFTTT_URL = "https://maker.ifttt.com/trigger/motion detected/with/key/bsj-dHeriamlgJKSO9bL9X6xPlSzb8kBht_k98pBb9r"
THING_SPEAK_READ_URL = "https://api.thingspeak.com/channels/2777954/feeds.json?api_key=706LRZOBFZENTTF0&results=2"

# MPU Configuration
i2c = I2C(0, scl=Pin(14), sda=Pin(22))
mpu = MPU(i2c)

# System Configuration
active = False # Initial state (deactivated/off)
MOTION_THRESHOLD = 2.0
red_led = Pin(13, Pin.OUT)
Pin(2, Pin.IN, Pin.PULL_UP)
pixel = neopixel.NeoPixel(Pin(0), 1)
thingspeak_timer = Timer(0)
check_motion_timer = Timer(1)



def calibrate_accelerometer(mpu, samples=100):
    print("Calibrating accelerometer. Keep the MPU stationary...")
    acc_x_tot, acc_y_tot, acc_z_tot = 0, 0, 0

    for _ in range(samples):
        acc_x, acc_y, acc_z = mpu.acceleration()
        acc_x_tot += acc_x
        acc_y_tot += acc_y
        acc_z_tot += acc_z
        time.sleep(0.05)

    # Calculate averages
    acc_x_avg = acc_x_tot / samples
    acc_y_avg = acc_y_tot / samples
    acc_z_avg = acc_z_tot / samples
    # Adjust the z-axis offset to account for gravity
    gravity = 9.81
    z_offset = acc_z_avg - gravity
    print(f"Calibration complete.\nOffsets -> X: {acc_x_avg:.2f}, Y: {acc_y_avg:.2f}, Z: {z_offset:.2f}")
    return acc_x_avg, acc_y_avg, z_offset


x_offset, y_offset, z_offset = calibrate_accelerometer(mpu)



def connect_wifi():
    # reset wifi
    wifi = network.WLAN(network.STA_IF)
    wifi.active(False)
    time.sleep(1)
    wifi.active(True)


    wifi.connect(ssid, password)
    print("Connecting to Wi-Fi...")
    attempts = 0
    while not wifi.isconnected() and attempts < 10:
        time.sleep(1)
        print(f"Attempt {attempts}/10 to connect...")
        attempts += 1
        
    if wifi.isconnected():
        print(f"Connected to {ssid}")
        print(f"IP Address: {wifi.ifconfig()[0]}")
    else:
        print("Failed to connect to Wi-Fi after several attempts.")



def send_ifttt_notification():
    try:
        print("Sending Notification...")
        response = urequests.post(IFTTT_URL)
        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print(f"Error: {response.status_code}")
        response.close()
    except Exception as e:
        print("Failed to send notification:", e)



def read_from_thingspeak(t):
    try:
        print("Reading data from ThingSpeak...")
        response = urequests.get(THING_SPEAK_READ_URL)

        if response.status_code == 200:
            data = response.json()
            feeds = data.get("feeds", [])

            if feeds:
                field_value = int(feeds[-1].get("field1", 0))
                print(f"Received field value: {field_value}")
                toggle_system(field_value)
                
            else:
                print("No data available in ThingSpeak feed.")

        else:
            print(f"Failed to fetch data. Status Code: {response.status_code}")
            return 0
        
    except Exception as e:
        print("Error reading from ThingSpeak:", e)




def toggle_system(state):
    """
    Toggle the system activation based on the ThingSpeak field value.
    1 (Activate) or 0 (Deactivate)
    """
    global active
    if state == 1 and not active:
        print("Activating the system...")
        active = True
        pixel[0] = (0, 255, 0) # NeoPixel green
        pixel.write()
        check_motion_timer.init(period=1000,mode=Timer.PERIODIC,callback=check_motion)

    elif state == 0 and active:
        print("Deactivating the system...")
        active = False
        pixel[0] = (0, 0, 0) # NeoPixel off
        pixel.write()
        red_led.value(0)
        check_motion_timer.deinit()

    else:
        print(f"System is still {'active' if active else 'inactive'}\n.")



def check_motion(t):
    acc_x, acc_y, acc_z = mpu.acceleration()
    acc_x -= x_offset
    acc_y -= y_offset
    acc_z -= z_offset
    if abs(acc_x) > MOTION_THRESHOLD or abs(acc_y) > MOTION_THRESHOLD or abs(acc_z - 9.81) > MOTION_THRESHOLD:
        print("Motion detected! Acceleration:", (acc_x, acc_y, acc_z))
        red_led.value(1)
        send_ifttt_notification()
    else:
        red_led.value(0)



def main():
    connect_wifi()
    #print("Monitoring for motion and sending data...")
    # Check thingspeak every 30 seconds
    print("Starting read timer")
    thingspeak_timer.init(period=30000,mode=Timer.PERIODIC,callback=read_from_thingspeak)

if __name__ == "__main__":
    main()
