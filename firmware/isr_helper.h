/*
    This file is part of the Firmware project to interface with small Neuromorphic chips
    Copyright (C) 2022 Ole Richter - University of Groningen

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

#ifndef ISR_HELPER_H
#define ISR_HELPER_H
#include <cstdint>
#include "ring_buffer.h"
#include "datatypes.h"
#include "AER_from_chip.h"




void aer_ISR(uint8_t id);
void aer0_ISR();
void aer1_ISR();
void aer2_ISR();
void aer3_ISR();
void aer4_ISR();
void aer5_ISR();
void aer6_ISR();
void aer7_ISR();
void pin_ISR(uint8_t id);
void pin_ISR0();
void pin_ISR1();
void pin_ISR2();
void pin_ISR3();
void pin_ISR4();
void pin_ISR5();
void pin_ISR6();
void pin_ISR7();
void pin_ISR8();
void pin_ISR9();
void pin_ISR10();
void pin_ISR11();
void pin_ISR12();
void pin_ISR13();
void pin_ISR14();
void pin_ISR15();
void pin_ISR16();
void pin_ISR17();
void pin_ISR18();
void pin_ISR19();
void pin_ISR20();
void pin_ISR21();
void pin_ISR22();
void pin_ISR23();
void pin_ISR24();
void pin_ISR25();
void pin_ISR26();
void pin_ISR27();
void pin_ISR28();
void pin_ISR29();
void pin_ISR30();
void pin_ISR31();
void pin_ISR32();
void pin_ISR33();
void pin_ISR34();
void pin_ISR35();
void pin_ISR36();
void pin_ISR37();
void pin_ISR38();
void pin_ISR39();
void pin_ISR40();
void pin_ISR41();
void pin_ISR42();
void pin_ISR43();
void pin_ISR44();
void pin_ISR45();
void pin_ISR46();
void pin_ISR47();
void pin_ISR48();
void pin_ISR49();
void pin_ISR50();
void pin_ISR51();
void pin_ISR52();
void pin_ISR53();
void pin_ISR54();

void delay20ns( uint32_t clocks );

#endif