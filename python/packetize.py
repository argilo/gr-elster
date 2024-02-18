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
        pkt = bytes(numpy.packbits(bits) ^ 0x55)
        length = pkt[0]
        if length + 2 > len(pkt):
            print("Invalid packet length.")
            return
        pkt = pkt[0:length+2]
        if self.crc_x25(pkt[0:length]) != pkt[length:length+2]:
            print("Invalid checksum.")
            return

        caplen = len(pkt)-2
        wirelen = caplen
        now = time.time()
        sec = int(now)
        usec = int(round((now-sec)*1000000))
        self.file.write(struct.pack("IIII", sec, usec, caplen, wirelen))
        self.file.write(pkt[0:-2])
        self.file.flush()

        len1, flag1, src, dst = struct.unpack(">BBII", pkt[0:10])
        time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")
        print(f"{time_str} {channel:02}  {len1:02x} {flag1:02x} {src:08x} {dst:08x} {pkt[10:13].hex()} {pkt[13:16].hex()} {pkt[16:-2].hex()} {pkt[-2:].hex()}")

        if src & 0x80000000 == 0 and len(pkt) > 16:
            len4 = pkt[16]
            if len4 == len1 - 17:  # 1st byte of payload is a length
                if len(pkt) > 18:
                    cmd = pkt[18]
                    if cmd == 0xce and len(pkt) >= 64:  # hourly usage data, every 6 hours
                        print()

                        main_reading = pkt[61:64].hex()
                        print(f"  Meter reading for meter #{src}: {main_reading} kWh")

                        n_hours = pkt[26]
                        if n_hours > 17:
                            print(f"  Number of hourly readings is too high: {n_hours}")
                            n_hours = 17
                        hourly_readings = [reading / 100 for reading in struct.unpack(">" + "H"*n_hours, pkt[27:27 + 2*n_hours])]
                        readings_str = ", ".join(f"{reading:.2f}" for reading in hourly_readings)
                        print(f"  Hourly readings: {readings_str}")

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
