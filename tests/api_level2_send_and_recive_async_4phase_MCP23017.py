import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../')
sys.path.append('./')

from uC_api import *

logging.basicConfig(level=logging.DEBUG)

uc = uC_api('/dev/ttyACM0',2)

uc.async_to_chip[0].activate( req_pin=8, ack_pin=10, data_width=4, data_pins=[0,1,2,3], mode="4Phase_Chigh_Dhigh", req_delay = 0)
uc.async_from_chip[0].activate( req_pin=9, ack_pin=11, data_width=32, data_pins=[0]*32, mode="4Phase_MCP23017", req_delay = 0)

uc.async_to_chip[0].send(0,time=2)
uc.async_to_chip[0].send(1,time=2)
uc.async_to_chip[0].send(2,time=2)
uc.async_to_chip[0].send(3,time=2)
uc.async_to_chip[0].send(8,time=2)
uc.async_to_chip[0].send(15,time=2)
uc.async_to_chip[0].send(14,time=2)

time.sleep(1)

uc.start_experiment()



time.sleep(3)
uc.update_state()
print(uc.async_to_chip[0])

print(uc.async_from_chip[0])

uc.close_connection()



