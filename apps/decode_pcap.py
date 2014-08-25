import sys
import struct
import time


def decode_ts(bytes):
    ts1, ts2, ts3 = struct.unpack(">BBB", bytes)
    ts = ((ts1 << 16) + (ts2 << 8) + ts3)
    ts_h = ts / 128 / 3600
    ts -= ts_h * 128 * 3600
    ts_m = ts / 128 / 60
    ts -= ts_m * 128 * 60
    ts_s = ts / 128.
    return ts_h, ts_m, ts_s

def to_hex(bytes):
    return "".join(["{0:02x}".format(ord(byte)) for byte in bytes])

def print_pkt(t, pkt):
    print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t)),
    l, flag, src, dst, unk1, unk2, unk3 = struct.unpack(">BBIIBBB", pkt[0:13])
    print "flag={0:02x} src={1:08x} dst={2:08x} {3:02x}{4:02x}{5:02x}".format(flag, src, dst, unk1, unk2, unk3),
    if (src & 0x80000000) or (dst == 0):
        ts_h, ts_m, ts_s = decode_ts(pkt[13:16])
        print "ts={0:02}:{1:02}:{2:06.3f}".format(ts_h, ts_m, ts_s),
    else:
        print to_hex(pkt[13:16]),
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
