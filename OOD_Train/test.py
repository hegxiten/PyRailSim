from train import Train

trs = []

for i in range(5):
    tr = Train(0, i, [[0, 0]], 0, 0)
    tr.curr_pos = i
    trs.append(tr)

trs[3].curr_pos = 4
trs[4].curr_pos = 4
trs[4].max_speed = 66
trs[3].max_speed = 77

trs.sort()
for i, tr in enumerate(trs):
    tr.rank = i

for i,tr in enumerate(trs):
    # print("idx: {}, pos: {}, speed: {}, rank: {}".format(i, tr.curr_pos, tr.max_speed, tr.rank))

x = [[1,1], [2,2], [3,3], [4,4], [5,5]]


print([i for i in x if x[0] < 3])

