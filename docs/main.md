# Overview

## uC chip interface for async/neuromorphic test chips

This firmware project is built to have a reusable interface for testing async/neuromorphic chips, also known as Device under Test (DuT).

The goal is that the firmware is free of any application-specific integrated circuit (ASIC) or printed circuit board (PCB) specific code. The User provides this configuration at runtime via an easy-to-use mid-level API. We are keeping the firmware maintainable and portable.

### Key features are:
 - different Async, SPI, I2C interfaces and I/O pin functionality
 - every action and incoming data is timestamped and reported 
 - all actions can be precisely timed with ~100us precision
 - simple mid-level python API
 - defensively programmed with many error notifications

### Currently supported uC (MicroController):
 - Teensy 4.1 (recommended for device testing)
 - Teensy 4.0
 - Arduino Zero (recommended for firmware development - debugger)
 - Arduino MKR variants

### Project home
The project is located at https://github.com/olerichter/uC-chip-interface

The documentation can be found at https://olerichter.github.io/uC-chip-interface

## the PC <--usb--> uC protocol

The communication happens via a USB serial connection. The communication protocol is handled via fixed-length 9-byte packages @ref packet_t, where the first byte is the header, which specifies the data format of the following 8 bytes, and the next 4 bytes (except for the error packets) are a timestamp in microseconds, leaving the last 4 bytes for data. In detail, the following data formats exist:
 - @ref data32_t , @ref uC_api.packet.Data32bitPacket "Data32bitPacket" using the headers listed in @ref uC_api.header.Data32bitHeader "Data32bitHeader" 
    ```
    [header: 1 byte][time: 4 byte][value: 4 byte]
    ```
 - @ref data_i2c_t , @ref uC_api.packet.DataI2CPacket "DataI2CPacket" using the headers listed in @ref uC_api.header.DataI2CHeader "DataI2CHeader" 
    ```
    [header : 1 byte][time: 4 byte][address: 7 bit][R/W: 1 bit][Reg Address: 1 byte][value: 2 byte]
    ```
 - @ref pin_t , @ref uC_api.packet.PinPacket "PinPacket" using the headers listed in @ref uC_api.header.PinHeader "PinHeader" 
    ```
    [header : 1 byte][time: 4 byte][Pin number: 1 byte][value: 1 byte][not used: 2 byte]
    ```
 - @ref config_t , @ref uC_api.packet.ConfigPacket "ConfigPacket" using the headers listed in @ref uC_api.header.ConfigMainHeader "ConfigMainHeader" and the sub-headers in @ref uC_api.header.ConfigSubHeader "ConfigSubHeader" 
    ```
    [header : 1 byte][time: 4 byte][config header: 1 byte][value: 1 byte][not used: 2 byte]
    ```
 - @ref error_t , 
 @ref uC_api.packet.ErrorPacket "ErrorPacket" using the headers listed in @ref uC_api.header.ErrorHeader "ErrorHeader" 
    ```
    [header : 1 byte][causing header: 1 byte][value: 4 byte][causing sub header: 1 byte][not used: 2 byte]
    ```

## API levels 

### API level 2
All interfaces are entirely abstracted at this level as Python objects, and packets are wholly hidden.

```python
import uC_api

# Open connection
uc = uC_api.uC_api('/dev/ttyACM0',2)

# Access all interface objects via 
uc.async_to_chip[X]     # up to outgoing 8 async interfaces, X -> 0-7
uc.async_from_chip[X]   # up to incoming 8 async interfaces, X -> 0-7
uc.i2c[X]               # up to 3 i2c interfaces (currently only master), X -> 0-2
uc.pin[X]               # up to 55 (teensy4.1), 40 teensy4.0, 22 Arduino Zero and MKR pins, X -> 0-54
uc.spi[X]               # up to 3 spi interfaces (currently only master), X -> 0-2

uc.start_experiment()   # start recoding and timed sending

us.close_connection()   # close connection to uC, the User can still access the recorded data.
```
All interfaces record data with timestamps for sending and receiving data from the uC to the DuT. For all available functions, see:
 - @ref uC_api.interface_async.Interface_Async "Interface_Async"
 - @ref uC_api.interface_i2c.Interface_I2C "Interface_I2C"
 - @ref uC_api.interface_spi.Interface_SPI "Interface_SPI"
 - @ref uC_api.interface_pin.Interface_PIN "Interface_PIN"
 - @ref uC_api.uC.uC_api "uC_api"

