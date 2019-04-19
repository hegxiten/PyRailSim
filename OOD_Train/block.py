class Block():
    def __init__(self, index, length, track_number=1):
        self.index = index
        self.length = length
        # There is track_number tracks in this block.
        self.track_number = track_number
        self.tracks = [None] * self.track_number
        self.track_isOccupied = [False] * self.track_number    # needs to be re-written into a list-like format
        self.topo = [[] for i in range(self.track_number+1)]
        self.trgt_spd = 0
        self.sys_pos = [0, self.length]

    def has_available_track(self):
        for oc in self.track_isOccupied:
            if not oc:
                return True
        return False

    def find_available_track(self):
        assert self.has_available_track()
        for idx, oc in enumerate(self.track_isOccupied):
            if not oc:
                return idx

    def occupied_track(self, idx, train):
        assert not self.track_isOccupied[idx]
        self.track_isOccupied[idx] = True
        self.tracks[idx] = train
    
    def free_track(self, idx):
        assert self.track_isOccupied[idx]
        self.track_isOccupied[idx] = False
        self.tracks[idx] = None
''' 
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
'''