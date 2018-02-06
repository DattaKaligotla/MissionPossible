import serial
import time
import math
import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import urllib2
import os
import glob
import time
from mpu6050 import mpu6050
import RPi.GPIO as GPIO
import time

#SKYPISKYPISKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI  
 
rover = Adafruit_MotorHAT(addr=0x60)

leftm=rover.getMotor(1)#left motor
leftm.setSpeed(255)

rightm=rover.getMotor(2)#right motor
rightm.setSpeed(255)

FULL_TURN_TIME = 3.04 # TIME TAKES TO TURN 360, IN SECONDS
DIST_THRESHOLD = 200
fo = open("output.txt", "w") #file to write data into


#SKYPI/NAV
def getGPS():
    try:
        data = urllib2.urlopen("http://10.144.7.184/coord.txt").read()
        return int(data.split(",")[0]), int(data.split(",")[1])
    except:
        print("Could not access coordinates...")
    
def forward(t):
    leftm.run(Adafruit_MotorHAT.FORWARD)
    rightm.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(t)

def calcAngle(x, y):
    angle = math.atan(float(y)/float(x)) * 180.0 / math.pi
    if x == 0:
        if y >= 0:
            return 90
        else:
            return 270
    elif x > 0:
        return angle % 360
    else:
        return (180+angle) % 360

def angleTime(angle):
    return FULL_TURN_TIME * float(angle) / 360.0

def turn(direction, angle):
    direction = direction.upper()
    if direction[0] == "L":
        leftm.run(Adafruit_MotorHAT.BACKWARD)
        rightm.run(Adafruit_MotorHAT.FORWARD)
        time.sleep(angleTime(angle))
    else:
        leftm.run(Adafruit_MotorHAT.FORWARD)
        rightm.run(Adafruit_MotorHAT.BACKWARD)
        time.sleep(angleTime(angle))
    stop()

def stop():
    leftm.run(Adafruit_MotorHAT.RELEASE)
    rightm.run(Adafruit_MotorHAT.RELEASE)


def goToPoint(x, y): #to go to one point
    curX, curY = getGPS() # get current position
    while not (x - DIST_THRESHOLD <= curX <= x + DIST_THRESHOLD) or not(y - DIST_THRESHOLD <= curY <= y + DIST_THRESHOLD):
        curX, curY = getGPS() # get current position
        print("currentPosition:", curX, curY)
        forward(3) # move forwards for 3 seconds
        stop()
        time.sleep(5)
        collect_data() #COMMENT OUT IF NEED TO TEST WITHOUT SENSORS
        nextX, nextY = getGPS() # get current position (again)
        print("nextCoords: ", nextX, nextY)
        difX = nextX - curX
        difY = nextY - curY
        headAngle = calcAngle(difX, difY) #gets the current heading
        print("Heading: ", headAngle)
        targetAngle = calcAngle(x - curX, y - curY) #angle ya wannabe
        moveAngle = (targetAngle - headAngle) % 360 #turn to get correct angle
        print("Turning: ", moveAngle)
        turn("LEFT", moveAngle) #turns left
        forward(3)
    stop()

    
#TEMP
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
def get_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

#PHOTO
def get_ldr():
    pin_to_circuit = 11 #photoresitor pin
    count = 0
    #Output on the pin for 
    GPIO.setup(pin_to_circuit, GPIO.OUT)
    GPIO.output(pin_to_circuit, GPIO.LOW)
    time.sleep(0.1)

    #Change the pin back to input
    GPIO.setup(pin_to_circuit, GPIO.IN)
  
    #Count until the pin goes high
    while (GPIO.input(pin_to_circuit) == GPIO.LOW):
        count += 1
    return count

#ACCEL
sensor = mpu6050(0x68)
def get_accel():
    sensor = mpu6050(0x68)
    accel_data = sensor.get_accel_data()
    gyro_data = sensor.get_gyro_data()

    for i in ["x","y","z"]:
        accel_data[i] = str(accel_data[i])
        gyro_data[i] = str(gyro_data[i])

    return accel_data, gyro_data

#REED
ReedPin = 13

def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(ReedPin, GPIO.BOTH, callback=detect, bouncetime=200)

def reed():
	setup()
	time.sleep(2)
	if GPIO.input(13) == 0: return 1
	return 0

#DATA COLLECTION

def collect_data():
    time.sleep(10)
    location = getGPS()
    c, f = get_temp()
    ldr = get_ldr()
    reed = reed()
    accel, gyro = get_accel()
    print("Location:", location)
    print("Temperature:", c, "C  ",f, "F") #prints temperature
    print("Albedo:", ldr) #prints ldr
    print("Acceleration:", accel) #print acccel
    print("Gyro:", gyro) #prints gyro
    print("Reed:", reed)
    fo.write(location + ": " + str(c) + " C " + str(f) + " F " + str(ldr) + " " + str(accel) + " " + str(gyro)+ " " + str(reed) + " \n")

#RUNTIME
while True:
    x = int(input("X: "))
    y = int(input("Y: "))
    goToPoint(x, y)
    collect_data()
