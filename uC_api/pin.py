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

from header import ConfigMainHeader, PinHeader, ConfigSubHeader
from packet import ConfigPacket, PinPacket
from time import sleep
import logging

class PIN:
    def __init__(self, api_object, interface_id):
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.status = 0
        self.status_timestamp = 0
        """
        - "INPUT" 
        - "OUTPUT"
        - "PWM" not implemented yet
        - "ANALOG_INPUT" not implemented yet
        - "ANALOG_OUTPUT" not implemented yet
        """
        self.mode = "NONE"
        self.__mode_pending = "NONE"
        self.mode_timestamp = 0
        self.interval = 0
        self.interval_timestamp = 0
        self.data_from_chip = []
        self.data_from_chip_times = []
        self.data_to_chip = []
        self.data_to_chip_times = []
        self.errors = []
        self.__pin_id = interface_id
        self.__api = api_object
        self.__header = [ConfigMainHeader.IN_CONF_PIN, PinHeader.IN_PIN, PinHeader.IN_READ_PIN, PinHeader.OUT_PIN]


    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.original_header() == ConfigSubHeader.CONF_INPUT:
                    self.status = 2
                    self.status_timestamp = packet.time()
                    self.type = "INPUT"
                    self.type_timestamp = packet.time()
                    return
                elif packet.original_header() == ConfigSubHeader.CONF_OUTPUT:
                    self.status = 2
                    self.status_timestamp = packet.time()
                    self.type = "OUTPUT"
                    self.type_timestamp = packet.time()
                    return
            elif packet.header() == self.__header[1] and packet.pin_id() == self.__pin_id:
                self.data_to_chip.append(packet.value())
                self.data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2] and packet.pin_id() == self.__pin_id:
                return
            elif packet.header() == self.__header[3] and packet.pin_id() == self.__pin_id:
                self.data_from_chip.append(packet.value())
                self.data_from_chip_times.append(packet.time())
                return
        self.errors.append(str(packet))
        self.status = -1


    def activate(self, pin_mode="OUTPUT", interval=0, time=0):
        if self.status >= 1:
            logging.warning("Pin "+str(self.__pin_id)+" is already activated or waiting activation, doing nothing")
        else:
            if pin_mode == "OUTPUT":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_OUTPUT, value=self.__pin_id, time = time))
                self.status = 1
                self.__mode_pending = pin_mode
                sleep(0.001)
                return
            elif pin_mode == "INPUT":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_INPUT, value=self.__pin_id,time = time))
                self.status = 1
                self.__mode_pending = pin_mode
                sleep(0.001)
                return
            elif pin_mode == "PWM":
                logging.warning("pin mode not implmented yet")
            elif pin_mode == "ANALOG_INPUT":
                logging.warning("pin mode not implmented yet")
            elif pin_mode == "ANALOG_OUPUT":
                logging.warning("pin mode not implmented yet")
            else:
                logging.error("pin.activate got wrong type "+str(pin_mode)+" only INPUT, OUTPUT, PWM, ANALOG_INPUT, ANALOG_OUTPUT are allowed")

        

    def send(self, value, time = 0):
        self.__api.update_state()
        if (time == 0 and self.status == 2 and (self.mode == "OUTPUT" or self.mode == "ANALOG_OUTPUT")) or (time > 0 and self.status >= 1 and (self.__mode_pending == "OUTPUT" or self.__mode_pending == "ANALOG_OUTPUT")):
            self.__api.send_packet(PinPacket(header = self.__header[1],pin_id=self.__pin_id , value = value, time = time))
        else:
            logging.error("Pin "+str(self.__pin_id)+" is not in OUTPUT/ANALOG_OUTPUT mode - data is not sent.")


    def update(self):
        self.__api.update_state()