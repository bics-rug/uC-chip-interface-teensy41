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

class Async_interface:
    def __init__(self, api_object, interface_id, direction):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.status = 0
        self.status_timestamp = 0
        self.mode = "NONE"
        self.mode_timestamp = 0
        self.req_pin = -1
        self.req_pin_timestamp = 0
        self.ack_pin = -1
        self.ack_pin_timestamp = 0
        self.data_width = -1
        self.data_width_timestamp = 0
        self.data_pins = [-1]*32
        self.data_pins_timestamp = [0]*32
        self.req_delay = -1
        self.req_delay_timestamp = 0
        self.data_from_chip = []
        self.data_from_chip_times = []
        self.data_to_chip = []
        self.data_to_chip_times = []
        self.__api = api_object
        self.__direction = direction
        if direction == "TO_CHIP":
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

    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.original_header() == ConfigSubHeader.CONF_ACTIVE:
                    self.status = 2
                    self.status_timestamp = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_HS_ACTIVE_LOW:
                    """@todo replace with type"""  
                    if packet.value() == 0:
                        self.mode = "4Phase_Chigh_Dhigh"
                    else:
                        self.mode = "4Phase_Clow_Dhigh"
                    self.mode_timestamp = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_ACK:
                    self.ack_pin = packet.value()
                    self.ack_pin_timestamp = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_REQ:
                    self.req_pin = packet.value()
                    self.req_pin_timestamp = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_WIDTH:
                    self.data_width = packet.value()
                    self.data_width_timestamp = packet.time()
                    return
                elif packet.original_header() < 32:
                    self.data_pins[packet.original_header()] = packet.value()
                    self.data_pins_timestamp[packet.original_header()] = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_REQ_DELAY:
                    self.req_delay = packet.value()
                    self.req_delay_timestamp = packet.time()
                    return
                
            elif packet.header() == self.__header[1]:
                if self.__direction == "TO_CHIP":
                    self.data_to_chip.append(packet.value())
                    self.data_to_chip_times.append(packet.time())
                    return
                elif self.__direction == "FROM_CHIP":
                    self.data_from_chip.append(packet.value())
                    self.data_from_chip_times.append(packet.time())
                    return
        self.errors.append(str(packet))
        self.status = -1

    def activate(self, req_pin, ack_pin, data_width, data_pins, mode="4Phase_Chigh_Dhigh", req_delay = 0, time = 0):
        if self.status >= 1:
            logging.warning("ASYNC_to_chip interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            if pin_mode == "4Phase_Chigh_Dhigh":
                self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_TYPE, value = 0, time = time))
                self.status = 1
                return
            elif pin_mode == "4Phase_Clow_Dhigh":
                self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_TYPE, value = 1, time = time))

                return
            elif pin_mode == "2Phase_Chigh_Dhigh":
                logging.warning("pin mode not implmented yet")
            elif pin_mode == "2Phase_Clow_Dhigh":
                logging.warning("pin mode not implmented yet")
            else:
                logging.error("pin.activate got wrong type "+str(pin_mode)+" only 4Phase_Chigh_Dhigh, 4Phase_Clow_Dhigh, 2Phase_Chigh_Dhigh, 2Phase_Clow_Dhigh are allowed, more modes implemted on request")
                return
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACK, value = ack_pin, time = time))
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_REQ, value = req_pin, time = time))
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_WIDTH, value = data_width, time = time))
            for pin in range(data_width):
                self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader(pin), value = data_pins[pin], time = time))
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_REQ_DELAY, value = req_delay, time = time))
            self._api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE, time = time))
            self.status = 1
            time.sleep(0.001)

    def send(self, word, time = 0):
        self.__api.update_state()
        if self.__direction == "TO_CHIP":
            if (time == 0 and self.status == 2) or (time > 0 and self.status >= 1):
                self.__api.send_packet(Data32bitPacket(header = self.__header[1], value = word, time = time))
            else:
                logging.error("AER to chip interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")
        else:
            logging.error("AER to chip interface "+str(self.__header[1])+" is reading interface - word is not sent.")

    def update(self):
        self.__api.update_state()
