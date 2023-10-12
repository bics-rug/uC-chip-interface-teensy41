/*
    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
    Copyright (C) 2023 Ole Richter - University of Groningen

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

/*
This is a limited reimplmentaion of the teensy IntervalTimer API for the SAMD21 processors
on the teensy the build in function is used

the porting was needed as no libraries with usec could be found (by limited serching) for the SAMD21 uCs
it can only handle 2 timers, but could be extended to TC3 and so on
it can only handle periods up to 21844 usec (can be easily extended on demand)
it is hardcoded to a CPU ferquency of 48MHz (could be made flexible on demand)
it uses TC4 and TC5 for interrupts
*/

#if defined(ARDUINO_ARCH_SAMD)
// hardcoded to 48MHz should check via F_CPU flag
#ifndef INTERVALTIMER_H
#define INTERVALTIMER_H
#define INTERVALTIMER_MAX_TIMERS 2
#include <Arduino.h>

typedef void (*callfunction_t) ();

class IntervalTimer {
    public:
        IntervalTimer() {
            counter_id = INTERVALTIMER_MAX_TIMERS;
            last_period = 100U;
            last_priority = 3U;
        }
        ~IntervalTimer() {end();}
        
        bool begin(callfunction_t callback, uint32_t usec) volatile;
        void update(uint32_t usec) volatile;
        void end() volatile;
        void priority(uint8_t priority) volatile;
        static callfunction_t _TC5_callfunc;
        static callfunction_t _TC4_callfunc;

    private:
        //static TcCount16* TC[INTERVALTIMER_MAX_TIMERS];
        static bool counter_active[INTERVALTIMER_MAX_TIMERS];
        uint8_t counter_id;
        uint32_t last_period;
        uint8_t last_priority;
        bool init_ran;

};
/* 
Interrupt Service Routine for TC4
for use by class
*/
extern void TC4_Handler();
/* 
Interrupt Service Routine for TC5
for use by class
*/
extern void TC5_Handler();

#endif
#endif