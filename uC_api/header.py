
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
    """Data32bitHeader are all command headers used in Data32bitPacket.

       the description explains the function of the individual commands.
       some commands ignore the value.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self
    
    UC_CLOSE_CONNECTION = 255, """
    this packet tells the PC buffer to close the connection to the uC
    """
    
    IN_RESET = 254, """
     this packet is used to software reset the uC (clear the config), no harware reset is performed
    """
    
    IN_READ = 0, """
    read all availiable output packets out of the output buffer, and clear the buffer afterwards
    uses data:
     - value is ignored
    """  
    
    IN_READ_LAST = 4, """
    read only the last package, does not remove this package from the ring buffer
    - value is ignored
    """  
   
    IN_READ_TIME = 2,  """
     return the current execution time to the output buffer
     uses data
      - value is ignored
    """
    
    IN_READ_INSTRUCTIONS = 3, """
     read all availiable input packets out of the input buffer that have not been processed
     uses data
      - value is ignored
    """  
    
    OUT_BUFFER_LAST_READ = 250, """
     this packet is used to destinguish between an empty and a full buffer
     uses data
      - value is 1 so ignore
    """
    
    IN_FREE_INSTRUCTION_SPOTS = 5, """
     this packet is used to request how many free spots there are in the instruction ring buffer
    """
    
    OUT_FREE_INSTRUCTION_SPOTS = 101, """
     this packet is used to report how many free spots there are in the instruction ring buffer
    """
    
    IN_CONF_READ_ON_REQUEST = 6, """
     legacy mode: turn off automatic sending of the output buffer
     uses config
     - value 1 for read on request (legacy)
     - value 0 for continous read (default)
         @todo move to sub config
    """
    
    IN_SET_TIME = 1, """
     set the execution time, if set to 0 recording and exec are halted
     if set to 1 (or bigger) exec and recoding will be started from timestep 1 (or bigger)
     uses data
      - value is the time current to be set, maximum experiment time is 2^32 usec
    """
    
    OUT_TIME = 100, """
     responce to the READ_TIME packet
     uses data
      - exec_time the current run time 
      - value the system_time (without run time offset)
    """
    
    
    IN_SPI0 = 20, """
     sends an 32bit word on the SPI0 interface
     uses data32
     - value is the 32bit to be send
    """

    
    IN_SPI1 = 21, """
     sends an 32bit word on the SPI1 interface
     uses data32
     - value is the 32bit to be send
    """
    
    IN_SPI2 = 22, """
     sends an 32bit word on the SPI2 interface
     uses data32
     - value is the 32bit to be send
    """
    
    OUT_SPI0 = 120, """
     responce to the IN_SPI0_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    
    OUT_SPI1 = 121, """
     responce to the IN_SPI1_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    
    OUT_SPI2 = 122, """
     responce to the IN_SPI2_32 packet
     uses data32
      - exec_time the current run time 
      - value the 32bit word that was read on the SPI
    """
    
    IN_ASYNC_TO_CHIP0 = 30, """
     sends an 0-32bit word on the ASYNC_TO_CHIP0 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP1 = 31 , """
     sends an 0-32bit word on the ASYNC_TO_CHIP1 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP2 = 32, """
     sends an 0-32bit word on the ASYNC_TO_CHIP2 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP3 = 33, """
     sends an 0-32bit word on the ASYNC_TO_CHIP3 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP4 = 34, """
     sends an 0-32bit word on the ASYNC_TO_CHIP4 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP5 = 35, """
     sends an 0-32bit word on the ASYNC_TO_CHIP5 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP6 = 36, """
     sends an 0-32bit word on the ASYNC_TO_CHIP6 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """
    
    IN_ASYNC_TO_CHIP7 = 37, """
     sends an 0-32bit word on the ASYNC_TO_CHIP7 interface
     uses data
      - value is the word to be send, if the width is configured to >32 the MS bits are ignored
    """

    
    OUT_ASYNC_FROM_CHIP0 = 130, """
     a event was reseved on ASYNC_FROM_CHIP0
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP1 = 131, """
     a event was reseved on ASYNC_FROM_CHIP1
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP2 = 132, """
     a event was reseved on ASYNC_FROM_CHIP2
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP3 = 133, """
     a event was reseved on ASYNC_FROM_CHIP3
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP4 = 134, """
     a event was reseved on ASYNC_FROM_CHIP4
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP5 = 135, """
     a event was reseved on ASYNC_FROM_CHIP5
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP6 = 136, """
     a event was reseved on ASYNC_FROM_CHIP6
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """
    
    OUT_ASYNC_FROM_CHIP7 = 137, """
     a event was reseved on ASYNC_FROM_CHIP7
     uses data
      - exec_time the current run time 
      - value the 0-32bit word that was read on the AER
    """

    IN_MAPPER_KEY = 190, """
    in mapper key switches into sequence transmission mode,
    the next packet is considered the key all subsequent packages 
    are considdered values until IN_MAPPER_END.
    """

    IN_MAPPER_END = 191, """
    In mapper end switches back to normal packet exec mode.
    """

@enum.unique
class PinHeader(enum.IntEnum) :
    """PinHeader are all command headers used in PinPacket.
  
       the description explains the function of the individual commands.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self
    
    IN_PIN = 10, """
     send a modify output pin command
     uses pin
      - pin is the pin number
      - value is 0 or 1 for low or high
    """
    
    IN_PIN_READ = 11, """
     send a read input pin command
     uses pin
      - pin is the pin number
      - value is ignored
    """
    
    OUT_PIN_LOW = 110, """
     After a input pin change this records the change
     uses pin
      - exec_time the time the change occured
      - pin the pin id
      - value the new state
    """

    OUT_PIN_HIGH = 111, """
     After a input pin change this records the change
     uses pin
      - exec_time the time the change occured
      - pin the pin id
      - value the new state
    """

