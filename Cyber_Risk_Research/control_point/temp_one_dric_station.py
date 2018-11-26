from generate_train_one_dric import generate_train_one_dric
import time
import simpy

class temp_one_dric_station:
    'dynamic train in networkX'

    def name(self):
        a = generate_train_one_dric(5000,1500,15,3,'2018-01-01 00:00:00', '2018-01-02 00:00:00')
        train = a.generate_schedule()
        station = 1
        for i in xrange(1, len(train)):
            ticks1 = time.mktime(time.strptime(train[1]['time_departure'], "%Y-%m-%d %H:%M%S"))
            ticks = time.mktime(time.strptime(train[i]['time_departure'], "%Y-%m-%d %H:%M%S"))
            if ticks - ticks1 >= 5 * 60:
                station += 1
            break
        return station