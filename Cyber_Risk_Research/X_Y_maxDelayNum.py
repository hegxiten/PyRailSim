import time
from train_delay_one_dric import train_delay_one_dric


class X_Y_maxDelayNum:
    'delay 1 dric'

    # the format of DoS time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex: DoS_time = '2016-05-05 20:28:54'
    def __init__(self, DoS_time):
        self.DoS_time = DoS_time

    def drawA_B(self):
        lx = {}

        i = 0
        for x in range(0, 10):
            for y in range(0, 20):
                d = train_delay_one_dric(x, y, '2018-01-01 00:00:00')
                #time = (a.end - a.begin) / 60 / 60
                #b, c, delay_schedule = a.print_diff()
                # for j in range(0, 100):
                #     if time.mktime(time.strptime(delay_schedule[j][1], "%Y-%m-%d %H:%M:%S")) >= a.begin + x * 60 * 60:
                #         z = int(delay_schedule[j][0])
                a, b, c = d.print_diff()
                z = len(c)
                lx[i] = [x, y, z, 0, 0, 0]

                i += 1
        print lx
        return lx
