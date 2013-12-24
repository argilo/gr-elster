#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Elster Rx Nogui
# Generated: Tue Dec 24 09:35:29 2013
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import elster
import math
import osmosdr

class elster_rx_nogui(gr.top_block):

    def __init__(self):
        gr.top_block.__init__(self, "Elster Rx Nogui")

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2400000
        self.rx_gain = rx_gain = 45
        self.corr = corr = 0
        self.channel_rate = channel_rate = 400000
        self.channel_decimation = channel_decimation = 4
        self.center_freq = center_freq = 904600000

        ##################################################
        # Blocks
        ##################################################
        self.osmosdr_source_0 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.osmosdr_source_0.set_sample_rate(samp_rate)
        self.osmosdr_source_0.set_center_freq(center_freq, 0)
        self.osmosdr_source_0.set_freq_corr(corr, 0)
        self.osmosdr_source_0.set_dc_offset_mode(0, 0)
        self.osmosdr_source_0.set_iq_balance_mode(0, 0)
        self.osmosdr_source_0.set_gain_mode(0, 0)
        self.osmosdr_source_0.set_gain(rx_gain, 0)
        self.osmosdr_source_0.set_if_gain(20, 0)
        self.osmosdr_source_0.set_bb_gain(20, 0)
        self.osmosdr_source_0.set_antenna("", 0)
        self.osmosdr_source_0.set_bandwidth(0, 0)
          
        self.low_pass_filter_1 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, 20000, 5000, firdes.WIN_HAMMING, 6.76))
        self.elster_packetize_0 = elster.packetize(1)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, samp_rate/channel_rate)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(-channel_rate/(115000*2*3.1416))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.osmosdr_source_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.low_pass_filter_1, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.elster_packetize_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))


# QT sink close method reimplementation

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate/self.channel_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.osmosdr_source_0.set_gain(self.rx_gain, 0)

    def get_corr(self):
        return self.corr

    def set_corr(self, corr):
        self.corr = corr
        self.osmosdr_source_0.set_freq_corr(self.corr, 0)

    def get_channel_rate(self):
        return self.channel_rate

    def set_channel_rate(self, channel_rate):
        self.channel_rate = channel_rate
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate/self.channel_rate)
        self.analog_quadrature_demod_cf_0.set_gain(-self.channel_rate/(115000*2*3.1416))
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.channel_rate, 20000, 5000, firdes.WIN_HAMMING, 6.76))

    def get_channel_decimation(self):
        return self.channel_decimation

    def set_channel_decimation(self, channel_decimation):
        self.channel_decimation = channel_decimation
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.osmosdr_source_0.set_center_freq(self.center_freq, 0)

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = elster_rx_nogui()
    tb.start()
    tb.wait()

