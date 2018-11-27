import time
from generate_train_two_dirc import generate_train_two_dirc


class xy_maxdelay:
    'delay 1 dirc'

    # the format of DoS time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex: DoS_time = '2016-05-05 20:28:54'
    def __init__(self, X, Y, DoS_time):
        self.X = X
        self.Y = Y
        self.DoS_time = DoS_time


    def print_diff(self):
        self.Y = 0
        list_max_delay = {}
        max_delay = 0
        for x in range(1, 22):
            self.X = x

            list_max_delay[x] = {}

            exp_MGT = 5000
            var_MGT = 1500
            exp_headway = 20
            var_buffer = 3
            begin_time = '2018-01-01 00:00:00'
            end_time = '2018-01-10 00:00:00'

            self.begin = time.mktime(time.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
            self.end = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
            num_train = (self.end - self.begin) / 60 / exp_headway
            a = generate_train_two_dirc(exp_MGT, var_MGT, exp_headway, var_buffer, begin_time, end_time)
            # map_value = number, train_time, train_direction(cur_direction), weight[n], variance[n]
            orig_schedule = a.generate_schedule()

            # transfer str into int, store it into map
            DoS_ticks = time.mktime(time.strptime(self.DoS_time, "%Y-%m-%d %H:%M:%S"))

            if DoS_ticks > self.end or DoS_ticks < self.begin:
                print "The DoS time is not in the right section."
                return 0

            # num_first_delay is the number of first delay train
            num_first_delay = 1
            self.ticks_first_delay = self.begin
            while self.ticks_first_delay < DoS_ticks:
                self.ticks_first_delay = time.mktime(
                    time.strptime(orig_schedule[num_first_delay]['time_arrival'], "%Y-%m-%d %H:%M:%S"))
                num_first_delay += 1
            num_first_delay -= 1

            # calculate delay schedule. num_delay is the number of delay trains.
            delay_schedule = {}
            n = 1
            ticks = DoS_ticks + (self.X + self.Y) * 60 * 60

            while 1:
                delay_value = {}
                # train time
                train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
                ticks += 3 * 60
                # fill '0' before n, ex: turn '1' into '0001'
                m = "%04d" % (num_first_delay + n)

                orig_time = orig_schedule[num_first_delay + n - 1]['time_arrival']
                orig_ticks = time.mktime(time.strptime(orig_time, "%Y-%m-%d %H:%M:%S"))
                time_diff = int((ticks - orig_ticks) / 60)
                max_delay = max(max_delay, time_diff)
                if time_diff < 0:
                    break
                print 'x= ', x
                list_max_delay[x]['X+Y'] = x
                list_max_delay[x]['delay_num'] = n

                # delay_schedule[num_first_delay + n - 1] = delay_value
                n += 1
        print list_max_delay
        return list_max_delay

