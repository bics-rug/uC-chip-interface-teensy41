import serial
from SPI import *

ArduinoUnoSerial = serial.Serial('/dev/ttyACM0', 115200, timeout = 1)
ArduinoUnoSerial.reset_input_buffer()

spi0 = SPI(serialPort = ArduinoUnoSerial, spiConf = 0) # spiConf: 0, 1 or 2
