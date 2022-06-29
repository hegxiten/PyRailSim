#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    PyRailSim
    Copyright (C) 2019  Zezhou Wang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def timestamper(timestamp):
    time_str = datetime.strftime(datetime.fromtimestamp(timestamp), "%Y-%m-%d %H:%M:%S")
    return '[' + time_str + ']'


def string_diagram(sys):
    '''To draw the string diagram based on the schedule dictionary for all the trains. 
    '''
    plt.rcParams['figure.dpi'] = 200
    plt.ion()
    start_time, end_time = sys.init_time, sys.term_time
    colors = ['red', 'green', 'blue', 'black', 'orange', 'cyan', 'magenta']
    color_num = len(colors)
    t_color = [colors[i % color_num] for i in range(len(sys.trains))]
    x, y = [], []
    plt.clf()
    for i in range(len(sys.trains)):
        x.append([mdates.date2num(datetime.fromtimestamp(j)) for (j, _) in sys.trains[i].time_pos_list])
        y.append([j for (_, j) in sys.trains[i].time_pos_list])
        plt.plot([mdates.date2num(datetime.fromtimestamp(j)) for (j, _) in sys.trains[i].time_pos_list], \
                 [j for (_, j) in sys.trains[i].time_pos_list], color=t_color[i])

    train_idx = list(range(len(sys.trains)))
    min_t, max_t = min([i[0] for i in x if i]), max([i[-1] for i in x if i])

    plt.title('String Diagram')
    hours = mdates.HourLocator()
    minutes = mdates.MinuteLocator()
    seconds = mdates.SecondLocator()
    dateFmt = mdates.DateFormatter("%H:%M")
    plt.gca().xaxis.set_major_locator(hours)
    plt.gca().xaxis.set_minor_locator(minutes)
    plt.gca().xaxis.set_major_formatter(dateFmt)
    plt.xticks(rotation=90)
    plt.grid(True, linestyle="-.", color="r", linewidth="0.1")
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Mile Post/miles')
    plt.axis([(datetime.fromtimestamp(start_time - 500)), \
              (datetime.fromtimestamp(end_time + 500)), -5, 55])
    #     ===============================================================================
    # time_length = int(end_time - start_time)
    # step_size = 10
    # for start in range(1, int(time_length + 1), int(step_size)):
    #     plt.axis([(datetime.fromtimestamp(start_time - 500)), \
    #         (datetime.fromtimestamp(end_time + 500)), -5 , 55])

    #     for n in range(len(x)-1):
    #         new_x_y = [[mdates.date2num(datetime.fromtimestamp(i)), j] for i, j in zip(x[n], y[n]) if i < start_time + start and i > start_time + start - 1 - step_size]
    #         new_x = []
    #         new_y = []
    #         for i , j in new_x_y:
    #             new_x.append(i)
    #             new_y.append(j)
    #         if(len(new_x) == 0):
    #             continue
    #         plt.plot(new_x, new_y, color=t_color[n])
    #         # print('==============')
    #         # print('Length of new_x: {}'.format(len(new_x)))
    #         # print('Length of new_y: {}'.format(len(new_y)))
    #     plt.pause(0.00001)
    #     ===============================================================================
    plt.gca().axhspan(15, 20, color='yellow', alpha=0.5)
    plt.gca().axhspan(30, 35, color='yellow', alpha=0.6)
    plt.gca().axhspan(25, 40, color='orange', alpha=0.3)
    # plt.gca().axvspan((datetime.fromtimestamp(start_time + 90 * 60)),(datetime.fromtimestamp(start_time + 150 * 60)),color='black',alpha=0.5)
    plt.pause(1)
    plt.ioff()
    plt.show()


def speed_curve(sys, train, scatter=False):
    '''To draw the speed curve based on a train's mileposts and speed . 
    '''
    colors = ['red', 'green', 'purple']
    mp, spd, spdlmt, tgt_spd = [], [], [], []
    for i in range(len(train.pos_spd_list)):
        mp.append(train.pos_spd_list[i][0])
        spd.append(abs(train.pos_spd_list[i][1] * 3600))
        spdlmt.append(train.pos_spd_list[i][2] * 3600)
        tgt_spd.append(train.pos_spd_list[i][3] * 3600)

    min_mp, max_mp = min(mp), max(mp)

    plt.ion()
    plt.title('Speed Curve')
    plt.xticks(rotation=90)
    plt.grid(True, linestyle="-.", color="r", linewidth="0.1")
    plt.legend()
    plt.xlabel('Mile Post/miles')
    plt.ylabel('MPH')
    if not scatter:
        plt.plot(mp, spd, color=colors[1])  # train speed
        plt.plot(mp, spdlmt, color=colors[0])  # train speed lmt
        # plt.plot(mp, tgt_spd, '--', color=colors[2])  # train tgt speed
    if scatter:
        plt.scatter(mp, spd, color=colors[1])  # train speed
        plt.scatter(mp, spdlmt, color=colors[0])  # train speed lmt
        # plt.scatter(mp, tgt_spd, color=colors[2])  # train tgt speed
    plt.figure(figsize=(18, 16), dpi=80, facecolor='w', edgecolor='k')
    plt.rcParams['figure.dpi'] = 200
    import pylab;
    pylab.rcParams['figure.figsize'] = (15.0, 8.0)
    plt.pause(0.01)

