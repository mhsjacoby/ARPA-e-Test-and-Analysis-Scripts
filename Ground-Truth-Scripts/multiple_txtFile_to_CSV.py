import os
import sys
import csv
import ast
import json
from datetime import datetime
import numpy as np
import pandas as pd


"""
Line format:
Gregor entered at July 16, 2019 at 07:04PM.
Gregor exited at April 1, 2019 at 01:56PM.
"""

def read_in_file(original_files, fname):
    with open(original_files[0], 'r') as f1, open( original_files[1], 'r') as f2: 
        with open(fname, 'w+') as new_f:
            file1_read, file2_read = csv.reader(f1, delimiter = ' '), csv.reader(f2, delimiter = ' ') 
            i = 0
            new_file = csv.writer(new_f, delimiter = ',')

            for r1, r2 in zip(file1_read, file2_read):
                name1, status1, name2, status2 = r1[0], r1[1], r2[0], r2[1]
                time1, time2 = ' '.join(r1[3:]).strip('.'), ' '.join(r2[3:]).strip('.')
                entry1, entry2 = [name1, status1, time1], [name2, status2, time2]
                new_file.writerow(entry1)
                new_file.writerow(entry2)
            print(i)

# def read_in_file(original_files, fname):
#     with open(original_files[0], 'r') as f1, open( original_files[1], 'r') as f2: 
#         with open(fname, 'w+') as new_f:
#             file1_read, file2_read = csv.reader(f1, delimiter = ' '), csv.reader(f2, delimiter = ' ') 
#             i = 0
#             for r1 in file2_read:
#                 name1, status1 = r1[0], r1[1]
#                 time1= ' '.join(r1[3:]).strip('.')
#                 new_file = csv.writer(new_f, delimiter = ',')
#                 entry1 = [name1, status1, time1]
#                 print(entry1)
#                 i+=1

#                 new_file.writerow(entry1)
#             print(i)



file_loc = '/Users/maggie/Desktop'
text_files = ['Gregor_red_p2.txt','Gregor_red_p1.txt']
store_loc = '/Users/maggie/Desktop'
fname = 'Gregor-Round2.csv'

read_files = [os.path.join(file_loc, f) for f in text_files]
write_file = os.path.join(store_loc, fname) 

read_in_file(read_files, write_file)