
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Electrisense Test
# Generated: Fri Feb 15 15:30:49 2019
##################################################

from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
from gnuradio import uhd
from gnuradio.fft import logpwrfft
from gnuradio.filter import firdes
from optparse import OptionParser

import time
import sys
import os
import numpy as np
from scipy.signal import medfilt

class data_logger(gr.top_block):
	def __init__(self):
		gr.top_block.__init__(self)

		############# Define variables #############
		self.samp_rate = 2e6
		self.fc = 100e3
		self.fft_size = 2048
		self.num_avg_window = 25
		self.fileNum = 1
		self.filt_win_size = 501
		#self.filename = "data_logging" + str(self.fileNum) + ".txt"
		#self.exists = os.path.isfile(self.filename)

		#while self.exists:
		#	self.fileNum += 1
		#	self.filename = "data_logging" + str(self.fileNum) + ".txt"
		#	self.exists = os.path.isfile(self.filename)
		#else:
		#	print("New file: " + self.filename)

		############# Initalize blocks #############
		self.uhd_usrp_source = uhd.usrp_source(
			",".join(('addr=192.168.10.2',"")),
			uhd.stream_args(
				cpu_format="fc32",
				channels=range(1),
				),
			)

		self.uhd_usrp_source.set_samp_rate(self.samp_rate)
		self.uhd_usrp_source.set_center_freq(self.fc, 0)
		self.uhd_usrp_source.set_gain(0,0)
		self.uhd_usrp_source.set_antenna('TX/RX', 0)
		self.uhd_usrp_source.set_bandwidth(1e6, 0)

		self.lpwrfft = logpwrfft.logpwrfft_c(
			sample_rate=self.samp_rate,
			fft_size=self.fft_size,
			ref_scale=2,
			frame_rate=1000,
			avg_alpha=1.0,
			average=False,
		)

		#self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.filename, False)
		#self.file_sink.set_unbuffered(False)
		self.data_sink= blocks.vector_sink_f(2048, int(2e6))

		############# Connect blocks #############
		#self.connect((self.lpwrfft,0),(self.file_sink,0))
		self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))
		self.connect((self.lpwrfft,0), (self.data_sink, 0))
		

	def start_new_file(self):
		time.sleep(210)
		tb.stop()
		tb.wait()

		#self.disconnect((self.lpwrfft,0),(self.file_sink,0))
		self.disconnect((self.lpwrfft,0), (self.data_sink, 0))
		self.disconnect((self.uhd_usrp_source,0), (self.lpwrfft, 0))

		processed_data = self.process_data(self.data_sink.data(), self.fft_size, self.num_avg_window, self.filt_win_size)

		print("Checking for previous files...")
		self.filename = "data_logging" + str(self.fileNum) + ".txt"
		self.exists = os.path.isfile(self.filename)
		while self.exists:
			self.fileNum += 1
			self.filename = "data_logging" + str(self.fileNum) + ".txt"
			self.exists = os.path.isfile(self.filename)
		print("New file: " + self.filename)
		
		print('Saving data..')
		np.savetxt(self.filename, processed_data)
		#self.file_sink = blocks.file_sink(gr.sizeof_float*2048, self.filename, False)
		#self.file_sink.set_unbuffered(False)
		print('Complete.')
		self.connect((self.lpwrfft,0),(self.data_sink,0))
		self.connect((self.uhd_usrp_source,0), (self.lpwrfft, 0))
		tb.start()
		print('Collecting Data..')
		time.sleep(30)



	def process_data(self, data, fft_size, num_avg_window, filt_win_size):
		print("Processing Data...")

		# Reshape Data
		T = int(len(data)/fft_size)
		data = np.reshape(data, (fft_size, T), order="F")

		# Compute Averaged Frames
		spectra_avg = np.zeros((fft_size, int(np.floor(T)/num_avg_window)))
		count = 0

		for i in range(0, T-num_avg_window, num_avg_window):
			spectra_avg[:,count] = np.mean(data[:,i:i+num_avg_window-1], axis=1)
			count += 1

		# Abs & Sum each FFT Bin
		[rows, columns] = np.shape(spectra_avg)
		signal = np.zeros(columns)

		for i in range(columns):
			signal[i] = np.sum(np.abs(spectra_avg[:,i]))

		# Normalize and Filter
		sig_norm = (signal - np.min(signal))/(np.max(signal)-np.min(signal))
		sig_filt = medfilt(sig_norm, filt_win_size)

		print("Processing Complete...")
		return sig_filt

def main():
	global tb
	tb = data_logger()
	tb.start()

	while 1:
		#c = raw_input("'q' to quit\n")
		tb.start_new_file()
		


if __name__ == '__main__':
	main()
