import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../')
sys.path.append('./')

from uC_api import *

logging.basicConfig(level=logging.DEBUG)

uc = uC_api('/dev/ttyACM0',2)

uc.pin[13].activate("OUTPUT") #LED on Tennsy
#uc.pin[23].activate("OUTPUT") #LED on MKRZero
uc.pin[12].activate("INPUT") # wired up to one of the others

toggle = 1
for step in range(100,10000000, 1000000):
    uc.pin[13].send(value=toggle, time=step)
    #uc.pin[23].send(value=toggle, time=step)
    toggle = not toggle

uc.start_experiment()

time.sleep(10)
uc.update_state()

print(uc.pin[13])

print(uc.pin[12])

uc.close_connection()


