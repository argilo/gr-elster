#!/usr/bin/env python

# Copyright 2013-2014 Clayton Smith
#
# This file is part of gr-elster
#
# gr-elster is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.
#
# gr-elster is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with gr-elster; see the file COPYING.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street,
# Boston, MA 02110-1301, USA.

import sys
import struct
import time
import datetime

meter_first_hour = {}
meter_last_hour = {}
meter_readings = {}

def add_hourly(meter, last_hour, readings):
    first_hour = last_hour - len(readings) + 1
    if meter not in meter_readings:
        meter_first_hour[meter] = first_hour
        meter_last_hour[meter] = last_hour
        meter_readings[meter] = [-1] * 65536
    if (first_hour - meter_first_hour[meter]) % 65536 > 32768:
        meter_first_hour[meter] = first_hour
    if (last_hour - meter_last_hour[meter]) % 65536 < 32768:
        meter_last_hour[meter] = last_hour
    for i in range(len(readings)):
        meter_readings[meter][i + first_hour] = readings[i]

def decode_ts(bytes):
    ts1, ts2, ts3 = struct.unpack(">BBB", bytes)
    ts = ((ts1 << 16) + (ts2 << 8) + ts3)
    ts_h = ts / 128 / 3600
    ts -= ts_h * 128 * 3600
    ts_m = ts / 128 / 60
    ts -= ts_m * 128 * 60
    ts_s = ts / 128.
    return ts_h, ts_m, ts_s

def decode_date(bytes):
    short, = struct.unpack(">H", bytes)
    year = 2000 + (short >> 9)
    days = short & 0x1FF
    date = datetime.date(year, 1, 1)
    delta = datetime.timedelta(days)
    return date + delta

def to_hex(bytes):
    return "".join(["{0:02x}".format(ord(byte)) for byte in bytes])

def print_pkt(t, pkt):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
    l1, flag1, src, dst, unk1, unk2, unk3 = struct.unpack(">BBIIBBB", pkt[0:13])
    print "len={0:02x} flag={1:02x} src={2:08x} dst={3:08x} {4:02x}{5:02x}{6:02x}".format(l1, flag1, src, dst, unk1, unk2, unk3),
    if (src & 0x80000000) or (dst == 0):
        ts_h, ts_m, ts_s = decode_ts(pkt[13:16])
        print "ts={0:02}:{1:02}:{2:06.3f}".format(ts_h, ts_m, ts_s),
    else:
        print "rpt=" + to_hex(pkt[13:14]) + " " + to_hex(pkt[14:16]),

    if dst == 0: # flood broadcast message
        unk4, unk5, unk6, unk7, addr, unk8, l2 = struct.unpack(">BBBBIIB", pkt[16:29])
        print "{0:02x}{1:02x}{2:02x}{3:02x} addr={4:08x} {5:08x} len={6:02x}".format(unk4, unk5, unk6, unk7, addr, unk8, l2),
        if l2 == 0:
            print to_hex(pkt[29:33]),
            unk9, l3 = struct.unpack(">BB", pkt[33:35])
            print "{0:02x}".format(unk9),
            print "next_" + str(l3) + "_days=" + to_hex(pkt[35:])
        elif l2 == 6:
            print to_hex(pkt[29:33]),
            print "date=" + str(decode_date(pkt[33:35]))
        else:
            print to_hex(pkt[29:])
    else:
        if src & 0x80000000:
            print "path=" + to_hex(pkt[16:24]) + " " + to_hex(pkt[24:])
        else:
            if len(pkt) > 16:
                l4 = ord(pkt[16])
                if l4 == l1 - 17: # 1st byte of payload is a length
                    if len(pkt) > 18 and ord(pkt[18]) == 0xce: # hourly data is present
                        unk10, cmd, ctr, unk11, flag2, curr_hour, last_hour, n_hours = struct.unpack(">BBBBBHHB", pkt[17:27])
                        print "{0:02x} cmd={1:02x} ctr={2:02x} {3:02x} {4:02x} {5:05} {6:05} n_hour={7:02}".format(unk10, cmd, ctr, unk11, flag2, curr_hour, last_hour, n_hours), to_hex(pkt[27:])
                        add_hourly(src, last_hour, struct.unpack(">" + "H"*n_hours, pkt[27:27 + 2*n_hours]))
                    else:
                        print "todo=" + to_hex(pkt[16:])
                else:
                    print "weird=" + to_hex(pkt[16:]) # this happens from time to time
            else:
                print


if len(sys.argv) < 2:
    sys.stderr.write("Usage: decode_pcap.py input_file...\n");
    sys.exit(1)

for filename in sys.argv[1:]:
    f = open(filename,"rb")
    magic = f.read(4)

    if magic == "\xa1\xb2\xc3\xd4": #big endian
        endian = ">"
    elif  magic == "\xd4\xc3\xb2\xa1": #little endian
        endian = "<"
    else:
        raise Exception("Not a pcap capture file (bad magic)")
    hdr = f.read(20)
    if len(hdr)<20:
        raise Exception("Invalid pcap file (too short)")
    vermaj,vermin,tz,sig,snaplen,linktype = struct.unpack(endian+"HHIIII",hdr)

    packets = {}
    while True:
        hdr = f.read(16)
        if len(hdr) < 16:
            break
        sec,usec,caplen,wirelen = struct.unpack(endian+"IIII", hdr)
        pkt = f.read(caplen)
        if pkt in packets:
            packets[pkt] += 1
        else:
            packets[pkt] = 1
            print_pkt(sec + usec / 1000000., pkt)

print

for meter in sorted(meter_readings.keys()):
    print "Readings for LAN ID " + str(meter) + ":",
    if meter_first_hour[meter] > meter_last_hour[meter]:
        meter_last_hour[meter] += 65536
    for hour in range(meter_first_hour[meter], meter_last_hour[meter] + 1):
        print "{0:5.2f}".format(meter_readings[meter][hour % 65536] / 100.0) if meter_readings[meter][hour % 65536] >= 0 else "   ? ",
    print
