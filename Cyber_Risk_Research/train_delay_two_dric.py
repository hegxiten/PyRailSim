import time
from generate_train_two_dric import generate_train_two_dric


class train_delay_two_dric:
    'delay'

    # the format of DoS time is 'yyyy-mm-dd hh:mm:ss', and it must be a string.
    # ex: DoS_time = '2016-05-05 20:28:54'
    def __init__(self, X, Y, DoS_time):
        self.X = X
        self.Y = Y
        self.DoS_time = DoS_time

    def print_diff(self):
        # exp_MGT = input('Expection of weight is: ')
        # var_MGT = input('Variance of weight is: ')
        # exp_buffer = input('Expection of buffer time is: ')
        # var_buffer = input('Variance of buffer time is: ')
        # begin_time = input('The begin time is(''yyyy-mm-dd hh:mm:ss''): ')
        # end_time = input('The end time is(''yyyy-mm-dd hh:mm:ss''): ')

        exp_MGT = 5000
        var_MGT = 1500
        exp_buffer = 15
        var_buffer = 3
        begin_time = '2018-01-01 00:00:00'
        end_time = '2018-01-05 00:00:00'

        begin = time.mktime(time.strptime(begin_time, "%Y-%m-%d %H:%M:%S"))
        end = time.mktime(time.strptime(end_time, "%Y-%m-%d %H:%M:%S"))
        num_train = (end - begin) / 60 / exp_buffer
        general_train = generate_train_two_dric(exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time)
        # map_value contains [number, train_time, train_direction(cur_direction), weight[n], variance[n]]
        orig_schedule = general_train.generate_schedule()

        # transfer time stamp into ticks
        DoS_ticks = time.mktime(time.strptime(self.DoS_time, "%Y-%m-%d %H:%M:%S"))

        # when error
        if DoS_ticks > end or DoS_ticks < begin:
            print "The DoS time is not in the right section."
            return 0

        # num_first_delay is the number of first delay train
        num_first_delay = 1
        ticks_first_delay = begin

        while ticks_first_delay < DoS_ticks:
            ticks_first_delay = time.mktime(time.strptime(orig_schedule[num_first_delay]['time_arrival'], "%Y-%m-%d %H:%M:%S"))
            num_first_delay += 1
        num_first_delay -= 1

        # calculate delay schedule. num_delay is the number of delay trains.
        delay_schedule = {}
        n = 1
        ticks = DoS_ticks + (self.X + self.Y) * 60 * 60
        print 'Delay happens from Train ' + str(num_first_delay) + '\nSchedule:'

        cur_direction = orig_schedule[1]['direction']
        while 1:
            delay_value = {}
            # train time
            if n > 1:
                # direction
                cur_direction = orig_schedule[n]['direction']
                prev_direction = orig_schedule[n - 1]['direction']

                if cur_direction != prev_direction:
                    ticks += 28 * 60
                elif cur_direction == prev_direction:
                    ticks += 3 * 60

            # get diff time between 'orig' and 'delay'
            orig_time = orig_schedule[num_first_delay + n - 1]['time_arrival']
            orig_ticks = time.mktime(time.strptime(orig_time, "%Y-%m-%d %H:%M:%S"))
            time_diff = int((ticks - orig_ticks) / 60)
            if time_diff < 0:
                break
            # fill '0' before n, ex: turn '1' into '0001'
            m = "%04d" % (num_first_delay + n)
            # get the schedule of every delay train
            train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))

            delay_value['time_arrival'] = orig_schedule[num_first_delay + n - 1]['time_arrival']
            delay_value['time_departure'] = train_time
            delay_value['delay'] = time_diff
            delay_value['direction'] = cur_direction
            delay_value['headway_prev'] = orig_schedule[num_first_delay + n - 1]['headway_prev']
            delay_value['headway_next'] = orig_schedule[num_first_delay + n - 1]['headway_next']
            delay_value['total_weight'] = orig_schedule[num_first_delay + n - 1]['total_weight']
            delay_value['index'] = orig_schedule[num_first_delay + n - 1]['index']
            delay_value['misrouted'] = 'False'
            delay_value['train_type'] = 'Default'
            delay_value['train_length'] = None
            delay_value['train_speed'] = None
            delay_value['train_acceleration'] = None
            delay_value['train_deceleration'] = None
            delay_value['Future_parameters'] = None

            delay_schedule[num_first_delay + n - 1] = delay_value
            n += 1
            if num_first_delay + n - 1 > len(orig_schedule):
                break

        i = 1
        ans = {}
        while i < num_first_delay:
            ans[i] = orig_schedule[i]
            i += 1

        j = num_first_delay
        while j < num_first_delay + len(delay_schedule) - 1:
            ans[j] = delay_schedule[j]
            j += 1

        k = num_first_delay + len(delay_schedule) - 1
        while k < len(orig_schedule):
            ans[k] = orig_schedule[k]
            k += 1

        return orig_schedule, ans
