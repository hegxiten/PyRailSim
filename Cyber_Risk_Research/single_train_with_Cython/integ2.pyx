import networkx as nx
import matplotlib.pyplot as plt
import simpy
import numpy as np
import time
import collections
from collections import defaultdict
from scipy.interpolate import interp1d
import heapq
# import pandas as pd



def innerloop(self_number, rank, self_one_schedule, self_all_schedule, n, self_refresh, self_time, self_is_DoS, self_DoS_begin_ticks, self_DoS_end_ticks, self_DoS_block, self_cur_block, self_distance, self_sum_block_dis, self_block, self_speed, self_siding, self_pos, self_ncolor, self_labels, self_pos_labels, self_T, headway):
    def get_sum_and_cur_block(number):
        # if (distance > block_begin), block go further; if (distance < block_end), block go close.
        while not (self_sum_block_dis[number] - self_block[self_cur_block[number]]) < self_distance[number] <= (
        self_sum_block_dis[number]):
            if self_distance[number] >= self_sum_block_dis[number]:
                self_sum_block_dis[number] += self_block[self_cur_block[number]]
                self_cur_block[number] += 1

            elif self_distance[number] <= (self_sum_block_dis[number] - self_block[self_cur_block[number]]):
                self_sum_block_dis[number] -= self_block[self_cur_block[number]]
                self_cur_block[number] -= 1

    m = self_number + 1
    x = 1
    while x < m:
        i = rank[x]
        self_one_detail = {}
        self_time[i] += self_refresh * 60
        if self_is_DoS is True:
            # self.time[n] is (the time for a train to move) + (begin time), so self.train[1] is current time.
            if self_DoS_begin_ticks < self_time[1] < self_DoS_end_ticks:
                if self_cur_block[i] != self_DoS_block:
                    self_distance[i] += self_speed[i] * self_refresh
                    get_sum_and_cur_block(i)
            else:
                self_distance[i] += self_speed[i] * self_refresh
                get_sum_and_cur_block(i)

        elif self_is_DoS is False:
            self_distance[i] += self_speed[i] * self_refresh
            get_sum_and_cur_block(i)

        '''
        Traverse the rank of all train, if low rank catch up high rank, it should follow instead of surpass. 
        Unless there is a siding.
        '''
        if x > 1:
            # The block position of prev train and current train
            '''
            Overtake Policy:

            # when block small enough and speed large enough, there would be a bug
            '''
            if self_cur_block[rank[x - 1]] <= self_cur_block[rank[x]] + 1:
                for j in self_siding:
                    if self_cur_block[rank[x - 1]] == j:
                        if self_speed[rank[x - 1]] < self_speed[rank[x]]:
                            rank[x], rank[x - 1] = rank[x - 1], rank[x]
                            self_distance[rank[x]] -= self_speed[rank[x]] * self_refresh
                            get_sum_and_cur_block(i)
                        break

                    elif j == self_siding[-1]:
                        self_distance[rank[x]] = self_sum_block_dis[rank[x]] - self_block[
                            self_cur_block[rank[x]]]
                        self_distance[rank[x]] = max(0, self_distance[rank[x]])
                get_sum_and_cur_block(i)

        k = self_cur_block[i]


        # set the color of train node
        if 0 < k < len(self_pos):
            self_ncolor[k - 1] = 'r'

        if 0 < k < len(self_pos):
            self_labels[k] = i
            self_pos_labels[k] = self_pos[k]

        self_one_detail['time'] = round(self_speed[i], 2)
        self_one_detail['speed(mils/min)'] = round(self_speed[i], 2)
        self_one_detail['distance(miles)'] = round(self_distance[i], 2)
        self_one_detail['headway(mins)'] = round(headway, 2)
        time_standard = self_T.strftime("%Y-%m-%d %H:%M:%S", self_T.localtime(self_time[1]))
        self_one_schedule[time_standard] = self_one_detail
        self_all_schedule[i][time_standard] = self_one_schedule[time_standard]
        n += 1
        x += 1

    return self_number, rank, self_one_schedule, self_all_schedule, n, self_refresh, self_time, self_is_DoS, self_DoS_begin_ticks, self_DoS_end_ticks, self_DoS_block, self_cur_block, self_distance, self_sum_block_dis, self_block, self_speed, self_siding, self_pos, self_ncolor, self_labels, self_pos_labels, self_T, headway