import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../')
sys.path.append('./')

from uC_api import *

logging.basicConfig(level=logging.DEBUG)

uc = uC_api('/dev/ttyACM0',2)

uc.async_to_chip[0].activate( req_pin=1, ack_pin=4, data_width=2, data_pins=[8,13], mode="4Phase_Chigh_Dhigh", req_delay = 0)
uc.async_from_chip[0].activate( req_pin=0, ack_pin=2, data_width=2, data_pins=[7,12], mode="4Phase_MCP23017", req_delay = 0)

time.sleep(1)
uc.start_experiment()

uc.async_to_chip[0].send(0)
uc.async_to_chip[0].send(1)
uc.async_to_chip[0].send(2)
uc.async_to_chip[0].send(3)

time.sleep(1)
uc.update_state()
print(uc.async_to_chip[0])

print(uc.async_from_chip[0])

uc.close_connection()



