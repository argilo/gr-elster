#!/usr/bin/env python

# Copyright 2013, 2014, 2019 Clayton Smith
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

from __future__ import division, print_function, unicode_literals
import datetime
import struct
import sys
import time
import pygraphviz

meter_first_hour = {}
meter_last_hour = {}
meter_readings = {}

meter_parents = {}
meter_gatekeepers = {}
meter_levels = {}


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
    for i, reading in enumerate(readings):
        meter_readings[meter][i + first_hour] = reading


def decode_ts(ts_bytes):
    ts1, ts2, ts3 = struct.unpack(">BBB", ts_bytes)
    ts = ((ts1 << 16) + (ts2 << 8) + ts3)
    ts_h = ts // (128 * 3600)
    ts -= ts_h * 128 * 3600
    ts_m = ts // (128 * 60)
    ts -= ts_m * 128 * 60
    ts_s = ts / 128
    return ts_h, ts_m, ts_s


def decode_date(date_bytes):
    short, = struct.unpack(">H", date_bytes)
    year = 2000 + (short >> 9)
    days = short & 0x1FF
    date = datetime.date(year, 1, 1)
    delta = datetime.timedelta(days)
    return date + delta


def to_hex(in_bytes):
    return "".join(["{:02x}".format(ord(byte)) for byte in in_bytes])


def print_pkt(timestamp, pkt):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)), end=" ")
    len1, flag1, src, dst, unk1, unk2, unk3 = struct.unpack(">BBIIBBB", pkt[0:13])
    print("len={:02x} flag={:02x} src={:08x} dst={:08x} {:02x}{:02x}{:02x}".format(len1, flag1, src, dst, unk1, unk2, unk3), end=" ")
    if (src & 0x80000000) or (dst == 0 and len1 >= 35):
        ts_h, ts_m, ts_s = decode_ts(pkt[13:16])
        print("ts={:02}:{:02}:{:06.3f}".format(ts_h, ts_m, ts_s), end=" ")
    else:
        print("rpt=" + to_hex(pkt[13:14]) + " " + to_hex(pkt[14:16]), end=" ")

    if dst == 0 and len1 >= 35:  # flood broadcast message
        unk4, unk5, hop, unk7, addr, unk8, len2 = struct.unpack(">BBBBIIB", pkt[16:29])
        print("{:02x}{:02x} hop={:02x} {:02x} addr={:08x} {:08x} len={:02x}".format(unk4, unk5, hop, unk7, addr, unk8, len2), end=" ")
        if len2 == 0:
            print(to_hex(pkt[29:33]), end=" ")
            unk9, len3 = struct.unpack(">BB", pkt[33:35])
            print("{:02x}".format(unk9), end=" ")
            print("next_" + str(len3) + "_days=" + to_hex(pkt[35:]))
        elif len2 == 6:
            print(to_hex(pkt[29:33]), end=" ")
            print("date=" + str(decode_date(pkt[33:35])))
        elif len2 == 0x27:
            print(to_hex(pkt[29:33]), end=" ")
            for x in range(7):  # 7 meter numbers (with first bit sometimes set to 1) followed by number 0x01-0x45
                print(to_hex(pkt[33 + 5*x:37 + 5*x]), end=" ")
                print(to_hex(pkt[37 + 5*x:38 + 5*x]), end=" ")
            print()
        else:
            print(to_hex(pkt[29:]))
    else:
        if src & 0x80000000:
            print("path=" + to_hex(pkt[16:24]), end=" ")
            if ord(pkt[24]) == 0x40:
                print(to_hex(pkt[24:28]), end=" ")
                len4, unk12, cmd, cnt = struct.unpack(">BBBB", pkt[28:32])
                print("len={:02x} {:02x} cmd={:02x} cnt={:02x}".format(len4, unk12, cmd, cnt), end=" ")

                if cmd == 0xce:  # fetch hourly usage data, every 6 hours
                    unk13, hour = struct.unpack(">BH", pkt[32:])
                    print("{:02x} first_hour={:05}".format(unk13, hour))
                elif cmd == 0x22:
                    print(to_hex(pkt[32:]))
                elif cmd == 0x23:  # path building stuff? every 6 hours
                    unk14, unk15, unk16, your_id, parent_id, parent, unk17, n_children, unk19, level, unk21, unk22, unk23, unk24, unk25, unk26, unk27, unk28, unk29 = struct.unpack(">BBBBBIBBBBBBBBBBHIB", pkt[32:58])
                    print("{:02x} {:02x} {:02x} id={:02x} par_id={:02x} parent={:08x} {:02x} #child={} {:02x} lvl={} {:02x}{:02x}{:02x} {:02x} {:02x} {:02x} {:04x} {:08x} {:02x}".format(
                        unk14, unk15, unk16, your_id, parent_id, parent, unk17, n_children, unk19, level, unk21, unk22, unk23, unk24, unk25, unk26, unk27, unk28, unk29), end=" ")
                    if len4 == 0x20:
                        print("{:02x}".format(ord(pkt[58])), end=" ")
                        print("date=" + str(decode_date(pkt[59:61])))
                    else:
                        print()

                    # Prepare graph edges
                    meter_parents[dst] = parent
                    if level == 2:
                        meter_parents[parent] = src  # Fill this in now, in case we don't hear from parent

                    meter_gatekeepers[dst] = src
                    if level >= 2:
                        meter_gatekeepers[parent] = src  # Fill this in now, in case we don't hear from parent

                    meter_levels[dst] = level
                    meter_levels[parent] = level - 1
                    meter_levels[src] = 0
                elif cmd == 0x28:
                    print(to_hex(pkt[32:]))
                elif cmd == 0x6a:
                    print(to_hex(pkt[32:]))
                else:  # unknown command
                    print(to_hex(pkt[32:]))
            else:
                print(to_hex(pkt[24:]))
        else:
            if len(pkt) > 16:
                len4 = ord(pkt[16])
                if len4 == len1 - 17:  # 1st byte of payload is a length
                    if len(pkt) > 18:
                        cmd = ord(pkt[18])
                        if cmd == 0xce:  # hourly usage data, every 6 hours
                            unk10, cmd, ctr, unk11, flag2, curr_hour, last_hour, n_hours = struct.unpack(">BBBBBHHB", pkt[17:27])
                            print("len={:02x} {:02x} cmd={:02x} ctr={:02x} {:02x} {:02x} cur_hour={:05} last_hour={:05} n_hour={:02}".format(len4, unk10, cmd, ctr, unk11, flag2, curr_hour, last_hour, n_hours), to_hex(pkt[27:]))
                            add_hourly(src, last_hour, struct.unpack(">" + "H"*n_hours, pkt[27:27 + 2*n_hours]))
                            # TODO: Get total meter reading
                        elif cmd == 0x22:  # just an acknowledgement
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print("len={:02x} {:02x} cmd={:02x} ctr={:02x}".format(len4, unk10, cmd, ctr), to_hex(pkt[20:]))
                        elif cmd == 0x23:  # path building stuff? every 6 hours
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print("len={:02x} {:02x} cmd={:02x} ctr={:02x}".format(len4, unk10, cmd, ctr), to_hex(pkt[20:]))
                            # TODO: Parse the rest
                        elif cmd == 0x28:  # just an acknowledgement
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print("len={:02x} {:02x} cmd={:02x} ctr={:02x}".format(len4, unk10, cmd, ctr), to_hex(pkt[20:]))
                        elif cmd == 0x6a:
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print("len={:02x} {:02x} cmd={:02x} ctr={:02x}".format(len4, unk10, cmd, ctr), to_hex(pkt[20:]))
                            # TODO: Parse the rest
                        else:
                            print("todo=" + to_hex(pkt[16:]))
                            # TODO: Investigate these
                    else:
                        print("len={:02x}".format(len4) + " data=" + to_hex(pkt[17:]))
                else:
                    print("weird=" + to_hex(pkt[16:]))  # this happens from time to time
            else:
                print()


