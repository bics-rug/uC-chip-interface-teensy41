"""
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
    Copyright (C) 2022 Willian Soares Girao - University of Groningen

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import serial, sys, time, struct
from enum import Enum

sys.path.append('../uC_api')
sys.path.append('./uC_api')

from packet import Data32bitPacket
from header import Data32bitHeader

# creating data packet to be sent to the uC.
dataPacket1 = Data32bitPacket(header = Data32bitHeader.IN_READ_TIME, time = 1)

# convets packet content to byte array (C struct) with 9 bytes.
packetBytes = dataPacket1.to_bytearray()

# connecting to uC (open serial port).
ArduinoUnoSerial = serial.Serial('/dev/ttyACM1', 115200, timeout = 1)

print('> port used: {}'.format(ArduinoUnoSerial.name))

# write/read uC.

ArduinoUnoSerial.reset_input_buffer()           # flush input buffer.

ArduinoUnoSerial.write(packetBytes)             # write packet content.

print('> data read: {}'.format(
    dataPacket1.from_bytearray(ArduinoUnoSerial.read(size = len(packetBytes))))
)

dataPacket2 = Data32bitPacket(header = Data32bitHeader.IN_READ_INSTRUCTIONS)

ArduinoUnoSerial.write(dataPacket2.to_bytearray())

print('> data read: {}'.format(
    dataPacket2.from_bytearray(ArduinoUnoSerial.read(size = len(dataPacket2.to_bytearray()))))
)
print('> data read: {}'.format(
    dataPacket1.from_bytearray(ArduinoUnoSerial.read(size = len(packetBytes))))
)
print('> data read: {}'.format(
    dataPacket1.from_bytearray(ArduinoUnoSerial.read(size = len(packetBytes))))
)

# close port.
ArduinoUnoSerial.close()
