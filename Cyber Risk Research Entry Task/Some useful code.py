# Write what was print in txt file
with open("/Users/guokai/Desktop/entry_task.txt", 'a') as f:
    print >> f, 'Train', n, train_time, train_direction(next_direction), int(weight[n]), 'Tons'

# Read and fetch data from txt file
# Change the data into list, int or string
with open("/Users/guokai/Desktop/entry_task.txt", 'r') as f2:
    for line in open("/Users/guokai/Desktop/entry_task.txt", 'r'):
        tons.append(int(line[36:41].replace(' ', '')))
        direc.append(line[25:35].replace(' ', ''))
        time_buffer.append(line[59:62].replace(' ', ''))
    print tons, direc, time_buffer
