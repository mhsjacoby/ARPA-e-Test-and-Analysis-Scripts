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
        # self.min_x = 0
        # self.max_x = 20
        # self.instant=0
        #self.json_name='/mnt/vdb/BS2/env_params/2019-02-10/' #Parameterize this to change date and sensor hub
        #self.json_time=1515 #periodically increase by 5 minutes
        #self.dist=[0,0,0,0,0] #may use append style
        #self.dist_data = []
        #self.times = []
        self.pi_address = '192.168.0.112'
        self.local_path = '/Users/maggie/Desktop/json'
        self.look_back = 5
        self.now = datetime.now()
        self.day_now = self.now.strftime('%Y-%m-%d')
        self.root_addr = '/home/pi/env_params/' + str(self.day_now)
        self.max = 36
        self.times = deque(maxlen = self.max)
        self.dist_data = deque(maxlen = self.max)
        self.first_pull = True
        self.i = 0


    def get_initial(self):
        t = self.now
        prev_mins = []
        for x in range(1, self.look_back + 1):
            pt = t - timedelta(minutes = x)
            prev_mins.append(self.day_now +' '+ str(pt.hour).zfill(2) + str(pt.minute).zfill(2) + '_env_params.json')
        self.get_json(prev_mins)
        self.store_data()
        #self.first_pull = False


    def get_all(self):
        t = datetime.now()
        last_min = []
        for x in range(1,2):
            pt = t-timedelta(minutes = x)
            last_min.append(self.day_now +' '+ str(pt.hour).zfill(2) + str(pt.minute).zfill(2) + '_env_params.json')
        print(last_min)
        self.get_json(last_min)

    def store_data(self):
        for time_point in self.data:
            self.dist_data.append(time_point['dist_mm'])
            #elapsed_secs = datetime.strptime(time_point['time'],'%Y-%m-%dT%H:%M:%SZ').strftime('%M%S')
            #self.times.append(datetime.strptime(time_point['time'],'%Y-%m-%dT%H:%M:%SZ').strftime('%M%S'))
            self.times.append(self.i)
            self.i += 10
            # if self.first_pull == False:
            #     #self.draw_plot()
            #     time.sleep(10)





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
                                self.data = json.load(json_file)

            # def store_data(self):                    
                                # for time_point in data:
                                #     self.dist_data.append(time_point['dist_mm'])
                                #     elapsed_secs = datetime.strptime(time_point['time'],'%Y-%m-%dT%H:%M:%SZ').strftime('%M%S')
                                #     #self.times.append(datetime.strptime(time_point['time'],'%Y-%m-%dT%H:%M:%SZ').strftime('%M%S'))
                                #     self.times.append(self.i)
                                #     self.i += 10
                                #     if self.first_pull == False:
                                #         #self.draw_plot()
                                #         time.sleep(10)
                            #self.x, self.y = list(self.times), list(self.dist_data)


    # def animate(self):
    #     self.get_all()
    #     self.ax1.clear()
    #     self.ax1.plot(list(self.times), list(self.dist_data))

    #     plt.xlabel('Elapsed Time (s)')
    #     plt.ylabel('Distance (mm)')
    #     #plt.xticks(np.range(1, 36, 1.0))
    #     plt.title('Distance from sensor to nearest object')	


    # def draw_animation(self):
    #     fig = plt.figure()
    #     self.ax1 = fig.add_subplot(1,1,1)

    #     anim = animation.FuncAnimation(fig, self.animate(), interval=1000)

    #     plt.show()
    
    def draw_plot(self):

        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1)    

        while True:
            
        ax1.clear()
        ax1.plot(self.times, self.dist_data)

        plt.xlabel('Elapsed Time (s)')
        plt.ylabel('Distance (mm)')
        #plt.xticks(np.range(1, 36, 1.0))
        plt.title('Distance from sensor to nearest object')
        plt.show()
        #time.sleep(10)
        	
    # def show_data(self):
    #     while True:
    #         print('{}:{}'.format(datetime.now().minute, datetime.now().second))
    #         print(list(self.times))
    #         #print(len(self.dist_data), self.dist_data[0])
    #         self.get_all()
    #         #time.sleep(10)


def main():
    plt.ion()
    self.get_initial()

    







if __name__ == '__main__':
    #plt.ion()
    start_time = sys.argv[1] if len(sys.argv) > 1 else None
    d = DynamicUpdatePlot(start_time)
    d.get_initial()

    # d.get_all()
    # #d.show_data()
    # #d.draw_plot()
    # #d.draw_animation()




    def animate(i):
        if datetime.now().second % 30 == 0:
            print(datetime.now().time)
            d.get_all()

        ax1.clear()

        for time_point in d.data:
            d.i += 10
            d.dist_data.append(time_point['dist_mm'])
            d.times.append(d.i)
            ax1.plot(list(d.times), list(d.dist_data))
            time.sleep(10)

        plt.xlabel('Elapsed Time (s)')
        plt.ylabel('Distance (mm)')
        #plt.xticks(np.range(1, 36, 1.0))
        plt.title('Distance from sensor to nearest object')	

    anim = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

    #d.draw()






    # def on_launch(self):
    #     #Set up plot
    #     self.figure, self.ax = plt.subplots()
    #     self.lines, = self.ax.plot([],[], 'o')
    #     #Autoscale on unknown axis and known lims on the other
    #     self.ax.set_autoscaley_on(True)
    #     self.ax.set_xlim(self.min_x, self.max_x)
    #     #Other stuff
    #     self.ax.grid()

    # def on_running(self, xdata, ydata, max_readings):
    #     #Update data (with the new _and_ the old points)
    #     self.lines.set_xdata(xdata)
    #     self.lines.set_ydata(ydata)
    #     #Need both of these in order to rescale
    #     self.ax.relim()
    #     self.ax.autoscale_view()
    #     if(max_readings%20==0):
    #         self.ax.set_xlim(self.min_x+max_readings, self.max_x+max_readings)
    #     #We need to draw *and* flush
    #     self.figure.canvas.draw()
    #     self.figure.canvas.flush_events()

    # def draw(self):
    #     max_readings=0
    #     self.on_launch()     
    #     xdata = []
    #     ydata = []
    #     while(True): #this is how many readings to plot 
    #         self.get_json(self.instant)
    #         for i in range(5):
    #             max_readings += 1
    #             xdata.append(max_readings)
    #             ydata.append(self.dist[i])
    #         self.on_running(xdata, ydata, max_readings)
    #         #time.sleep(1)
    #     return xdata, ydata

# def main():
#     plt.ion()
#     d = DynamicUpdatePlot()
#     #d.draw()

