"""
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
    Copyright (C) 2022-2023 Ole Richter - University of Groningen

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

import enum

"""
 the packet header are byte that identifies the instruction to be executed by the uC
 order is as follows
  - general commands
  - write to interface PIN, AER, SPI
  - configure Interfaces
"""

"""
for simplisity Commands use the Data32bitPacket class
with value field empty
"""

@enum.unique
class Data32bitHeader(enum.IntEnum) :
    """
     this packet is used to software reset the uC (clear the config), no harware reset is performed
    """
    IN_RESET = 254
    """
    read all availiable output packets out of the output buffer, and clear the buffer afterwards
    uses data:
     - value is ignored
    """  
    IN_READ = 0
    """
    use
    """  
    IN_READ_LAST = 4
    """
     return the current execution time to the output buffer
     uses data
      - value is ignored
    """
    IN_READ_TIME = 2 
    """
     read all availiable input packets out of the input buffer that have not been processed
     uses data
      - value is ignored
    """  
    IN_READ_INSTRUCTIONS = 3
    """
     this packet is used to destinguish between an empty and a full buffer
     uses data
      - value is 1 so ignore
    """
    OUT_BUFFER_LAST_READ = 250
    """
     this packet is used to request how many free spots there are in the instruction ring buffer
    """
    IN_FREE_INSTRUCTION_SPOTS = 5
    """
     this packet is used to report how many free spots there are in the instruction ring buffer
    """
    OUT_FREE_INSTRUCTION_SPOTS = 101

    """
     set the execution time, if set to 0 recording and exec are halted
     if set to 1 (or bigger) exec and recoding will be started from timestep 1 (or bigger)
     uses data
      - value is the time current to be set, maximum experiment time is 2^32 usec
    """
    IN_SET_TIME = 1 
    """
     responce to the READ_TIME packet
     uses data
      - exec_time the current run time 
      - value the system_time (without run time offset)
    """
    OUT_TIME = 100
    """
     sends an 32bit word on the SPI0 interface
     uses data32
     - value is the 32bit to be send
    """
    
    IN_SPI0 = 20
    """
     sends an 32bit word on the SPI1 interface
     uses data32
     - value is the 32bit to be send
    """
    IN_SPI1 = 21
    """
     sends an 32bit word on the SPI2 interface
     uses data32
     - value is the 32bit to be send
    """
    IN_SPI2 = 22
    """
     responce to the IN_SPI0_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    OUT_SPI0 = 120
    """
     responce to the IN_SPI1_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    OUT_SPI1 = 121
    """
     responce to the IN_SPI2_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    OUT_SPI2 = 122

    """
     sends an 0-32bit word on the ASYNC_TO_CHIP0 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP0 = 30
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP1 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP1 = 31
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP2 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP2 = 32
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP3 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP3 = 33
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP4 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP4 = 34
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP5 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP5 = 35
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP6 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP6 = 36
    """
     sends an 0-32bit word on the ASYNC_TO_CHIP7 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    IN_ASYNC_TO_CHIP7 = 37

    """
     a event was reseved on ASYNC_FROM_CHIP0
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP0 = 130
    """
     a event was reseved on ASYNC_FROM_CHIP1
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP1 = 131
    """
     a event was reseved on ASYNC_FROM_CHIP2
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP2 = 132
    """
     a event was reseved on ASYNC_FROM_CHIP3
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP3 = 133
    """
     a event was reseved on ASYNC_FROM_CHIP4
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP4 = 134
    """
     a event was reseved on ASYNC_FROM_CHIP5
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP5 = 135
    """
     a event was reseved on ASYNC_FROM_CHIP6
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP6 = 136
    """
     a event was reseved on ASYNC_FROM_CHIP7
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    OUT_ASYNC_FROM_CHIP7 = 137

    OUT_SUCCESS_PIN_CONFIGURED = 240

