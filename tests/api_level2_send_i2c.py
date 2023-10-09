import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../uC_api')
sys.path.append('./uC_api')

from uC import uC_api

logging.basicConfig(level=logging.DEBUG)

uc = uC_api('/dev/ttyACM0',2)

uc.i2c[0].activate( speed=400000, order="LSBFIRST", number_of_bytes=1)


uc.start_experiment()
time.sleep(1)
uc.i2c[0].send_write(0,0,0,0)
uc.i2c[0].send_read_request(0,0,0,0)

time.sleep(1)
uc.update_state()

print(uc.i2c[0])





