"""
    This file is part of the Firmware project to interface with small Neuromorphic chips
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

sys.path.append('../api')

from packet import ConfigPacket, PinPacket, Data32bitPacket, Packet
from header import ConfigMainHeader, ConfigSubHeader, PinHeader, Data32bitHeader

# 1. connecting to uC (open serial port).

ArduinoUnoSerial = serial.Serial('/dev/ttyACM0', 115200, timeout = 1)
ArduinoUnoSerial.reset_input_buffer()           		# flush input buffer.

print('> port used: {}'.format(ArduinoUnoSerial.name))

# 2. creating data packet to be sent to the uC.

PIN_ID = 2

pinConfigPacket = ConfigPacket(
	header = ConfigMainHeader.IN_CONF_PIN,				# pin configuration.
	config_header = ConfigSubHeader.CONF_OUTPUT,		# pin as OUTPUT.
	value = PIN_ID)										# pin ID.

# 3. send pin configuration to uC.

ArduinoUnoSerial.write(pinConfigPacket.to_bytearray())  # send pin configuration.

status = Data32bitPacket(header = Data32bitHeader.IN_READ_LAST)

ArduinoUnoSerial.write(status.to_bytearray())  			# request config exec status.

# 4. create pin control packet.

stat_return = (Packet.from_bytearray(ArduinoUnoSerial.read(size = len(status.to_bytearray()))))._header

if (stat_return == 240):

	print('> pin config status: {}'.format(str(stat_return)))

	pinPacket = PinPacket(
		header = PinHeader.IN_PIN,							# set pin as output pin.
		pin_id = PIN_ID,
		value = 0)											# set pin HIGH.

	ArduinoUnoSerial.write(pinPacket.to_bytearray())  		# send set pin HIGH cmd.

else:

	print('> pin config status: {}'.format(str(status.from_bytearray(ArduinoUnoSerial.read(size = len(status.to_bytearray()))))))

# close port.
ArduinoUnoSerial.close()
