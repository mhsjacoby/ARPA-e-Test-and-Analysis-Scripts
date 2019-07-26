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
        self.dist_data = []
        self.temp_data = []
        self.light_data = []
        self.eco2_data = []
        self.times = []
        self.pi_address = '192.168.0.112'
        self.local_path = '/Users/maggie/Desktop/json'
        self.look_back = 10
        self.now = datetime.now()
        self.day_now = self.now.strftime('%Y-%m-%d')
        self.root_addr = '/home/pi/env_params/' + str(self.day_now)
        self.max = 10
        self.x = deque(maxlen = self.max)
        self.y1 = deque(maxlen = self.max)
        self.y2 = deque(maxlen = self.max)
        self.y3 = deque(maxlen = self.max)
        self.y4 = deque(maxlen = self.max)

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
                                    self.dist_data.append(time_point['dist_mm'])
                                    self.temp_data.append(time_point['temp_c'])
                                    self.eco2_data.append(time_point['co2eq_ppm'])
                                    self.light_data.append(time_point['light_lux'])
                                    


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
    
    # def draw_plot(self):

    #     #while True:
    #     #self.get_all()
    #     fig = plt.figure()
    #     ax1 = fig.add_subplot(1,1,1)        
    #     ax1.clear()
    #     ax1.plot(self.times, self.dist_data)

    #     plt.xlabel('Elapsed Time (s)')
    #     plt.ylabel('Distance (mm)')
    #     #plt.xticks(np.range(1, 36, 1.0))
    #     plt.title('Distance from sensor to nearest object')
    #     plt.show()
    #     #time.sleep(10)
        	
    # def show_data(self):
    #     while True:
    #         print('{}:{}'.format(datetime.now().minute, datetime.now().second))
    #         print(list(self.times))
    #         #print(len(self.dist_data), self.dist_data[0])
    #         self.get_all()
    #         #time.sleep(10)

# def on_launch(self):
#         #Set up plot
#         self.figure, self.ax = plt.subplots()
#         self.lines, = self.ax.plot([],[], 'o')
#         #Autoscale on unknown axis and known lims on the other
#         self.ax.set_autoscaley_on(True)
#         self.ax.set_xlim(self.min_x, self.max_x)
#         #Other stuff
#         self.ax.grid()

    # def on_running(self, xdata, ydata, max_readings):
    #     #Update data (with the new _and_ the old points)
    #     self.lines.set_xdata(xdata)
    #     self.lines.set_ydata(ydata)
    #     #Need both of these in order to rescale
    #     self.ax.relim()
    #     self.ax.autoscale_view()
    #     if(max_readings%30==0): #adjust this to control how fast the graph slides rightwards
    #         self.ax.set_xlim(self.min_x+30, self.max_x+30)
    #     #We need to draw *and* flush
    #     self.figure.canvas.draw()
    #     self.figure.canvas.flush_events()

    # def draw(self):
    #     self.on_launch()     
    #     xdata = []
    #     ydata = []
    #     half_min_len=0
    #     inc_readings=0
    #     while(True): #this is how many readings to plot 
    #         self.get_json()
    #         max_readings=self.half_min_len
    #         for i in range(self.half_min_len,len(self.dist)):
    #             max_readings+=1 #time counter is incremented nonetheless
    #             inc_readings+=1
    #             if(self.dist[i]==-1):
    #                 print("break")
    #                 break #means new data has not been added
    #             if(self.dist[i]!=None):
    #                 #if(max_readings in xdata==False):
    #                 xdata.append(max_readings)
    #                 ydata.append(self.dist[i])
    #         self.on_running(xdata, ydata, inc_readings)
    #         time.sleep(1)
    #         #print("xdata ",xdata)
    #         #print("ydata ",ydata)
    #         if(len(xdata)>30): #Chop off the unnecessary data to prevent blow up
    #             xdata=xdata[30:]
    #             ydata=ydata[30:]
    #         self.write_to_csv()
    #         now = datetime.datetime.now()
    #         if(self.local_test==False):
    #             self.date=now.strftime("%Y-%m-%d") #uncomment to update dates
    #     return xdata, ydata

    def plot_lines(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(2,1,1)
        ax2 = fig.add_subplot(2,1,2)
        # ax3 = fig.add_subplot(2,2,3)
        # ax4 = fig.add_subplot(2,2,4)
        

        for x,y1,y2 in zip(self.times[0:self.max], self.dist_data[0:self.max], self.temp_data[0:self.max]):
           self.x.append(x), self.y1.append(y1), self.y2.append(y2) 
        

        ax1.xlabel('Elapsed Time (s)')
        ax1.ylabel('Distance (mm)')
        #ax1.title('Distance from sensor to nearest object')	

        ax2.xlabel('Elapsed Time (s)')
        ax2.ylabel('Temperature (C)')        
        #ax2.title('Temperature (C)')	

        line1, = ax1.plot(self.x, self.y1, 'b-')
        ax1.set_ylim(0,4000)

        line2, = ax2.plot(self.x, self.y2, 'g-')
        ax2.set_ylim(15,30)

        for x,y1,y2 in zip(self.times[self.max:], self.dist_data[self.max:]):
            self.x.append(x), self.y.append(y)

            #print(list(self.x), list(self.y))
            line1.set_xdata(list(self.x))
            line1.set_ydata(list(self.y1))
            ax1.set_xlim(self.x[0], self.x[-1])
            line2.set_xdata(list(self.x))
            line2.set_ydata(list(self.y2))
            ax2.set_xlim(self.x[0], self.x[-1])
            plt.pause(0.001)
            fig.canvas.draw()
            time.sleep(10)
            fig.canvas.flush_events()

        


            

        #line1.set_ydata(y)
        

        


        # for phase in np.linspace(0, 10*np.pi, 100):
        # line1.set_ydata(np.sin(0.5 * x + phase))
        # fig.canvas.draw()



    def main(self):
        plt.ion()
        self.get_initial()
        self.plot_lines()
        #plt.ioff()
        plt.show()
        
        # print(self.times)
        # print(self.dist_data)








if __name__ == '__main__':

    start_time = sys.argv[1] if len(sys.argv) > 1 else None
    d = DynamicUpdatePlot(start_time)
    d.main()


    # #d.show_data()
    # #d.draw_plot()
    # #d.draw_animation()




    # def animate(i):
    #     if datetime.now().second % 30 == 0:
    #         print(datetime.now().time)
    #         d.get_all()

    #     ax1.clear()

    #     for time_point in d.data:
    #         d.i += 10
    #         d.dist_data.append(time_point['dist_mm'])
    #         d.times.append(d.i)
    #         ax1.plot(list(d.times), list(d.dist_data))
    #         time.sleep(10)

    #     plt.xlabel('Elapsed Time (s)')
    #     plt.ylabel('Distance (mm)')
    #     #plt.xticks(np.range(1, 36, 1.0))
    #     plt.title('Distance from sensor to nearest object')	

    # anim = animation.FuncAnimation(fig, animate, interval=1000)
    # plt.show()

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

