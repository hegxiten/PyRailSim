# 2 problems:  num_delay & orig_schedule

import time
from generate_train import generate_train


class train_delay:
    'delay'

    # the format of DoS time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex: DoS_time = '2016-05-05 20:28:54'
    def __init__(self, X, Y, DoS_time):
        self.X = X
        self.Y = Y
        self.DoS_time = DoS_time

    def print_diff(self):
        exp_MGT = input('Expection of weight is: ')
        var_MGT = input('Variance of weight is: ')
        exp_buffer = input('Expection of buffer time is: ')
        var_buffer = input('Variance of buffer time is: ')
        begin_time = input('The begin time is(''yyyy-mm-dd hh:mm:ss''): ')
        end_time = input('The end time is(''yyyy-mm-dd hh:mm:ss''): ')

        # exp_MGT = 5000
        # var_MGT = 1500
        # exp_buffer = 20
        # var_buffer = 3
        # begin_time = '2016-05-05 00:00:00'
        # end_time = '2016-05-07 00:00:00'

        begin = time.mktime(time.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
        end = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
        num_train = (end - begin) / 60 / exp_buffer
        general_train = generate_train(exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time)
        # map_value = number, train_time, train_direction(cur_direction), weight[n], variance[n]
        orig_schedule = general_train.generate_schedule()

        # transfer str into int, store it into map
        DoS_ticks = time.mktime(time.strptime(self.DoS_time, "%Y-%m-%d %H:%M:%S"))

        if DoS_ticks > end or DoS_ticks < begin:
            print "The DoS time is not in the right section."
            return 0

        # num_first_delay is the number of first delay train
        num_first_delay = 0
        ticks_first_delay = begin
        while ticks_first_delay < DoS_ticks:
            variance = orig_schedule[num_first_delay][4]
            ticks_first_delay += variance * 60
            num_first_delay += 1

        # num_delay is the number of delay train
        num_delay = 0
        traffic = 0.0
        while traffic < (self.X + self.Y) * 60:
            time_buffer = orig_schedule[num_delay][4]
            traffic += time_buffer - 3
            num_delay += 1

        # calculate delay schedule. num_delay is the number of delay trains.
        delay_schedule = {}
        n = 1
        print 'Delay happens from Train ' + str(num_first_delay) + '\nSchedule:'
        while n <= num_delay:
            delay_value = []
            # train time
            ticks = DoS_ticks + (self.X + self.Y) * 60 * 60
            # direction
            cur_direction = orig_schedule[n][2]
            prev_direction = orig_schedule[n - 1][2]

            if cur_direction != prev_direction:
                ticks += 28 * 60
            elif cur_direction == prev_direction:
                ticks += 3 * 60

            # fill '0' before n, ex: turn '1' into '0001'
            m = "%04d" % num_first_delay
            # get the schedule of every delay train
            train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
            delay_value.append(m)
            delay_value.append(train_time)
            delay_value.append(cur_direction)
            delay_value.append(orig_schedule[n - 1][3])
            delay_value.append(orig_schedule[n - 1][4])
            orig_time = orig_schedule[n - 1][1]
            orig_ticks = time.mktime(time.strptime(orig_time, "%Y-%m-%d %H:%M:%S"))
            delay_value.append((ticks - orig_ticks) / 60)
            # print (ticks - orig_ticks) / 60
            # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks)), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(orig_ticks))
            delay_schedule[n] = delay_value
            print 'Train ' + str(delay_schedule[n][0]) + ' ' + str(delay_schedule[n][1]) + ' ' + delay_schedule[n][2] + ' ' + str(delay_schedule[n][3]) + ' Tons' + ' Delay: ' + str(int(delay_schedule[n][5])) + ' mins'
            n += 1