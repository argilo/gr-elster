#!/usr/bin/env python
##################################################
# Gnuradio Python Flow Graph
# Title: Elster Rx
# Generated: Sat Jan  4 11:51:18 2014
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import digital
from gnuradio import eng_notation
from gnuradio import filter
from gnuradio import gr
from gnuradio import wxgui
from gnuradio.eng_option import eng_option
from gnuradio.fft import window
from gnuradio.filter import firdes
from gnuradio.wxgui import fftsink2
from gnuradio.wxgui import forms
from gnuradio.wxgui import scopesink2
from gnuradio.wxgui import waterfallsink2
from grc_gnuradio import wxgui as grc_wxgui
from optparse import OptionParser
import elster
import math
import osmosdr
import wx

class elster_rx(grc_wxgui.top_block_gui):

    def __init__(self):
        grc_wxgui.top_block_gui.__init__(self, title="Elster Rx")
        _icon_path = "/usr/share/icons/hicolor/32x32/apps/gnuradio-grc.png"
        self.SetIcon(wx.Icon(_icon_path, wx.BITMAP_TYPE_ANY))

        ##################################################
        # Variables
        ##################################################
        self.window_size = window_size = (800,600)
        self.samp_rate = samp_rate = 2400000
        self.rx_gain = rx_gain = 45
        self.corr = corr = 0
        self.channel_rate = channel_rate = 400000
        self.channel_decimation = channel_decimation = 4
        self.center_freq = center_freq = 904600000

        ##################################################
        # Blocks
        ##################################################
        self.nb = self.nb = wx.Notebook(self.GetWin(), style=wx.NB_TOP)
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Band spectrum")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Band waterfall")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "1-channel waterfall")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Scope")
        self.nb.AddPage(grc_wxgui.Panel(self.nb), "Bit stream")
        self.Add(self.nb)
        _corr_sizer = wx.BoxSizer(wx.VERTICAL)
        self._corr_text_box = forms.text_box(
        	parent=self.GetWin(),
        	sizer=_corr_sizer,
        	value=self.corr,
        	callback=self.set_corr,
        	label="Freq. correction",
        	converter=forms.float_converter(),
        	proportion=0,
        )
        self._corr_slider = forms.slider(
        	parent=self.GetWin(),
        	sizer=_corr_sizer,
        	value=self.corr,
        	callback=self.set_corr,
        	minimum=-100,
        	maximum=100,
        	num_steps=200,
        	style=wx.SL_HORIZONTAL,
        	cast=float,
        	proportion=1,
        )
        self.Add(_corr_sizer)
        self.wxgui_waterfallsink2_1 = waterfallsink2.waterfall_sink_c(
        	self.nb.GetPage(2).GetWin(),
        	baseband_freq=0,
        	dynamic_range=50,
        	ref_level=-30,
        	ref_scale=2.0,
        	sample_rate=channel_rate,
        	fft_size=512,
        	fft_rate=30,
        	average=False,
        	avg_alpha=None,
        	title="Waterfall Plot",
        	size=(window_size),
        )
        self.nb.GetPage(2).Add(self.wxgui_waterfallsink2_1.win)
        self.wxgui_waterfallsink2_0 = waterfallsink2.waterfall_sink_c(
        	self.nb.GetPage(1).GetWin(),
        	baseband_freq=center_freq,
        	dynamic_range=50,
        	ref_level=-30,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=1024,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="Waterfall Plot",
        	size=(window_size),
        )
        self.nb.GetPage(1).Add(self.wxgui_waterfallsink2_0.win)
        self.wxgui_scopesink2_1 = scopesink2.scope_sink_f(
        	self.nb.GetPage(4).GetWin(),
        	title="Scope Plot",
        	sample_rate=2/56.48E-6,
        	v_scale=0.5,
        	v_offset=1,
        	t_scale=8*56.48E-6,
        	ac_couple=False,
        	xy_mode=False,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        	size=(window_size),
        )
        self.nb.GetPage(4).Add(self.wxgui_scopesink2_1.win)
        self.wxgui_scopesink2_0 = scopesink2.scope_sink_f(
        	self.nb.GetPage(3).GetWin(),
        	title="Scope Plot",
        	sample_rate=channel_rate/4,
        	v_scale=0.4,
        	v_offset=0,
        	t_scale=56.48E-6 *8,
        	ac_couple=False,
        	xy_mode=False,
        	num_inputs=1,
        	trig_mode=wxgui.TRIG_MODE_AUTO,
        	y_axis_label="Counts",
        	size=(window_size),
        )
        self.nb.GetPage(3).Add(self.wxgui_scopesink2_0.win)
        self.wxgui_fftsink2_0 = fftsink2.fft_sink_c(
        	self.nb.GetPage(0).GetWin(),
        	baseband_freq=center_freq,
        	y_per_div=10,
        	y_divs=10,
        	ref_level=0,
        	ref_scale=2.0,
        	sample_rate=samp_rate,
        	fft_size=512,
        	fft_rate=15,
        	average=False,
        	avg_alpha=None,
        	title="FFT Plot",
        	peak_hold=True,
        	size=(window_size),
        )
        self.nb.GetPage(0).Add(self.wxgui_fftsink2_0.win)
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
        self.digital_correlate_access_code_bb_0 = digital.correlate_access_code_bb("1010101010101010101010101010101001010101101001011001101010100110", 0)
        self.digital_clock_recovery_mm_xx_0 = digital.clock_recovery_mm_ff(channel_rate * 56.48E-6 / 2 / channel_decimation, 0.25*(0.05*0.05), 0.5, 0.05, 0.005)
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_uchar_to_float_0 = blocks.uchar_to_float()
        self.blocks_keep_one_in_n_0 = blocks.keep_one_in_n(gr.sizeof_gr_complex*1, samp_rate/channel_rate)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf(-channel_rate/(115000*2*3.1416))

        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_uchar_to_float_0, 0), (self.wxgui_scopesink2_1, 0))
        self.connect((self.digital_correlate_access_code_bb_0, 0), (self.blocks_uchar_to_float_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.digital_correlate_access_code_bb_0, 0))
        self.connect((self.low_pass_filter_1, 0), (self.wxgui_scopesink2_0, 0))
        self.connect((self.digital_clock_recovery_mm_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.low_pass_filter_1, 0))
        self.connect((self.low_pass_filter_1, 0), (self.digital_clock_recovery_mm_xx_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.blocks_keep_one_in_n_0, 0), (self.wxgui_waterfallsink2_1, 0))
        self.connect((self.osmosdr_source_0, 0), (self.wxgui_waterfallsink2_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.wxgui_fftsink2_0, 0))
        self.connect((self.osmosdr_source_0, 0), (self.blocks_keep_one_in_n_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.elster_packetize_0, 0))


