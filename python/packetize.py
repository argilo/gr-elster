#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2013, 2014, 2019 Clayton Smith.
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

import datetime
import os.path
import struct
import time
import numpy
from gnuradio import gr


class packetize(gr.basic_block):
    # The preamble (32 ones) and SFD (0000 1100 1011 1101) in Manchester form
    preamble_sfd = numpy.array([1, 0]*32 + [0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0], dtype=numpy.int8).tostring()

    """
    docstring for block packetize
    """
    def __init__(self, num_inputs):
        gr.basic_block.__init__(self,
                                name="packetize",
                                in_sig=[numpy.int8]*num_inputs,
                                out_sig=None)

        i = 1
        filename = f"elster-{i:03}.pcap"
        while os.path.exists(filename):
            i += 1
            filename = f"elster-{i:03}.pcap"
        self.file = open(filename, "wb")
        self.linktype = 147
        self.file.write(struct.pack("IHHIIII", 0xa1b2c3d4, 2, 4, 0, 0, 32767, self.linktype))
        self.file.flush()

    def __del__(self):
        self.file.close()

    def crc_x25(self, message):
        poly = 0x8408
        reg = 0xffff
        for byte in message:
            mask = 0x01
            while mask < 0x100:
                lowbit = reg & 1
                reg >>= 1
                if byte & mask:
                    lowbit ^= 1
                mask <<= 1
                if lowbit:
                    reg ^= poly
        reg ^= 0xffff
        return bytes([reg & 0xff, reg >> 8])

    def process_packet(self, channel, bits):
        packet = bytes(numpy.packbits(bits) ^ 0x55)
        length = packet[0]
        if length + 2 > len(packet):
            print("Invalid packet length.")
            return
        packet = packet[0:length+2]
        if self.crc_x25(packet[0:length]) != packet[length:length+2]:
            print("Invalid checksum.")
            return

        caplen = len(packet)-2
        wirelen = caplen
        now = time.time()
        sec = int(now)
        usec = int(round((now-sec)*1000000))
        self.file.write(struct.pack("IIII", sec, usec, caplen, wirelen))
        self.file.write(packet[0:-2])
        self.file.flush()

        bytestring = packet.hex()
        bytestring = bytestring[0:2] + ' ' + bytestring[2:4] + ' ' + bytestring[4:12] + ' ' + bytestring[12:20] + ' ' + bytestring[20:26] + ' ' + bytestring[26:32] + ' ' + bytestring[32:-4] + ' ' + bytestring[-4:]
        print(datetime.datetime.now().strftime("%H:%M:%S.%f") + ' ' + "{:02}".format(channel) + '  ' + bytestring)
        if length == 0x44:
            # This packet probably contains meter readings!
            print()
            meter_number = int(bytestring[6:14], 16)
            try:
                main_reading = int(bytestring[128:134])
            except ValueError:
                print("  Error decoding main reading: " + bytestring[128:134])
                main_reading = 0
            num_hourly = int(bytestring[58:60], 16)
            if num_hourly > 17:
                print("  Number of hourly readings is too high: " + hex(num_hourly))
                num_hourly = 17
            hourly_readings = []
            for reading in range(num_hourly):
                hourly_readings.append(int(bytestring[60 + reading*4:64 + reading*4], 16) / 100)
            print("  Meter reading for meter #" + str(meter_number) + ": " + str(main_reading) + " kWh")
            print("  Hourly readings: " + str(hourly_readings)[1:-1])
            print()

    def manchester_demod_packet(self, channel, man_bits):
        for offset in range(0, len(man_bits), 2):
            if man_bits[offset] == man_bits[offset+1]:
                # Manchester error. Discard packet.
                break
        else:
            # We've got a valid packet! Throw out the preamble and SFD
            # and extract the bits from the Manchester encoding.
            self.process_packet(channel, man_bits[96::2])

    def forecast(self, noutput_items, ninputs):
        return [2496] * ninputs

    def general_work(self, input_items, output_items):
        # Wait until we get at least one packet worth of Manchester bits
        if len(input_items[0]) < 1248:
            return 0

        for channel, bits in enumerate(input_items):
            bits_string = bits.tostring()
            index = bits_string.find(self.preamble_sfd, 0, -1248+96)
            while index != -1:
                self.manchester_demod_packet(channel, bits[index:index+1248])
                index = bits_string.find(self.preamble_sfd, index+1248, -1248+96)
            self.consume(channel, len(bits)-1247)

        return 0
