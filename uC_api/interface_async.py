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
import logging, time

class Interface_Async:
    def __init__(self, api_object, interface_id, direction):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.__status = 0
        self.__status_timestamp = 0
        self.__mode = "NONE"
        self.__mode_timestamp = 0
        self.__req_pin = -1
        self.__req_pin_timestamp = 0
        self.__ack_pin = -1
        self.__ack_pin_timestamp = 0
        self.__data_width = -1
        self.__data_width_timestamp = 0
        self.__data_pins = [-1]*32
        self.__data_pins_timestamp = [0]*32
        self.__req_delay = -1
        self.__req_delay_timestamp = 0
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        self.__errors = []
        self.__api = api_object
        self.__direction = direction
        self.__name = "ASYNC_"+direction+str(interface_id)
        if direction == "TO_CHIP":
            self.__name = "ASYNC_"+direction+str(interface_id)
            if interface_id == 0:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP0, Data32bitHeader.IN_ASYNC_TO_CHIP0]
            elif interface_id == 1:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP1, Data32bitHeader.IN_ASYNC_TO_CHIP1] 
            elif interface_id == 2:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP2, Data32bitHeader.IN_ASYNC_TO_CHIP2]
            elif interface_id == 3:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP3, Data32bitHeader.IN_ASYNC_TO_CHIP3]
            elif interface_id == 4:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP4, Data32bitHeader.IN_ASYNC_TO_CHIP4]
            elif interface_id == 5:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP5, Data32bitHeader.IN_ASYNC_TO_CHIP5]
            elif interface_id == 6:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP6, Data32bitHeader.IN_ASYNC_TO_CHIP6]
            elif interface_id == 7:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_TO_CHIP7, Data32bitHeader.IN_ASYNC_TO_CHIP7]
            else:
                logging.error("only 8 AER to chip interfaces are supported at the moment")
        elif direction == "FROM_CHIP":
            if interface_id == 0:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP0, Data32bitHeader.OUT_ASYNC_FROM_CHIP0]
            elif interface_id == 1:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP1, Data32bitHeader.OUT_ASYNC_FROM_CHIP1] 
            elif interface_id == 2:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP2, Data32bitHeader.OUT_ASYNC_FROM_CHIP2]
            elif interface_id == 3:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP3, Data32bitHeader.OUT_ASYNC_FROM_CHIP3]
            elif interface_id == 4:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP4, Data32bitHeader.OUT_ASYNC_FROM_CHIP4]
            elif interface_id == 5:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP5, Data32bitHeader.OUT_ASYNC_FROM_CHIP5]
            elif interface_id == 6:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP6, Data32bitHeader.OUT_ASYNC_FROM_CHIP6]
            elif interface_id == 7:
                self.__header = [ConfigMainHeader.IN_CONF_ASYNC_FROM_CHIP7, Data32bitHeader.OUT_ASYNC_FROM_CHIP7]
            else:
                logging.error("only 8 AER to chip interfaces are supported at the moment")
        else:
            logging.error("AER unknown direction only TO_CHIP and FROM CHIP allowed")

    def __str__(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return "ASYNC_" + str(self.__direction) + \
            "\nHeader: " + str(self.__header) + \
            "\nStatus: " + state_str + " at " + str(self.__status_timestamp) + "us" + \
            "\nType "+ str(self.__mode) +" at " + str(self.__mode_timestamp) + "us" + \
            "\nHS req pin "+ str(self.__req_pin) +" at " + str(self.__req_pin_timestamp) + "us with delay of 20us*" + str(self.__req_delay) +" at " + str(self.__req_delay_timestamp) + "us" + \
            "\nHS ack pin "+ str(self.__ack_pin) +" at " + str(self.__ack_pin_timestamp) + \
            "\nData width "+ str(self.__data_width) +" at " + str(self.__data_width_timestamp) + "us" + \
            "\nData pins "+ str(self.__data_pins[:self.__data_width]) +" at " + str(self.__data_pins_timestamp[:self.__data_width]) + "us" + \
            "\nSend: "+ str(self.__data_to_chip) +" at " + str(self.__data_to_chip_times) + "us" + \
            "\nRecived: "+ str(self.__data_from_chip) +" at " + str(self.__data_from_chip_times) + "us" + \
            "\nERRORS: "+str(self.__errors) + "\n"

    def header(self):
        return self.__header

    def status(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return (state_str,self.__status_timestamp)
    
    def interface_type(self):
        self.update()
        return (self.__mode,self.__mode_timestamp)

    def data_pins(self):
        self.update()
        return (self.__data_pins[:self.__data_width],self.__data_pins_timestamp[:self.__data_width])
    
    def data_width(self):
        self.update()
        return (self.__data_width,self.__data_width_timestamp)
    
    def req_pin(self):
        self.update()
        return (self.__req_pin,self.__req_pin_timestamp)

    def ack_pin(self):
        self.update()
        return (self.__ack_pin,self.__ack_pin_timestamp)

    def req_delay(self):
        self.update()
        return (self.__req_delay,self.__req_delay_timestamp)

    def data_from_chip(self):
        self.update()
        return (self.__data_from_chip, data_from_chip_times)
    
    def data_to_chip(self):
        self.update()
        return (self.__data_to_chip, self.__data_to_chip_times)
    
    def errors(self):
        self.update()
        return self.__errors


    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.config_header() == ConfigSubHeader.CONF_ACTIVE:
                    self.__status = 2
                    self.__status_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_TYPE:
                    """@todo replace with type"""  
                    if packet.value() == 0:
                        self.__mode = "4Phase_Chigh_Dhigh"
                    else:
                        self.__mode = "4Phase_Clow_Dhigh"
                    self.__mode_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_ACK:
                    self.__ack_pin = packet.value()
                    self.__ack_pin_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_REQ:
                    self.__req_pin = packet.value()
                    self.__req_pin_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_WIDTH:
                    self.__data_width = packet.value()
                    self.__data_width_timestamp = packet.time()
                    return
                elif packet.config_header() < 32:
                    self.__data_pins[packet.config_header()] = packet.value()
                    self.__data_pins_timestamp[packet.config_header()] = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_REQ_DELAY:
                    self.__req_delay = packet.value()
                    self.__req_delay_timestamp = packet.time()
                    return
                
            elif packet.header() == self.__header[1]:
                if self.__direction == "TO_CHIP":
                    self.__data_to_chip.append(packet.value())
                    self.__data_to_chip_times.append(packet.time())
                    return
                elif self.__direction == "FROM_CHIP":
                    self.__data_from_chip.append(packet.value())
                    self.__data_from_chip_times.append(packet.time())
                    return
        self.__errors.append(str(packet))
        self.__status = -1

    def activate(self, req_pin, ack_pin, data_width, data_pins, mode="4Phase_Chigh_Dhigh", req_delay = 0, time = 0):
        if self.__status >= 1:
            logging.warning("ASYNC_to_chip interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            if mode == "4Phase_Chigh_Dhigh":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_TYPE, value = 0, time = time))
                self.__status = 1
            elif mode == "4Phase_Clow_Dhigh":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_TYPE, value = 1, time = time))
                self.__status = 1
            elif mode == "2Phase_Chigh_Dhigh":
                logging.warning("pin mode not implmented yet")
                return
            elif mode == "2Phase_Clow_Dhigh":
                logging.warning("pin mode not implmented yet")
                return
            else:
                logging.error("pin.activate got wrong type "+str(pin_mode)+" only 4Phase_Chigh_Dhigh, 4Phase_Clow_Dhigh, 2Phase_Chigh_Dhigh, 2Phase_Clow_Dhigh are allowed, more modes implemted on request")
                return
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACK, value = ack_pin, time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_REQ, value = req_pin, time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_WIDTH, value = data_width, time = time))
            for pin in range(data_width):
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader(pin), value = data_pins[pin], time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_REQ_DELAY, value = req_delay, time = time))
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE, time = time))
            self.__status = 1

    def send(self, word, time = 0):
        self.update()
        if self.__direction == "TO_CHIP":
            if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
                self.__api.send_packet(Data32bitPacket(header = self.__header[1], value = word, time = time))
            else:
                logging.error("AER to chip interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")
        else:
            logging.error("AER to chip interface "+str(self.__header[1])+" is reading interface - word is not sent.")

    def update(self):
        self.__api.update_state()
