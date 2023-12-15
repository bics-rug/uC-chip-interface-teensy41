
#    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
#    Copyright (C) 2022-2023 Ole Richter - University of Groningen
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


import logging
import struct
from .header import *


class Packet:
    def __init__(self):
        self._header = 0
        self._exec_time = 0
    
    @classmethod
    def from_bytearray(cls, byte_array):
        try:
            unpacked = struct.unpack("<BII", byte_array)
            """
            from pyhton 3.12 the in operator can be used to do the same check
            until then:
            """
            try:
                header = Data32bitHeader(unpacked[0]);
                logging.debug("detected: Data32bit : "+ str(header))
                return Data32bitPacket.from_bytearray(byte_array)
            except ValueError:
                try:
                    header = DataI2CHeader(unpacked[0]);
                    logging.debug("detected: DataI2C : "+ str(header))
                    return DataI2CPacket.from_bytearray(byte_array)
                except ValueError:
                    try:
                        header = PinHeader(unpacked[0]);
                        logging.debug("detected: Pin : "+ str(header))
                        return PinPacket.from_bytearray(byte_array)
                    except ValueError:
                        try:
                            header = ConfigMainHeader(unpacked[0]);
                            logging.debug("detected: Config Main : "+ str(header))
                            return ConfigPacket.from_bytearray(byte_array)
                        except ValueError:
                            try:
                                header = ErrorHeader(unpacked[0]);
                                logging.debug("detected: Error : "+ str(header))
                                return ErrorPacket.from_bytearray(byte_array)
                            except ValueError:
                                logging.error("Header "+ str(unpacked[0]) +" is not a valid header, Packet:" + str(byte_array) +" "+ str(unpacked[0]) +" "+ str(unpacked[1]) +" "+ str(unpacked[2]))
                                raise ValueError("Header "+ str(unpacked[0]) +" is not a valid header")
        except Exception as e:
            logging.error(e)
    def header(self):
        return self._header
    def time(self):
        return self._exec_time

    def set_header(self, header):
        if (header < 256 and header >= 0 and isinstance(header, int)):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")
    
    def set_exec_time(self, time):
        if (time < 2**32 and time >= 0 and isinstance(time, int)):
            self._exec_time=time
        else:
            logging.error("exec_time "+str(time)+" is not a valid unsigned integer of 4 bytes")

    def to_bytearray(self):
        logging.warning("the method to_bytearray needs to be implemented by the child class")

