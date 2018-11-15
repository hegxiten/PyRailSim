# Description of all Classes
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