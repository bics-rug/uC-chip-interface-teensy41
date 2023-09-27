"""
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
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

from header import ConfigMainHeader, Data32bitHeader, ConfigSubHeader
from packet import ConfigPacket, Data32bitPacket
import logging

class SPI:
    def __init__(self, api_object, interface_id):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.status = 0
        self.status_timestamp = 0
        self.mode = "NONE"
        self.mode_timestamp = 0
        self.speed = 0
        self.speed_timestamp = 0
        self.order = "NONE"
        self.order_timestamp = 0
        self.data_from_chip = []
        self.data_from_chip_times = []
        self.data_to_chip = []
        self.data_to_chip_times = []
        self.__api = api_object
        if interface_id == 0:
            self.__header = [ConfigMainHeader.IN_CONF_SPI0, Data32bitHeader.IN_SPI0, Data32bitHeader.OUT_SPI0]
        elif interface_id == 1:
            self.__header = [ConfigMainHeader.IN_CONF_SPI1, Data32bitHeader.IN_SPI1, Data32bitHeader.OUT_SPI1]
        elif interface_id == 2:
            self.__header = [ConfigMainHeader.IN_CONF_SPI2, Data32bitHeader.IN_SPI2, Data32bitHeader.OUT_SPI2]
        else:
            logging.error("SPI only up to 3 interfaces are supported at the moment")

    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.original_header() == ConfigSubHeader.CONF_ACTIVE:
                    self.status = 2
                    self.status_timestamp = packet.time()
                    return
            elif packet.header() == self.__header[1] :
                self.data_to_chip.append(packet.value())
                self.data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2]:
                self.data_from_chip.append(packet.value())
                self.data_from_chip_times.append(packet.time())
                return
        self.errors.append(str(packet))
        self.status = -1

    def activate(self, mode="SPI_MODE0", speed=4000000, order="LSBFIRST",time=0):
        if self.status >= 1:
            logging.warning("SPI interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            """@todo add config options"""
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE,time = time))
            self.status = 1
            time.sleep(0.001)

    def send_8bit(self, word, time = 0):
        self.__api.update_state()
        if (time == 0 and self.status == 2) or (time > 0 and self.status >= 1):
            self.__api.send_packet(Data8bitPacket(header = self.__header[1], value = word, time = time))
        else:
            logging.error("SPI interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")

    def send_32bit(self, word, time = 0):
        self.__api.update_state()
        if (time == 0 and self.status == 2) or (time > 0 and self.status >= 1):
            self.__api.send_packet(Data32bitPacket(header = self.__header[2], value = word, time = time))
        else:
            logging.error("SPI interface "+str(self.__header[2])+" is not active, please activate first - word is not sent.")

    def update(self):
        self.__api.update_state()