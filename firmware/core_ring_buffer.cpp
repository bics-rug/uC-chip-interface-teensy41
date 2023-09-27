/*
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
    Copyright (C) 2022-2023 Ole Richter - University of Groningen

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

#include "core_ring_buffer.h"

volatile packet_t input_ring_buffer[INPUT_BUFFER_SIZE] = {};
volatile uint16_t input_ring_buffer_start = 0;
volatile uint16_t input_ring_buffer_next_free = 0;
volatile packet_t output_ring_buffer[OUTPUT_BUFFER_SIZE] = {};
volatile uint16_t output_ring_buffer_start = 0;
volatile uint16_t output_ring_buffer_next_free = 0;
volatile bool output_buffer_overflow = 0;
volatile bool output_buffer_read = 1;

volatile unsigned long offset_time = 0; // offset time is in microseconds, 0 also doubles as no recording
volatile bool read_active = 0;

void setup_ring_buffer(){
  //input_ring_buffer = (packet_t*) malloc(sizeof(packet_t)*INPUT_BUFFER_SIZE);
  //output_ring_buffer = (packet_t*) malloc(sizeof(packet_t)*OUTPUT_BUFFER_SIZE);
  output_ring_buffer_start = 0;
  output_ring_buffer_next_free = 0;
  input_ring_buffer_next_free = 0;
  input_ring_buffer_start = 0;
}

void set_read_on_request(uint8_t state){
  output_buffer_read = (state > 0);
  //send confirmation
  send_config(IN_CONF_READ_ON_REQUEST,CONF_NONE,state);
}

bool is_output_buffer_not_full(){
  if (output_ring_buffer_start == (output_ring_buffer_next_free + 2) % OUTPUT_BUFFER_SIZE) {
    output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_OUTPUT_FULL;
    output_ring_buffer[output_ring_buffer_next_free].error.org_header = OUT_ERROR_OUTPUT_FULL;
    output_ring_buffer[output_ring_buffer_next_free].error.value = 1;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE; 
    return false;         
  } 
  else if(output_ring_buffer_start == (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE) {
    uint16_t index = output_ring_buffer_next_free == 0 ? OUTPUT_BUFFER_SIZE-1 : output_ring_buffer_next_free-1;
    output_ring_buffer[index].data.value++;
    return false;
  }
  else return true;
}

void send_input_ring_buffer_free_spots(){
  packet_t data_packet;
  data_packet.data.header = OUT_FREE_INSTRUCTION_SPOTS;
  data_packet.data.exec_time = micros()-offset_time;
  if (input_ring_buffer_start > input_ring_buffer_next_free){
    data_packet.data.value = input_ring_buffer_start-input_ring_buffer_next_free-1;
  }
  else{
    data_packet.data.value = INPUT_BUFFER_SIZE-input_ring_buffer_next_free+input_ring_buffer_start-1;
  }
  uint8_t position;
  // due to different storage alignment need to write data bytes individual
  for (position = 0; position < sizeof(packet_t); position++) Serial.write(data_packet.bytes[position]);
  //send confirmation
  send_data32(IN_FREE_INSTRUCTION_SPOTS,0,true);

}

void send_output_ring_buffer(){
  noInterrupts(); 
  if (!read_active){
    read_active = true;
    interrupts(); 
    while (output_ring_buffer_start != output_ring_buffer_next_free){
      noInterrupts();
      packet_t out = copy_packet(&output_ring_buffer[output_ring_buffer_start]);
      output_ring_buffer_start = (output_ring_buffer_start + 1) % OUTPUT_BUFFER_SIZE; 
      interrupts();
      uint8_t position;
      // due to different storage alignment need to write data bytes individual
      for (position = 0; position < sizeof(packet_t); position++) Serial.write(out.bytes[position]);
    }
    read_active = false;
    //send confirmation
    send_data32(IN_READ,0,true);
    send_output_ring_buffer_first();
  }
}

void send_output_ring_buffer_first(){
  if (!read_active && output_ring_buffer_start != output_ring_buffer_next_free){
    packet_t out = copy_packet(&output_ring_buffer[output_ring_buffer_start]);
    output_ring_buffer_start = (output_ring_buffer_start + 1) % OUTPUT_BUFFER_SIZE; 
    interrupts();
    uint8_t position;
    // due to different storage alignment need to write data bytes individual
    for (position = 0; position < sizeof(packet_t); position++) {
      Serial.write(out.bytes[position]);
    }
  }
}

void send_output_ring_buffer_last(bool conf){
  if (!read_active){
      noInterrupts();
      packet_t out = copy_packet(&output_ring_buffer[(output_ring_buffer_next_free-1)% OUTPUT_BUFFER_SIZE]);
      interrupts();
      uint8_t position;
      // due to different storage alignment need to write data bytes individual
      for (position = 0; position < sizeof(packet_t); position++) Serial.write(out.bytes[position]);
    //send confirmation
    if (conf){
      send_data32(IN_READ_LAST,0,true);
      send_output_ring_buffer_first();
    }
  }
}

void send_input_ring_buffer(){
  
  uint32_t ring_buffer_start = input_ring_buffer_start;
  interrupts(); 
  while (ring_buffer_start != input_ring_buffer_next_free){

    noInterrupts();
    packet_t out = copy_packet(&input_ring_buffer[ring_buffer_start]);
    ring_buffer_start = (ring_buffer_start + 1) % INPUT_BUFFER_SIZE; 
    interrupts();
    uint8_t position;
    // due to different storage alignment need to write data bytes individual
    for (position = 0; position < sizeof(packet_t); position++) Serial.write(out.bytes[position]);
  }
  //send confirmation
  send_data32(IN_READ_INSTRUCTIONS,0,true);
}

void send_data32(uint8_t header, uint32_t value, bool is_confirmation){
  if (is_output_buffer_not_full() && (is_confirmation || offset_time != 0)) {
    noInterrupts();
    output_ring_buffer[output_ring_buffer_next_free].data.header = header;
    output_ring_buffer[output_ring_buffer_next_free].data.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].data.value = value;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
    interrupts(); 
  }   
}

void send_data_i2c(uint8_t header,uint8_t device_address_8, uint8_t register_address, uint8_t value_ms, uint8_t value_ls, bool is_confirmation){
  if (is_output_buffer_not_full() && (is_confirmation || offset_time != 0)) {
    noInterrupts();
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.header = header;
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.component_address = device_address_8;
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.register_address = register_address;
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.value_ms = value_ms;
    output_ring_buffer[output_ring_buffer_next_free].data_i2c.value_ms = value_ls;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
    interrupts();   
  } 
}

void send_pin(uint8_t header, uint8_t id, uint8_t value, bool is_confirmation){
  if (is_output_buffer_not_full() && (is_confirmation || offset_time != 0)) {
    noInterrupts();
    output_ring_buffer[output_ring_buffer_next_free].pin.header = header;
    output_ring_buffer[output_ring_buffer_next_free].pin.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].pin.id = id;
    output_ring_buffer[output_ring_buffer_next_free].pin.value = value;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
    interrupts();   
  } 
}

void send_config(uint8_t header, uint8_t config_header, uint8_t value){
  if (is_output_buffer_not_full()) {
    noInterrupts();
    output_ring_buffer[output_ring_buffer_next_free].config.header = header;
    output_ring_buffer[output_ring_buffer_next_free].config.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].config.config_header = config_header;
    output_ring_buffer[output_ring_buffer_next_free].config.value = value;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
    interrupts();   
  } 
}

void error_message(uint8_t error_header, uint8_t source_header, uint32_t value, uint8_t sub_source_header){
  if (is_output_buffer_not_full()){
    noInterrupts();
    output_ring_buffer[output_ring_buffer_next_free].error.header = error_header;
    output_ring_buffer[output_ring_buffer_next_free].error.org_header = source_header;
    output_ring_buffer[output_ring_buffer_next_free].error.value = value;
    output_ring_buffer[output_ring_buffer_next_free].error.sub_header = sub_source_header;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
    interrupts();          
  }
}

void error_message(uint8_t error_header, uint8_t source_header){
  error_message(error_header,source_header,micros()-offset_time,255);
}

void error_message_bypass_buffer(uint8_t error_header, uint8_t source_header, uint32_t value, uint8_t sub_source_header){
  packet_t error_packet;
  error_packet.error.header = error_header;
  error_packet.error.org_header = source_header;
  error_packet.error.value = value;
  error_packet.error.sub_header = sub_source_header;

  uint8_t position;
  // due to different storage alignment need to write data bytes individual
  for (position = 0; position < sizeof(packet_t); position++) Serial.write(error_packet.bytes[position]);
}