@enum.unique
class PinHeader(enum.IntEnum) :
    """
     send a modify output pin command
     uses pin
      - pin is the pin number
      - value is 0 or 1 for low or high
    """
    IN_PIN = 10
    """
     send a read input pin command
     uses pin
      - pin is the pin number
      - value is ignored
    """
    IN_PIN_READ = 11
    """
     After a input pin change this records the change
     uses pin
      - exec_time the time the change occured
      - pin the pin id
      - value the new state
    """
    OUT_PIN = 110

@enum.unique
class DataI2CHeader(enum.IntEnum) :
    """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    IN_I2C0 = 25
    """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    IN_I2C1 = 26
    """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    IN_I2C2 = 27
    """
     responce to the IN_SPI0 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """
    OUT_I2C0 = 125
    """
     responce to the IN_SPI1 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """
    OUT_I2C1 = 126
    """
     responce to the IN_SPI2 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """
    OUT_I2C2 = 127

@enum.unique
class ConfigMainHeader(enum.IntEnum) :

    """
     legacy mode: turn off automatic sending of the output buffer
     - value 1 for read on request (legacy)
     - value 0 for continous read (default)
    """
    IN_CONF_READ_ON_REQUEST = 6
    """
     sets the pin configuration
     uses config
      - config/sub header is the config state to be applied the pin
      - value is the pin id
    """
    IN_CONF_PIN = 50
    """
     sets the spi0 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_SPI0 = 60
    """
    sets the spi1 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_SPI1 = 61 
    """
     sets the spi2 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_SPI2 = 62 
    """
     sets the i2c0 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_I2C0 = 65
    """
    sets the i2c1 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_I2C1 = 66
    """
     sets the i2c2 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    IN_CONF_I2C2 = 67
    """
     sets the ASYNC_TO_CHIP0 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP0 = 70
    """
     sets the ASYNC_TO_CHIP1 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP1 = 71
    """
     sets the ASYNC_TO_CHIP2 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP2 = 72
    """
     sets the ASYNC_TO_CHIP3 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP3 = 73
    """
     sets the ASYNC_TO_CHIP4 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP4 = 74
    """
     sets the ASYNC_TO_CHIP5 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP5 = 75
    """
     sets the ASYNC_TO_CHIP6 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP6 = 76
    """
     sets the ASYNC_TO_CHIP7 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_TO_CHIP7 = 77
    """
     sets the ASYNC_FROM_CHIP0 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP0 = 80
    """
     sets the ASYNC_FROM_CHIP1 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP1 = 81
    """
     sets the ASYNC_FROM_CHIP2 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP2 = 82
    """
     sets the ASYNC_FROM_CHIP3 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP3 = 83 
    """
     sets the ASYNC_FROM_CHIP4 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP4 = 84
    """
     sets the ASYNC_FROM_CHIP5 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP5 = 85 
    """
     sets the ASYNC_FROM_CHIP6 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP6 = 86
    """
     sets the ASYNC_FROM_CHIP7 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    IN_CONF_ASYNC_FROM_CHIP7 = 87 


"""
@TODO some of them use other formates but did not had time to sort them yet
"""
@enum.unique
class ErrorHeader(enum.IntEnum) :
    """
     
     uses 
    """
    OUT_ERROR = 200
    """
     
     uses 
    """
    OUT_ERROR_PIN_ALREADY_INUSE = 201
    """
     
     uses 
    """
    OUT_ERROR_PIN_NOT_CONFIGURED = 202
    """
     
     uses 
    """
    OUT_ERROR_INPUT_FULL = 203
    """
     
     uses 
    """
    OUT_ERROR_OUTPUT_FULL = 204
    """
     
     uses 
    """
    OUT_ERROR_INTERFACE_ALREADY_ACTIVE = 205
    """
     
     uses 
    """
    OUT_ERROR_UNKNOWN_INSTRUCTION = 206
    """
     
     uses 
    """
    OUT_ERROR_INTERFACE_NOT_ACTIVE = 207
    """
     
     uses 
    """
    OUT_ERROR_UNKNOWN_CONFIGURATION = 208
    """
     
     uses 
    """
    OUT_ERROR_ASYNC_HS_TIMEOUT = 209
    """
    this error is thrown when a peripheral interface is not ready
    For example: the I2C for the MCP23017 is not ready
    uses 
    """
    OUT_ERROR_PERIPHERAL_INTERFACE_NOT_READY = 210
    """
    the configuration id you send is out of bounds of the available uC resources
    uses error_package
    - id is the wrong id
    """
    OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS = 211



"""
to make sure that all headers are unique, and to access all of them independen of thier class
"""
"""
@enum.unique
class AllHeaders(Data32bitHeader, PinHeader, Data8bitHeader, ConfigMainHeader, ErrorHeader):
    pass