class Data32bitPacket(Packet): 

    def __init__(self, header, value=0, time=0):
        self.set_header(header)
        self.set_value(value)
        self.set_exec_time(time)

    def value(self):
        return self._value

    def set_header(self, header):
        if (header in Data32bitHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")

    def set_value(self, value):
        if (value < 2**32 and value >= 0 and isinstance(value, int)):
            self._value=value
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 4 bytes")

    def to_bytearray(self):
        return struct.pack("<BII", self._header, self._exec_time, self._value)
    
    def __str__(self):
        return "[Packet]: data 32bit: header = "+ str(self._header) +", value = "+ str(self._value) + ", at time = "+ str(self._exec_time) +"us"

    @classmethod
    def from_bytearray(self, byte_array):
        """
        constructs a Data32bitPacket from a bytearray
        @param byte_array: 9 byte bytearray to construct the Packet from
        @return: Data32bitPacket
        @raise Exception: if package construction fails
        """
        unpacked = struct.unpack("<BII", byte_array)
        return Data32bitPacket(header=Data32bitHeader(unpacked[0]),
        value = unpacked[2],
        time = unpacked[1])

    
class DataI2CPacket(Packet): 

    def __init__(self, header, device_address, register_address, read=False, value=0, time=0):
        self.set_header(header)
        self.set_value(value)
        self.set_exec_time(time)
        self.set_device_address(device_address)
        self.set_register_address(register_address)
        self.set_read(read)

    def value(self):
        return self._value_ls+ self._value_ms<<8

    def read(self):
        return self._read
    
    def device_address(self):
        return self._device_address

    def register_address(self):
        return self._register_address

    def set_header(self, header):
        if (header in DataI2CHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")

    def set_value(self, value):
        if (value < 2**16 and value >= 0 and isinstance(value, int)):
            self._value_ls=value & 0xF
            self._value_ms= value >> 8
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 2 byte")

    def set_device_address(self, value):
        if (value < 2**7 and value >= 0 and isinstance(value, int)):
            self._device_address = value
        else:
            logging.error("device_address "+str(value)+" is not a valid unsigned integer of 7 bit")

    def set_read(self, value):
        if value:
                self._read = 1
        else:
                self._read = 0
    def set_register_address(self, value):
        if (value < 2**8 and value >= 0 and isinstance(value, int)):
            self._register_address = value
        else:
            logging.error("register_address "+str(value)+" is not a valid unsigned integer of 8 bit")
    def to_bytearray(self):
        return struct.pack("<BIBBBB", self._header, self._exec_time, self._device_address<<1+self._read ,self._register_address,self._value_ms,self._value_ls)
    
    def __str__(self):
        return "[Packet]: data i2c: header = "+ str(self._header) +",device_address = "+ str(self._device_address) +",register address = "+ str(self._register_address) +",read = "+ str(self._read) +", value = "+ str(self._value_ls+self._value_ms<<8) + ", at time = "+ str(self._exec_time) +"us"
    
    @classmethod
    def from_bytearray(self, byte_array):
        """
        constructs a DataI2CPacket from a bytearray
        @param byte_array:  9 byte bytearray to construct the Packet from
        @return: DataI2CPacket
        @raise Exception: if package construction fails
        """
        unpacked = struct.unpack("<BIBBBB", byte_array)
        return DataI2CPacket(header=DataI2CHeader(unpacked[0]),
        device_address=unpacked[2]>>1,
        register_address=unpacked[3], read=unpacked[2] & 0x1, value=unpacked[4]<<8+unpacked[5],
        time = unpacked[1])


"""
value: (int) 0 to set pin LOW, 1 to set pin HIGH.
"""
class PinPacket(Packet): 

    def __init__(self, header, pin_id, value=0, time=0):
        self.set_header(header)
        self.set_pin_id(pin_id)
        self.set_value(value)
        self.set_exec_time(time)
    
    def pin_id(self):
        return self._pin_id

    def value(self):
        return self._value

    def set_header(self, header):
        if (header in PinHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")

    def set_pin_id(self, pin_id):
        if (pin_id < 55 and pin_id >= 0 and isinstance(pin_id, int)):
            self._pin_id=pin_id
        else:
            logging.error("di "+str(pin_id)+" is not a valid unsigned integer of 1 byte + id < 55")


    def set_value(self, value):
        if (value < 2**8 and value >= 0 and isinstance(value, int)):
            self._value=value
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 1 byte")

    def to_bytearray(self):
        return struct.pack("<BIBBBB", self._header, self._exec_time, self._pin_id, self._value,0,0)
    
    def __str__(self):
        return "[Packet]: pin: header = "+ str(self._header) +", pin_id = "+ str(self._pin_id) + ", value = "+ str(self._value) + ", at time = "+ str(self._exec_time) +"us"

    @classmethod
    def from_bytearray(self, byte_array):
        """
        constructs a PinPacket from a bytearray
        @param byte_array: 9 byte bytearray to construct the Packet from
        @return: PinPacket
        @raise Exception: if package construction fails
        """
        unpacked = struct.unpack("<BIBBBB", byte_array)
        return PinPacket(header=PinHeader(unpacked[0]),
        pin_id = unpacked[2],
        value = unpacked[3],
        time = unpacked[1])


"""
header: (ConfigMainHeader) what's to be configured (e.g. PIN, SPI,...).
config_header: (ConfigSubHeader) configuration properties.
"""
class ConfigPacket(Packet): 

    def __init__(self, header, config_header, value=0, time=0):
        self.set_header(header)
        self.set_config_header(config_header)
        self.set_value(value)
        self.set_exec_time(time)

    def value(self):
        return self._value

    def config_header(self):
        return self._config_header

    def set_header(self, header):
        if (header in ConfigMainHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")
            
    def set_config_header(self, config_header):
        if (config_header in ConfigSubHeader):
            self._config_header=config_header
        else:
            logging.error("config sub header "+str(header)+" is not a valid header")

    def set_value(self, value):
        if (value < 2**8 and value >= 0 and isinstance(value, int)):
            self._value=value
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 1 byte")

    def to_bytearray(self):
        return struct.pack("<BIBBBB", self._header, self._exec_time, self._config_header ,self._value,0,0)
    
    def __str__(self):
        return "[Packet]: config: header = "+ str(self._header) +", config = "+ str(self._config_header) + ", value = "+ str(self._value) + ", at time = "+ str(self._exec_time) +"us"

    @classmethod
    def from_bytearray(self, byte_array):
        """
        constructs a ConfigPacket from a bytearray
        @param byte_array: 9 byte bytearray to construct the Packet from
        @return: ConfigPacket
        @raise Exception: if package construction fails
        """
        unpacked = struct.unpack("<BIBBBB", byte_array)
        return ConfigPacket(header=ConfigMainHeader(unpacked[0]),
        config_header = ConfigSubHeader(unpacked[2]),
        value = unpacked[3],
        time = unpacked[1])



class ErrorPacket(Packet): 

    def __init__(self, header, original_header, value=0, print_errors=True):
        self.set_header(header)
        self.set_org_header(original_header)
        self.set_value(value)

        if (print_errors):
            logging.error(self.__str__())

    def value(self):
        return self._value

    def original_header(self):
        return self._org_header

    def set_header(self, header):
        if (header in ErrorHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")
            
    def set_org_header(self, header):
        try:
            self._org_header = Data32bitHeader(header);
        except ValueError:
            try:
                self._org_header = DataI2CHeader(header);
            except ValueError:
                try:
                    self._org_header = PinHeader(header);
                except ValueError:
                    try:
                        self._org_header = ConfigMainHeader(header);
                    except ValueError:
                        try:
                            self._org_header = ErrorHeader(header);
                        except ValueError:
                            logging.error("source Header "+ str(header) +" is not a valid header,")
                            self._org_header = None;
    


    def set_value(self, value):
        if (value < 2**32 and value >= 0 and isinstance(value, int)):
            self._value=value
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 1 byte")
    def __str__(self):
        return "[uC Error]: "+ str(self._header) +" caused by "+ str(self._org_header)+ " with value "+ str(self._value)

    def to_bytearray(self):
        return struct.pack("<BBIBBB", self._header, self._org_header, self._value,0,0,0)

    @classmethod
    def from_bytearray(self, byte_array):
        """
        constructs a ErrorPacket from a bytearray
        @param byte_array: 9 byte bytearray to construct the Packet from
        @return: ErrorPacket
        @raise Exception: if package construction fails
        """
        unpacked = struct.unpack("<BBIBBB", byte_array)
        return ErrorPacket(header=ErrorHeader(unpacked[0]),
        original_header = unpacked[1],
        value = unpacked[2])

