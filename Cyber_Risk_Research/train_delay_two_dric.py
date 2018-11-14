import time
from generate_train import generate_train


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
        general_train = generate_train(exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time)
        # map_value contains [number, train_time, train_direction(cur_direction), weight[n], variance[n]]
        orig_schedule = general_train.generate_schedule()

        # transfer time stamp into ticks
        DoS_ticks = time.mktime(time.strptime(self.DoS_time, "%Y-%m-%d %H:%M:%S"))

        # when error
        if DoS_ticks > end or DoS_ticks < begin:
            print "The DoS time is not in the right section."
            return 0

        # num_first_delay is the number of first delay train
        num_first_delay = 0
        ticks_first_delay = begin

        while ticks_first_delay < DoS_ticks:
            ticks_first_delay = time.mktime(time.strptime(orig_schedule[num_first_delay][1], "%Y-%m-%d %H:%M:%S"))
            num_first_delay += 1
        #num_first_delay -= 1

        # calculate delay schedule. num_delay is the number of delay trains.
        delay_schedule = {}
        n = 0
        ticks = DoS_ticks + (self.X + self.Y) * 60 * 60
        print 'Delay happens from Train ' + str(num_first_delay) + '\nSchedule:'
        print len(orig_schedule)
        print orig_schedule
        cur_direction = orig_schedule[0][2]
        while num_first_delay + n - 1 < num_train:
            delay_value = []
            # train time
            if n > 0:
                # direction
                cur_direction = orig_schedule[n][2]
                prev_direction = orig_schedule[n - 1][2]

                if cur_direction != prev_direction:
                    ticks += 28 * 60
                elif cur_direction == prev_direction:
                    ticks += 3 * 60

            # fill '0' before n, ex: turn '1' into '0001'
            m = "%04d" % (num_first_delay + n )
            # get the schedule of every delay train
            train_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
            delay_value.append(m)
            delay_value.append(train_time)
            delay_value.append(cur_direction)
            delay_value.append(orig_schedule[num_first_delay + n - 1][3])

            # get diff time between 'orig' and 'delay'
            delay_value.append(orig_schedule[num_first_delay + n - 1][4])
            orig_time = orig_schedule[num_first_delay + n - 1][1]
            orig_ticks = time.mktime(time.strptime(orig_time, "%Y-%m-%d %H:%M:%S"))
            time_diff = int((ticks - orig_ticks) / 60)
            # print orig_time, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))

            delay_value.append(time_diff)

            # print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ticks))
            delay_schedule[n] = delay_value
            n += 1

        i = 0
        ans = {}
        while i <= num_first_delay:
            ans[i] = orig_schedule[i]
            i += 1

        j = num_first_delay
        while j < num_first_delay + len(delay_schedule) - 1:
            ans[j] = delay_schedule[j - num_first_delay + 1]
            j += 1

        k = num_first_delay + len(delay_schedule) - 1
        while k < len(orig_schedule):
            ans[k] = orig_schedule[k]
            k += 1

        return orig_schedule, ans
