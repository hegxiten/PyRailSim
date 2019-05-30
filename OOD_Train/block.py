from track import Track
from signal_light import Observable

class Block(Observable):

    def __init__(self, index, length, max_sp=0.02, track_number=1):
        self.index = index
        self.length = length
        self.max_sp = max_sp
        # There is track_number tracks in this block.
        self.track_number = track_number
        self.tracks = []
        if self.track_number > 1:
            for i in range(self.track_number):
                self.tracks.append(Track(self.length, self.max_sp, 'home'))
        else:
            self.tracks.append(Track(self.length, self.max_sp, 'abs'))

    def has_train(self):
        for tr in self.tracks:
            if tr.is_Occupied:
                return True
        return False

    def has_available_track(self):
        for tk in self.tracks:
            if not tk.is_Occupied:
                return True
        return False

    def find_available_track(self):
        assert self.has_available_track()
        for idx, tk in enumerate(self.tracks):
            if not tk.is_Occupied:
                return idx

    def occupied_track(self, idx, train):
        train.curr_blk = self.index
        train.curr_track = idx
        self.tracks[idx].enter(train)
    
    def free_track(self, idx):
        train = self.tracks[idx].train
        train.curr_blk = -1
        train.curr_track = 0
        self.tracks[idx].leave()
    