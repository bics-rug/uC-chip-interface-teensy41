
#    This file is part of the Firmware project to interface with small Async or Neuromorphic chips
#    Copyright (C) 2023 Ole Richter - University of Groningen
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.


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
    """ 
    the class uC_api exposes the full interface to the uC as an object, 
    all the interface like i2c, spi, pin and async can be found as exposed variables

    Interfaces need to be activated before use, and the activation is ackloaged by the uC
    you might need to time.sleep(0.01) after the activation for the python object to update register the state change

    if you want to record data you need to use function start_experiment() to be abel to see the data send back
    the maximum time of each experiment is 72min, please call stop experiment before that to start agian

    after you are done call close_connection to sever the serial connection to the uC, 
    the recorded data in the python object remains and can be processed after
    """
    def __init__(self, serial_port_path, api_level=2):
        """__init__ creates the uC interface object and establishes the connection to the uC on the given port

        :param serial_port_path: the path of your system to the serial port, eg. on linux it might be /dev/ttyAMC0 or higher, on mac /dev/tty.usbmodem<XXXXX> on windows <COM port>
        :type serial_port_path: string 
        :param api_level: level 1 is that the api only espablishes the connection to the uC and the "infinite" write and read buffers, you need to construct the instruction packages your self, 
        level 2 it wraps the full representation of the uC interfaces in objects that are made availible as variables on this object, defaults to 2
        :type api_level: int, optional
        """
        self.__experiment_state = []
        self.__experiment_state_timestamp = []
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
        # wait for 10 seconds for the uC to align
        connection = False
        for i in range(40):
            sleep(0.25)
            if self.__read_buffer.empty() == False:
                read_packet = self.__read_buffer.get()
                self.__read_buffer.task_done()
                if read_packet.header() == DataI2CHeader.OUT_ALIGN_SUCCESS_VERSION:
                    logging.warning("uC is ready - firmware version: "+str(read_packet.device_address())+"."+str(read_packet.register_address())+"."+str(read_packet.value()))
                    connection = True
                    break
                else:
                    logging.warning("unknown packet received, while connecting to uC for the first time: "+str(read_packet))
        if connection == False:
            logging.error("uC is not responding, wrong port?")
            self.close_connection()

    def update_state(self):
        """update_state This method processes all availible messages from the uC and updates the internal representaion
        in detail it distributes the recorded packages to the coresponding interfaces for processing.

        level 2 only
        """
        while not self.__read_buffer.empty():
            packet_to_process = self.__read_buffer.get()
            if isinstance(packet_to_process, ErrorPacket):
                header_for_sorting = packet_to_process.original_header()
            else:
                header_for_sorting = packet_to_process.header()
            no_match = True
            if header_for_sorting == Data32bitHeader.IN_SET_TIME:
                self.__experiment_state.append(packet_to_process.value())
                self.__experiment_state_timestamp.append(packet_to_process.time())
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
        """start_experiment This will reset the uC clock, enable that data is collected and that timed instructions are executed by the uC
        latest after 72min stop_experiment has to be called, after which a new experiment can be programmed and the function can be called again.
        """
        packet_to_send = Data32bitPacket(header=Data32bitHeader.IN_SET_TIME,value=1)
        self.send_packet(packet_to_send)

    def stop_experiment(self, time = 0):
        """stop_experiment this will stop recording and flush all not jet excecuted timed instructions

        :param time: the time in us after start_experiment when this function should be called, defaults to 0 (execute instantly)
        :type time: int, optional
        """
        packet_to_send = Data32bitPacket(header=Data32bitHeader.IN_SET_TIME,value=0,time=time)
        self.send_packet(packet_to_send)

    def experiment_state(self):
        """experiment_state returns the state history

        1 or larger: experiment is running
        0 experiment stopped
        -1 uC reset

        :return: 2 lists: first the state second the uC timesteps in us of the state change
        :rtype: ([int],[int])
        """
        return (self.__experiment_state, self.__experiment_state_timestamp)

    def send_packet(self, packet_to_send):
        """send_packet send a packet to the uC via the "infinite" buffer
        needs a package object see package.py

        :param packet_to_send: the package to be send
        :type packet_to_send: Packet, or any subclass
        """
        if packet_to_send.header() == Data32bitHeader.IN_SET_TIME:
            self.__last_timed_packet = packet_to_send.value()

        if packet_to_send.time() == 0:
            self.__write_buffer.put(packet_to_send)
        else:
            self.__write_buffer_timed.put(packet_to_send)
            if packet_to_send.time() < self.__last_timed_packet:
                logging.warning("the instructions are not sorted in time - execution order will be inconsistent")

    def read_packet(self):
        """read_packet returns one package from the uC via the "infinte" buffer

        if there is no packet availible it blocks and waits until a packet becomes availible

        :return: one package from the uC
        :rtype: Packet, or any subclass
        """
        if self.__api_level == 1:
            read_packet = self.__read_buffer.get()
            self.__read_buffer.task_done()
            return read_packet
        else:
            logging.error("reading raw packets is only availible in API level 1")

    def has_packet(self):
        """has_packet checks if a packet is availible for reading from the buffer

        :return: true if packet is avilible, false if not
        :rtype: boolean
        """
        if self.__api_level == 1:
            return (self.__read_buffer.empty() == False)
        else:
            logging.error("reading raw packets is only availible in API level 1")

    #def print_all_errors(self):

    def close_connection(self):
        """close_connection closes the serial connection to the uC and blocks until this is done
        resets the uC too
        """
        self.__write_buffer.put(Data32bitPacket(Data32bitHeader.UC_CLOSE_CONNECTION))
        self.__experiment_state.append(-1)
        self.__experiment_state_timestamp.append(-1)
        self.__communication_thread.join()

    def reset(self):
        """reset uC and hope the serial connection survives
        """
        self.__write_buffer.put(Data32bitPacket(Data32bitHeader.IN_RESET))
        self.__experiment_state.append(-1)
        self.__experiment_state_timestamp.append(-1)


    def __thread_function(self):
        """__thread_function internal function managing the actual async communication with the uC in the background
        """
        idle_write_pc = False
        idle_write_uc = 0
        idle_read = False
        # init communication by forcing the uC to align
        logging.info("send: aligning commuication")
        self.__connection.write(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff')
        # start communication
        while True:
            if not self.__write_buffer_timed.empty() or not self.__write_buffer.empty():
                idle_write_pc = False
                if not self.__write_buffer.empty():
                    data_packet = self.__write_buffer.get()
                    if data_packet.header() == Data32bitHeader.UC_CLOSE_CONNECTION:
                        self.__connection.write(Data32bitPacket(Data32bitHeader.IN_RESET).to_bytearray())
                        self.__connection.close()
                        return
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
                # do reading alingnment
                byte_packet = byte_packet.lstrip(b'\xff')
                if len(byte_packet) < 9:
                    if len(byte_packet) != 0:
                        logging.warning("outgoing uC alignment needed, shifted by "+str(len(byte_packet))+ " bytes")
                        # partial packet
                        if self.__connection.in_waiting < 9-len(byte_packet):
                            logging.error("partial packet received, but not enough bytes send by uC, trying to recover by realigning")
                            self.__connection.write(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff')
                            continue
                        byte_packet = bytearray(byte_packet).append(self.__connection.read(size = 9-len(byte_packet)))
                        
                    else:
                        logging.debug("alignment triggered shifted by "+str(len(byte_packet))+ " bytes")
                        # no packet, jump to next iteration
                        continue
                # is now aligned
                try:
                    read_packet = Packet.from_bytearray(byte_packet)
                except:
                    logging.error("packet is malformed, maybe misaligned, trying to recover by realigning")
                    self.__connection.write(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff')
                    continue
                logging.debug("read: "+str(read_packet))
                if read_packet.header() is Data32bitHeader.OUT_FREE_INSTRUCTION_SPOTS:
                    self.__free_input_queue_spots_on_uc = read_packet.value()
                    idle_write_uc = 0
                elif read_packet.header() is ErrorHeader.OUT_ERROR_UNKNOWN_INSTRUCTION or read_packet.header() is ErrorHeader.OUT_ERROR_UNKNOWN_CONFIGURATION:
                    logging.error("uC is reporting that it cant understand a send packet, either API and firmware are a different version or communication is not aligned, trying to recover by realigning")
                    self.__connection.write(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff')
                else:
                    self.__read_buffer.put(read_packet)
            else:
                idle_read = True
            
            if idle_read and (idle_write_pc or idle_write_uc > 0):
                sleep(0.000003)
                idle_read = False
                idle_write_pc = False

            
                    
