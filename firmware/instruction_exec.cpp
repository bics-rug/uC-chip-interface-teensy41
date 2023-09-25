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
#include "instruction_exec.h"

volatile bool exec_active = false;
volatile IntervalTimer myTimer;

void exec_instruction(packet_t* instruction, bool is_ISR_call) {
  switch(instruction->data.header){
  case IN_READ: send_output_ring_buffer(); break;
  case IN_READ_LAST: send_output_ring_buffer_last(); break;
  case IN_READ_INSTRUCTIONS: send_input_ring_buffer(); break;
  case IN_SET_TIME: set_time_offset(instruction->data.value); break;
  case IN_READ_TIME: read_time(is_ISR_call); break;
  case IN_PIN: set_pin(instruction->pin.id,instruction->pin.value); break;
  case IN_SPI0: send_spi_packet(0,instruction->data_8.value); break;  
  case IN_SPI1: send_spi_packet(1,instruction->data_8.value); break;  
  case IN_SPI2: send_spi_packet(2,instruction->data_8.value); break;  
  case IN_SPI0_32: send_spi_packet_32bit(0,instruction->data.value); break;  
  case IN_SPI1_32: send_spi_packet_32bit(1,instruction->data.value); break;  
  case IN_SPI2_32: send_spi_packet_32bit(2,instruction->data.value); break;  
  case IN_AER_TO_CHIP0: AER_to_chip::send_aer_packet(0,instruction->data.value); break;  
  case IN_AER_TO_CHIP1: AER_to_chip::send_aer_packet(1,instruction->data.value); break;
  case IN_AER_TO_CHIP2: AER_to_chip::send_aer_packet(2,instruction->data.value); break;  
  case IN_AER_TO_CHIP3: AER_to_chip::send_aer_packet(3,instruction->data.value); break;
  case IN_AER_TO_CHIP4: AER_to_chip::send_aer_packet(4,instruction->data.value); break;  
  case IN_AER_TO_CHIP5: AER_to_chip::send_aer_packet(5,instruction->data.value); break;
  case IN_AER_TO_CHIP6: AER_to_chip::send_aer_packet(6,instruction->data.value); break;  
  case IN_AER_TO_CHIP7: AER_to_chip::send_aer_packet(7,instruction->data.value); break;  
  case IN_CONF_PIN: configure_pin(instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_SPI0: configure_spi(0,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_SPI1: configure_spi(1,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_SPI2: configure_spi(2,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP0: AER_to_chip::configure(0,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP1: AER_to_chip::configure(1,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP2: AER_to_chip::configure(2,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP3: AER_to_chip::configure(3,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP4: AER_to_chip::configure(4,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP5: AER_to_chip::configure(5,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP6: AER_to_chip::configure(6,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_TO_CHIP7: AER_to_chip::configure(7,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP0: AER_from_chip::configure(0,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP1: AER_from_chip::configure(1,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP2: AER_from_chip::configure(2,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP3: AER_from_chip::configure(3,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP4: AER_from_chip::configure(4,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP5: AER_from_chip::configure(5,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP6: AER_from_chip::configure(6,instruction->config.config_header,instruction->config.value); break;
  case IN_CONF_AER_FROM_CHIP7: AER_from_chip::configure(7,instruction->config.config_header,instruction->config.value); break;
  default:   
    if (is_ISR_call) error_message(OUT_ERROR_UNKNOWN_INSTRUCTION,instruction->data.header,instruction->data.value);
    else error_message_bypass_buffer(OUT_ERROR_UNKNOWN_INSTRUCTION,instruction->data.header,instruction->data.value);
    break;
  }
}

void exec_timed_commands(){
  noInterrupts();
  uint8_t attempt = 0;
  if (exec_active) return;
  exec_active = true;
  uint32_t current_time = micros() - offset_time; // time does not move forward in interupts  
  
  packet_t instruction = copy_packet(&input_ring_buffer[input_ring_buffer_start]);
  
  while (
    (input_ring_buffer_start % INPUT_BUFFER_SIZE != input_ring_buffer_next_free) &&
     instruction.data.exec_time <= current_time ) {
    interrupts();
    exec_instruction(&instruction,true);
    noInterrupts();
    input_ring_buffer_start = (input_ring_buffer_start + 1) % INPUT_BUFFER_SIZE;
    instruction = copy_packet(&input_ring_buffer[input_ring_buffer_start]);
  }
  exec_active = false;
  interrupts();
}

void set_time_offset(uint32_t offset){
  if (offset){
    offset_time = micros() + offset;
    myTimer.begin(exec_timed_commands, EXEC_PRESISION);
  }
  else{
    offset_time = 0;  
    myTimer.end();  
  }
}

void read_time(bool is_ISR_call){
  if (is_ISR_call) error_message(OUT_ERROR_UNKNOWN_INSTRUCTION,OUT_ERROR_UNKNOWN_INSTRUCTION);
  else error_message_bypass_buffer(OUT_ERROR_UNKNOWN_INSTRUCTION,OUT_ERROR_UNKNOWN_INSTRUCTION,micros());
}
