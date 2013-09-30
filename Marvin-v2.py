#!/usr/bin/env python

import socket, OSC, re, time, threading, serial, math

ser_port = "/dev/ttyACM0"
ser_timeout = 0.1 # 100 millis
ser_baud = 115200

receive_address = '10.0.1.6', 2222
send_address = '10.0.1.3', 2223

movesList = []
lastMove = '$MOVE,0,0,0' # Last move is stop all motors.

class PiException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)


# Read serial stream.
def doRead(ser,term):
	matcher = re.compile(term)    #gives you the ability to search for anything
	buff    = ""
	tic     = time.clock()
	buff   += ser.read(128)
  	# you can use if not ('\n' in buff) too if you don't like re
	while (time.clock() - tic) and (not matcher.search(buff)):
		buff += ser.read(128)
	return buff




# Initialize serial stream.
while True:
	try:
		SER = serial.Serial(ser_port,ser_baud,timeout=ser_timeout)
		# http://stackoverflow.com/questions/11385915/serial-interface-initialisation-with-arduino-and-c
		#disable DTR
		#SER.setDTR(level=False)
		#wait for 2 seconds
		#time.sleep(2)
		break;
	except serial.SerialException:
		print "Waiting for device " + ser_port + " to be availaible"
		time.sleep(3)

SER.flushInput()
# Closing the serial port will reboot the Arduino.
# SER.close()


##########################
#	OSC
##########################

# Initialize the OSC server and the client.
s = OSC.OSCServer(receive_address)
c = OSC.OSCClient()
c.connect(send_address)

s.addDefaultHandlers()

# define a message-handler function for the server to call.
def test_handler(addr, tags, stuff, source):
	print "---"
	print "received new osc msg from %s" % OSC.getUrlStr(source)
	print "with addr : %s" % addr
	print "typetags %s" % tags
	print "data %s" % stuff
	msg = OSC.OSCMessage()
	msg.setAddress(addr)
	msg.append(stuff)
	c.send(msg)
	print "return message %s" % msg
	print "---"


def moveStop_handler(add, tags, stuff, source):
	addMove(0,0)

def moveJoystick_handler(add, tags, stuff, souce):
	addMove(int(stuff[0]), int(stuff[1]))


def addMove(moveLeft, moveRight):
	
	mLeft, mRight = rotate45(moveLeft,moveRight)

	if(mLeft > 255):
		mLeft = 255
	if(mLeft < -255):
		mLeft = -255

	if(mRight > 255):
		mRight = 255
	
	if(mRight < -255):
		mRight = -255

	# Add the move commande to the pile.
	movesList.append('$MOVE,' + str(mLeft) + ',' + str(mRight) + ',\r\n')
	
# https://github.com/jmckib/two-wheel-arduino-robot/blob/master/remote_control.ino
# Rotate a vector 45 degrees clockwise.
def rotate45(x, y):
	neg_45 = -1 * math.pi / 4
	new_x = x * math.cos(neg_45) - y * math.sin(neg_45)
	new_y = x * math.sin(neg_45) + y * math.cos(neg_45)
	return (int(new_x), int(new_y))

def getLastmove():
	global movesList
	if len(movesList) > 0 :
		newMove = movesList.pop() # Get the last item in the list.
		del movesList[:] # Empy the list.
		return newMove
	return 0

class moveThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.ready = 0
		self.continueloop = True

	def __call__(self):
		move(self)

	def run(self):
		while self.continueloop :
			newMove = getLastmove()
			if newMove and lastMove != newMove :
				
				if(SER.isOpen()):
					SER.write(newMove)
					print newMove
					serialValue = doRead(SER,term='\n')
					if serialValue:
						self.ready = 1
					else:
						self.ready = 0

				else:
					raise PiExecption("Can't connect to serial device.")
	def close(self):
		self.continueloop = False	

mover = moveThread()

# adding my functions
s.addMsgHandler("/basic/stop", moveStop_handler)
s.addMsgHandler("/basic/joystick", moveJoystick_handler)
# just checking which handlers we have added
print "Registered Callback-functions are :"
for addr in s.getOSCAddressSpace():
	print addr
 
 
# Start OSCServer
print "\nStarting OSCServer. Use ctrl-C to quit."
st = threading.Thread( target = s.serve_forever )
st.start()

# Start moveThread
mvt = moveThread()
mvt.start()

# Loop while threads are running.
try :
	while 1 :
		time.sleep(5)
 
except KeyboardInterrupt :
	print "\nClosing OSCServer."
	s.close()
	mvt.close()
	print "Waiting for Server-thread to finish"
	mvt.join()
	st.join()
	print "Done"