"""


class ConfigSubHeader(enum.IntEnum):
    """
     set an interface to active, after activation the pins/width cant be changed anymore
     works for spi and aer, activation will fail if pins are already used for other interfaces
     @TODO deactivation not implemented yet sould be new header for compatebility
     uses config
      - value is ignored
    """
    CONF_ACTIVE = 60
    """
     set a pin to output to be able to write on it
     uses config
      - value is ID of pin
    """
    CONF_OUTPUT = 61
    """
     set a pin to input, it registers an interupt service 
     to record all incomming changes
     uses config
      - value is ID of pin
    """
    CONF_INPUT = 62
    """
     sets the Req pin for the given AER interface
     uses config
         - value is ID of pin
    """
    CONF_REQ = 70
    """
     sets the Ack pin for the given AER interface
     uses config
         - value is ID of pin
    """
    CONF_ACK = 71
    """
     sets the bit width of the given AER interface
     uses config
      - value is width 0-32
    """
    CONF_WIDTH = 72
    """
     set the delay on the request line
     uses config
      - value the delay in multiple of 20ns
    """
    CONF_REQ_DELAY = 73
    """
     interface_order
      - value LSFIRST = 0 and MSFIRST = 1 - default is 0
    """
    CONF_BYTE_ORDER = 74
    """
     interface speed class se interface doc
    """
    CONF_SPEED_CLASS = 75
    """
    interface_type
    - value type id (see interface doc) - default is 0
    """
    CONF_TYPE = 76
    """
     setting the pin for AER data channel X
     uses config
      - value is the pin ID
    """
    CONF_CHANNEL0 = 0
    CONF_CHANNEL1 = 1
    CONF_CHANNEL2 = 2
    CONF_CHANNEL3 = 3
    CONF_CHANNEL4 = 4
    CONF_CHANNEL5 = 5
    CONF_CHANNEL6 = 6
    CONF_CHANNEL7 = 7
    CONF_CHANNEL8 = 8
    CONF_CHANNEL9 = 9
    CONF_CHANNEL10 = 10
    CONF_CHANNEL11 = 11
    CONF_CHANNEL12 = 12
    CONF_CHANNEL13 = 13
    CONF_CHANNEL14 = 14
    CONF_CHANNEL15 = 15
    CONF_CHANNEL16 = 16
    CONF_CHANNEL17 = 17
    CONF_CHANNEL18 = 18
    CONF_CHANNEL19 = 19
    CONF_CHANNEL20 = 20
    CONF_CHANNEL21 = 21
    CONF_CHANNEL22 = 22
    CONF_CHANNEL23 = 23
    CONF_CHANNEL24 = 24
    CONF_CHANNEL25 = 25
    CONF_CHANNEL26 = 26
    CONF_CHANNEL27 = 27
    CONF_CHANNEL28 = 28
    CONF_CHANNEL29 = 29
    CONF_CHANNEL30 = 30
    CONF_CHANNEL31 = 31
    CONF_CHANNEL32 = 32
