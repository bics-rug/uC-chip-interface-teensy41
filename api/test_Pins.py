import serial
from Pins import *

ArduinoUnoSerial = serial.Serial('/dev/ttyACM0', 115200, timeout = 1)

# ArduinoUnoSerial.reset_input_buffer()

pinA = Pins(serialPort = ArduinoUnoSerial, pinID = 2, pinType = 'output')

pinA.setPin(value = 0)

for i in range(10000000):
	pass

pinA.setPin(value = 1)

for i in range(10000000):
	pass

pinA.setPin(value = 0)