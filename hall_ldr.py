import serial

arduino = serial.Serial("/dev/ttyACM0", 9600)

while True:
    read_data = ser.readline()
    print(read_data)
