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
#include "AER_to_chip.h"

volatile uint8_t AER_to_chip::data_pins[8][32] = {};
volatile uint8_t AER_to_chip::data_width[8] = {};
volatile uint8_t AER_to_chip::req_pin[8] = {};
volatile uint8_t AER_to_chip::ack_pin[8] = {};
volatile uint8_t AER_to_chip::req_delay[8] = {};
volatile bool AER_to_chip::hs_lowactive[8] = {};
volatile bool AER_to_chip::data_lowactive[8] = {};
volatile bool AER_to_chip::active[8] = {};
volatile AER_to_chip* AER_to_chip::inst[8] = {};

void AER_to_chip::configure(uint8_t id, uint8_t config, uint8_t data){
  if (id >= 8) {
    error_message(OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS,CONF_ACTIVE,id);
    return;
  }  

    
  switch (config){
    case CONF_ACTIVE:
      AER_to_chip::inst[id] = new AER_to_chip(id,
                                          AER_to_chip::req_pin[id],
                                          AER_to_chip::ack_pin[id],
                                          AER_to_chip::data_pins[id],
                                          AER_to_chip::data_width[id],
                                          AER_to_chip::req_delay[id],
                                          AER_to_chip::hs_lowactive[id]);
      break;
    case CONF_REQ:
      AER_to_chip::req_pin[id] = data;
      break;
    case CONF_ACK:
      AER_to_chip::ack_pin[id] = data;
      break;
    case CONF_WIDTH:
      if (data > 32) {
        error_message(OUT_ERROR_CONFIGURATION_OUT_OF_BOUNDS,config,id);
        AER_to_chip::data_width[id] = 32;
      }
      else AER_to_chip::data_width[id] = data;
      break;
    case CONF_REQ_DELAY:
      AER_to_chip::req_delay[id] = data;
      break;
    case CONF_HS_ACTIVE_LOW:
      AER_to_chip::hs_lowactive[id] = data;
      break;
    case CONF_DATA_ACTIVE_LOW:
      AER_to_chip::data_lowactive[id] = data;
      break;
    default:
      if (config < 32){
        AER_to_chip::data_pins[id][config] = data;
      }
      else error_message(OUT_ERROR_UNKNOWN_CONFIGURATION,config,id);
  }
}

void AER_to_chip::send_aer_packet(uint8_t id, uint32_t data){
  if (AER_to_chip::active[id]){
    AER_to_chip::inst[id]->dataWrite(data);
  }
  else {
    uint8_t interface;
    switch(id){
      case 0: interface = IN_AER_TO_CHIP0; break;
      case 1: interface = IN_AER_TO_CHIP1; break;
      case 2: interface = IN_AER_TO_CHIP2; break;
      case 3: interface = IN_AER_TO_CHIP3; break;
      case 4: interface = IN_AER_TO_CHIP4; break;
      case 5: interface = IN_AER_TO_CHIP5; break;
      case 6: interface = IN_AER_TO_CHIP6; break;
      case 7: interface = IN_AER_TO_CHIP7; break;
      default:interface = OUT_ERROR; break;
    }
    error_message(OUT_ERROR_INTERFACE_NOT_ACTIVE,interface,data);          
  }
}



//---------------------------------------------------------------------------------------------------------------------------------------
// Class constructor; initialises the AER_to_chip object and sets up the relevant pins on Teensy
//---------------------------------------------------------------------------------------------------------------------------------------

AER_to_chip::AER_to_chip(uint8_t id, uint8_t reqPin, uint8_t ackPin, volatile uint8_t dataPins[], uint8_t numDataPins, uint8_t delay, bool activeLow)
{
  _reqPin = reqPin;
  _ackPin = ackPin;
  _dataPins = dataPins;
  _numDataPins = numDataPins;
  _delay = delay;
  _activeLow = activeLow;
  _id = id;

  AER_to_chip::active[id] = setupPins();
}

//---------------------------------------------------------------------------------------------------------------------------------------
// dataWrite: Executes REQ/ACK handshake and writes  to chip
//---------------------------------------------------------------------------------------------------------------------------------------

bool AER_to_chip::dataWrite(uint32_t data) volatile 
{
  unsigned long t0 = millis();
  bool handshakeStatus = true;

  setData(data);
  reqWrite(1);

  while(!ackRead()) {
    if (millis() > t0 + AER_HANDSHAKE_TIMEOUT) {
      handshakeStatus = false;
      uint8_t interface;
      switch(_id){
        case 0: interface = IN_AER_TO_CHIP0; break;
        case 1: interface = IN_AER_TO_CHIP1; break;
        case 2: interface = IN_AER_TO_CHIP2; break;
        case 3: interface = IN_AER_TO_CHIP3; break;
        case 4: interface = IN_AER_TO_CHIP4; break;
        case 5: interface = IN_AER_TO_CHIP5; break;
        case 6: interface = IN_AER_TO_CHIP6; break;
        case 7: interface = IN_AER_TO_CHIP7; break;
        default:interface = OUT_ERROR; break;
      }
      error_message(OUT_ERROR_AER_HS_TIMEOUT,interface);    
      break;
    }
  }

  reqWrite(0);

  return handshakeStatus;
}

//---------------------------------------------------------------------------------------------------------------------------------------
// setupPins: Sets up the relevant pins for communication
//---------------------------------------------------------------------------------------------------------------------------------------

bool AER_to_chip::setupPins() {
  if (reserve_input_pin(_ackPin)) pinMode(_ackPin, INPUT);
  else return false;
  if (reserve_output_pin(_reqPin)) pinMode(_reqPin, OUTPUT);
  else return false;

  for(int i = 0; i < _numDataPins; i++) {
    if (reserve_output_pin(_dataPins[i])) pinMode(_dataPins[i], OUTPUT);
    else return false;
  }
  return true;
}


//---------------------------------------------------------------------------------------------------------------------------------------
// ackRead: Reads ACK pin state
//---------------------------------------------------------------------------------------------------------------------------------------

bool AER_to_chip::ackRead() 
{
  #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
  return digitalReadFast(_ackPin)^_activeLow;
  #else
  return digitalRead(_ackPin)^_activeLow;
  #endif
}


//---------------------------------------------------------------------------------------------------------------------------------------
// reqWrite: Writes to REQ pin
//---------------------------------------------------------------------------------------------------------------------------------------

void AER_to_chip::reqWrite(bool val) 
{
  if (_delay) 
  {
    delay20ns(_delay);
  }
  #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
  digitalWriteFast(_reqPin, val^_activeLow); 
  #else
  digitalWrite(_reqPin, val^_activeLow);
  #endif
  
}


//---------------------------------------------------------------------------------------------------------------------------------------
// setData: Write data to  pins
//---------------------------------------------------------------------------------------------------------------------------------------

void AER_to_chip::setData(uint32_t data) {
  for (int i=0; i<_numDataPins; i++) {
    bool bit = bitRead(data, i)^_activeLow;
    #if defined(ARDUINO_TEENSY41) || defined(ARDUINO_TEENSY40)
    digitalWriteFast(_dataPins[i], bit);
    #else
    digitalWrite(_dataPins[i], bit);
    #endif
    
  }
}
