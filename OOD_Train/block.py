class Block():
    def __init__(self, index, length, has_siding):
        self.index = index
        self.length = length
        self.curr_train = None
        self.isOccupied = False
        self.has_siding = has_siding
        self.siding_occupied = False
        self.siding_train = None

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
        if not self.has_siding:
            print("There is no siding in Block: "+str(self.index))
            return False
        elif self.siding_occupied:
            print("Block: "+str(self.index)+" This siding has been occupied!")
            return False
        else:
            self.siding_train = train
            self.siding_occupied = True

    def exit_siding(self, train):
        if not self.has_siding:
            print("There is no siding in Block: "+str(self.index))
            return False
        elif not self.siding_occupied:
            print("Block: "+str(self.index)+" There is no train on siding, no need to exit siding!")
            return False
        else:
            self.siding_train = None
            self.siding_occupied = False