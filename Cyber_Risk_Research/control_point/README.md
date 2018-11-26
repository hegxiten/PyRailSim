# Description of all Classes
package: numpy, pickle, matplotlib, cvs

1. Class: main.py
	# call all classes

2. Class: generate_train_one_dric.py
	# generate schedule of two drictions
	1)input(exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time)
		the format of start and end time is 'yyyy-mm-dd hh:mm:ss', and it must be a string. ex:begin_time = '2016-05-05 20:28:54'
	2)Function
		def generate_schedule(self):
        	return # dic of train schedule: dic{dic{}}
    	def print_schedule(self):
        	print # a string which is schedule of train schedule
        	
3. Class: generate_train_two_dric.py
	# generate schedule of two drictions
	1)input(exp_MGT, var_MGT, exp_buffer, var_buffer, begin_time, end_time)
		the format of start and end time is 'yyyy-mm-dd hh:mm:ss', and it must be a string. ex:begin_time = '2016-05-05 20:28:54'
	2)Function
		def generate_schedule(self):
        	return # dic of train schedule: dic{dic{}}
    	def print_schedule(self):
        	print # a string which is schedule of train schedule
        	
4. Class: train_delay_one_dric.py
	# generate schdule after the DoS attack
	1)input(X, Y, DoS_time)
		the format of DoS_time is 'yyyy-mm-dd hh:mm:ss', and it must be a string. ex:DoS_time = '2016-05-05 20:28:54'
	2)Function
		return #orig_schedule, delay_schedule
		it will return two schedule, both of them are dic{dic{}}.

5. Class: train_delay_two_dric.py
	# generate schdule after the DoS attack
	1)input(X, Y, DoS_time)
		the format of DoS_time is 'yyyy-mm-dd hh:mm:ss', and it must be a string. ex:DoS_time = '2016-05-05 20:28:54'
	2)Function
		return #orig_schedule, delay_schedule
		it will return two schedule, both of them are dic{dic{}}.
		
6. Class: write_csv.py
	# generate a csv file named "orig_schedule.csv"
	
7. Class: write_csv2.py
	# generate a csv file named "delay_schedule.csv"

8. Class: X_Y_maxDelayNum.py
	# not completed: wish to deaw a 3-D graph
	
9. # 关于火车时刻表与networkX结合的想法，首先考虑2个点 A&B。它们分别按正态分布产生双向火车。
# condition 1: A点产生的火车到达B点，为了不与B点同向火车相撞，A点产生的火车必须在进站前等待，伺机启动
# condition 2: B点产生的火车到达A点，同上，在A站前等待
# condition 3: A点产生的火车，与B点产生的火车相向而行，此情况较复杂：
#			con 3.1: A和B都产生很多火车，会不断的相遇，也会不断发生避让的情况，后车又不能超越前车，后车也可能会停，并且会不断增加停车数量