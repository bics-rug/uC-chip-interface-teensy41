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
#include <Arduino.h>
#include "AER_from_chip.h"
#include <Wire.h>



// reserve and clear the memory of the static global variables.
// see header for description
volatile uint8_t AER_from_chip::data_pins[8][32] = {};
volatile uint8_t AER_from_chip::data_width[8] = {};
volatile uint8_t AER_from_chip::req_pin[8] = {};
volatile uint8_t AER_from_chip::ack_pin[8] = {};
volatile uint8_t AER_from_chip::req_delay[8] = {};
volatile bool AER_from_chip::hs_lowactive[8] = {};
volatile bool AER_from_chip::data_lowactive[8] = {};
volatile bool AER_from_chip::active[8] = {};
volatile AER_from_chip* AER_from_chip::inst[8] = {};
volatile uint8_t  count_shift = 0;
const uint8_t GPIOA = 18U;
const uint8_t MCP0 = 32U;
const uint8_t MCP1 = 33U;


// handles incomming configuraion packets
void AER_from_chip::configure(uint8_t id, uint8_t config, uint8_t data){
  // check if the ID is valid otherwise throw error
  if (id >= 8) {
    if (is_output_buffer_not_full()){
      output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_UNKNOWN_CONFIGURATION;
      output_ring_buffer[output_ring_buffer_next_free].error.org_header = CONF_ACTIVE;
      output_ring_buffer[output_ring_buffer_next_free].error.value = id;
      output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
    }
    return;
  }
  // handle the different config sub headers
  switch (config){
    // activate the interface and reserve the pins
    case CONF_ACTIVE:
      AER_from_chip::inst[id] = new AER_from_chip(id,
                                          AER_from_chip::req_pin[id],
                                          AER_from_chip::ack_pin[id],
                                          AER_from_chip::data_pins[id],
                                          AER_from_chip::data_width[id],
                                          AER_from_chip::req_delay[id],
                                          AER_from_chip::hs_lowactive[id],
                                          AER_from_chip::data_lowactive[id]);
      break;
    // configure the location of the request pin
    case CONF_REQ:
      AER_from_chip::req_pin[id] = data;
      break;
    // configure the location of the ack pin
    case CONF_ACK:
      AER_from_chip::ack_pin[id] = data;
      break;
    // configure how many data channels are used in the AER interface
    case CONF_WIDTH:
      // throw error if interface is to wide
      if (data > 32) {
        if (is_output_buffer_not_full()){
          output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_UNKNOWN_CONFIGURATION;
          output_ring_buffer[output_ring_buffer_next_free].error.org_header = config;
          output_ring_buffer[output_ring_buffer_next_free].error.value = id;
          output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
        }
        AER_from_chip::data_width[id] = 32;
      }
      else AER_from_chip::data_width[id] = data;
      break;
    // configure the delay on the req line
    case CONF_REQ_DELAY:
      AER_from_chip::req_delay[id] = data;
      break;
    // conf if handshake signals are active low or not
    case CONF_HS_ACTIVE_LOW:
      AER_from_chip::hs_lowactive[id] = data;
      break;
    // configure if data channels are active low or not
    case CONF_DATA_ACTIVE_LOW:
      AER_from_chip::data_lowactive[id] = data;
      break;
    // configure the pin locations of the data channels
    default:
      if (config < 32){
        AER_from_chip::data_pins[id][config] = data;
      }
      // throw and error if the config header is not implemented
      else if (is_output_buffer_not_full()){
        output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_UNKNOWN_CONFIGURATION;
        output_ring_buffer[output_ring_buffer_next_free].error.org_header = config;
        output_ring_buffer[output_ring_buffer_next_free].error.value = id;
        output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
      }
  }
}


//---------------------------------------------------------------------------------------------------------------------------------------
// AER_from_chip constructor
//---------------------------------------------------------------------------------------------------------------------------------------

AER_from_chip::AER_from_chip(uint8_t id, uint8_t reqPin, uint8_t ackPin, uint8_t dataPins[], uint8_t numDataPins, uint8_t delay, bool handshakeActiveLow, bool dataActiveLow) {
  _reqPin = reqPin;
  _ackPin = ackPin;
  _dataPins = dataPins;
  _numDataPins = numDataPins;
  _delay = delay;
  _handshakeActiveLow = handshakeActiveLow;
  _dataActiveLow = dataActiveLow;
  _id = id;

  if (setupPins()){ 
    switch(_id){
      case 0: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer0_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 1: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer1_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 2: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer2_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 3: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer3_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 4: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer4_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 5: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer5_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 6: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer6_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      case 7: 
        attachInterrupt(digitalPinToInterrupt(reqPin), aer7_ISR, CHANGE); 
        AER_from_chip::active[id] = true;
        break;
      default:
        if (is_output_buffer_not_full()){
          output_ring_buffer[output_ring_buffer_next_free].error.header = OUT_ERROR_UNKNOWN_CONFIGURATION;
          output_ring_buffer[output_ring_buffer_next_free].error.org_header = CONF_ACTIVE;
          output_ring_buffer[output_ring_buffer_next_free].error.value = id;
          output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;          
        }
    }
  } 
}



