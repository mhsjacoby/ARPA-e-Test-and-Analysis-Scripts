import os
import sys
import csv
import ast
import json
from datetime import datetime
import numpy as np
import pandas as pd

class HomeOccupancy():
    def __init__(self, path, home, freq = 5):
        self.ground_path = os.path.join(path, 'GroundTruth')
        self.write_dir = os.path.join(path, 'Full_Occupancy_Files')
        self.occupant_names = []

    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if x.endswith('.csv')]

    def make_storage_directory(self, target_dir):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        return target_dir

    def get_ground_truth(self):
        occupant_files = self.mylistdir(self.ground_path)
        occupants = {}
        for occ in occupant_files:
            #occupant_name = occ.strip('.csv').split('-')[1] ## H3
            occupant_name = occ.strip('.csv').split('-')[0]  ## H1, H3-round2
            self.occupant_names.append(occupant_name)
            ishome = []
            with open(os.path.join(ground_path, occ)) as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=',')
                for row in csv_reader:
                    status, when = row[1], row[2].split('at')
                    #print(status, when)
                    dt_day = datetime.strptime(str(when[0] + when[1]), '%B %d, %Y  %I:%M%p')
                    ishome.append((status, dt_day))
            occupants[occupant_name] = ishome
        return occupants

    def main(self):
        occupancy = self.get_ground_truth()


    