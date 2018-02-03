import serial
import time
import math
import sys
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import atexit
import urllib2
rover = Adafruit_MotorHAT(addr=0x60)

leftm=rover.getMotor(1)#left motor
leftm.setSpeed(255)

rightm=rover.getMotor(2)#right motor
rightm.setSpeed(255)

FULL_TURN_TIME = 19 # TIME TAKES TO TURN 360, IN SECONDS
TPOS_X = 1433
TPOS_Y = 408
DIST_THRESHOLD = 200
points = [(936, 666), (592, 795), (574, 1131), (570, 1466)]

def getGPS():
    try:
        data = urllib2.urlopen("http://10.144.7.184/coord.txt").read()
        return int(data.split(",")[0]), int(data.split(",")[1])
    except:
        print("Could not access coordinates...")

def getUntilDifferent(x, y):
    dx, dy = getGPS()
    while dx == x and dy == y:
        try:
            dx, dy = getGPS()
        except:
            pass
    
def around(x, y, tx, ty):
    return (tx - x) ** 2 + (ty - y) ** 2 <= DIST_THRESHOLD ** 2
#    return (tx - DIST_THRESHOLD <= x <= tx + DIST_THRESHOLD) and (ty - DIST_THRESHOLD <= y <= ty + DIST_THRESHOLD)

def moveUntilAt(tx, ty):
    dx, dy = getGPS()
    while not around(dx, dy, tx, ty):
        forward(3)
        stop()
        getUntilDifferent(dx, dy)
        try:
            dx, dy = getGPS()
        except:
            print("Couldn't Get GPS")
    stop()
    
def forward(t):
    leftm.run(Adafruit_MotorHAT.FORWARD)
    rightm.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(t)

def calcAngle(x, y):
    x = -x
    print("differences: ", x, y)
    angle = math.atan(float(y)/float(x)) * 180.0 / math.pi
    print("calc aangle", angle)
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


time.sleep(13)
# get current position
curX, curY = getGPS()
print("currentPosition (start)", curX, curY)
# move forwards for 3 seconds
forward(3)
stop()

getUntilDifferent(curX, curY)
# get current position (again)
nextX, nextY = getGPS()
print("nextCoords", nextX, nextY)
difX = nextX - curX
difY = nextY - curY
curAngle = calcAngle(difX, difY)
print("currentAngle", curAngle)

for point in points:
    time.sleep(3)
    TPOS_X = point[0]
    TPOS_Y = point[1]
    stop()
    curX, curY = getGPS()
    print("curPos", curX, curY)
    # get target position
    moveX = TPOS_X - curX
    moveY = TPOS_Y - curY
    # get angle
    targetAngle = calcAngle(moveX, moveY)
    # turn to get correct angle
    moveAngle = (targetAngle - curAngle) % 360
    print("moveangle", moveAngle)
    turn("LEFT", moveAngle)
    curAngle = targetAngle

    moveUntilAt(TPOS_X, TPOS_Y)
    stop()
