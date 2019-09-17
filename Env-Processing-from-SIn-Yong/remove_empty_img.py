import numpy as np
from numpy.random import seed 
seed(1)
from glob import glob
import os
from matplotlib.pyplot import imread

# check and print folder size
H_num = 1
BS_num = 5
# continue with :
img_threshold = 10
'''
threshold 10 = remove empty images
threshold 30 = remove images with VERY low light intensity (later)

NOTE: These threshold are meant for img dim of 336x336!
	  Threshold might vary if img is downsized

'''

root_path = "H%s/BS%s/img/*"%(H_num,BS_num)


dates = sorted(glob(root_path))
dates = dates[1:]
#A

for date_folder_path in dates:
	print("Checking date folder: "+os.path.basename(date_folder_path)+"...")

	'''
	Check if Directory is empty
	'''
	times = os.listdir(date_folder_path)

	if len(times) == 0:
		print("Date folder "+ os.path.basename(date_folder_path) + " is empty")

		# Remove empty directory:
		# os.rmdir(date_folder_path)

#	A

	else:
		# Read date folders
		date_folder_path = os.path.join(date_folder_path,"*")
		
		for time_folder_path in sorted(glob(date_folder_path)):
			print("Checking time folder: "+ os.path.basename(time_folder_path)+"...")
		

			imgs = os.listdir(time_folder_path)

			if len(imgs) == 0:
				print("Time folder "+ os.path.basename(time_folder_path) + " is empty")

				# Remove empty directory:
				print("Removing time folder..")
				os.rmdir(time_folder_path)
#				A


#			else:
#				print("Folder not empty!")
#				a


			else:
				# Read time folders
				img_paths = os.path.join(time_folder_path,"*")

				for img_path in sorted(glob(img_paths)):




					#========================================================= Main checking part=========================================================
					try:
						img = imread(img_path)
						img *= 255
						img_mean = np.mean(img)
		#				print(img_mean)
						
						if img_mean < img_threshold:
		
							# Remove a file:
							print("Remove "+os.path.basename(img_path))
							os.remove(img_path)
					except:
						print("Reading error, removing "+ os.path.basename(img_path))
						os.remove(img_path)
					#========================================================= Main checking part=========================================================

	print("======================================")

print("Done")


'''
Remove the empty directory as well

check if it can detect directory with files first!

print all teh folder length! Last time it prints all zero even for folder with subfolders!


'''
