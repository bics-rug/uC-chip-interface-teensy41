/*
    This file is part of the Firmware project to interface with small Neuromorphic chips
    Copyright (C) 2022 Ole Richter - University of Groningen
    Copyright (C) 2022 Benjamin Hucko

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

// -DARDUINO_SAMD_MKRZERO -DARDUINO_ARCH_SAMD -DUSE_ARDUINO_MKR_PIN_LAYOUT -D__SAMD21G18A__ -DF_CPU=48000000L
// -D__IMXRT1062__ -DARDUINO_TEENSY41 -DF_CPU=600000000
4f -DUSBCON "-DUSB_MANUFACTURER=\"Arduino LLC\"" "-DUSB_PRODUCT=\"Arduino MKRZero\"" -I/home/p302212/.arduino15/packages/arduino/tools/CMSIS/4.5.0/CMSIS/Include/ -I/home/p302212/.arduino15/packages/arduino/tools/CMSIS-Atmel/1.2.0/CMSIS/Device/ATMEL/ -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/cores/arduino/api/deprecated -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/cores/arduino/api/deprecated-avr-comp -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/cores/arduino -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/variants/mkrzero -I/home/p302212/Arduino/libraries/Adafruit_MCP23017_Arduino_Library/src -I/home/p302212/Arduino/libraries/Adafruit_BusIO -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/libraries/Wire -I/home/p302212/.arduino15/packages/arduino/hardware/samd/1.8.13/libraries/SPI /tmp/arduino/sketches/A2C572F20539BEE7818185C5EA24C6E9/sketch/instruction_exec.cpp -o /tmp/arduino/sketches/A2C572F20539BEE7818185C5EA24C6E9/sketch/instruction_exec.cpp.o



#include <Arduino.h>
#include "ring_buffer.h"
#include "instruction_exec.h"


/*
 This programm is supposed to be used for interfacing with small neuromorphic chips,
 the pin and interface configuration is uploaded on runtime via configuration packets,
 so for most chips/modules a change of the uC firmware is not nessesary.

 the Idea behind the firmware is that you can send command packets with a exec time in the future, 
and the command is executed at that time via interrupt. (see instruction_exec.h/cpp)
 if you send exec_time=0 the execution is done right away. The exec_time needs to be sorted and assending. 
 the execuion is done via interrupts the execution only happens every ~100us => see instruction_exec.h
 timesteps are in usec and the role over occurs after ~71min after boot of the uC. roleover is not supported.

 the folloeing interfaces are supported:
 - SPI - Serial Periferal Interface for memory and fifo access (see "spi_helper.h/cpp")
 - AER - paralell databus with 4-phase handshake (see "AER_tochip.h/cpp" and "AER_from_chip.h/cpp")
 - PIN - manual pin raising and lowering (see "pin_helper.h/cpp")
 

 see datatypes.h for all available commands and thier use.

 to start recording and execution set the TIME to anything other than 0, to stop execution and recording sent TIME to 0.

 recording of events is handeled in "isr_helper.h/cpp"

 the coding style is following the Arduino Style of having interfaces staticly allocatated for access. 
 In a future version this shoud be at least changed to static Object Oriented Programing

*/


/*
 setup starts the serial connection and allocates the ring buffers
 aswell as sets the interruptpriority for command execution
*/
void setup() { 
  Serial.begin(115200);   // the speed is ignored the USB native speed is used. 
  Serial.setTimeout(1);    
  setup_ring_buffer();
  myTimer.priority(200);

}

/*
 the main loop just handels comunication with the host via the serial interface and instuction execution if exec_time == 0, 
 in all other cases the instruction is stored in the instruction ring buffer.
*/
void loop() {
  if (Serial.available()) {

    // read instruction packet
    packet_t current_instruction;    
    Serial.readBytes(current_instruction.bytes, sizeof(packet_t));

    // exec instruction if exec_time == 0
    if (current_instruction.data.exec_time == 0) {
      exec_instruction(&current_instruction, false);
    }

    // if instruction buffer is not full store instruction
    else if (input_ring_buffer_start != (input_ring_buffer_next_free + 1) % INPUT_BUFFER_SIZE) {
      noInterrupts();
      input_ring_buffer[input_ring_buffer_next_free] = current_instruction;
      input_ring_buffer_next_free = (input_ring_buffer_next_free + 1) % INPUT_BUFFER_SIZE;
      interrupts();
    }

    // if instruction buffer is full send error, error_message not used because send without que
    else {
      error_message_bypass_buffer(OUT_ERROR_INPUT_FULL,current_instruction.data.header,current_instruction.data.value);
    }


  }
  // send error if output buffer is full,
  if (output_ring_buffer_start == output_ring_buffer_next_free) {
    error_message_bypass_buffer(OUT_ERROR_OUTPUT_FULL,OUT_ERROR_OUTPUT_FULL,output_ring_buffer_next_free);
  } 
  // write output buffer

}