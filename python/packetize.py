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
    preamble = numpy.repeat(numpy.array([1, 0]*16, dtype=numpy.uint8), 4).tobytes()
    sfd_1 = numpy.repeat(numpy.array([0, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0], dtype=numpy.uint8), 4).tobytes()
    sfd_2 = numpy.repeat(numpy.array([1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0], dtype=numpy.uint8), 4).tobytes()
    manchester = [int(f"{b:08b}"[:4].count("1") > f"{b:08b}"[4:].count("1")) for b in range(256)]

    def __init__(self, num_inputs):
        gr.basic_block.__init__(self,
                                name="packetize",
                                in_sig=[numpy.uint8]*num_inputs,
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

        self.packet_bits = [numpy.array([], dtype=numpy.uint8) for _ in range(num_inputs)]
        self.packet_type = [0] * num_inputs
        self.bits_remaining = [0] * num_inputs

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

    def process_packet(self, channel, pkt):
        if pkt[0] >= 2:
            len_bytes = 1
            length = pkt[0]
        else:
            len_bytes = 2
            length = (pkt[0] << 8) | pkt[1]

        if length + 2 != len(pkt):
            print("Invalid packet length.")
            return
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

        payload = pkt[len_bytes:-2]
        flag1, src, dst = struct.unpack(">BII", payload[0:9])
        time_str = datetime.datetime.now().strftime("%H:%M:%S.%f")
        print(f"{time_str} {channel:02}  {pkt[0:len_bytes].hex()} {flag1:02x} {src:08x} {dst:08x} {payload[9:12].hex()} {payload[12:15].hex()} {payload[15:].hex()} {pkt[-2:].hex()}")

        if src & 0x80000000 == 0 and len(pkt) > 16:
            len4 = payload[15]
            if len4 == length - 17:  # 1st byte of payload is a length
                if len(pkt) > 18:
                    cmd = payload[17]
                    if cmd == 0xce and len(pkt) >= 64:  # hourly usage data, every 6 hours
                        print()

                        main_reading = payload[60:63].hex()
                        print(f"  Meter reading for meter #{src}: {main_reading} kWh")

                        n_hours = payload[25]
                        if n_hours > 17:
                            print(f"  Number of hourly readings is too high: {n_hours}")
                            n_hours = 17
                        hourly_readings = [reading / 100 for reading in struct.unpack(">" + "H"*n_hours, payload[26:26 + 2*n_hours])]
                        readings_str = ", ".join(f"{reading:.2f}" for reading in hourly_readings)
                        print(f"  Hourly readings: {readings_str}")

                        print()

    def forecast(self, noutput_items, ninputs):
        return [640] * ninputs

    def general_work(self, input_items, output_items):
        for channel, bits in enumerate(input_items):
            if self.bits_remaining[channel] > 0:
                bits_to_take = min(self.bits_remaining[channel], len(bits))
                self.packet_bits[channel] = numpy.append(self.packet_bits[channel], bits[:bits_to_take])
                self.bits_remaining[channel] -= bits_to_take
                if self.bits_remaining[channel] == 0:
                    if self.packet_type[channel] == 1:
                        packet_manchester = numpy.packbits(self.packet_bits[channel])
                        packet_bits = numpy.fromiter((self.manchester[b] for b in packet_manchester), dtype=numpy.uint8)
                        packet = (numpy.packbits(packet_bits) ^ 0x55).tobytes()
                        self.process_packet(channel, packet)
                    if self.packet_type[channel] == 2:
                        packet = (numpy.packbits(self.packet_bits[channel]) ^ 0xaa).tobytes()
                        self.process_packet(channel, packet)
                    self.packet_bits[channel] = numpy.array([], dtype=numpy.uint8)
                self.consume(channel, bits_to_take)
            else:
                if len(bits) >= 320:
                    bits_string = bits.tobytes()
                    offset = 0
                    while True:
                        index = bits_string.find(self.preamble, offset, -192)
                        if index == -1:
                            offset = len(bits) - 319
                            break
                        else:
                            offset = index

                        if bits_string[offset+128:offset+256] == self.sfd_1:
                            offset += 256
                            length = 0
                            for digit_offset in range(0, 64, 8):
                                digit_bits = bits_string[offset + digit_offset:offset + digit_offset + 8]
                                digit_byte = 0
                                for digit_bit in digit_bits:
                                    digit_byte = (digit_byte << 1) | digit_bit
                                length = (length << 1) | self.manchester[digit_byte]
                            if length != -1:
                                length ^= 0x55
                                self.bits_remaining[channel] = (length + 2) * 64
                                self.packet_type[channel] = 1
                                break
                        elif bits_string[offset+128:offset+256] == self.sfd_2:
                            offset += 256
                            length = 0
                            for bit in bits_string[offset:offset+16]:
                                length = (length << 1) | bit
                            length ^= 0xaaaa
                            if length < 512:
                                self.bits_remaining[channel] = (length + 2) * 8
                                self.packet_type[channel] = 2
                                break
                        else:
                            offset += 8
                    self.consume(channel, offset)

        return 0
