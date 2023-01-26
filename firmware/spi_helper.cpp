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

#include "spi_helper.h"

volatile bool spi0_active = 0;
volatile bool spi1_active = 0;
volatile bool spi2_active = 0;

void configure_spi(int id, uint8_t config_option, uint8_t data){
    switch (config_option){
      case CONF_ACTIVE:
            if ((spi0_active == 1 && id == 0) ||
                (spi1_active == 1 && id == 1) ||
                (spi2_active == 1 && id == 2)) {
              packet_t error_packet;
              error_packet.error.header = OUT_ERROR_INTERFACE_ALREADY_ACTIVE;
              switch (id){
                case 0: error_packet.error.org_header = IN_CONF_SPI0; break;
                case 1: error_packet.error.org_header = IN_CONF_SPI1; break;
                case 2: error_packet.error.org_header = IN_CONF_SPI2; break;
              }
              error_packet.error.value = micros() - offset_time;
              if (is_output_buffer_not_full()){
                output_ring_buffer[output_ring_buffer_next_free] = error_packet;
                output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
              }
            }
            else{
              packet_t out;
              switch (id){
                case 0: 
                  if (reserve_input_pin(12) && reserve_output_pin(11) && reserve_output_pin(13)){
                    SPI.begin();
                    spi0_active = 1;
                    // if (is_output_buffer_not_full()) {
                    //   output_ring_buffer[output_ring_buffer_next_free].pin.header = OUT_SUCCESS_PIN_CONFIGURED;
                    //   output_ring_buffer[output_ring_buffer_next_free].pin.exec_time = micros()-offset_time;
                    //   output_ring_buffer[output_ring_buffer_next_free].pin.id = data;
                    //   output_ring_buffer[output_ring_buffer_next_free].pin.value = OUTPUT;
                    //   output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
                    // }                 
                  }
                  break;               
                case 1: 
                  if (reserve_input_pin(1) && reserve_output_pin(26) && reserve_output_pin(27)){
                    SPI1.begin();
                    spi1_active = 1;                    
                  }
                  break;  
                case 2: 
                  if (reserve_input_pin(42) && reserve_output_pin(43) && reserve_output_pin(45)){
                    SPI2.begin();
                    spi2_active = 1;                    
                  }
                  break;  
              }
            }

        
        break;
      default:
      if (is_output_buffer_not_full()){
        output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_UNKNOWN_CONFIGURATION;
        output_ring_buffer[output_ring_buffer_next_free].error.org_header = config_option;
        output_ring_buffer[output_ring_buffer_next_free].error.value = data;
        output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
      }
      break;
    }
}     
        
        
void send_spi_packet(int id, uint8_t data){
  if ((spi0_active == 0 && id == 0) ||
      (spi1_active == 0 && id == 1) ||
      (spi2_active == 0 && id == 2)) {
    
    packet_t error_packet;
    error_packet.error.header = OUT_ERROR_INTERFACE_NOT_ACTIVE;
    switch (id){
      case 0: error_packet.error.org_header = IN_SPI0; break;
      case 1: error_packet.error.org_header = IN_SPI1; break;
      case 2: error_packet.error.org_header = IN_SPI2; break;
    }
    error_packet.error.value = micros() - offset_time;
    if (is_output_buffer_not_full()){
      output_ring_buffer[output_ring_buffer_next_free] = error_packet;
      output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
    }
    return;
  }
  
  packet_t out;
  switch (id){
    case 0:
      SPI.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI.transfer(data);
      SPI.endTransaction();
      out.data_8.header = OUT_SPI0;
      out.data_8.value = data;
      break;
    case 1:
      SPI1.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI1.transfer(data);
      SPI1.endTransaction(); 
      out.data_8.header = OUT_SPI1;
      out.data_8.value = data;    
      break;
    case 2:
      SPI2.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI2.transfer(data);
      SPI2.endTransaction(); 
      out.data_8.header = OUT_SPI2;
      out.data_8.value = data;  
      break;
  }
  out.data_8.exec_time = micros()-offset_time;
  if (is_output_buffer_not_full() && offset_time != 0){
    output_ring_buffer[output_ring_buffer_next_free] = out;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
  }
}

void send_spi_packet_32bit(int id, uint32_t data){
  if ((spi0_active == 0 && id == 0) ||
      (spi1_active == 0 && id == 1) ||
      (spi2_active == 0 && id == 2)) {
    
    packet_t error_packet;
    error_packet.error.header = OUT_ERROR_INTERFACE_NOT_ACTIVE;
    switch (id){
      case 0: error_packet.error.org_header = IN_SPI0_32; break;
      case 1: error_packet.error.org_header = IN_SPI1_32; break;
      case 2: error_packet.error.org_header = IN_SPI2_32; break;
    }
    error_packet.error.value = micros() - offset_time;
    if (is_output_buffer_not_full()){
      output_ring_buffer[output_ring_buffer_next_free] = error_packet;
      output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
    }
    return;
  }
  
  packet_t out;
  switch (id){
    case 0:
      SPI.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI.transfer32(data);
      SPI.endTransaction();
      out.data.header = OUT_SPI0_32;
      out.data.value = data;
      break;
    case 1:
      SPI1.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI1.transfer32(data);
      SPI1.endTransaction(); 
      out.data.header = OUT_SPI1_32;
      out.data.value = data;    
      break;
    case 2:
      SPI2.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      SPI2.transfer32(data);
      SPI2.endTransaction(); 
      out.data.header = OUT_SPI2_32;
      out.data.value = data;  
      break;
  }
  out.data_8.exec_time = micros()-offset_time;
  if (is_output_buffer_not_full() && offset_time != 0){
    output_ring_buffer[output_ring_buffer_next_free] = out;
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
  }
}
