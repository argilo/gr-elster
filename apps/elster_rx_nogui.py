#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Elster Rx Nogui
# Generated: Sun Aug 24 17:08:35 2014
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from gnuradio.filter import pfb
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
        self.ch_filt_trans = ch_filt_trans = 10000
        self.ch_filt_cut = ch_filt_cut = 35000
        self.center_freq = center_freq = 904600000

        ##################################################
        # Blocks
        ##################################################
        self.pfb_channelizer_ccf_0 = pfb.channelizer_ccf(
        	  samp_rate / channel_rate,
        	  (firdes.low_pass(1, samp_rate, 175000, 50000, firdes.WIN_HAMMING, 6.76)),
        	  1.0,
        	  100)
        self.pfb_channelizer_ccf_0.set_channel_map(([]))
        	
        self.osmosdr_source_1 = osmosdr.source( args="numchan=" + str(1) + " " + "" )
        self.osmosdr_source_1.set_sample_rate(samp_rate)
        self.osmosdr_source_1.set_center_freq(center_freq, 0)
        self.osmosdr_source_1.set_freq_corr(corr, 0)
        self.osmosdr_source_1.set_dc_offset_mode(0, 0)
        self.osmosdr_source_1.set_iq_balance_mode(0, 0)
        self.osmosdr_source_1.set_gain_mode(False, 0)
        self.osmosdr_source_1.set_gain(rx_gain, 0)
        self.osmosdr_source_1.set_if_gain(20, 0)
        self.osmosdr_source_1.set_bb_gain(20, 0)
        self.osmosdr_source_1.set_antenna("", 0)
        self.osmosdr_source_1.set_bandwidth(0, 0)
          
        self.low_pass_filter_1_4 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_3 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_2 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_1 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_0 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1 = filter.fir_filter_fff(channel_decimation, firdes.low_pass(
        	1, channel_rate, ch_filt_cut, ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.elster_packetize_0 = elster.packetize(6)
        self.digital_clock_recovery_mm_xx_0_4 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_clock_recovery_mm_xx_0_3 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_clock_recovery_mm_xx_0_2 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_clock_recovery_mm_xx_0_1 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_clock_recovery_mm_xx_0_0 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_binary_slicer_fb_0_4 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_3 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_2 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_1 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0_0 = digital.binary_slicer_fb()
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.analog_sig_source_x_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, -200000, 1, 0)
        self.analog_quadrature_demod_cf_0_4 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_3 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_2 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_1 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_0 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(channel_rate/(115000*2*3.1416))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.elster_packetize_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.pfb_channelizer_ccf_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.low_pass_filter_1_0, 0), (self.digital_clock_recovery_mm_xx_0_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0_0, 0), (self.low_pass_filter_1_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_0, 0), (self.digital_binary_slicer_fb_0_0, 0))
        self.connect((self.low_pass_filter_1_1, 0), (self.digital_clock_recovery_mm_xx_0_1, 0))
        self.connect((self.analog_quadrature_demod_cf_0_1, 0), (self.low_pass_filter_1_1, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_1, 0), (self.digital_binary_slicer_fb_0_1, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_2, 0), (self.digital_binary_slicer_fb_0_2, 0))
        self.connect((self.analog_quadrature_demod_cf_0_2, 0), (self.low_pass_filter_1_2, 0))
        self.connect((self.low_pass_filter_1_2, 0), (self.digital_clock_recovery_mm_xx_0_2, 0))
        self.connect((self.low_pass_filter_1_3, 0), (self.digital_clock_recovery_mm_xx_0_3, 0))
        self.connect((self.analog_quadrature_demod_cf_0_3, 0), (self.low_pass_filter_1_3, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_3, 0), (self.digital_binary_slicer_fb_0_3, 0))
        self.connect((self.analog_quadrature_demod_cf_0_4, 0), (self.low_pass_filter_1_4, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0_4, 0), (self.digital_binary_slicer_fb_0_4, 0))
        self.connect((self.pfb_channelizer_ccf_0, 1), (self.analog_quadrature_demod_cf_0_0, 0))
        self.connect((self.pfb_channelizer_ccf_0, 2), (self.analog_quadrature_demod_cf_0_1, 0))
        self.connect((self.pfb_channelizer_ccf_0, 3), (self.analog_quadrature_demod_cf_0_2, 0))
        self.connect((self.pfb_channelizer_ccf_0, 4), (self.analog_quadrature_demod_cf_0_3, 0))
        self.connect((self.pfb_channelizer_ccf_0, 5), (self.analog_quadrature_demod_cf_0_4, 0))
        self.connect((self.digital_binary_slicer_fb_0_4, 0), (self.elster_packetize_0, 5))
        self.connect((self.digital_binary_slicer_fb_0_0, 0), (self.elster_packetize_0, 1))
        self.connect((self.digital_binary_slicer_fb_0_1, 0), (self.elster_packetize_0, 2))
        self.connect((self.digital_binary_slicer_fb_0_2, 0), (self.elster_packetize_0, 3))
        self.connect((self.digital_binary_slicer_fb_0_3, 0), (self.elster_packetize_0, 4))
        self.connect((self.low_pass_filter_1_4, 0), (self.digital_clock_recovery_mm_xx_0_4, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.pfb_channelizer_ccf_0, 0))
        self.connect((self.osmosdr_source_1, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_sig_source_x_0, 0), (self.blocks_multiply_xx_0, 1))



    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.pfb_channelizer_ccf_0.set_taps((firdes.low_pass(1, self.samp_rate, 175000, 50000, firdes.WIN_HAMMING, 6.76)))
        self.analog_sig_source_x_0.set_sampling_freq(self.samp_rate)
        self.osmosdr_source_1.set_sample_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.osmosdr_source_1.set_gain(self.rx_gain, 0)

    def get_corr(self):
        return self.corr

    def set_corr(self, corr):
        self.corr = corr
        self.osmosdr_source_1.set_freq_corr(self.corr, 0)

    def get_channel_rate(self):
        return self.channel_rate

    def set_channel_rate(self, channel_rate):
        self.channel_rate = channel_rate
        self.analog_quadrature_demod_cf_0.set_gain(self.channel_rate/(115000*2*3.1416))
        self.digital_clock_recovery_mm_xx_0_4.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.analog_quadrature_demod_cf_0_0.set_gain(self.channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_4.set_gain(self.channel_rate/(115000*2*3.1416))
        self.digital_clock_recovery_mm_xx_0_3.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.digital_clock_recovery_mm_xx_0_2.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.low_pass_filter_1_3.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.analog_quadrature_demod_cf_0_3.set_gain(self.channel_rate/(115000*2*3.1416))
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_1.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.analog_quadrature_demod_cf_0_1.set_gain(self.channel_rate/(115000*2*3.1416))
        self.analog_quadrature_demod_cf_0_2.set_gain(self.channel_rate/(115000*2*3.1416))
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_4.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_2.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))

    def get_channel_decimation(self):
        return self.channel_decimation

    def set_channel_decimation(self, channel_decimation):
        self.channel_decimation = channel_decimation
        self.digital_clock_recovery_mm_xx_0_4.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_3.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_2.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.digital_clock_recovery_mm_xx_0_1.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)

    def get_ch_filt_trans(self):
        return self.ch_filt_trans

    def set_ch_filt_trans(self, ch_filt_trans):
        self.ch_filt_trans = ch_filt_trans
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_3.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_4.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_2.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))

    def get_ch_filt_cut(self):
        return self.ch_filt_cut

    def set_ch_filt_cut(self, ch_filt_cut):
        self.ch_filt_cut = ch_filt_cut
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_3.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_0.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_4.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_2.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))
        self.low_pass_filter_1_1.set_taps(firdes.low_pass(1, self.channel_rate, self.ch_filt_cut, self.ch_filt_trans, firdes.WIN_HAMMING, 6.76))

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.osmosdr_source_1.set_center_freq(self.center_freq, 0)

if __name__ == '__main__':
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = elster_rx_nogui()
    tb.start()
    tb.wait()