### API level 1
This level handles the communication and buffering. The User has to construct and process all packets themselves.

```python
import uC_api

# open connection
uc = uC_api.uC_api('/dev/ttyACM0',1)

# create packet
pinConfigPacket = uC_api.packet.ConfigPacket(
	header = uC_api.header.ConfigMainHeader.IN_CONF_PIN,		# pin configuration.
	config_header = uC_api.header.ConfigSubHeader.CONF_OUTPUT,	# pin as OUTPUT.
	value = 13)										    # pin ID.

# Send packet to uC.
uc.send_packet(pinConfigPacket) 
time.sleep(1)

#read the response from uC
if uc.has_packet():
    print(uc.read_packet()) #blocking

us.close_connection()   # close connection to uC, the User can still access the recorded data.
```
For all available packets and headers, see:
@ref packet.py and @ref header.py or @ref datatypes.h

For all availible `uC_api` commands see @ref uC_api.uC.uC_api

### API level 0
This level is the raw packets, and the User must handle the communication.
```python
import serial, uC_api

# creating data packet to be sent to the uC.
data_packet = uC_api.packet.Data32bitPacket(header = uC_api.header.Data32bitHeader.IN_READ_TIME)

# convet packet content to a byte array (C struct) with 9 bytes.
packet_bytes = data_packet.to_bytearray()

# connecting to uC (open serial port).
uC_serial = serial.Serial('/dev/ttyACM0', 115200, timeout = 1)

uC_serial.reset_input_buffer()           # flush input buffer.

uC_serial.write(packet_bytes)            # write packet content.

# read byte array (C struct)
read_bytes = uC_serial.read(size = len(packet_bytes))

#convert to packet
read_packet =  uC_api.packet.Packet.from_bytearray(read_bytes)

print('> data read: {}'.format(read_packet))

# close port.
uC_serial.close()
```

For all available packets and headers, see:
@ref packet.py and @ref header.py or @ref datatypes.h


## Architecture

The Python API consists of a main thread containing the API and a background thread buffering the communication to and from the microcontroller (uC) via the USB serial connection. The API uses the buffers to provide the possibility to run long test cases with lots of test vectors that can not all be preloaded on the uC. The test vectors (packets) are transferred whenever space frees up on the uC.

The uC has the main loop communicating with the PC, and incoming events with time information are stored in a ring buffer. An equivalent output buffer exists, which the main loop packet by packet sends to the PC.

The data acquisition and timed execution of commands are handled via interrupts. 


## File structure

### Arduino code (firmware)
the uC firmware files are located in `firmware`. The main file is the firmware.ino, all files starting with `core_` handle the packet buffers and timed execution. The interfaces begin with `interface_`. The User can find all uC board-specific configurations in `uc_boards.h`, and all packet definitions and data structure for the PC communication are in `datatypes.h`.

### Python code (uC_api)
The Python code is in the module `uC_api` and can be imported with `import uC_api` when adding the repository root to the Python search path 
```python
import sys
sys.path.append('<path to git repo>')
import uC_api
```
For a more detailed description, look at the section API levels.

### Tests & Examples (tests)
tests can be found in `tests`. These scripts are good starting points for using the individual features. 

## Known bugs

 - on SAMD21 uC (Zero, MKR), testing async interfaces via loopback is currently not working due to an unfixed bug in the interrupt priority.
   Regular DuT operation should work without problems.

## How to contribute

Contributions are very welcome. Please reach out and open a pull request!

It would help us and your pull request if you add code/function docs and, ideally, if it makes sense to a test/example, 
please note down your changes in CHANGELOG.md below [Unreleased].

@people with direct repo access do not commit to main or dev directly. Do feature branches and pull requests! 

All DuT-specific files and higher-level APIs should be in their separate repositories.
