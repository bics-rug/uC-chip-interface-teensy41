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

#ifndef RING_BUFFER_H
#define RING_BUFFER_H
#include <cstdint>
#include "datatypes.h"
#include <stdlib.h>
#include <Arduino.h>


#define INPUT_BUFFER_SIZE 4096
#define OUTPUT_BUFFER_SIZE 4096

/*
  the ring buffer 
*/

extern volatile packet_t input_ring_buffer[INPUT_BUFFER_SIZE];
extern volatile uint16_t input_ring_buffer_start;
extern volatile uint16_t input_ring_buffer_next_free;
extern volatile packet_t output_ring_buffer[OUTPUT_BUFFER_SIZE];
extern volatile uint16_t output_ring_buffer_start;
extern volatile uint16_t output_ring_buffer_next_free;
extern volatile bool output_buffer_overflow;

extern volatile unsigned long offset_time; // offset time is in microseconds, 0 also doubles as no recording
extern volatile bool read_active;

void setup_ring_buffer();
bool is_output_buffer_not_full();
void send_output_ring_buffer();
void send_output_ring_buffer_last();
void send_input_ring_buffer();
void error_message(uint8_t error_header, uint8_t source_header, uint32_t value);
void error_message(uint8_t error_header, uint8_t source_header);
void send_pin(uint8_t header, uint8_t id, uint8_t value);
void send_data8(uint8_t header, uint8_t value);
void send_data32(uint8_t header, uint32_t value);
void error_message_bypass_buffer(uint8_t error_header, uint8_t source_header, uint32_t value);

#endif