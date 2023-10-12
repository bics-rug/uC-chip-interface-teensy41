import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../')
sys.path.append('./')

from uC_api import *

logging.basicConfig(level=logging.INFO)

uc = uC_api('/dev/ttyACM0',2)

uc.pin[13].activate("OUTPUT") #LED on Tennsy

configPacket = Data32bitPacket(
	header = Data32bitHeader.IN_CONF_READ_ON_REQUEST,	# turn off reading.
	value = 1)										# turn off
uc.send_packet(configPacket) # send pin configuration.

uc.start_experiment()
toggle = 1
for step in range(4200):
    uc.pin[13].send(value=toggle, time=0)
    toggle = not toggle

configPacket = Data32bitPacket(
	header = Data32bitHeader.IN_READ,	# read.
	value = 1)										
uc.send_packet(configPacket) 

time.sleep(10)
uc.update_state()

print(uc.pin[13])

#toggle = 1
#for step in range(2**32 + 4100):
#    uc.pin[13].send(value=toggle, time=0)
#    toggle = not toggle
#
#configPacket = Data32bitPacket(
#	header = Data32bitHeader.IN_READ,	# read.
#	value = 1)										
#uc.send_packet(configPacket) 
#
#time.sleep(10)
#uc.update_state()
#
#print(uc.pin[13])

uc.close_connection()


