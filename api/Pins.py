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

import sys
from packet import ConfigPacket, Packet, Data32bitPacket, PinPacket
from header import ConfigMainHeader, ConfigSubHeader, Data32bitHeader, PinHeader

class Pins:

    def __init__(self, serialPort, pinID: int, pinType: str):

        if pinType != 'output' and pinType != 'input':
            sys.exit('\'pinType\' (\'input\'/\'output\') not defined (exiting).')

        self.pinID = pinID
        self.pinType = pinType

        self.serialPort = serialPort
        self.portName = self.serialPort.name

        # configure pin for usage.
        status = self.__pinConfig()
        if status != Data32bitHeader.OUT_SUCCESS_PIN_CONFIGURED:
            sys.exit(f'[api error] pin {self.pinID} could not be configured successfully (header {status} returned).')

    """
    Configures a pin to be used as input or output.
    """
    def __pinConfig(self):

        # configuration packet.
        self.pinConfigPacket = ConfigPacket(
            header = ConfigMainHeader.IN_CONF_PIN,             
            config_header = ConfigSubHeader.CONF_OUTPUT if self.pinType == 'output' else ConfigSubHeader.CONF_INPUT,
            value = self.pinID)                                     

        # send pin configuration.
        self.serialPort.write(self.pinConfigPacket.to_bytearray())

        # read back request status.
        status = Data32bitPacket(header = Data32bitHeader.IN_READ_LAST)
        self.serialPort.write(status.to_bytearray())

        # return status header.
        return (Packet.from_bytearray(self.serialPort.read(size = len(status.to_bytearray()))))._header

    """
    Sets a pin HIGH (1) or LOW (0).
    """
    def setPin(self, value: int):

        # pin control packet.
        pinPacket = PinPacket(
            header = PinHeader.IN_PIN,                         
            pin_id = self.pinID,
            value = value)                                         

        self.serialPort.write(pinPacket.to_bytearray())