if len(sys.argv) < 2:
    sys.stderr.write("Usage: decode_pcap.py input_file...\n")
    sys.exit(1)

for filename in sys.argv[1:]:
    f = open(filename, "rb")
    magic = f.read(4)

    if magic == b"\xa1\xb2\xc3\xd4":  # big endian
        endian = ">"
    elif magic == b"\xd4\xc3\xb2\xa1":  # little endian
        endian = "<"
    else:
        raise Exception("Not a pcap capture file (bad magic)")
    hdr = f.read(20)
    if len(hdr) < 20:
        raise Exception("Invalid pcap file (too short)")
    vermaj, vermin, tz, sig, snaplen, linktype = struct.unpack(endian+"HHIIII", hdr)

    packets = {}
    while True:
        hdr = f.read(16)
        if len(hdr) < 16:
            break
        sec, usec, caplen, wirelen = struct.unpack(endian+"IIII", hdr)
        pkt = f.read(caplen)
        print_pkt(sec + usec / 1000000, pkt)

print()

for meter in sorted(meter_readings.keys()):
    print("Readings for LAN ID " + str(meter) + ":", end=" ")
    if meter_first_hour[meter] > meter_last_hour[meter]:
        meter_last_hour[meter] += 65536
    for hour in range(meter_first_hour[meter], meter_last_hour[meter] + 1):
        print("{:5.2f}".format(meter_readings[meter][hour % 65536] / 100) if meter_readings[meter][hour % 65536] >= 0 else "   ? ", end=" ")
    print()


G = pygraphviz.AGraph(directed=True, ranksep=2.0, rankdir="RL")

for meter, parent in meter_parents.items():
    meter_name = "{:08x}".format(meter)
    parent_name = "{:08x}".format(parent)
    if parent & 0x80000000:
        G.add_node(parent_name, color="red", rank="max")
    G.add_edge(meter_name, parent_name)

    if (meter_levels[parent] >= 2) and (parent not in meter_parents):
        gatekeeper_name = "{:08x}".format(meter_gatekeepers[meter])

        G.add_node(gatekeeper_name, color="red", rank="max")
        G.add_node("Level 1\n(" + gatekeeper_name + ")", color="gray")
        G.add_edge("Level 1\n(" + gatekeeper_name + ")", gatekeeper_name)
        for x in range(1, meter_levels[parent] - 1):
            G.add_node("Level " + str(x+1) + "\n(" + gatekeeper_name + ")", color="gray")
            G.add_edge("Level " + str(x+1) + "\n(" + gatekeeper_name + ")", "Level " + str(x) + "\n(" + gatekeeper_name + ")")
        G.add_edge(parent_name, "Level " + str(meter_levels[parent] - 1) + "\n(" + gatekeeper_name + ")")

G.layout(prog="dot")
G.draw("mesh.pdf")
