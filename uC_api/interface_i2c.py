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


from .header import ConfigMainHeader, DataI2CHeader, ConfigSubHeader
from .packet import ConfigPacket, DataI2CPacket
import logging

class Interface_I2C:
    def __init__(self, api_object, interface_id):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.__status = 0
        self.__status_timestamp = 0
        self.__number_of_bytes = 0
        self.__number_of_bytes_timestamp = 0
        self.__speed = 0
        self.__speed_timestamp = 0
        self.__order = "NONE"
        self.__order_timestamp = 0
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        self.__errors = []
        self.__api = api_object
        if interface_id == 0:
            self.__header = [ConfigMainHeader.IN_CONF_I2C0, DataI2CHeader.IN_I2C0, DataI2CHeader.OUT_I2C0]
        elif interface_id == 1:
            self.__header = [ConfigMainHeader.IN_CONF_I2C1, DataI2CHeader.IN_I2C1, DataI2CHeader.OUT_I2C1]
        elif interface_id == 2:
            self.__header = [ConfigMainHeader.IN_CONF_I2C2, DataI2CHeader.IN_I2C2, DataI2CHeader.OUT_I2C2]
        else:
            logging.error("I2C only up to 3 interfaces are supported at the moment")
    
    def header(self):
        return self.__header

    def status(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return (state_str,self.__status_timestamp)
    
    def number_of_bytes(self):
        self.update()
        return (self.__number_of_bytes,self.__number_of_bytes_timestamp)

    def speed(self):
        self.update()
        return (self.__speed,self.__speed_timestamp)

    def byte_order(self):
        self.update()
        return (self.__order,self.__order_timestamp)

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
        return "I2C"+ \
            "\nHeader: " + str(self.__header) + \
            "\nStatus: " + state_str + " at " + str(self.__status_timestamp) + "us" + \
            "\nNumber of Bytes "+ str(self.__number_of_bytes) +" at " + str(self.__number_of_bytes_timestamp) + "us" + \
            "\nSpeed "+ str(self.__speed) +" at " + str(self.__speed_timestamp) + "us" + \
            "\nOrder "+ str(self.__order) +" at " + str(self.__order_timestamp) + "us" + \
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
                    self.__order = "MSBFIRST" if (packet.value() > 0) else "LSBFIRST"
                    self.__order_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_WIDTH:
                    self.__number_of_bytes = packet.value()
                    self.__number_of_bytes_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_SPEED_CLASS:
                    if packet.value() == 4:
                        self.__speed = 10000
                    elif packet.value() == 0:
                        self.__speed == 100000
                    elif packet.value() == 1:
                        self.__speed == 400000
                    elif packet.value() == 2:
                        self.__speed == 1000000
                    elif packet.value() == 3:
                        self.__speed == 3400000
                    else:
                        self.__speed = packet.value()
                    self.__speed_timestamp = packet.time()
                    return
            elif packet.header() == self.__header[1]:
                self.__data_to_chip.append((packet.read(),packet.device_address(),packet.register_address(),packet.value()))
                self.__data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2]:
                self.__data_from_chip.append((packet.read(),packet.device_address(),packet.register_address(),packet.value()))
                self.__data_from_chip_times.append(packet.time())
                return
        self.__errors.append(str(packet))
        self.__status = -1

    def activate(self, speed=400000, order="LSBFIRST", number_of_bytes=1, time=0):
        self.__api.update_state()
        if self.__status >= 1:
            logging.warning("I2C interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_BYTE_ORDER, value= (1 if (order == "MSBFIRST") else 0),time = time))
            if speed == 10000:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS, value=4,time = time))
            elif speed == 100000:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS, value=0,time = time))
            elif speed == 400000:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS, value=1,time = time))
            elif speed == 1000000:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS, value=2,time = time))
            elif speed == 3400000:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_SPEED_CLASS, value=3,time = time))
            else:
                logging.warning("I2C only supports 10000,100000,400000,1000000,3400000 Hz, defaulting to 100000")
            if number_of_bytes > 2:
                logging.warning("I2C ony supports one or two bytes, defaulting to 1")
            else:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_WIDTH, value=number_of_bytes,time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE,time = time))
            self.__status = 1

    def send_write(self,device_address, register_address, word, time = 0):
        self.__api.update_state()
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(DataI2CPacket(self.__header[1], device_address=device_address, register_address=register_address,read=0,value=word,time=time))
        else:
            logging.error("I2C interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")

    def send_read_request(self, device_address, register_address, word, time = 0):
        self.__api.update_state()
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(DataI2CPacket(self.__header[1], device_address=device_address, register_address=register_address,read=1,value=word,time=time))
        else:
            logging.error("I2C interface "+str(self.__header[2])+" is not active, please activate first - word is not sent.")

    def update(self):
        self.__api.update_state()