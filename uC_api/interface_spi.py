
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


from .header import ConfigMainHeader, Data32bitHeader, ConfigSubHeader
from .packet import ConfigPacket, Data32bitPacket
from time import sleep
import logging

class Interface_SPI:
    """ The interface SPI creates and object though which the interface can be accessed

    the pins on the uC are fixed and depend on the specific uC model, please consult the pin out diagram of you uC

    to read out the state use the object funtions to get the state returned, this is done so an state ubdate can be triggered before returning the values
    """
    def __init__(self, api_object, interface_id):
        """__init__ creates a not activate interface object

        :param api_object: the parent manageing the conection to the uC
        :type api_object: uC_api
        :param interface_id: the identifier of the interface, so the interface number in the hardware it is usulay depiced after the port name like 0 -> SCK, COPI, CIPO; 1-> SCK1, COPI1, CIPO1 and so on;
        :type interface_id: int
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
    
    def interface_mode(self):
        """interface_mode the currently active mode, consult spi arduino docs for more information

        spi has 4 modes which are numbered SPI_MODE0 ...

        :return: the mode and the timestamp in us as touple
        :rtype: (string, int)
        """
        self.update()
        return (self.__mode,self.__mode_timestamp)

    def speed(self):
        """speed the speed class result of the current

        :return: the frequency and the timestamp in us
        :rtype: (int, int)
        """
        self.update()
        return (self.__speed,self.__speed_timestamp)

    def bit_order(self):
        """bit_order the bit order in which the word is send

        :return: the active bitorder and the timestamp in us
        :rtype: (string, int)
        """
        self.update()
        return (self.__order,self.__order_timestamp)

    def number_of_bytes():
        """number_of_bytes the width of each send word, it can be 1,2,3 or 4 bytes

        :return: the wisth of each word and the timestamp in us
        :rtype: (int, int)
        """
        self.update()
        return (self.__number_of_bytes,self.__number_of_bytes_timestamp)

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
        """__str__ will return the current state, properies and data as a string

        :return: the current state, properies and data
        :rtype: string
        """
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
        """process_packet this function accepts packages fro this interface from the api and updates its internal state

        :param packet: the packet to be processed
        :type packet: Packet, or any sub class
        """
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
        """activate activates and configures the interface, 
        if the interface is not availible on the UC it will put its state in en error state and prevent further use

        waits for the activation to be acknolaged by the uC if no exec_time is given

        :param mode: choose between "SPI_MODE0" "SPI_MODE1" "SPI_MODE2" or "SPI_MODE3" see arduino SPI docs, defaults to "SPI_MODE0"
        :type mode: str, optional
        :param speed_class: 0-8 0:10kHz 1:50kHz 2:100kHz 3:500kHz 4:1MHz 5:2MHz 6:4MHz 7:8MHz 8:12MHz, defaults to 0
        :type speed_class: int, optional
        :param order: Choose between "MSBFIRST" or "LSBFIRST" for order in which the word is transmitted, defaults to "LSBFIRST"
        :type order: str, optional
        :param number_of_bytes: 1-4 number of bytes contained in a word or better the length of a word, defaults to 1
        :type number_of_bytes: int, optional
        :param time: the time in us after start_experiment when this function should be executed, defaults to 0 (execute instantly)
        :type time: int, optional
        """
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
            if time == 0:
                self.__wait_for_activation()

    def send(self, word, time = 0):
        """send send a word via this interface

        :param word: the word to send
        :type word: int
        :param time: the time in us after start_experiment when this word should be send, defaults to 0 (execute instantly)
        :type time: int, optional
        """
        self.__api.update_state()
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(Data32bitPacket(header = self.__header[1], value = word, time = time))
        else:
            logging.error("SPI interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")

    def update(self):
        """update updates the internal state form the uC
        """
        self.__api.update_state()

    def __wait_for_activation(self):
        """ wait for the activation of the interface to be acknolaged by the uC
        """
        # bug need to push additional packets to get the uC to respond
        # something is waiting on something else or idle - soft deadlock
        self.__api.send_packet(Data32bitPacket(header = Data32bitHeader.IN_READ_TIME))
        self.__api.send_packet(Data32bitPacket(header = Data32bitHeader.IN_READ_TIME))
        self.__api.send_packet(Data32bitPacket(header = Data32bitHeader.IN_READ_TIME))
        self.__api.send_packet(Data32bitPacket(header = Data32bitHeader.IN_READ_TIME))
        self.__api.send_packet(Data32bitPacket(header = Data32bitHeader.IN_READ_TIME))
        while True:
            self.__api.update_state()
            if self.__status == 2:
                return
            elif self.__status != 1:
                break
            if not self.__api.wait_for_data.wait(10):
                logging.warning("Interface "+str(self.__header[0])+" activation was not acknolaged - 10 sec no responce from uC, status is "+str(self.__status))
                return
