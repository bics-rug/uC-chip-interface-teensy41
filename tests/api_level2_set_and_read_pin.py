import serial, sys, time, struct
from enum import Enum

sys.path.append('../api')
sys.path.append('./api')

import uC

uc = uC.uC_api('/dev/ttyACM0',2)

uc.pin[13].activate("OUTPUT") #LED on Tennsy
uc.pin[23].activate("OUTPUT") #LED on MKRZero
uc.pin[14].activate("INPUT") # wired up to one of the others

toggle = 1
for step in range(100,10000000, 1000000):
    uc.pin[13].send(value=toggle, time=step)
    uc.pin[23].send(value=toggle, time=step)
    toggle = not toggle

uc.start_experiment()

time.sleep(10)
uc.update_state()
print(uc.pin[13].status)
print(uc.pin[13].data_to_chip)
print(uc.pin[13].data_to_chip_times)



