import numpy as np
from numpy.random import seed 
seed(1)
from glob import glob
import os
import scipy.io.wavfile
import argparse


def create_folder(folder_name):
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
	else:
		print(folder_name, "folder exist\n")


parser = argparse.ArgumentParser(description='Convert Wav to text files')
parser.add_argument('-house','--H_num', default='1', type=int,
					help='House number: 1,2,3,4,5,6')
parser.add_argument('-sta','--station_num', default=1, type=int,
					help='Station Number')

parser.add_argument('-read','--wav_read_root_path', default=os.getcwd(), type=str,
					help='HOUSE Directory location/path')
parser.add_argument('-save','--text_save_root_path', default=os.path.join(os.getcwd(),"audio_txt"), type=str,
					help='Directory location to save output text')

args = parser.parse_args()


if __name__ == '__main__':

	H_num = args.H_num
	station_num = args.station_num
	wav_read_root_path = args.wav_read_root_path
	text_save_root_path = args.text_save_root_path

	if H_num == 1 or H_num == 3:
		station_color = "B"
	elif H_num == 2 or H_num == 5:
		station_color = "R"


	read_root_path = os.path.join(wav_read_root_path,"H%s"%(H_num),"%sS%s"%(station_color,station_num),"audio","*")
	print("read_root_path: ", read_root_path)

	save_root_path = os.path.join(text_save_root_path,"H%s"%(H_num),"%sS%s"%(station_color,station_num))
	print("save_root_path: ", save_root_path)


	dates = sorted(glob(read_root_path))


	for date_folder_path in dates:
		date = os.path.basename(date_folder_path)
		print("Loading date folder: " + date + "...")

		'''
		Check if Directory is empty
		'''
		times = os.listdir(date_folder_path)

		if len(times) == 0:
			print("Date folder "+ os.path.basename(date_folder_path) + " is empty")

			# Remove empty directory: Not recommended
			# os.rmdir(date_folder_path)


		else:
			# Read date folders
			date_folder_path = os.path.join(date_folder_path,"*")
			
			for time_folder_path in sorted(glob(date_folder_path)):
				time = os.path.basename(time_folder_path)
				print("Checking time folder: "+ time +"...")

				wavs = os.listdir(time_folder_path)

				if len(wavs) == 0:
					print("Time folder "+ os.path.basename(time_folder_path) + " is empty")

					# Remove empty directory: Not recommended
					# print("Removing time folder..")
					# os.rmdir(time_folder_path)

				else:
					# Read time folders
					wav_paths = os.path.join(time_folder_path,"*")

					# create save folder
					save_folder = os.path.join(save_root_path,date,time)
					create_folder(save_folder)

					for wav_path in sorted(glob(wav_paths)):
						print("wav_path:",wav_path)
						_, wav = scipy.io.wavfile.read(wav_path)
						fname, _ = os.path.splitext(os.path.basename(wav_path))
						print("fname:", fname)
						save_path = os.path.join(save_folder, fname+".txt")
						print("save_path:", save_path)
						np.savetxt(save_path,wav)



		print("======================================")

	print("Done")


'''
Expected Folder structure:
F:/H1/BS1/audio/2019-02-10/2229/2019-02-10 222900_audio.wav


"wav_read_root_path" in this case would be "F:\\"
by default, it set set the read root path in current working directory

"text_save_root_path" by default creates a "audio_txt" folder in current working directory to store output text files




Run the line:
python wav_to_text.py -H 1 -sta 1 -read F:\\ -save F:\\audio_txt

'''
