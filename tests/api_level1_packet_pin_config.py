"""
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
    Copyright (C) 2022 Willian Soares Girao - University of Groningen
    Copyright (C) 2023 Ole Richter - University of Groningen

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

import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../uC_api')
sys.path.append('./uC_api')

from packet import ConfigPacket, PinPacket, Data32bitPacket, Packet
from header import ConfigMainHeader, ConfigSubHeader, PinHeader, Data32bitHeader
from uC import uC_api

logging.basicConfig(level=logging.INFO)

# 1. connecting to uC (open serial port).

uc = uC_api('/dev/ttyACM0',1)

# 2. creating data packet to be sent to the uC.

PIN_ID = 13

pinConfigPacket = Data32bitPacket(
	header = Data32bitHeader.IN_SET_TIME,				# start experiment.
	value = 1)	

uc.send_packet(pinConfigPacket) # send start.
time.sleep(1)
if uc.has_packet():
    print('> pin config request responce: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin config request responce: ')	

pinConfigPacket = ConfigPacket(
	header = ConfigMainHeader.IN_CONF_PIN,				# pin configuration.
	config_header = ConfigSubHeader.CONF_OUTPUT,		# pin as OUTPUT.
	value = PIN_ID)										# pin ID.

# 3. send pin configuration to uC.

uc.send_packet(pinConfigPacket) # send pin configuration.
time.sleep(1)
if uc.has_packet():
    print('> pin config request responce: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin config request responce: ')

pinPacket = PinPacket(
	header = PinHeader.IN_PIN_READ,							# read from pin.
	pin_id = PIN_ID,
	value = 0)		

uc.send_packet(pinPacket) # send pin read.
time.sleep(1)
if uc.has_packet():
    print('> pin state: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin read responce: ')
time.sleep(1)
if uc.has_packet():
    print('> pin state: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin read confirmation responce: ')
time.sleep(1)
pinPacket = PinPacket(
	header = PinHeader.IN_PIN,							# write to  pin.
	pin_id = PIN_ID,
	value = 1)											# set pin HIGH.

uc.send_packet(pinPacket) # send pin write.
time.sleep(1)
if uc.has_packet():
    print('> pin wriute request responce: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin write request responce: ')

pinPacket = PinPacket(
	header = PinHeader.IN_PIN_READ,							# read from pin.
	pin_id = PIN_ID,
	value = 0)											

uc.send_packet(pinPacket) # send pin read.
time.sleep(1)
if uc.has_packet():
    print('> pin state: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin read responce: ')

if uc.has_packet():
    print('> pin state: {}'.format(str(uc.read_packet())))
else:
    print('> [error] no pin read confirmation responce: ')

# close port.
