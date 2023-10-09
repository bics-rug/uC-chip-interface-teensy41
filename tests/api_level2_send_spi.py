import serial, sys, time, struct, logging
from enum import Enum

sys.path.append('../uC_api')
sys.path.append('./uC_api')

from uC import uC_api

logging.basicConfig(level=logging.DEBUG)

uc = uC_api('/dev/ttyACM0',2)

uc.spi[0].activate(mode="SPI_MODE0", speed_class=2, order="LSBFIRST", number_of_bytes=4)


uc.start_experiment()
time.sleep(0.1)
uc.spi[0].send((2**31)-1)
uc.spi[0].send(0)
uc.spi[0].send((2**16)-1)
uc.spi[0].send(((2**16)-1)<<16)

time.sleep(1)
uc.update_state()

print(uc.spi[0])





