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

#define NUMBER_OF_SPI_INTERFACES_MAX 3

volatile bool spi_active[NUMBER_OF_SPI_INTERFACES_MAX] = {};

void configure_spi(int id, uint8_t config_option, uint8_t data){
    switch (config_option){
      case CONF_ACTIVE:
        switch (id){
          case 0: 
            if (spi_active[0] == 1) error_message(OUT_ERROR_INTERFACE_ALREADY_ACTIVE,IN_CONF_SPI0);
            else if (reserve_input_pin(12) && reserve_output_pin(11) && reserve_output_pin(13)){
              SPI.begin();
              spi_active[0] = 1;                    
            }
            break;               
          case 1: 
            if (spi_active[1] == 1) error_message(OUT_ERROR_INTERFACE_ALREADY_ACTIVE,IN_CONF_SPI1);
            else if (reserve_input_pin(1) && reserve_output_pin(26) && reserve_output_pin(27)){
              SPI1.begin();
              spi_active[1] = 1;                    
            }
            break;
          #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)  
          case 2: 
            if (spi_active[2] == 1) error_message(OUT_ERROR_INTERFACE_ALREADY_ACTIVE,IN_CONF_SPI2);
            else if (reserve_input_pin(42) && reserve_output_pin(43) && reserve_output_pin(45)){
              SPI2.begin();
              spi_active[2] = 1;                    
            }
            break;
          #endif
          default:
            error_message(OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS,config_option,id);
            break;
        }
        break;
      default:
        error_message(OUT_ERROR_UNKNOWN_CONFIGURATION,config_option,data);
        break;
    }
}     
         
void send_spi_packet(int id, uint8_t data){
  switch (id){
    case 0:
      if (spi_active[0] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI0); break;}
      SPI.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      send_data8(OUT_SPI0,SPI.transfer(data));
      SPI.endTransaction();
      break;
    case 1:
      if (spi_active[1] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI1); break;}
      SPI1.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      send_data8(OUT_SPI1,SPI1.transfer(data));
      SPI1.endTransaction(); 
      break;
    #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
    case 2:
      if (spi_active[2] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI2); break;}
      SPI2.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      send_data8(OUT_SPI2,SPI2.transfer(data));
      SPI2.endTransaction();  
      break;
    #endif
    default:
      error_message(OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS,IN_SPI0,id);
      break;
  }
}

void send_spi_packet_32bit(int id, uint32_t data){
  switch (id){
    case 0:
      if (spi_active[0] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI0_32); break;}
      SPI.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
      send_data32(OUT_SPI0_32, SPI.transfer32(data));
      #else
      error_message(OUT_ERROR,IN_SPI0_32,data);
      // @TODO implement with transfer16 on first demand
      #endif
      SPI.endTransaction();
      break;
    case 1:
      if (spi_active[1] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI1_32); break;}
      SPI1.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
      send_data32(OUT_SPI1_32, SPI1.transfer32(data));
      #else
      error_message(OUT_ERROR,IN_SPI1_32,data);
      // @TODO implement with transfer16 on first demand
      #endif
      SPI1.endTransaction();  
      break;
    #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
    case 2:
      if (spi_active[2] != 1) { error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,IN_SPI2_32); break;}
      SPI2.beginTransaction(SPISettings(4000000, LSBFIRST, SPI_MODE0));
      send_data32(OUT_SPI2_32, SPI2.transfer32(data));
      SPI2.endTransaction(); 
      break;
    #endif
    default:
      error_message(OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS,IN_SPI0_32,id);
      break;
  }
}
