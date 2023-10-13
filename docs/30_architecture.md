# Architecture

## Python API

The Python API consists of a main thread containing the API and a background thread buffering the communication to and from the microcontroller (uC) via the USB serial connection. The API uses the buffers to provide the possibility to run long test cases with lots of test vectors that can not all be preloaded on the uC. The test vectors (packets) are transferred whenever space frees up on the uC.


## The Firmware
```
                                                         [Timer interrupt every 100us] -->--. 
                                                                                             \
                              ,--(packet \w time)--> timed ring buffer --(packets < clock)--> &    ,--> configuration --.
                             /                                             ,-----<------------'   /                     |
                            /--------------(packet)----------------------->  instruction execution ---> IO data out ---,| 
                           /                                                                                            |
PC <--(usb)--> [main loop] <--(packet \w time) -- output ring buffer <-------------------(ack packet \w time) ---<------'
                                                                       \
                                                                        `--<--(data packet \w time)--<--[IO interrupt in]
                          
```
The uC has the main loop communicating with the PC, and incoming events with time information are stored in a ring buffer. An equivalent output buffer exists, which the main loop packet by packet sends to the PC.

The data acquisition and timed execution of commands are handled via interrupts. 
