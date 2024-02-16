
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



from .header import ConfigMainHeader, DataI2CHeader, ConfigSubHeader
from .packet import ConfigPacket, DataI2CPacket
import logging

class Interface_I2C:
    """ This class is the API for the I2C interfaces of the uC
        It is used to configure, send and recive data from the I2C interfaces
    """
    def __init__(self, api_object, interface_id):
        """ Constructor for the I2C interface
            @param api_object: the parent API object
            @param interface_id: the id of the I2C interface
        """
        # the status of the I2C interface, and the time of when this status was processed by the uC
        # 0 means not activated
        # 1 means activation pending
        # 2 means activted
        # -1 means error
        self.__status = 0
        self.__status_timestamp = 0
        # the protocol data word width of the I2C interface, and the time of when this status was processed by the uC
        self.__number_of_bytes = 0
        self.__number_of_bytes_timestamp = 0
        # the speed of the I2C interface, and the time of when this status was processed by the uC
        # 10000, 100000, 400000, 1000000, 3400000
        self.__speed = 0
        self.__speed_timestamp = 0
        # the byte order of the I2C interface, and the time of when this status was processed by the uC
        self.__order = "NONE"
        self.__order_timestamp = 0
        # the data recived from the chip, and the time it was processed by the uC
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        # the data send to the chip, and the time it was processed by the uC
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        # the errors and unhandled packets reported by the uC
        self.__errors = []
        # the parent API object
        self.__api = api_object
        # the headers this I2C interface object is responsible for
        if interface_id == 0:
            self.__header = [ConfigMainHeader.IN_CONF_I2C0, DataI2CHeader.IN_I2C0, DataI2CHeader.OUT_I2C0]
        elif interface_id == 1:
            self.__header = [ConfigMainHeader.IN_CONF_I2C1, DataI2CHeader.IN_I2C1, DataI2CHeader.OUT_I2C1]
        elif interface_id == 2:
            self.__header = [ConfigMainHeader.IN_CONF_I2C2, DataI2CHeader.IN_I2C2, DataI2CHeader.OUT_I2C2]
        else:
            logging.error("I2C only up to 3 interfaces are supported at the moment")
    
    def header(self):
        """ Returns the headers this I2C interface object is responsible for
        @return: the headers this I2C interface object is responsible for
        """
        return self.__header

    def status(self):
        """ Returns the status of the I2C interface, and the time of when this status was processed by the uC
        @return: (state_str,timestamp) where state_str is the status of the I2C interface, and timestamp is the time of when this status was processed by the uC
        """
        self.update()
        state_str = ("active" if self.__status == 2 else ("activation pending" if self.__status == 1 else ("not active" if self.__status == 0 else "error" )))
        return (state_str,self.__status_timestamp)
    
    def number_of_bytes(self):
        """ Returns the protocol data word width of the I2C interface, and the time of when this status was processed by the uC
        @return: (number_of_bytes,timestamp) where number_of_bytes is the protocol data word width of the I2C interface, and timestamp is the time of when this status was processed by the uC
        """
        self.update()
        return (self.__number_of_bytes,self.__number_of_bytes_timestamp)

    def speed(self):
        """ Returns the speed of the I2C interface, and the time of when this status was processed by the uC
        @return: (speed,timestamp) where speed is the speed of the I2C interface, and timestamp is the time of when this status was processed by the uC
        """
        self.update()
        return (self.__speed,self.__speed_timestamp)

    def byte_order(self):
        """ Returns the byte order of the I2C interface, and the time of when this status was processed by the uC
        @return: (order,timestamp) where order is the byte order of the I2C interface, and timestamp is the time of when this status was processed by the uC
        """
        self.update()
        return (self.__order,self.__order_timestamp)

    def data_from_chip(self):
        """ Returns the data recived from the chip, and the time it was processed by the uC

        will retun 2 lists: one with the word recoded and one with the time when it was recorded, linked by index

        @return: ([data_from_chip], [data_from_chip_times]) where data_from_chip is the data recived from the chip, and data_from_chip_times is the time it was processed by the uC
        """
        self.update()
        return (self.__data_from_chip, data_from_chip_times)
    
    def data_to_chip(self):
        """ Returns the data send to the chip, and the time it was processed by the uC

        data_to_chip will retun the data send by the uC to the device under test (DUT)

        will retun 2 lists: one with the word send and one with the exact time when it was send, linked by index

        the time might differ slightly from the time you sheduled the send word, 
        as it is the time when it was send out and the uC can only send one word at a time

        @return: ([data_to_chip], [data_to_chip_times]) where data_to_chip is the data send to the chip, and data_to_chip_times is the time it was processed by the uC
        """
        self.update()
        return (self.__data_to_chip, self.__data_to_chip_times)

    def data_from_chip_and_clear(self):
        """ Returns the data recived from the chip, and the time it was processed by the uC, and clears the data

        will retun 2 lists: one with the word recoded and one with the time when it was recorded, linked by index
        
        @return: ([data_from_chip], [data_from_chip_times]) where data_from_chip is the data recived from the chip, and data_from_chip_times is the time it was processed by the uC
        """
        self.update()
        data = self.__data_from_chip
        time = self.__data_from_chip_times
        self.__data_from_chip = []
        self.__data_from_chip_times = []
        return (data, time)
    
    def data_to_chip_and_clear(self):
        """ Returns the data send to the chip, and the time it was processed by the uC, and clears the data
        data_to_chip will retun the data send by the uC to the device under test (DUT)

        will retun 2 lists: one with the word send and one with the exact time when it was send, linked by index

        the time might differ slightly from the time you sheduled the send word, 
        as it is the time when it was send out and the uC can only send one word at a time

        @return: ([data_to_chip], [data_to_chip_times]) where data_to_chip is the data send to the chip, and data_to_chip_times is the time it was processed by the uC
        """
        self.update()
        data = self.__data_to_chip
        time = self.__data_to_chip_times
        self.__data_to_chip = []
        self.__data_to_chip_times = []
        return (data, time)
    
    def errors(self):
        """ Returns the errors and unhandled packets reported by the uC for this interface
        @return: [errors] where errors is the errors and unhandled packets reported by the uC for this interface
        """
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
        """ Processes a packet from the uC, and updates the status and stores the data of/in the I2C interface object 
        @param packet: the packet to process
        """
        if packet.header() in self.__header:
            # handle a configuration acknoledgement
            if packet.header() == self.__header[0]:
                # activation of the interface
                if packet.config_header() == ConfigSubHeader.CONF_ACTIVE:
                    self.__status = 2
                    self.__status_timestamp = packet.time()
                    return
                # byte order
                elif packet.config_header() == ConfigSubHeader.CONF_BYTE_ORDER:
                    self.__order = "MSBFIRST" if (packet.value() > 0) else "LSBFIRST"
                    self.__order_timestamp = packet.time()
                    return
                # number of bytes
                elif packet.config_header() == ConfigSubHeader.CONF_WIDTH:
                    self.__number_of_bytes = packet.value()
                    self.__number_of_bytes_timestamp = packet.time()
                    return
                # speed
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
            # handle a data packet
            elif packet.header() == self.__header[1]:
                self.__data_to_chip.append((packet.read(),packet.device_address(),packet.register_address(),packet.value()))
                self.__data_to_chip_times.append(packet.time())
                return
            elif packet.header() == self.__header[2]:
                self.__data_from_chip.append((packet.read(),packet.device_address(),packet.register_address(),packet.value()))
                self.__data_from_chip_times.append(packet.time())
                return
        # if it was not handled, store it as an error
        self.__errors.append(str(packet))
        self.__status = -1

    def activate(self, speed=400000, order="LSBFIRST", number_of_bytes=1, time=0):
        """ Activat the I2C interface and configure it with the given speed, byte order and number of bytes
        @param speed: the speed of the I2C interface possible values are 10000, 100000, 400000, 1000000, 3400000
        @param order: the byte order of the I2C interface possible values are "LSBFIRST" or "MSBFIRST"
        @param number_of_bytes: the protocol data word width of the I2C interface possible values are 1 or 2
        @param time: the time when the activation should be processed by the uC (0 means as soon as possible)
        """
        self.__api.update_state()
        # if the interface is already active or waiting activation, do nothing
        if self.__status >= 1:
            logging.warning("I2C interface "+str(self.__header[0])+" is already activated or waiting activation, doing nothing")
        else:
            # byte order
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_BYTE_ORDER, value= (1 if (order == "MSBFIRST") else 0),time = time))
            # speed
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
            # number of bytes
            if number_of_bytes > 2:
                logging.warning("I2C ony supports one or two bytes, defaulting to 1")
            else:
                self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_WIDTH, value=number_of_bytes,time = time))
            # and activate            
            self.__api.send_packet(ConfigPacket(header = self.__header[0], config_header = ConfigSubHeader.CONF_ACTIVE,time = time))
            self.__status = 1

    def send_write(self,device_address, register_address, word, time = 0):
        """ Send a write request on the I2C interface
        @param device_address: the address of the device to write to (7bit)
        @param register_address: the address of the register to write to (8bit)
        @param word: the word to write (8 or 16 bit depending on the number of bytes configured)
        @param time: the time when the write request should be processed by the uC (0 means as soon as possible)
        """
        self.__api.update_state()
        # if the interface is active or waiting activation in case of a timed event, send the word
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(DataI2CPacket(self.__header[1], device_address=device_address, register_address=register_address,read=0,value=word,time=time))
        else:
            logging.error("I2C interface "+str(self.__header[1])+" is not active, please activate first - word is not sent.")

    def send_read_request(self, device_address, register_address, word, time = 0):
        """ Send a read request on the I2C interface
        @param device_address: the address of the device to read from (7bit)
        @param register_address: the address of the register to read from (8bit)
        @param word: ?
        @param time: the time when the read request should be processed by the uC (0 means as soon as possible)
        """
        self.__api.update_state()
        # if the interface is active or waiting activation in case of a timed event, send the word
        if (time == 0 and self.__status == 2) or (time > 0 and self.__status >= 1):
            self.__api.send_packet(DataI2CPacket(self.__header[1], device_address=device_address, register_address=register_address,read=1,value=word,time=time))
        else:
            logging.error("I2C interface "+str(self.__header[2])+" is not active, please activate first - word is not sent.")

    def update(self):
        """ update the data repersentation of the API object
        """
        self.__api.update_state()