#
# def simulation_setup():
#     sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
#     sim_term_time = datetime.strptime('2018-01-10 12:30:00', "%Y-%m-%d %H:%M:%S")
#     spd_container = [random.uniform(0.01, 0.02) for i in range(20)]
#     acc_container = [0.5 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15) for i in range(20)]
#     dcc_container = [0.2 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15) for i in range(20)]
#     headway = 300 + random.random() * 400
#     sys = System(sim_init_time, spd_container, acc_container, dcc_container,
#                  term_time=sim_term_time,
#                  dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],
#                  dos_pos=(15, 20),
#                  headway=headway,
#                  refresh_time=50)
#     dp = Dispatcher(sys)
#     return sys

#
# def launch(sys, downtrain=True):
#     while sys.sys_time - sys.init_time <= sys.term_time - sys.init_time:
#         _semaphore_to_return = False
#         for t in sys.trains:
#             sys.dispatcher.request_routing(t)
#             t.move()
#         if sys.sys_time + sys.refresh_time - sys.last_train_init_time >= simulation_core.network.System.system.headway:
#             if downtrain:
#                 if not sys.signal_points[0].curr_train_with_route.keys():
#                     if all([t.curr_routing_path_segment != ((None, None), (sys.signal_points[0], 0)) for t in
#                             sys.trains]):
#                         if not sys.signal_points[0].track_by_port[1].trains:
#                             t = sys.generate_train(sys.signal_points[0], 0,
#                                                    sys.signal_points[10], 1,
#                                                    length=1)
#             else:
#                 if not sys.signal_points[10].curr_train_with_route.keys():
#                     if all([t.curr_routing_path_segment != ((None, None), (sys.signal_points[10], 1)) for t in
#                             sys.trains]):
#                         if not sys.signal_points[10].track_by_port[0].trains:
#                             t = sys.generate_train(sys.signal_points[10], 1,
#                                                    sys.signal_points[0], 0,
#                                                    length=1)
#         sys.sys_time += sys.refresh_time
#

if __name__ == "__main__":
    pass
    # sys = simulation_setup()
    # launch(sys)
    # string_diagram(sys)
    # format = "%(asctime)s: %(message)s"
    # logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    # logging.info("Main    : before simulator thread starts")
    # sys_launch_thread = threading.Thread(
    #     target=sys.launch,
    #     kwargs={'launch_duration': (sys.term_time - sys.init_time)})
    # logging.info("Main    : before running thread")
    # sys_launch_thread.start()
    # logging.info("Main    : wait for the thread to finish")
    # sys_launch_thread.join()
    # logging.info("Main    : all done")

    # # https://medium.com/@grvsinghal/speed-up-your-python-code-using-multiprocessing-on-windows-and-jupyter-or-ipython-2714b49d6fac

    # sys.launch(launch_duration=(sys.term_time - sys.init_time))

    # plt.rcParams['figure.dpi'] = 100  # set the canvas dpi as 100
    # fig = plt.figure(figsize=(8, 6))
    # ax1 = fig.add_subplot(1, 1, 1)
    # hours = mdates.HourLocator()
    # minutes = mdates.MinuteLocator()
    # seconds = mdates.SecondLocator()
    # dateFmt = mdates.DateFormatter("%H:%M")
    # fig.suptitle('String Diagram')
    # ax1.xaxis.set_major_locator(hours)
    # ax1.xaxis.set_minor_locator(minutes)
    # ax1.xaxis.set_major_formatter(dateFmt)
    # plt.xticks(rotation=90)
    # plt.grid(True, linestyle="-.", color="r", linewidth="0.1")
    # plt.legend()
    # plt.xlabel('Time')
    # plt.ylabel('Mile Post/miles')
    # plt.axis([(datetime.fromtimestamp(sys.init_time - 500)),
    #         (datetime.fromtimestamp(sys.term_time + 500)), -5, 55])
