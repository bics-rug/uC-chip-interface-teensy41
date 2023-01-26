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
from header import ConfigMainHeader, ConfigSubHeader, Data32bitHeader
from packet import ConfigPacket, Data32bitPacket, Packet

class SPI:

    def __init__(self, serialPort, spiConf: int):

        if spiConf not in [0, 1, 2]:
            sys.exit('\'spiConf\' value must be either 0, 1 or 2 (exiting).')

        self.serialPort = serialPort
        self.portName = self.serialPort.name

        if spiConf == 0:
            self.spiConf = ConfigMainHeader.IN_CONF_SPI0
        elif spiConf == 1:
            self.spiConf = ConfigMainHeader.IN_CONF_SPI1
        else:
            self.spiConf = ConfigMainHeader.IN_CONF_SPI2

        # setup spi for usage.
        status = self.__setupSPI()

        print('status: ', status)

    """
    Creates and send a data packet that configures/initializes the SPI bus.
    """
    def __setupSPI(self):

        # configuration packet.
        self.spiConfPacket = ConfigPacket(
            header = self.spiConf, 
            config_header = ConfigSubHeader.CONF_ACTIVE)

        # send packet.
        self.serialPort.write(self.spiConfPacket.to_bytearray())

        # read back request status.
        status = Data32bitPacket(header = Data32bitHeader.IN_READ_LAST)
        self.serialPort.write(status.to_bytearray())

        return (Packet.from_bytearray(self.serialPort.read(size = len(status.to_bytearray()))))._header



