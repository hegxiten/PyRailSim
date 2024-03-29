from simulation_core.infrastructure.track.track_segment import TrackSegment
from simulation_core.observation_model.observe import Observable, Observer


class Yard(Observable, Observer):
    __lt__ = TrackSegment.__lt__

    def __init__(self, network):
        self.network = network
        self.tracks = []

    @property
    def MP(self):
        return (min([t.MP for t in self.tracks]), max([t.MP for t in self.tracks])) \
            if self.tracks \
            else (None,None)

    @property
    def available_tracks(self):
        count = 0
        for trk in self.tracks:
            if not trk.trains:
                count += 1
        return count

    @property
    def all_trains(self):
        _all_trains = []
        for trn_list in [trk.trains for trk in self.tracks]:
            _all_trains.extend(trn_list)
        return _all_trains