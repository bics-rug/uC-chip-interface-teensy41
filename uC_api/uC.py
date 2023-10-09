"""
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
"""

import logging
import threading
import serial
from .packet import *
from .header import *
from time import sleep
from .interface_pin import Interface_PIN
from .interface_i2c import Interface_I2C
from .interface_spi import Interface_SPI
from .interface_async import Interface_Async
from queue import Queue

class uC_api:
    def __init__(self, serial_port_path, api_level=2):
        self.experiment_state = []
        self.experiment_state_timestamp = []
        self.__connection = serial.Serial(serial_port_path,115200, timeout= None) #its USB so the speed setting gets ignored and it runes at max speed
        self.__read_buffer = Queue()
        self.__write_buffer_timed = Queue()
        self.__write_buffer = Queue()
        self.__communication_thread = threading.Thread(target=self.__thread_function)
        self.__free_input_queue_spots_on_uc = -1
        self.__last_timed_packet = 0
        self.__api_level = api_level
        if api_level == 2:
            self.errors = []
            self.spi = [Interface_SPI(self,0), Interface_SPI(self,1), Interface_SPI(self,2)]
            self.i2c = [Interface_I2C(self,0), Interface_I2C(self,1), Interface_I2C(self,2)]
            self.pin = []
            for pin_id in range(55):
                self.pin.append(Interface_PIN(self,pin_id))
            self.async_to_chip = []
            for async_id in range(8):
                self.async_to_chip.append(Interface_Async(self,async_id,"TO_CHIP"))
            self.async_from_chip = []
            for async_id in range(8):
                self.async_from_chip.append(Interface_Async(self,async_id,"FROM_CHIP"))
        self.__communication_thread.start()

    def update_state(self):
        while not self.__read_buffer.empty():
            packet_to_process = self.__read_buffer.get()
            if isinstance(packet_to_process, ErrorPacket):
                header_for_sorting = packet_to_process.original_header()
            else:
                header_for_sorting = packet_to_process.header()
            no_match = True
            if header_for_sorting == Data32bitHeader.IN_SET_TIME:
                self.experiment_state.append(packet_to_process.value())
                self.experiment_state_timestamp.append(packet_to_process.time())
                no_match = False
                continue
            
            for interface in self.async_to_chip + self.async_from_chip + self.spi + self.i2c:
                if header_for_sorting in interface.header():
                    interface.process_packet(packet_to_process)
                    self.__read_buffer.task_done()
                    no_match = False
                    break
            if header_for_sorting == self.pin[0].header()[0]:
                    self.pin[packet_to_process.value()].process_packet(packet_to_process)
                    self.__read_buffer.task_done()
                    no_match = False
                    continue
            elif header_for_sorting in self.pin[0].header():
                    self.pin[packet_to_process.pin_id()].process_packet(packet_to_process)
                    self.__read_buffer.task_done()
                    no_match = False
                    continue
            if no_match:
                self.errors.append(str(packet_to_process))
                self.__read_buffer.task_done()

    def start_experiment(self):
        packet_to_send = Data32bitPacket(header=Data32bitHeader.IN_SET_TIME,value=1)
        self.send_packet(packet_to_send)

    def stop_experiment(self, time = 0):
        packet_to_send = Data32bitPacket(header=Data32bitHeader.IN_SET_TIME,value=0,time=time)
        self.send_packet(packet_to_send)

    def send_packet(self, packet_to_send):
        if packet_to_send.header() == Data32bitHeader.IN_SET_TIME:
            self.__last_timed_packet = packet_to_send.value()

        if packet_to_send.time() == 0:
            self.__write_buffer.put(packet_to_send)
        else:
            self.__write_buffer_timed.put(packet_to_send)
            if packet_to_send.time() < self.__last_timed_packet:
                logging.warning("the instructions are not sorted in time - execution order will be inconsistent")

    def read_packet(self):
        if self.__api_level == 1:
            read_packet = self.__read_buffer.get()
            self.__read_buffer.task_done()
            return read_packet
        else:
            logging.error("reading raw packets is only availible in API level 1")

    def has_packet(self):
        if self.__api_level == 1:
            return (self.__read_buffer.empty() == False)
        else:
            logging.error("reading raw packets is only availible in API level 1")

    #def print_all_errors(self):


    def __thread_function(self):
        idle_write_pc = False
        idle_write_uc = 0
        idle_read = False
        while True:
            if not self.__write_buffer_timed.empty() or not self.__write_buffer.empty():
                idle_write_pc = False
                if not self.__write_buffer.empty():
                    data_packet = self.__write_buffer.get()
                    self.__connection.write(data_packet.to_bytearray())
                    logging.debug("send instant: "+str(data_packet))
                    self.__write_buffer.task_done()
                else:
                    if self.__free_input_queue_spots_on_uc > 0 :
                        data_packet = self.__write_buffer_timed.get()
                        self.__free_input_queue_spots_on_uc -= 1
                        self.__connection.write(data_packet.to_bytearray())
                        logging.debug("send timed: "+str(data_packet))
                        self.__write_buffer_timed.task_done()
                    else:
                        idle_write_uc += 1
                        if idle_write_uc%2000 == 1:
                            packet_to_send = Data32bitPacket(Data32bitHeader.IN_FREE_INSTRUCTION_SPOTS)
                            self.__connection.write(packet_to_send.to_bytearray())
                            logging.debug("send timed: "+str(packet_to_send))
            else:
                idle_write_pc = True

            if self.__connection.in_waiting >= 9:
                idle_read = False
                byte_packet = self.__connection.read(size = 9)
                read_packet = Packet.from_bytearray(byte_packet)
                logging.debug("read: "+str(read_packet))
                if read_packet.header() is Data32bitHeader.OUT_FREE_INSTRUCTION_SPOTS:
                    self.__free_input_queue_spots_on_uc = read_packet.value()
                    idle_write_uc = 0
                else:
                    self.__read_buffer.put(read_packet)
            else:
                idle_read = True
            
            if idle_read and (idle_write_pc or idle_write_uc > 0):
                sleep(0.000003)
                idle_read = False
                idle_write_pc = False

            
                    
