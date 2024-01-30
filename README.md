gr-elster
=========

Author: Clayton Smith  
Email: <argilo@gmail.com>

This GNU Radio block and sample flow graph are intended to receive
packets transmitted by Elster smart meters on the 902-928 MHz band.  In
particular, I have tested it with the Elster R2S hydro meters used in the
Ottawa area.  It may work with other Elster meters.  Please let me know
what you manage to receive with it.

It is not yet complete, as I have not fully reverse engineered the packet
structure, nor the payload data.  But it is able to dump complete
packets, and can display meter readings and hourly electricity usage
data.  When running, it dumps all packets to the console in hex, and
decodes those packets containing meter readings as follows:

    Meter reading for meter #XXXXXXX: YYYYY kWh
    Hourly readings: Z.ZZ, Z.ZZ, Z.ZZ, Z.ZZ, Z.ZZ, Z.ZZ

It also stores packets to a pcap file (beginning with elster-001.pcap)
which can then be decoded using the decode_pcap.py script.

In my area, usage data is transmitted every six hours (beginning at
05:30, 11:30, 17:30 and 23:30 UTC), so it may be necessary to wait a
while before such packets will appear.

The flow graph in /apps/elster_rx_multi.grc is intended for use with an
RTL-SDR dongle, but can likely be used with other SDR receivers as well.
It receives six out of the 25 frequency-hopping channels used in my area,
but that should be sufficient to receive most traffic since packets are
repeated a few times on different channels.  The number of simultaneous
channels is limited by the bandwidth of the SDR.  An RTL-SDR dongle can
reliably receive up to about 2.4 MHz, which is sufficient for six 400-kHz
channels.

For best reception with an RTL-SDR dongle, set the frequency correction
slider to the appropriate value (in PPM) for your particular tuner.

Build instructions:

    mkdir build
    cd build
    cmake ../
    make
    sudo make install

After following the build instructions, be sure to restart GNU Radio
Companion so that the new block will be available there.

Any help you can offer with reverse engineering or coding would be
greatly appreciated!
