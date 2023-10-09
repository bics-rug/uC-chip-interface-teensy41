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

from .header import ConfigMainHeader, Data32bitHeader, ConfigSubHeader
from .packet import ConfigPacket, Data32bitPacket
import logging

class Interface_SPI:
    def __init__(self, api_object, interface_id):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.__status = 0
        self.__status_timestamp = 0
        self.__mode = "NONE"
        self.__mode_timestamp = 0
        self.__speed = 0
        self.__speed_timestamp = 0
        self.__order = "NONE"
        self.__order_timestamp = 0
        self.__number_of_bytes = 0
        self.__number_of_bytes_timestamp=0
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        self.__api = api_object
        self.__errors = []
        if interface_id == 0:
            self.__header = [ConfigMainHeader.IN_CONF_SPI0, Data32bitHeader.IN_SPI0, Data32bitHeader.OUT_SPI0]
        elif interface_id == 1:
            self.__header = [ConfigMainHeader.IN_CONF_SPI1, Data32bitHeader.IN_SPI1, Data32bitHeader.OUT_SPI1]
        elif interface_id == 2:
            self.__header = [ConfigMainHeader.IN_CONF_SPI2, Data32bitHeader.IN_SPI2, Data32bitHeader.OUT_SPI2]
        else:
            logging.error("SPI only up to 3 interfaces are supported at the moment")

    def header(self):
        return self.__header

    def status(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return (state_str,self.__status_timestamp)
    
    def interface_mode(self):
        self.update()
        return (self.__mode,self.__mode_timestamp)

    def speed(self):
        self.update()
        return (self.__speed,self.__speed_timestamp)

    def bit_order(self):
        self.update()
        return (self.__order,self.__order_timestamp)

    def number_of_bytes():
        self.update()
        return (self.__number_of_bytes,self.__number_of_bytes_timestamp)

    def data_from_chip(self):
        self.update()
        return (self.__data_from_chip, data_from_chip_times)
    
    def data_to_chip(self):
        self.update()
        return (self.__data_to_chip, self.__data_to_chip_times)
    
    def errors(self):
        self.update()
        return self.__errors

    def __str__(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return "SPI"+ \
            "\nHeader: " + str(self.__header) + \
            "\nStatus: " + state_str + " at " + str(self.__status_timestamp) + "us" + \
            "\nMode "+ str(self.__mode) +" at " + str(self.__mode_timestamp) + "us" + \
            "\nSpeed "+ str(self.__speed) +" at " + str(self.__speed_timestamp) + "us" + \
            "\nOrder "+ str(self.__order) +" at " + str(self.__order_timestamp) + "us" + \
            "\nBytes per word "+ str(self.__number_of_bytes) +" at " + str(self.__number_of_bytes_timestamp) + "us" + \
            "\nSend: "+ str(self.__data_to_chip) +" at " + str(self.__data_to_chip_times) + "us" + \
            "\nRecived: "+ str(self.__data_from_chip) +" at " + str(self.__data_from_chip_times) + "us" + \
            "\nERRORS: "+str(self.__errors) + "\n"

    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.config_header() == ConfigSubHeader.CONF_ACTIVE:
                    self.__status = 2
                    self.__status_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_BYTE_ORDER:
                    self.__order = ("MSBFIRST" if (packet.value()==1) else "LSBFIRST")
                    self.__order_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_SPEED_CLASS:
                    self.__speed = packet.value()
                    self.__speed_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_TYPE:
                    self.__mode = packet.value()
                    self.__mode_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_WIDTH:
                    self.__number_of_bytes = packet.value()
                    self.__number_of_bytes_timestamp = packet.time()    
                    return
            elif packet.header() == self.__header[1] :
                self.__data_to_chip.append(packet.value())
                self.__data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2]:
                self.__data_from_chip.append(packet.value())
                self.__data_from_chip_times.append(packet.time())
                return
        self.__errors.append(str(packet))
        self.__status = -1

    def activate(self, mode="SPI_MODE0", speed_class=0, order="LSBFIRST",number_of_bytes=1,time=0):
        if self.__status >= 1:
            logging.warning("SPI interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_TYPE, \
                value=( 0 if mode == "SPI_MODE0" else (1 if mode == "SPI_MODE1" else (2 if mode == "SPI_MODE2" else 3))),time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS,value=speed_class,time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_BYTE_ORDER, \
                value=(1 if order == "MSBFIRST" else 0),time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_WIDTH,value=number_of_bytes,time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE,time = time))
            self.__status = 1

    def send(self, word, time = 0):
        self.__api.update_state()
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(Data32bitPacket(header = self.__header[1], value = word, time = time))
        else:
            logging.error("SPI interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")

    def update(self):
        self.__api.update_state()