//---------------------------------------------------------------------------------------------------------------------------------------
// reqRead: Reads REQ pin state
//---------------------------------------------------------------------------------------------------------------------------------------

bool AER_from_chip::reqRead() {
  return digitalReadFast(_reqPin)^_handshakeActiveLow;
}


//---------------------------------------------------------------------------------------------------------------------------------------
// ackWrite: Writes to ACK pin
//---------------------------------------------------------------------------------------------------------------------------------------

void AER_from_chip::ackWrite(bool val) {
  digitalWriteFast(_ackPin, val^_handshakeActiveLow);
}


//----------------------------------------------------------------------------------------------------------------------------------
// recordEvent: Records output events as they occur
//----------------------------------------------------------------------------------------------------------------------------------
void AER_from_chip::recordEvent() {
  noInterrupts();
  if (is_output_buffer_not_full() && offset_time != 0) {
    switch(_id){
      case 0: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP0; break;
      case 1: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP1; break;
      case 2: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP2; break;
      case 3: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP3; break;
      case 4: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP4; break;
      case 5: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP5; break;
      case 6: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP6; break;
      case 7: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_AER_FROM_CHIP7; break;
      default: output_ring_buffer[output_ring_buffer_next_free].data.header = OUT_ERROR; break;
    }    
    output_ring_buffer[output_ring_buffer_next_free].data.exec_time = micros()-offset_time;
    output_ring_buffer[output_ring_buffer_next_free].data.value = this->getData(); 
    output_ring_buffer_next_free = (output_ring_buffer_next_free + 1) % OUTPUT_BUFFER_SIZE;
  }
  interrupts();
}

//----------------------------------------------------------------------------------------------------------------------------------
// handshake: Executes REQ/ACK handshake between Teensy and ALIVE
//----------------------------------------------------------------------------------------------------------------------------------
void AER_from_chip::handshake() {
  if(_handshakeActiveLow) {
    if (!reqRead()) {
      ackWrite(0); //@TODO replace with direct pin access
    }
    else if (reqRead()) {
      ackWrite(1); //@TODO replace with direct pin access
    }

  }

  else if(!_handshakeActiveLow) {
    if (!reqRead()) {
      ackWrite(0); //@TODO replace with direct pin access
    }

    else if (reqRead()) {
      ackWrite(1); //@TODO replace with direct pin access
    }
  }
}


//----------------------------------------------------------------------------------------------------------------------------------
// setupPins: Sets up the relevant pins for communication
//----------------------------------------------------------------------------------------------------------------------------------

bool AER_from_chip::setupPins() {
if (reserve_input_pin(_reqPin)) pinMode(_reqPin, INPUT);
else return false;
if (reserve_output_pin(_ackPin)) pinMode(_ackPin, OUTPUT);
else return false;
Wire.begin();
Wire.setClock(400000);
// if (!reserve_input_pin(18) || !reserve_input_pin(19)) return false;
// Wire.beginTransmission(MCP0);
// Wire.write(GPIOA);
// uint8_t outcome;
// data = Wire.endTransmission();
// if (outcome == 0){
//   pinMode(13,OUTPUT);
//   digitalWrite(13,HIGH);
// }
return true;

}


//---------------------------------------------------------------------------------------------------------------------------------------
// getData: Retrieves event
//---------------------------------------------------------------------------------------------------------------------------------------

uint32_t AER_from_chip::getData() {
  uint32_t data = 0;
  uint8_t count_shift = 0;
  if (_delay) {
    delay20ns(_delay);
  }
  
  Wire.beginTransmission(MCP0);
  Wire.write(GPIOA);
  Wire.endTransmission();
  Wire.requestFrom(MCP0,2,true);
  while (Wire.available()>0){
    data |= Wire.read()<<8*count_shift;
    count_shift++;
  }
  Wire.beginTransmission(MCP1);
  Wire.write(GPIOA);
  Wire.endTransmission(false);
  Wire.requestFrom(MCP1,(uint8_t) 2,true);
  while (Wire.available()>0){
    data |= Wire.read()<<8*count_shift;
    count_shift++;
  }
  if (_dataActiveLow) {
    return ~data;
  }
  else {
    return data;
  }
}
