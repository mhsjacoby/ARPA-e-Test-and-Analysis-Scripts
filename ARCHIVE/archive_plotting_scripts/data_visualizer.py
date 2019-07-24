import json
import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

class StaticPlot():
    def __init__(self, path1, path2, path3):
        self.root_directory = os.path.join(path1, path2)
        self.sensor_date = path2
        self.csv_name = path3 + '.csv'
        self.store_path = os.path.join(path1, 'HPD_csv')
        self.data = {'time':[], 'tvoc_ppb':[], 'temp_c':[], 'rh_percent':[], 'light_lux':[], 'co2eq_ppm':[], 'dist_mm':[],'tvoc_base':[], 'co2eq_base':[]}

    def mylistdir(self, directory):
        filelist = os.listdir(directory)
        return [x for x in filelist if not (x.startswith('.'))]      

    def read_in_data(self, path):
        with open(path, 'r') as f:
            self.data_dicts = json.loads(f.read())
            for time_point in self.data_dicts:
                for measure in time_point:
                    self.data[measure].append(time_point[measure])        

    def get_all_data(self, path):
        sub_folders = self.mylistdir(self.root_directory)
        for folder in sub_folders:
            file_path = os.path.join(self.root_directory, folder)
            sub_files = self.mylistdir(file_path)         
            for file in sub_files:
                data_path = os.path.join(file_path, file)
                self.read_in_data(os.path.join(file_path, file))

    def plotting(self):
        df = pd.DataFrame(self.data['temp_c'], index = self.data['time'])
        plt.figure()
        df.plot()



    def main(self):
        self.get_all_data(self.root_directory)
        new_df = pd.DataFrame.from_dict(self.data)
        write_path_name = os.path.join(self.store_path, self.csv_name)
        self.plotting()
        #new_df.to_csv(write_path_name)


if __name__ == '__main__':
    dynamic_path = sys.argv[1]
    csv_name = sys.argv[2]
    static_path = '/Users/maggie/Desktop/HPD_mobile'
    full_path = os.path.join(static_path, dynamic_path)
    P = StaticPlot(static_path, dynamic_path, csv_name)
    P.main()