@enum.unique
class DataI2CHeader(enum.IntEnum) :
    """DataI2CHeader are all command headers used in DataI2CPacket.
  
       the description explains the function of the individual commands.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self
    
    IN_I2C0 = 25, """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    
    IN_I2C1 = 26, """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    
    IN_I2C2 = 27, """
    sends an 8 or 16 bit word or recives a specified number of bytes on the I2C interface
    uses data_i2c
    - device_address is the 7bit (MS) address of the device and the LSB indicates Read(1)/Write(0) following the i2c standard
    - register_address is the 8bit register address
    - value_ms is the MS 8bit to be send
    - value_ls is the LS 8bit to be send or the number of bytes to read
    """
    
    OUT_I2C0 = 125, """
     responce to the IN_SPI0 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """
    
    OUT_I2C1 = 126, """
     responce to the IN_SPI1 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """
    
    OUT_I2C2 = 127, """
     responce to the IN_SPI2 packet
     uses data_i2c
      - exec_time the current run time 
      - value the 8bit word that was read on the SPI
    """

    OUT_ALIGN_SUCCESS_VERSION = 253, """
     responce to alignment request, as the first communication is an alignment
     confirms the connection with the uC.
     also sends the firmware version - to see if the correct version is running
     uses data_i2c
      - exec_time the current run time 
      - device address - major version
      - register address - minor version
      - value_ms the MS 8bit of patch version
      - value_ls the LS 8bit of patch version
    """

@enum.unique
class ConfigMainHeader(enum.IntEnum) :
    """
    ConfigMainHeader are all command headers used in ConfigPacket in conjunction with ConfigSubHeader.
  
    The description explains the function of the individual commands.
    The main header specifies the interface to be configured and the sub header the property
    which should be configured.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self

    
    IN_CONF_READ_ON_REQUEST = 6, """
     legacy mode: turn off automatic sending of the output buffer
     - value 1 for read on request (legacy)
     - value 0 for continous read (default)
    """
    
    IN_CONF_PIN = 50, """
     sets the pin configuration
     uses config
      - config/sub header is the config state to be applied the pin
      - value is the pin id
    """
    
    IN_CONF_SPI0 = 60, """
     sets the spi0 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    
    IN_CONF_SPI1 = 61, """
    sets the spi1 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    
    IN_CONF_SPI2 = 62, """
     sets the spi2 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """ 
    
    IN_CONF_I2C0 = 65, """
     sets the i2c0 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    
    IN_CONF_I2C1 = 66, """
    sets the i2c1 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    
    IN_CONF_I2C2 = 67, """
     sets the i2c2 configuration
     uses config
      - config/sub header is the config state to be applied the spi
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP0 = 70, """
     sets the ASYNC_TO_CHIP0 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP1 = 71, """
     sets the ASYNC_TO_CHIP1 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP2 = 72, """
     sets the ASYNC_TO_CHIP2 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP3 = 73, """
     sets the ASYNC_TO_CHIP3 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP4 = 74, """
     sets the ASYNC_TO_CHIP4 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP5 = 75, """
     sets the ASYNC_TO_CHIP5 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP6 = 76, """
     sets the ASYNC_TO_CHIP6 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_TO_CHIP7 = 77, """
     sets the ASYNC_TO_CHIP7 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP0 = 80, """
     sets the ASYNC_FROM_CHIP0 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP1 = 81, """
     sets the ASYNC_FROM_CHIP1 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP2 = 82, """
     sets the ASYNC_FROM_CHIP2 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP3 = 83, """
     sets the ASYNC_FROM_CHIP3 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP4 = 84, """
     sets the ASYNC_FROM_CHIP4 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP5 = 85, """
     sets the ASYNC_FROM_CHIP5 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP6 = 86, """
     sets the ASYNC_FROM_CHIP6 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """
    
    IN_CONF_ASYNC_FROM_CHIP7 = 87, """
     sets the ASYNC_FROM_CHIP7 configuration
     uses config
      - config/sub header is the config state to be applied the aer interface
      - value is used according to the config sub header
    """


"""
@TODO some of them use other formates but did not had time to sort them yet
"""
@enum.unique
class ErrorHeader(enum.IntEnum) :
    """
    ErrorHeader are all command headers used in ErrorPacket.

    Errors are issued by the uC to tell the user what went wrong.
    The description explains the meaning of the individual errors.

    the causing errors can be found in org_header and org_sub_header
    the causeing valuse is stored in value, if a value does not make sense 
    for that error class it is the current timestamp of the uC.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self

    OUT_ERROR = 200,    """
     unspecified error.
    """
    
    OUT_ERROR_PIN_ALREADY_INUSE = 201, """
    This means your interface / pin that you are activating
    is trying to use a pin that is already in use by an other interface
    or you already configured the pin before.

    if you want to reconfigure the uC, call reset on the uC_api and create 
    a new uC_api object after to reestablish a new connection after the uC reset.
    """
    
    OUT_ERROR_PIN_NOT_CONFIGURED = 202, """
    this means you are trying to use a pin via the pin interface that is not configured yet,
    please call pin[X].activate(<options>) before useing the pin or send the required config packets. 
    """
    
    OUT_ERROR_INPUT_FULL = 203, """
    this means that the timed instruction buffer is full,
    and you cant send more instructions, the instruction send will be discarded
    """
    
    OUT_ERROR_OUTPUT_FULL = 204, """
    the output buffer is full, and pakets are being dropped
    the number of packets dropped you can read as value
    """
    
    OUT_ERROR_INTERFACE_ALREADY_ACTIVE = 205, """
    This means your interface you are activating is already configured and active.

    if you want to reconfigure the uC, call reset on the uC_api and create 
    a new uC_api object after to reestablish a new connection after the uC reset.
    """
    
    OUT_ERROR_UNKNOWN_INSTRUCTION = 206, """
    the header (packet) you send is not 
    known or does not make sense to the uC in that combination

    maybe your API and firmware verions are out of sync
    """
    
    OUT_ERROR_INTERFACE_NOT_ACTIVE = 207, """
    You are trying to use an interface that is not configured yet,
    please call <interface>[X].activate(<options>) before useing the 
    interface or send the required configuration packets
    """
    
    OUT_ERROR_UNKNOWN_CONFIGURATION = 208, """
    the config header you send is not 
    known or does not make sense to the uC in that combination

    maybe your API and firmware verions are out of sync
    """
    
    OUT_ERROR_ASYNC_HS_TIMEOUT = 209, """
    the async sending interface did not get an acknowlage for a while,
    it reset the request so you should take care off restarting/resetting the DuT
    """
 
    OUT_ERROR_PERIPHERAL_INTERFACE_NOT_READY = 210,    """
    this error is thrown when a peripheral interface is not ready
    For example: the I2C for the MCP23017 is not ready
    uses 
    """
    
    OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS = 211, """
    the configuration id you send is out of bounds of the available uC resources
    uses error_package
    - id is the wrong id
    """

    OUT_ERROR_DATA_OUT_OF_BOUNDS = 212, """
    the data you send is larger the the configured bit/byte width of the interface
    uses error_package
      - the wrong data
    """
     
    OUT_WARNING_DATA_COLLECTION_SQUEUED = 213, """
    the data collection is taking up to much time (to many requests)
    the uC does not have time to ship the data to the PC.
    from now on whenever this happens the uC will pause data collection
    for a moment and transmit ~ 10 pakages to the PC before it resumes 
    data collection. this warning only send once.
    """



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
    ConfigSubHeader are all command headers used in ConfigPacket in conjunction with ConfigMainHeader.
  
    The description explains the function of the individual commands.
    The main header specifies the interface to be configured and the sub header the property
    which should be configured.
    """

    def __new__(cls, value, doc=None):
      """
      overwrite to enable __doc__ strings for enum elements as second argument.
      """
      self = int.__new__(cls, value)  # calling super().__new__(value) here would fail
      self._value_ = value
      if doc is not None:
          self.__doc__ = doc
      return self
    
    CONF_ACTIVE = 60, """
     set an interface to active, after activation the pins/width cant be changed anymore
     works for spi and aer, activation will fail if pins are already used for other interfaces
     @TODO deactivation not implemented yet sould be new header for compatebility
     uses config
      - value is ignored
    """
    
    CONF_OUTPUT = 61, """
     set a pin to output to be able to write on it
     uses config
      - value is ID of pin
    """
    
    CONF_INPUT = 62, """
     set a pin to input, it registers an interupt service 
     to record all incomming changes
     uses config
      - value is ID of pin
    """
    
    CONF_REQ = 70, """
     sets the Req pin for the given AER interface
     uses config
         - value is ID of pin
    """
    
    CONF_ACK = 71, """
     sets the Ack pin for the given AER interface
     uses config
         - value is ID of pin
    """
    
    CONF_WIDTH = 72, """
     sets the bit width of the given AER interface
     uses config
      - value is width 0-32
    """
    
    CONF_REQ_DELAY = 73, """
     set the delay on the request line
     uses config
      - value the delay in multiple of 20ns
    """
    
    CONF_BYTE_ORDER = 74, """
     interface_order
      - value LSFIRST = 0 and MSFIRST = 1 - default is 0
    """
    
    CONF_SPEED_CLASS = 75, """
     interface speed class se interface doc
    """
    
    CONF_TYPE = 76, """
    interface_type
    - value type id (see interface doc) - default is 0
    """

    CONF_NONE = 255, "indication of no sub category"
  
    CONF_CHANNEL0 = 0, "setting the pin for Async data channel"
    CONF_CHANNEL1 = 1, "setting the pin for Async data channel"
    CONF_CHANNEL2 = 2, "setting the pin for Async data channel"
    CONF_CHANNEL3 = 3, "setting the pin for Async data channel"
    CONF_CHANNEL4 = 4, "setting the pin for Async data channel"
    CONF_CHANNEL5 = 5, "setting the pin for Async data channel"
    CONF_CHANNEL6 = 6, "setting the pin for Async data channel"
    CONF_CHANNEL7 = 7, "setting the pin for Async data channel"
    CONF_CHANNEL8 = 8, "setting the pin for Async data channel"
    CONF_CHANNEL9 = 9, "setting the pin for Async data channel"
    CONF_CHANNEL10 = 10, "setting the pin for Async data channel"
    CONF_CHANNEL11 = 11, "setting the pin for Async data channel"
    CONF_CHANNEL12 = 12, "setting the pin for Async data channel"
    CONF_CHANNEL13 = 13, "setting the pin for Async data channel"
    CONF_CHANNEL14 = 14, "setting the pin for Async data channel"
    CONF_CHANNEL15 = 15, "setting the pin for Async data channel"
    CONF_CHANNEL16 = 16, "setting the pin for Async data channel"
    CONF_CHANNEL17 = 17, "setting the pin for Async data channel"
    CONF_CHANNEL18 = 18, "setting the pin for Async data channel"
    CONF_CHANNEL19 = 19, "setting the pin for Async data channel"
    CONF_CHANNEL20 = 20, "setting the pin for Async data channel"
    CONF_CHANNEL21 = 21, "setting the pin for Async data channel"
    CONF_CHANNEL22 = 22, "setting the pin for Async data channel"
    CONF_CHANNEL23 = 23, "setting the pin for Async data channel"
    CONF_CHANNEL24 = 24, "setting the pin for Async data channel"
    CONF_CHANNEL25 = 25, "setting the pin for Async data channel"
    CONF_CHANNEL26 = 26, "setting the pin for Async data channel"
    CONF_CHANNEL27 = 27, "setting the pin for Async data channel"
    CONF_CHANNEL28 = 28, "setting the pin for Async data channel"
    CONF_CHANNEL29 = 29, "setting the pin for Async data channel"
    CONF_CHANNEL30 = 30, "setting the pin for Async data channel"
    CONF_CHANNEL31 = 31, "setting the pin for Async data channel"

