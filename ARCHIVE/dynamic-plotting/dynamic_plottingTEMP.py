import numpy as np
import matplotlib.pyplot as plt
import pysftp
import json
import time
import os
import sys
from datetime import datetime, timedelta
import matplotlib.animation as animation
from collections import deque

class DynamicUpdatePlot():
    def __init__(self, start_time):
        self.start_time = start_time
        self.temp_data = []
        self.times = []
        self.pi_address = '192.168.0.112'
        self.local_path = '/Users/maggie/Desktop/json'
        self.look_back = 3
        self.now = datetime.now()
        self.day_now = self.now.strftime('%Y-%m-%d')
        self.root_addr = '/home/pi/env_params/' + str(self.day_now)
        self.max = 6
        self.x = deque(maxlen = self.max)
        self.y = deque(maxlen = self.max)
        # self.first_pull = True
        # self.i = 0
        self.first_time = True


    def get_initial(self):
        t = self.now
        prev_mins = []
        for x in range(1, self.look_back + 1):
            pt = t - timedelta(minutes = x)
            prev_mins.append(self.day_now +' '+ str(pt.hour).zfill(2) + str(pt.minute).zfill(2) + '_env_params.json')
        self.get_json(prev_mins)






    def get_json(self, mins_to_pull):
        with pysftp.Connection(self.pi_address, username='pi', password='arpa-e') as sftp: 
            with sftp.cd(self.root_addr):
                hrs = sftp.listdir()[-2:]
                for hr in hrs:
                    with sftp.cd(os.path.join(self.root_addr, hr)):
                        retrieve_files = list(set(mins_to_pull) & set(sftp.listdir()))

                        for etd_file in sorted(retrieve_files):
                            local_dir = os.path.join(self.local_path, self.day_now)
                            if not os.path.isdir(local_dir):
                                os.makedirs(local_dir)

                            remote_path = os.path.join(self.root_addr, hr, etd_file)
                            local_path = os.path.join(local_dir, etd_file)
                            if not os.path.isfile(local_path):
                                try:
                                    env_json_file = sftp.get(remote_path, local_path)
                                    print('file downloaded: {}'.format(etd_file))
                                except Exception as e:
                                    print('Error: {}'.format(e))

                            with open(local_path) as json_file:
                                data = json.load(json_file)
                                for time_point in data:
                                    
                                    now_time = datetime.strptime(time_point['time'],'%Y-%m-%dT%H:%M:%SZ')

                                    if self.first_time == True:
                                        self.t_start = now_time
                                        self.first_time = False

                                    elapsed_time = now_time - self.t_start
                                    elapsed_sec = elapsed_time.seconds
                                    self.times.append(elapsed_sec)
                                    self.temp_data.append(time_point['temp_c'])


    def plot_lines(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1)

        for x,y in zip(self.times[0:self.max], self.temp_data[0:self.max]):
           self.x.append(x), self.y.append(y) 
        print(len(self.x))
        
        


        plt.xlabel('Elapsed Time (s)')
        plt.ylabel('Temperature (C)')
        plt.title('Temperature')	

        line1, = ax1.plot(self.x, self.y, 'b-')
        ax1.set_ylim(15, 35)

        for x,y in zip(self.times[self.max:], self.temp_data[self.max:]):
            self.x.append(x), self.y.append(y)
            print(list(self.x))
            print(list(self.y))

            line1.set_xdata(list(self.x))
            line1.set_ydata(list(self.y))
            ax1.set_xlim(self.x[0], self.x[-1])
            plt.pause(0.001)
            fig.canvas.draw()
            time.sleep(10)
            fig.canvas.flush_events()





    def main(self):
        plt.ion()
        self.get_initial()
        self.plot_lines()
        #plt.ioff()
        plt.show()





if __name__ == '__main__':

    start_time = sys.argv[1] if len(sys.argv) > 1 else None
    d = DynamicUpdatePlot(start_time)
    d.main()

