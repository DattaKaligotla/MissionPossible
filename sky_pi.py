
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_DCMotor
import time
import atexit
import math
import urllib2

SEC_TO_90_DEG=1.74 #amount of seconds it takes for the rover to turn 90 degrees *NOT ACTUAL VALUE
time_delta=4 #time in seconds for the rover to update its current location *NOT ACTUAL VALUE
length_delta=100 #how close the rover has to be of the desingnated point *NOT ACTUAL VALUE
i1=int(input("X: "))
i2=int(input("Y: "))
target=(i1,i2) #desired cordinated location *NOT ACTUAL VALUE

rover = Adafruit_MotorHAT(addr=0x60)

leftm = rover.getMotor(1)#left motor
leftm.setSpeed(255)

rightm = rover.getMotor(2)#right motor
rightm.setSpeed(255)

def getCord():
    cords=urllib2.urlopen("http://10.144.7.184/coord.txt").read()
    clist=cords.split(",")
    return (int(clist[0]),int(clist[1]))

def heading_calc(dx, deg): #makes sure angle in 360 degree domain
    if dx < 0:
        return 180 + deg
    if dx > 0:
        return 360 + deg

def turn_ang(end, target): #figures out angle between two points
    want_dx = target[0] - end[0]
    want_dy = target[1] - end[1]
    if want_dx == 0 and want_dx > 0: #if 90 or 270 degrees
        return 90
    elif want_dx == 0 and want_dx < 0:
        return 270
    else:
        want_tan = want_dy/want_dx
    want_deg = math.degrees(math.atan(want_tan))
    want_deg = heading_calc(want_dx, want_deg) #angle want to go
    return want_deg


def forward(time_length):
    leftm.run(Adafruit_MotorHAT.FORWARD)
    rightm.run(Adafruit_MotorHAT.FORWARD)
    time.sleep(time_length)
    
def backward(time_length):
    leftm.run(Adafruit_MotorHAT.BACKWARD)
    rightm.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep(time_length)

def right(deg):
    leftm.run(Adafruit_MotorHAT.FORWARD)
    rightm.run(Adafruit_MotorHAT.BACKWARD)
    time.sleep((deg/90) * SEC_TO_90_DEG)

def left(deg):
    leftm.run(Adafruit_MotorHAT.BACKWARD)
    rightm.run(Adafruit_MotorHAT.FORWARD)
    time.sleep((deg/90) * SEC_TO_90_DEG)
    
def stop():
    leftm.run(Adafruit_MotorHAT.RELEASE)
    rightm.run(Adafruit_MotorHAT.RELEASE)

start=getCord()
#continue the following loop until your x and y are both within "delta" of the target
while not(target[0] - length_delta <= start[0] <= target[0] + length_delta) or not(target[1] - length_delta <= start[1] <= target[1] + length_delta):
    print(start)
    forward(time_delta)
    stop()
    time.sleep(6)
    end=getCord()#not yet defined
    ang = (turn_ang(end,target) - turn_ang(start,end)) % 360 #makes sures no negative angles
    left(ang) #how much to turn by
    start=getCord()#not yet defined
stop()
