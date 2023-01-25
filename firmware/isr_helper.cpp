/*
    This file is part of the Firmware project to interface with small Neuromorphic chips
    Copyright (C) 2022 Matteo Cartiglia - University of Zurich
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

#include "isr_helper.h"

//@TODO move to AER_FROM_CHIP
void aer_ISR(uint8_t id) {
  if (AER_from_chip::inst[id]->reqRead()) {
      if ( offset_time != 0 ) { 
        AER_from_chip::inst[id]->recordEvent();
      }   
      AER_from_chip::inst[id]->ackWrite(1);
    }
  else if (!AER_from_chip::inst[id]->reqRead()) {
      AER_from_chip::inst[id]->ackWrite(0);
  }
}

void delay20ns( uint32_t clocks )
{
  do
  {
    __asm( "nop" );
    __asm( "nop" );
    __asm( "nop" );
    __asm( "nop" );
    __asm( "nop" );
    __asm( "nop" );
  }
  while ( --clocks );
}

void aer0_ISR() { aer_ISR(0); }
void aer1_ISR() { aer_ISR(1); }
void aer2_ISR() { aer_ISR(2); }
void aer3_ISR() { aer_ISR(3); }
void aer4_ISR() { aer_ISR(4); }
void aer5_ISR() { aer_ISR(5); }
void aer6_ISR() { aer_ISR(6); }
void aer7_ISR() { aer_ISR(7); }

//@TODO move to pin_helper
void pin_ISR(uint8_t id) {
  noInterrupts();
  if (is_output_buffer_not_full() && offset_time != 0) {
    output_ring_buffer[output_ring_buffer_next_free].pin.header = OUT_PIN;
    output_ring_buffer[output_ring_buffer_next_free].pin.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].pin.id = id;
    output_ring_buffer[output_ring_buffer_next_free].pin.value = digitalReadFast(id); //@TODO replace with direct pin access
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;  
  }
  interrupts();
}

void pin_ISR0() { pin_ISR(0); }
void pin_ISR1() { pin_ISR(1); }
void pin_ISR2() { pin_ISR(2); }
void pin_ISR3() { pin_ISR(3); }
void pin_ISR4() { pin_ISR(4); }
void pin_ISR5() { pin_ISR(5); }
void pin_ISR6() { pin_ISR(6); }
void pin_ISR7() { pin_ISR(7); }
void pin_ISR8() { pin_ISR(8); }
void pin_ISR9() { pin_ISR(9); }
void pin_ISR10() { pin_ISR(10); }
void pin_ISR11() { pin_ISR(11); }
void pin_ISR12() { pin_ISR(12); }
void pin_ISR13() { pin_ISR(13); }
void pin_ISR14() { pin_ISR(14); }
void pin_ISR15() { pin_ISR(15); }
void pin_ISR16() { pin_ISR(16); }
void pin_ISR17() { pin_ISR(17); }
void pin_ISR18() { pin_ISR(18); }
void pin_ISR19() { pin_ISR(19); }
void pin_ISR20() { pin_ISR(20); }
void pin_ISR21() { pin_ISR(21); }
void pin_ISR22() { pin_ISR(22); }
void pin_ISR23() { pin_ISR(23); }
void pin_ISR24() { pin_ISR(24); }
void pin_ISR25() { pin_ISR(25); }
void pin_ISR26() { pin_ISR(26); }
void pin_ISR27() { pin_ISR(27); }
void pin_ISR28() { pin_ISR(28); }
void pin_ISR29() { pin_ISR(29); }
void pin_ISR30() { pin_ISR(30); }
void pin_ISR31() { pin_ISR(31); }
void pin_ISR32() { pin_ISR(32); }
void pin_ISR33() { pin_ISR(33); }
void pin_ISR34() { pin_ISR(34); }
void pin_ISR35() { pin_ISR(35); }
void pin_ISR36() { pin_ISR(36); }
void pin_ISR37() { pin_ISR(37); }
void pin_ISR38() { pin_ISR(38); }
void pin_ISR39() { pin_ISR(39); }
void pin_ISR40() { pin_ISR(40); }
void pin_ISR41() { pin_ISR(41); }
void pin_ISR42() { pin_ISR(42); }
void pin_ISR43() { pin_ISR(43); }
void pin_ISR44() { pin_ISR(44); }
void pin_ISR45() { pin_ISR(45); }
void pin_ISR46() { pin_ISR(46); }
void pin_ISR47() { pin_ISR(47); }
void pin_ISR48() { pin_ISR(48); }
void pin_ISR49() { pin_ISR(49); }
void pin_ISR50() { pin_ISR(50); }
void pin_ISR51() { pin_ISR(51); }
void pin_ISR52() { pin_ISR(52); }
void pin_ISR53() { pin_ISR(53); }
void pin_ISR54() { pin_ISR(54); }

