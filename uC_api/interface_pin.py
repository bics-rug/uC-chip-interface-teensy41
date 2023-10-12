
#    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
#    Copyright (C) 2023 Ole Richter - University of Groningen
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


from .header import ConfigMainHeader, PinHeader, ConfigSubHeader
from .packet import ConfigPacket, PinPacket
from time import sleep
import logging

class Interface_PIN:
    """ This exposes all the pin functionality for use,

    for reading state and data please use the functions provided as they trigger an update of the internal state before returning values

    at the moment it is limited to digital read and write
    but is supposed to be extended to analog read and write and PWM functionality on first need / request
    """
    def __init__(self, api_object, interface_id):
        self.__status = 0
        """ 0 means not activated
            1 means activation pending
            2 means activted
            -1 means error
        """
        self.__status_timestamp = 0
        """
        - "INPUT" 
        - "OUTPUT"
        - "PWM" not implemented yet
        - "ANALOG_INPUT" not implemented yet
        - "ANALOG_OUTPUT" not implemented yet
        """
        self.__type = "NONE"
        self.__type_pending = "NONE"
        self.__type_timestamp = 0
        self.__interval = 0
        self.__interval_timestamp = 0
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        self.__errors = []
        self.__pin_id = interface_id
        self.__api = api_object
        self.__header = [ConfigMainHeader.IN_CONF_PIN, PinHeader.IN_PIN, PinHeader.IN_PIN_READ, PinHeader.OUT_PIN_LOW, PinHeader.OUT_PIN_HIGH]

    def header(self):
        """header returns the packet headers associated whith this interface

        :return: packet headers of this interface
        :rtype: Header (IntEnum)
        """
        return self.__header

    def status(self):
        """status returns the state of this interface,

        it can be:
         - active - everything is working fine
         - activation pending - the uC has not acknolaged the activation yet after the request to activate the interface
         - not active - the interface has not been configured and activate
         - error - there was an error during activation or during use, please consult the errors using the errors function

        :return: the state of the interface and the timestamp in us
        :rtype: (string, int)
        """
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return (state_str,self.__status_timestamp)
    
    def interface_type(self):
        """interface_type returns the currently configured mode of the pin

        :return: mode of the pin like "INPUT" or "OUTPUT"
        :rtype: string
        """
        self.update()
        return (self.__type,self.__type_timestamp)

    def interval(self):
        """interval not yet suported for PWM/analog read

        :return: _description_
        :rtype: _type_
        """
        self.update()
        return (self.__interval,self.__interval_timestamp)

    def data_from_chip(self):
        """data_from_chip will retun the data recoded by the uC send from the device under test (DUT)

        will retun 2 lists: one with the word recoded and one with the time when it was recorded, linked by index

        :return: the words from the DUT and the times of those words
        :rtype: ([int],[int])
        """
        self.update()
        return (self.__data_from_chip, data_from_chip_times)
    
    def data_to_chip(self):
        """data_to_chip will retun the data send by the uC to the device under test (DUT)

        will retun 2 lists: one with the word send and one with the exact time when it was send, linked by index

        the time might differ slightly from the time you sheduled the send word, 
        as it is the time when it was send out and the uC can only send one word at a time

        :return: the words send to the DUT and the times of those words
        :rtype: ([int],[int])
        """
        self.update()
        return (self.__data_to_chip, self.__data_to_chip_times)

    def data_from_chip_and_clear(self):
        self.update()
        data = self.__data_from_chip
        time = self.__data_from_chip_times
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        return (data, time)
    
    def data_to_chip_and_clear(self):
        self.update()
        data = self.__data_to_chip
        time = self.__data_to_chip_times
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        return (data, time)
    
    def errors(self):
        """errors all errors corresponding to this interface

        :return: list of all errors
        :rtype: [string]
        """
        self.update()
        return self.__errors

    def __str__(self):
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return "PIN_" + str(self.__pin_id) + \
            "\nHeader: " + str(self.__header) + \
            "\nStatus: " + state_str + " at " + str(self.__status_timestamp) + "us" + \
            "\nType "+ str(self.__type) +" at " + str(self.__type_timestamp) + "us" + \
            "\ninterval "+ str(self.__interval) +" at " + str(self.__interval_timestamp) + "us" + \
            "\nSend: "+ str(self.__data_to_chip) +" at " + str(self.__data_to_chip_times) + "us" + \
            "\nRecived: "+ str(self.__data_from_chip) +" at " + str(self.__data_from_chip_times) + "us" + \
            "\nERRORS: "+str(self.__errors) + "\n"

    def process_packet(self, packet):
        if packet.header() in self.__header:
            if packet.header() == self.__header[0]:
                if packet.config_header() == ConfigSubHeader.CONF_INPUT:
                    self.__status = 2
                    self.__status_timestamp = packet.time()
                    self.__type = "INPUT"
                    self.__type_timestamp = packet.time()
                    return
                elif packet.config_header() == ConfigSubHeader.CONF_OUTPUT:
                    self.__status = 2
                    self.__status_timestamp = packet.time()
                    self.__type = "OUTPUT"
                    self.__type_timestamp = packet.time()
                    return
            elif packet.header() == self.__header[1] and packet.pin_id() == self.__pin_id:
                self.__data_to_chip.append(packet.value())
                self.__data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2] and packet.pin_id() == self.__pin_id:
                return
            elif packet.header() == self.__header[3] and packet.pin_id() == self.__pin_id:
                self.__data_from_chip.append(packet.value())
                self.__data_from_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[4] and packet.pin_id() == self.__pin_id:
                self.__data_from_chip.append(packet.value())
                self.__data_from_chip_times.append(packet.time())
                return
        self.__errors.append(str(packet))
        self.__status = -1


    def activate(self, pin_mode="OUTPUT", interval=0, time=0):
        if self.__status >= 1:
            logging.warning("Pin "+str(self.__pin_id)+" is already activated or waiting activation, doing nothing")
        else:
            if pin_mode == "OUTPUT":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_OUTPUT, value=self.__pin_id, time = time))
                self.__status = 1
                self.__type_pending = pin_mode
                sleep(0.001)
                return
            elif pin_mode == "INPUT":
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_INPUT, value=self.__pin_id,time = time))
                self.__status = 1
                self.__type_pending = pin_mode
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
        if (time == 0 and self.__status == 2 and (self.__type == "OUTPUT" or self.__type == "ANALOG_OUTPUT")) or (time > 0 and self.__status >= 1 and (self.__type_pending == "OUTPUT" or self.__type_pending == "ANALOG_OUTPUT")):
            self.__api.send_packet(PinPacket(header = self.__header[1],pin_id=self.__pin_id , value = value, time = time))
        else:
            logging.error("Pin "+str(self.__pin_id)+" is not in OUTPUT/ANALOG_OUTPUT mode - data is not sent.")


    def update(self):
        self.__api.update_state()