#!/usr/bin/env python3

# Copyright 2013, 2014, 2019, 2021 Clayton Smith
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


def print_pkt(timestamp, pkt):
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)), end=" ")
    len1, flag1, src, dst, unk1, unk2, unk3 = struct.unpack(">BBIIBBB", pkt[0:13])
    print(f"len={len1:02x} flag={flag1:02x} src={src:08x} dst={dst:08x} {unk1:02x}{unk2:02x}{unk3:02x}", end=" ")
    if (src & 0x80000000) or (dst == 0 and len1 >= 35):
        ts_h, ts_m, ts_s = decode_ts(pkt[13:16])
        print(f"ts={ts_h:02}:{ts_m:02}:{ts_s:06.3f}", end=" ")
    else:
        print("rpt=" + pkt[13:14].hex() + " " + pkt[14:16].hex(), end=" ")

    if dst == 0 and len1 >= 35:  # flood broadcast message
        unk4, unk5, hop, unk7, addr, unk8, len2 = struct.unpack(">BBBBIIB", pkt[16:29])
        print(f"{unk4:02x}{unk5:02x} hop={hop:02x} {unk7:02x} addr={addr:08x} {unk8:08x} len={len2:02x}", end=" ")
        if len2 == 0:
            print(pkt[29:33].hex(), end=" ")
            unk9, len3 = struct.unpack(">BB", pkt[33:35])
            print(f"{unk9:02x}", end=" ")
            print("next_" + str(len3) + "_days=" + pkt[35:].hex())
        elif len2 == 6:
            print(pkt[29:33].hex(), end=" ")
            print("date=" + str(decode_date(pkt[33:35])))
        elif len2 == 0x27:
            print(pkt[29:33].hex(), end=" ")
            for x in range(7):  # 7 meter numbers (with first bit sometimes set to 1) followed by number 0x01-0x45
                print(pkt[33 + 5*x:37 + 5*x].hex(), end=" ")
                print(pkt[37 + 5*x:38 + 5*x].hex(), end=" ")
            print()
        else:
            print(pkt[29:].hex())
    else:
        if src & 0x80000000:
            print("path=" + pkt[16:24].hex(), end=" ")
            if pkt[24] == 0x40:
                print(pkt[24:28].hex(), end=" ")
                len4, unk12, cmd, cnt = struct.unpack(">BBBB", pkt[28:32])
                print(f"len={len4:02x} {unk12:02x} cmd={cmd:02x} cnt={cnt:02x}", end=" ")

                if cmd == 0xce:  # fetch hourly usage data, every 6 hours
                    unk13, hour = struct.unpack(">BH", pkt[32:])
                    print(f"{unk13:02x} first_hour={hour:05}")
                elif cmd == 0x22:
                    print(pkt[32:].hex())
                elif cmd == 0x23:  # path building stuff? every 6 hours
                    unk14, unk15, unk16, your_id, parent_id, parent, unk17, n_children, unk19, level, unk21, unk22, unk23, unk24, unk25, unk26, unk27, unk28, unk29 = struct.unpack(">BBBBBIBBBBBBBBBBHIB", pkt[32:58])
                    print(f"{unk14:02x} {unk15:02x} {unk16:02x} id={your_id:02x} par_id={parent_id:02x} parent={parent:08x} {unk17:02x} #child={n_children} {unk19:02x} lvl={level} {unk21:02x}{unk22:02x}{unk23:02x} {unk24:02x} {unk25:02x} {unk26:02x} {unk27:04x} {unk28:08x} {unk29:02x}", end=" ")
                    if len4 == 0x20:
                        print("{:02x}".format(pkt[58]), end=" ")
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
                    print(pkt[32:].hex())
                elif cmd == 0x6a:
                    print(pkt[32:].hex())
                else:  # unknown command
                    print(pkt[32:].hex())
            else:
                print(pkt[24:].hex())
        else:
            if len(pkt) > 16:
                len4 = pkt[16]
                if len4 == len1 - 17:  # 1st byte of payload is a length
                    if len(pkt) > 18:
                        cmd = pkt[18]
                        if cmd == 0xce:  # hourly usage data, every 6 hours
                            unk10, cmd, ctr, unk11, flag2, curr_hour, last_hour, n_hours = struct.unpack(">BBBBBHHB", pkt[17:27])
                            print(f"len={len4:02x} {unk10:02x} cmd={cmd:02x} ctr={ctr:02x} {unk11:02x} {flag2:02x} cur_hour={curr_hour:05} last_hour={last_hour:05} n_hour={n_hours:02}", pkt[27:].hex())
                            add_hourly(src, last_hour, struct.unpack(">" + "H"*n_hours, pkt[27:27 + 2*n_hours]))
                            # TODO: Get total meter reading
                        elif cmd == 0x22:  # just an acknowledgement
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print(f"len={len4:02x} {unk10:02x} cmd={cmd:02x} ctr={ctr:02x}", pkt[20:].hex())
                        elif cmd == 0x23:  # path building stuff? every 6 hours
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print(f"len={len4:02x} {unk10:02x} cmd={cmd:02x} ctr={ctr:02x}", pkt[20:].hex())
                            # TODO: Parse the rest
                        elif cmd == 0x28:  # just an acknowledgement
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print(f"len={len4:02x} {unk10:02x} cmd={cmd:02x} ctr={ctr:02x}", pkt[20:].hex())
                        elif cmd == 0x6a:
                            unk10, cmd, ctr = struct.unpack(">BBB", pkt[17:20])
                            print(f"len={len4:02x} {unk10:02x} cmd={cmd:02x} ctr={ctr:02x}", pkt[20:].hex())
                            # TODO: Parse the rest
                        else:
                            print("todo=" + pkt[16:].hex())
                            # TODO: Investigate these
                    else:
                        print(f"len={len4:02x}" + " data=" + pkt[17:].hex())
                else:
                    print("weird=" + pkt[16:].hex())  # this happens from time to time
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
    meter_name = f"{meter:08x}"
    parent_name = f"{parent:08x}"
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
