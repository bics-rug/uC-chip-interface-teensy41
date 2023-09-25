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

#ifndef PIN_HELPER_H
#define PIN_HELPER_H
#include <cstdint>
#include <Arduino.h>
#include <chrono>
#include "ring_buffer.h"
#include "isr_helper.h"


#if defined(ARDUINO_TEENSY41)
#define NUMBER_OF_DIGITAL_PINS 55
#elif defined(ARDUINO_TEENSY40)
#define NUMBER_OF_DIGITAL_PINS 40
#elif defined(ARDUINO_SAMD_MKRZERO)
#define NUMBER_OF_DIGITAL_PINS 22
#else 
#define NUMBER_OF_DIGITAL_PINS 12
#endif

/*
 the Pin helper tracks the usage and configuration off all the pins.
 and changes thier state
*/

// the usage of pins, to avoid double use
extern volatile bool input_pin_active[NUMBER_OF_DIGITAL_PINS];
extern volatile bool output_pin_active[NUMBER_OF_DIGITAL_PINS];

/*
 register a pin as input, changes the direction of the uC acordingly
 retuns true if sucessfull, false if pin was previously registered for something else.
*/
bool reserve_input_pin(uint8_t id, uint8_t from_instruction = OUT_ERROR_PIN_ALREADY_INUSE);

/*
 register a pin as output, changes the direction of the uC acordingly
 retuns true if sucessfull, false if pin was previously registered for something else.
*/
bool reserve_output_pin(uint8_t id, uint8_t from_instruction = OUT_ERROR_PIN_ALREADY_INUSE);

/*
 processes all pin related configuration instructions, exspects a PIN_CONF package.
 it registers recording interrups for input pins, and registeres pin usage.
*/
void configure_pin(uint8_t instruction, uint8_t data);

/*
 checks if the pin is a valid output pin and sets the pin to that value.
 it can also write output pins that are defind by other interfaces like SPI or AER
*/
void set_pin(uint8_t id, uint32_t data);

#endif