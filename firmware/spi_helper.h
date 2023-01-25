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

#ifndef SPI_HELPER_H
#define SPI_HELPER_H
#include <cstdint>
#include <Arduino.h>
#include "ring_buffer.h"
#include "pin_helper.h"
#include <SPI.h>

extern volatile bool spi0_active;
extern volatile bool spi1_active;
extern volatile bool spi2_active;

void configure_spi(int id, uint8_t config_option, uint8_t data); 
               
void send_spi_packet(int id, uint8_t data);
void send_spi_packet_32bit(int id, uint32_t data);

#endif