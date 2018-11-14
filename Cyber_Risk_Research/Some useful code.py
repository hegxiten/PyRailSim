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

# Main difference between list and json
list is a set of keys and values, json is a string.
ex: list = {1: a, 2: b, 3: c}
    json = '{1: a, 2: b, 3: c}'

# Python list -> Json
import json
data = [ { 'a' : 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5 } ]
json = json.dumps(data)
print json

# Json -> Python list
import json
jsonData = '{"a":1,"b":2,"c":3,"d":4,"e":5}';
text = json.loads(jsonData)
print text
