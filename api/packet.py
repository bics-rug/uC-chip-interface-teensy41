"""
    This file is part of the Firmware project to interface with small Neuromorphic chips
    Copyright (C) 2022 Ole Richter - University of Groningen

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

import logging
import struct
from header import *


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
                logging.info("Read: Data32bit : "+ str(header))
                return Data32bitPacket.from_bytearray(byte_array)
            except ValueError:
                try:
                    header = Data8bitHeader(unpacked[0]);
                    logging.info("Read: Data8bit : "+ str(header))
                    return Data8bitPacket.from_bytearray(byte_array)
                except ValueError:
                    try:
                        header = PinHeader(unpacked[0]);
                        logging.info("Read: Pin : "+ str(header))
                        return PinPacket.from_bytearray(byte_array)
                    except ValueError:
                        try:
                            header = ConfigMainHeader(unpacked[0]);
                            logging.info("Read: ConfigMain : "+ str(header))
                            return ConfigPacket.from_bytearray(byte_array)
                        except ValueError:
                            try:
                                header = ErrorHeader(unpacked[0]);
                                logging.info("Read: Error : "+ str(header))
                                return ErrorPacket.from_bytearray(byte_array)
                            except ValueError:
                                logging.error("Header "+ str(unpacked[0]) +" is not a valid header, Packet:" + str(byte_array) +" "+ str(unpacked[0]) +" "+ str(unpacked[1]) +" "+ str(unpacked[2]))
        except Exception as e:
            logging.error(e)
         

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
        try:
            unpacked = struct.unpack("<BII", byte_array)
            return Data32bitPacket(header=Data32bitHeader(unpacked[0]),
            value = unpacked[2],
            time = unpacked[1])
        except Exception as e:
            return str(e) + ' (error)'
    
class Data8bitPacket(Packet): 

    def __init__(self, header, value=0, time=0):
        self.set_header(header)
        self.set_value(value)
        self.set_exec_time(time)

    def set_header(self, header):
        if (header in Data8bitHeader):
            self._header=header
        else:
            logging.error("header "+str(header)+" is not a valid header")

    def set_value(self, value):
        if (value < 2**8 and value >= 0 and isinstance(value, int)):
            self._value=value
        else:
            logging.error("value "+str(value)+" is not a valid unsigned integer of 1 byte")

    def to_bytearray(self):
        return struct.pack("<BIBBBB", self._header, self._exec_time, self._value,0,0,0)
    
    def __str__(self):
        return "[Packet]: data 8bit: header = "+ str(self._header) +", value = "+ str(self._value) + ", at time = "+ str(self._exec_time) +"us"
    
    @classmethod
    def from_bytearray(self, byte_array):
        try:
            unpacked = struct.unpack("<BIBBBB", byte_array)
            return Data8bitPacket(header=Data8bitHeader(unpacked[0]),
            value = unpacked[2],
            time = unpacked[1])
        except Exception as e:
            return str(e) + ' (error)'

"""
value: (int) 0 to set pin LOW, 1 to set pin HIGH.
"""
class PinPacket(Packet): 

    def __init__(self, header, pin_id, value=0, time=0):
        self.set_header(header)
        self.set_pin_id(pin_id)
        self.set_value(value)
        self.set_exec_time(time)

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
        try:
            unpacked = struct.unpack("<BIBBBB", byte_array)
            return PinPacket(header=PinHeader(unpacked[0]),
            pin_id = unpacked[2],
            value = unpacked[3],
            time = unpacked[1])
        except Exception as e:
            return str(e) + ' (error)'

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
        try:
            unpacked = struct.unpack("<BIBBBB", byte_array)
            return ConfigPacket(header=ConfigMainHeader(unpacked[0]),
            config_header = ConfigSubHeader(unpacked[2]),
            value = unpacked[3],
            time = unpacked[1])
        except Exception as e:
            return str(e) + ' (error)'

    def from_bytearray(self, byteArray):
        try:
            return struct.unpack("<BII", byteArray)
        except Exception as e:
            return str(e) + ' (error)'

class ErrorPacket(Packet): 

    def __init__(self, header, original_header, value=0, print_errors=True):
        self.set_header(header)
        self.set_org_header(original_header)
        self.set_value(value)

        if (print_errors):
            logging.error(self.__str__())

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
                self._org_header = Data8bitHeader(header);
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
                            logging.error("Header "+ str(header) +" is not a valid header,")
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
        try:
            unpacked = struct.unpack("<BBIBBB", byte_array)
            return ErrorPacket(header=ErrorHeader(unpacked[0]),
            original_header = unpacked[1],
            value = unpacked[2])
        except Exception as e:
            return str(e) + ' (error)'

class SuccessPacket(Packet):

    def __init__(self, header):
        self.set_header(header)

    def set_header(self, header):
        if (header in ConfigMainHeader):
            self._header = header
        else:
            logging.error("[error] header \'"+header+"\' is not a valid header")
