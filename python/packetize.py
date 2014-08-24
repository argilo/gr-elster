#!/usr/bin/env python
# 
# Copyright 2013-2014 Clayton Smith.
# 
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
# 
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this software; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.
# 

import numpy
import datetime
from gnuradio import gr

class packetize(gr.basic_block):
    # The preamble (32 ones) and SFD (0000 1100 1011 1101) in Manchester form
    preamble_sfd = numpy.array([1,0]*32 + [0,1, 0,1, 0,1, 0,1, 1,0, 1,0, 0,1, 0,1, 1,0, 0,1, 1,0, 1,0, 1,0, 1,0, 0,1, 1,0],dtype=numpy.int8).tostring()

    """
    docstring for block packetize
    """
    def __init__(self, num_inputs):
        gr.basic_block.__init__(self,
            name="packetize",
            in_sig=[numpy.int8]*num_inputs,
            out_sig=[])

    def crc_x25(self, message):
        poly = 0x8408
        reg = 0xffff
        for byte in message:
            mask = 0x01
            while mask < 0x100:
                lowbit = reg & 1
                reg >>= 1
                if ord(byte) & mask:
                    lowbit ^= 1
                mask <<= 1
                if lowbit:
                    reg ^= poly
        reg ^= 0xffff
        return chr(reg & 0xff) + chr(reg >> 8)

    def process_packet(self, channel, bits):
        bytes = numpy.packbits(bits) ^ 0x55
        length = bytes[0]
        if length + 2 > len(bytes):
            print "Invalid packet length."
            return
        bytes = bytes[0:length+2]
        if self.crc_x25(bytes[0:length].tostring()) != bytes[length:length+2].tostring():
            print "Invalid checksum."
            return
        bytestring = ''.join(["0x{:02x}".format(int(byte))[2:4] for byte in bytes])
        bytestring = bytestring[0:2] + ' ' + bytestring[2:4] + ' ' + bytestring[4:12] + ' ' + bytestring[12:20] + ' ' + bytestring[20:28] + ' ' + bytestring[28:-4] + ' ' + bytestring[-4:]
        print(datetime.datetime.now().strftime("%H:%M:%S.%f") + '  ' + bytestring)
        if length == 0x44:
            # This packet probably contains meter readings!
            print
            meter_number = int(bytestring[6:14], 16)
            try:
                main_reading = int(bytestring[127:133])
            except ValueError:
                print "  Error decoding main reading: " + bytestring[127:133]
                main_reading = 0
            num_hourly = int(bytestring[57:59], 16)
            if num_hourly > 17:
                print "  Number of hourly readings is too high: " + hex(num_hourly)
                num_hourly = 17
            hourly_readings = []
            for x in range(num_hourly):
                hourly_readings.append(int(bytestring[59 + x*4 : 63 + x*4], 16) / 100.0)
            print "  Meter reading for meter #" + str(meter_number) + ": " + str(main_reading) + " kWh"
            print "  Hourly readings: " + str(hourly_readings)[1:-1]
            print

    def manchester_demod_packet(self, channel, man_bits):
        for x in range(0, len(man_bits), 2):
            if man_bits[x] == man_bits[x+1]:
                # Manchester error. Discard packet.
                break
        else:
            # We've got a valid packet! Throw out the preamble and SFD
            # and extract the bits from the Manchester encoding.
            self.process_packet(channel, man_bits[96::2])

    def forecast(self, noutput_items, ninput_items_required):
        for channel in range(len(ninput_items_required)):
            ninput_items_required[channel] = 5000

    def general_work(self, input_items, output_items):
        # Wait until we get at least one packet worth of Manchester bits
        if len(input_items[0]) < 1248:
            self.consume(0, 0)
            return 0

        for channel in range(len(input_items)):
            index = input_items[channel].tostring().find(self.preamble_sfd, 0, -1248+96)
            while index != -1:
                self.manchester_demod_packet(channel, input_items[channel][index:index+1248])
                index = input_items[channel].tostring().find(self.preamble_sfd, index+1248, -1248+96)
            self.consume(channel, len(input_items[0])-1247)

        return 0
