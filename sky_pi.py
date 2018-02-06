#SKYPISKYPISKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI SKYPI  
 
rover = Adafruit_MotorHAT(addr=0x60)

leftm=rover.getMotor(1)#left motor
leftm.setSpeed(255)

rightm=rover.getMotor(2)#right motor
rightm.setSpeed(255)

FULL_TURN_TIME = 3.04 # TIME TAKES TO TURN 360, IN SECONDS
DIST_THRESHOLD = 200

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
    angle = math.degrees(math.atan(float(y)/float(x)))
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

goToPoint(2370,1900)
