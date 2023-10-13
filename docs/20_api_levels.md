# API levels 

## API level 2
All interfaces are entirely abstracted at this level as Python objects, and packets are wholly hidden.

```python
import uC_api, time

# Open connection
uc = uC_api.uC_api('/dev/ttyACM0',2)

# Access all interface objects via 
uc.async_to_chip[X]     # up to outgoing 8 async interfaces, X -> 0-7
uc.async_from_chip[X]   # up to incoming 8 async interfaces, X -> 0-7
uc.i2c[X]               # up to 3 i2c interfaces (currently only master), X -> 0-2
uc.pin[X]               # up to 55 (teensy4.1), 40 teensy4.0, 22 Arduino Zero and MKR pins, X -> 0-54
uc.spi[X]               # up to 3 spi interfaces (currently only master), X -> 0-2

# Configure interfaces
uc.pin[13].activate(pin_mode="OUTPUT") #LED on Tennsy and Zero

uc.async_from_chip[0].activate(req_pin=0, ack_pin=1, data_width=2, data_pins=[2,3], mode="4Phase_Chigh_Dhigh", req_delay = 0)

# Set up experiment
uc.pin[13].send(value=1, time=10000)

# Execute experiment
uc.start_experiment()   # start recoding and execute the comands

time.sleep(1)
# Get results
pin_13, pin_13_times = uc.pin[13].data_to_chip_and_clear() # get the confimation of the pin raise with exact time

print(async_from_chip[0]) # print the async interface information

us.close_connection()   # close connection to uC, the User can still access the recorded data.
```
All interfaces record data with timestamps for sending and receiving data from the uC to the DuT. For all available functions, see:
 - @ref uC_api.interface_async.Interface_Async "Interface_Async"
 - @ref uC_api.interface_i2c.Interface_I2C "Interface_I2C"
 - @ref uC_api.interface_spi.Interface_SPI "Interface_SPI"
 - @ref uC_api.interface_pin.Interface_PIN "Interface_PIN"
 - @ref uC_api.uC.uC_api "uC_api"

## API level 1
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

## API level 0
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

