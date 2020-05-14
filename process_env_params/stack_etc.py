## Sin Yong's script
'''
Stacking csvs, foward backward fill, time avg window
'''
import numpy as np
from numpy.random import seed 
seed(1)
from glob import glob
# from func_multi import create_folder,extract_csv
import pandas as pd
import os

def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    else:
        print(folder_name, "folder exist\n")


def mylistdir(directory):
    filelist = os.listdir(directory)
    return [x for x in filelist if x.endswith('.csv')] 



def extract_csv(csv_file, var_names, extract_timestamp=False, step=0):
    df = pd.read_csv(csv_file)
    df.rename(columns={'Unnamed: 0':'timestamp'}, inplace=True)
    csv_data = []

    if extract_timestamp == True:
        print('extracting timestamp')
        csv_data.append(np.asarray(df.iloc[:,0])) # append timestamp (year,month,day,hour,min,second)

    for var in var_names:
        csv_data.append(np.asarray(df[var]))

    
    if step == 0:
        csv_data = np.transpose(csv_data)
        print("Number of rows in this csv: ",len(csv_data))
        csv_data = np.asarray(csv_data)
    elif step == 1:
        # keep it as list...
        print("Step 1, keeping output as list")
    else:
        print("Please specify which step you're in")

    return csv_data



H_num = 3
station_color = "R"
station_nums = [1,2,3,4,5]
#station_nums = [2]# test

# Add if else statement for station color
# if H_num == 1 or H_num == 3:
#     station_color = "B"
# elif H_num == 2 or H_num == 5:
#     station_color = "R"

filling_limit = 30 # 5 min
window_size = 30 # 5 min, window_size stride

headers = "timestamp,tvoc_ppb,temp_c,rh_percent,light_lux,co2eq_ppm,dist_mm,number,occupied"
var_names = headers.split(',')

# To handle some csv that doesn't have "timestamp" headers
odd_headers = "Unnamed: 0,tvoc_ppb,temp_c,rh_percent,light_lux,co2eq_ppm,dist_mm,number,occupied"
odd_var_names = odd_headers.split(',')


path = '/Users/maggie/Desktop/HPD_mobile_data/HPD_mobile-H3/H3-red/2019-08-15_to_2019-09-05/'
#path = "/Users/maggie/Documents/Github/HPDmobile-Test-and-Analysis-Scripts/Env-Processing-from-SIn-Yong/Compiled_CSV_Processing_Demo/"


# Save folder 
folder_name = "new_stacked_test/H%s"%(H_num)
create_folder(path+folder_name)


for station_num in station_nums:
    print('station: {}'.format(station_num))
    #target_files = os.path.join(path,"H%s/%sS%s/0_complete_csv/H%s*"%(H_num, station_color, station_num, H_num)) 
    target_files = os.path.join(path,"H%s/%sS%s/0_complete_csv/*"%(H_num, station_color, station_num))

    print('files: {}'.format(target_files))

    # ============== Stack csvs ==============
    first_data = True
    for file in sorted(glob(target_files)):
        print("Loading file: ",file)


        if first_data:
            print('Reading first data...')
            main_data = extract_csv(file, var_names,step=0)
            first_data = False

        else:
            print('Main data exists. Length = {}'.format(len(main_data)))
            try:
                next_data = extract_csv(file, var_names,step=0)
            except:
                next_data = extract_csv(file, odd_var_names,step=0)
    
            main_data = np.vstack((main_data,next_data))

    #     # if a variable exist: use it, if not, create it
    #     if 'main_data' not in locals():
    # #        print('Create main_data') # should only appear in first loop
    #         main_data = extract_csv(file, var_names,step=0)
    #     elif 'main_data' in locals():
    # #        print('Create next_data')
    #         try:
    #             next_data = extract_csv(file, var_names,step=0)
    #         except:
    #             next_data = extract_csv(file, odd_var_names,step=0)

    #         main_data = np.vstack((main_data,next_data))


    # ============== Forward and backward fill ==============    
    timestamp = np.asarray(main_data[:,0])
    data = np.asarray(main_data[:,1:])
    data = pd.DataFrame(data)

    data = pd.DataFrame.fillna(data, method="ffill", limit=filling_limit)
    data = pd.DataFrame.fillna(data, method="bfill", limit=filling_limit)
    
    main_data = np.vstack((timestamp,np.transpose(data)))
    main_data = np.transpose(main_data)
    
    # save data BEFORE averaging
    np.savetxt(os.path.join(path, folder_name+"/H%s_%sS%s_stacked.csv"%(H_num, station_color, station_num)), main_data, delimiter=',',fmt='%s',header=headers,comments='')


    # ============== Time Avg Window ==============    
     # Using the last timestamp in the window. (Eg: 1 min window 00:00, 00:10, 00:20, 00:30, 00:40, 00:50 ==> using 00:50)
    time_stamp_index = np.arange(window_size-1,len(main_data)+1,window_size)

    avg_timestamp = timestamp[time_stamp_index]
    print("avg_timestamp len:", len(avg_timestamp))

    # avg_data = []
    avg_data = np.zeros((len(avg_timestamp),np.shape(data)[1]))

    win_start = 0
    for i in range(len(time_stamp_index)):
        avg = np.nanmean(data[win_start:time_stamp_index[i]+1],axis=0)
        # print(avg)

        win_start = time_stamp_index[i]

        # avg_data.append(avg)
        avg_data[i] = avg
        
    print("avg_data len:", len(avg_data))

    main_avg_data = np.vstack((avg_timestamp,np.transpose(avg_data)))
    main_avg_data = np.transpose(main_avg_data)

    np.savetxt(os.path.join(path, folder_name+"/H%s_%sS%s_stacked_avg.csv"%(H_num, station_color, station_num)), main_avg_data, fmt='%s', delimiter=',',header=headers,comments='')

    del main_data
    print("============================ Next Station ==========================================")


'''
Add 10 sec to timestamp?
'''