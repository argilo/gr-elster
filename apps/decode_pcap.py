import sys
import struct
import time
import datetime


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
    l1, flag, src, dst, unk1, unk2, unk3 = struct.unpack(">BBIIBBB", pkt[0:13])
    print "len={0:02x} flag={1:02x} src={2:08x} dst={3:08x} {4:02x}{5:02x}{6:02x}".format(l1, flag, src, dst, unk1, unk2, unk3),
    if (src & 0x80000000) or (dst == 0):
        ts_h, ts_m, ts_s = decode_ts(pkt[13:16])
        print "ts={0:02}:{1:02}:{2:06.3f}".format(ts_h, ts_m, ts_s),
    else:
        print to_hex(pkt[13:16]),

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
            pass
        else:
            if len(pkt) > 16:
                l4 = ord(pkt[16])
                if l4 != l1 - 17:
                    raise Exception("Length mismatch: " + str(l1) + " " + str(l4))
        print to_hex(pkt[16:])


if len(sys.argv) == 2:
    filename = sys.argv[1]
else:
    sys.stderr.write("Usage: decode_pcap.py input_file\n");
    sys.exit(1)

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

while True:
    hdr = f.read(16)
    if len(hdr) < 16:
        break
    sec,usec,caplen,wirelen = struct.unpack(endian+"IIII", hdr)
    pkt = f.read(caplen)
    print_pkt(sec + usec / 1000000., pkt)
