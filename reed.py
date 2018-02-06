fo = open("output.txt", "w")
fo.write("hi\npizza")
fo.close()
'''
ReedPin = 13


def setup():
	GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(ReedPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.add_event_detect(ReedPin, GPIO.BOTH, callback=detect, bouncetime=200)


def Print(x):
	if x == 0:
		print '    ***********************************'
		print '    *   Detected Magnetic Material!   *'
		print '    ***********************************'

'''
