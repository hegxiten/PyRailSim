class Block():
    def __init__(self, index, length, siding_number=0):
        self.index = index
        self.length = length
        self.curr_train = []
        self.isOccupied = False
        self.siding_number = siding_number
        self.siding_occupied = False    # needs to be re-written into a list-like format
        self.siding_train = []
        self.topo = [[] for i in range(self.siding_number+1)]
        self.trgt_spd = 0
        self.sys_pos = [0, self.length]
    def enter_train(self, train):
        if self.isOccupied:
            print("Block: "+str(self.index)+" is occupied, cannot enter new train!")
            return False
        else:
            self.curr_train = train
            self.isOccupied = True
            return True

    def exit_train(self):
        if not self.isOccupied:
            print("Block: "+str(self.index)+" is not occupied, no need to exit!")
            return False
        else:
            self.curr_train = None
            self.isOccupied = False
            return True
    
    def enter_siding(self, train):
        if not self.siding:
            print("There is no siding in Block: "+str(self.index))
            return False
        elif self.siding_occupied:
            print("Block: "+str(self.index)+" This siding has been occupied!")
            return False
        else:
            self.siding_train = train
            self.siding_occupied = True

    def exit_siding(self, train):
        if not self.siding:
            print("There is no siding in Block: "+str(self.index))
            return False
        elif not self.siding_occupied:
            print("Block: "+str(self.index)+" There is no train on siding, no need to exit siding!")
            return False
        else:
            self.siding_train = None
            self.siding_occupied = False