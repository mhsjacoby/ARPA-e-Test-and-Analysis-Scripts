import os
import pandas as pd
from datetime import datetime
import json
import ast
import sys

class PhotoChecker():
    def __init__(self, path_to_import_conf, write_file, display_output, server_id):
        self.conf_file_path = path_to_import_conf
        self.import_conf(self.conf_file_path)
        self.write_file = write_file
        self.display_output = display_output
        self.all_seconds = pd.date_range(self.b_dt, self.e_dt, freq = self.conf_dict['img_freq']).tolist()
        self.expect_num_photos = len(self.all_seconds)
        self.expect_num_directories = len(pd.date_range(self.b_dt, self.e_dt, freq = self.conf_dict["dir_create_freq"]).tolist())
        self.root_dir = os.path.join(self.conf_dict['root'], server_id, 'img')
        self.date_dirs = self.conf_dict['date_dirs']
        self.hrs_to_pass = self.conf_dict['hr_dirs_to_skip']
        self.count_61 = {}
        self.count_60 = {}
        self.count_other = {}
        self.total_pics = 0
        self.count_61_double_00 = 0
        self.duplicates = 0
        self.counter_min = 2000
        self.duplicates_ts = []
        self.pics = []
        self.start_time = datetime.now()
        self.server = server_id


    def import_conf(self, path):
        with open(path, 'r') as f:
            self.conf_dict = json.loads(f.read())
        self.b_dt = self.conf_dict['begin_dt']
        self.e_dt = self.conf_dict['end_dt']
        self.b_dt_as_dt = datetime.strptime(self.b_dt, '%Y-%m-%d %H:%M:%S')
        self.e_dt_as_dt = datetime.strptime(self.e_dt, '%Y-%m-%d %H:%M:%S')

    def finder(self):
        for pic in self.pics:
            dt = datetime.strptime(pic.split('_')[0], '%Y-%m-%d %H%M%S')
            try:
                ind = self.all_seconds.index(dt)
                self.all_seconds.pop(ind)
            except:
                self.duplicates += 1
                self.duplicates_ts.append(dt.strftime('%Y-%m-%d %H:%M:%S'))
                # print('Total duplicates: {}\tdt: {}'.format(self.duplicates, dt))
                pass

    def writer(self, output_dict):
        if self.write_file:
            b = 'test_output.json'
            write_file = os.path.join(self.root_dir, b)
            print('Writing file to: {}'.format(write_file))
            with open(write_file, 'w+') as f:
                f.write(json.dumps(output_dict))

    def displayer(self, output_dict):
        if self.display_output:
            print(output_dict)

    def configure_output(self):
        if self.write_file:
            missed_seconds = []

            for ts in self.all_seconds:
                missed_seconds.append(ts.strftime('%Y-%m-%d %H:%M:%S'))
            rt = datetime.now() - self.start_time
            mins = rt.seconds / 60

            unique_pics = self.total_pics - self.duplicates
            #total = unique_pics + len(self.all_seconds)
            #diff = total - self.expect_num_photos
            perc = unique_pics / self.expect_num_photos
            self.perc_cap = float("{0:.2f}".format(perc))

            output_dict = {
                'Configuration dict': self.conf_dict,
                'Expected number of photos': self.expect_num_photos,
                'Number of photos counted (including duplicates)': self.total_pics,
                'Total number of duplicates': self.duplicates,
                'Total runtime in minutes': mins,
                'Number of not captured photos': len(self.all_seconds),
                'Percent of photos captured': self.perc_cap,
                'Expected number of directories': self.expect_num_directories,
                'Number of directories w/60 photos': len(self.count_60),
                'Number of directories w/61 photos': len(self.count_61),
                'Number of directories w/61 photos and 2x 00 second photos': self.count_61_double_00,
                'Number of directories w/not 60 OR 61 photos': len(self.count_other),
                'Non-60 or 61 directories': self.count_other,
                'Timestamps of not captured photos': missed_seconds,
                'Duplicates': self.duplicates_ts
            }
        else:
            output_dict = []
        return output_dict



    def main(self):
        for d in self.date_dirs:
            hr_min_dirs = os.listdir(os.path.join(self.root_dir, d))
            for hr_min in hr_min_dirs:
                if not hr_min == '.DS_Store' and not hr_min in self.hrs_to_pass:
                    a = datetime.strptime((d + ' ' + hr_min), '%Y-%m-%d %H%M')
                    if a < self.b_dt_as_dt or a > self.e_dt_as_dt:
                        continue
                    else:
                        temp = os.path.join(self.root_dir, d, hr_min)
                        if os.path.isdir(temp):
                            self.pics = os.listdir(os.path.join(self.root_dir, d, hr_min))
                            self.pics = [x for x in self.pics if x.endswith('.png')]
                            self.finder()
                            self.total_pics += len(self.pics)
                            if self.total_pics > self.counter_min:
                                print('Counting picture: {}'.format(self.total_pics))
                                rt = datetime.now() - self.start_time
                                mins = rt.seconds / 60
                                print('Current runtime in mins: {}'.format(mins))
                                self.counter_min += 2000
                            if len(self.pics) == 61:
                                double_00 = [x for x in self.pics if x.split('_')[0].endswith('00')]
                                if len(double_00) == 2:
                                    self.count_61_double_00 += 1
                                self.count_61[os.path.join(d,hr_min)] = 61

                            elif len(self.pics) == 60:
                                self.count_60[os.path.join(d,hr_min)] = 60
                            else:
                                self.count_other[os.path.join(d,hr_min)] = len(self.pics)

                        else:
                            print('{} is not a dir'.format(temp))
        
        output_dict = self.configure_output()
        self.writer(output_dict)
        #self.displayer(output_dict)
        print('All done!' + str(self.server))
        return(self.perc_cap)


if __name__ == '__main__':
    """
    Example of full path to configuration files:
        /Users/corymosiman/Github/ARPA-E-Sensor/tests/img/conf/cnt_img_1_final_conf.json
        /Users/corymosiman/Github/ARPA-E-Sensor/tests/img/conf/cnt_img_2_final_conf.json
        /Users/corymosiman/Github/ARPA-E-Sensor/tests/img/conf/cnt_img_3_final_conf.json
    """
    path = sys.argv[1]
    sensors = []
    total_capture = {}

    with open(path, 'r') as f:
        conf_dict = json.loads(f.read()) 
        sensors = conf_dict['sensor_hubs']

    for server_id in sensors:
        a = PhotoChecker(path, True, False, server_id)
        capt = a.main()
        total_capture[server_id] = capt
  
    print(total_capture)