# QT sink close method reimplementation

    def get_window_size(self):
        return self.window_size

    def set_window_size(self, window_size):
        self.window_size = window_size

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate/self.channel_rate)
        self.wxgui_fftsink2_0.set_sample_rate(self.samp_rate)
        self.wxgui_waterfallsink2_0.set_sample_rate(self.samp_rate)
        self.osmosdr_source_0.set_sample_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.osmosdr_source_0.set_gain(self.rx_gain, 0)

    def get_corr(self):
        return self.corr

    def set_corr(self, corr):
        self.corr = corr
        self._corr_slider.set_value(self.corr)
        self._corr_text_box.set_value(self.corr)
        self.osmosdr_source_0.set_freq_corr(self.corr, 0)

    def get_channel_rate(self):
        return self.channel_rate

    def set_channel_rate(self, channel_rate):
        self.channel_rate = channel_rate
        self.blocks_keep_one_in_n_0.set_n(self.samp_rate/self.channel_rate)
        self.analog_quadrature_demod_cf_0.set_gain(-self.channel_rate/(115000*2*3.1416))
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)
        self.wxgui_scopesink2_0.set_sample_rate(self.channel_rate/4)
        self.low_pass_filter_1.set_taps(firdes.low_pass(1, self.channel_rate, 20000, 5000, firdes.WIN_HAMMING, 6.76))
        self.wxgui_waterfallsink2_1.set_sample_rate(self.channel_rate)

    def get_channel_decimation(self):
        return self.channel_decimation

    def set_channel_decimation(self, channel_decimation):
        self.channel_decimation = channel_decimation
        self.digital_clock_recovery_mm_xx_0.set_omega(self.channel_rate * 56.48E-6 / 2 / self.channel_decimation)

    def get_center_freq(self):
        return self.center_freq

    def set_center_freq(self, center_freq):
        self.center_freq = center_freq
        self.wxgui_fftsink2_0.set_baseband_freq(self.center_freq)
        self.wxgui_waterfallsink2_0.set_baseband_freq(self.center_freq)
        self.osmosdr_source_0.set_center_freq(self.center_freq, 0)

if __name__ == '__main__':
    import ctypes
    import os
    if os.name == 'posix':
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"
    parser = OptionParser(option_class=eng_option, usage="%prog: [options]")
    (options, args) = parser.parse_args()
    tb = elster_rx()
    tb.Start(True)
    tb.Wait()

