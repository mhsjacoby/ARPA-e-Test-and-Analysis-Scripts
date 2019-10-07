import numpy as np
from numpy.random import seed 
seed(1)

from glob import glob
import os
from skimage.io import imread, imsave
from skimage.transform import resize
from skimage.measure import block_reduce
from skimage.filters import gaussian
#from skimage.util import view_as_blocks

def create_folder(folder_name):
	if not os.path.exists(folder_name):
		os.makedirs(folder_name)
	else:
		print(folder_name, "folder exist\n")


# =========== Parameter Setting ===================
H_num = 1
station_num = 1

# Image Loading Prameters:
occupancy = "Occupied"
#occupancy = "Unoccupied"
lighting = "bright"
#lighting = "dim"

# Blurring Method:
# blurring = "max"
# blurring = "mean"
blurring = "gaussian"

# Blurring Parameters:
# blur_filter = (3,3) # for max & mean
gaussian_sigma = 2 # for gaussian filters

# ====================================================

assert blurring == "max" or blurring == "mean" or blurring == "gaussian"

# Add if else statement for station color
if H_num == 1 or H_num == 3:
	station_color = "B"
elif H_num == 2 or H_num == 5:
	station_color = "R"


# =========== Main Code ===================
'''
Do not change the folder structure of "save_folder". 
It should have a structure that looks like H1/one_shot/H1_BS1_processed/Occupied_bright, or H2/one_shot/H2_BS3_processed/Unoccupied_dim etc
'''
# Get working directory:
path = os.getcwd()
# >>> p = os.getcwd()
# >>> os.chdir(p)

# Create folder to save output images:
save_folder = path+"/Desktop/HPD_mobile_data/HPD_mobile-H1/one_shot/H%s/one_shot/H%s_%sS%s_processed/%s_%s"%(H_num,H_num,station_color,station_num,occupancy,lighting)
create_folder(save_folder)

# Specify FOLDER to read images from:
target_files = path+"/Desktop/HPD_mobile_data/HPD_mobile-H1/one_shot/H%s/H%s-%sS%s-LABELED/%s-%s/*"%(H_num,H_num,station_color,station_num,occupancy,lighting)
#print(target_files)

print(path)
# test = glob(path+"/Desktop/HPD_mobile_data/HPD_mobile-H1/one_shot/"+target_files)
test = glob(target_files)
print(len(test))

'''
Expected input image size = 336x336 
'''
#print(target_files)
print("working....")
for i,file in enumerate(sorted(glob(target_files))): # file = path/img_filename.png
	print("still working....")
	# exit()
	# new_file = os.path.join(path, f)

	# print("New file: {}".format(new_file))
	if i>1: # for debugging
		print("breaking")
		break

	img = imread(file)

	# =========== Downsize 1 ===================
	img112 = resize(img,(112,112)) # image size that could be captured using Washington team camera
	# imsave(save_folder+"/test_112.png",img112) # for checking purpose
	

	# =========== Blur Image ===================
	# Problem with block reduce: changing block_size reduces the resulting img size tremendously
	if blurring == "max":
		imgblur = block_reduce(img112,block_size=blur_filter, func=np.max)
	elif blurring == "mean":
		imgblur = block_reduce(img112,block_size=blur_filter, func=np.mean)
	elif blurring == "gaussian":
		imgblur = gaussian(img112,sigma=gaussian_sigma) # higher sigma = blurer
	

	# =========== Downsize 2 ===================
	# imsave(save_folder+"/testblur.png",imgblur) # for checking purpose
	img32 = resize(imgblur,(32,32))
	img_name = os.path.basename(file)
	imsave(save_folder+"/"+img_name,img32)