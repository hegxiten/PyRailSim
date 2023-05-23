from simulation_core.infrastructure.track.track_segment import TrackSegment


class GroupBlock(TrackSegment):
    def __init__(self,
                 network,
                 L_cp,
                 L_cp_port,
                 R_cp,
                 R_cp_port,
                 edge_key=0,
                 raw_graph=None,
                 cp_graph=None):
        super().__init__(network, L_cp, L_cp_port, R_cp, R_cp_port, edge_key=edge_key)
        self.type = 'group block'
        self._routing = None
        self.tracks = []
        self.add_observer(L_cp)
        self.add_observer(R_cp)

    def __repr__(self):
        return 'GrpBlk <MP:{0}~{1}> <{2} port:{3}~{4} port:{5}> key:{6}'\
            .format(str("%.1f" % round(self.MP[0], 1)).rjust(5, ' '),
                    str("%.1f" % round(self.MP[1], 1)).ljust(5, ' '),
                    self.node1,
                    str(self.node1_port).rjust(2, ' '),
                    self.node2,
                    str(self.node2_port).rjust(2, ' '),
                    str(self.edge_key).rjust(2, ' '),)

    @property
    def trains(self):
        _trains = []
        for t in self.tracks:
            for tr in t.trains:
                if tr not in _trains:
                    _trains.append(tr)
        return _trains

    @property
    def routing(self):
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        if isinstance(new_routing, tuple):
            assert len(new_routing) == 2
            if self._routing != new_routing:
                if self._routing is not None:
                    # Only if when no trains in the GroupBlock, the GroupBlock is OK
                    # to change to a reversed routing
                    assert not self.trains
                    _curr_shooting_cp = self._routing[1][0]
                    _curr_shooting_port = self._routing[1][1]
                    assert _curr_shooting_cp == new_routing[0][0]
                    # If the GroupBlock is set with a reversed routing,
                    # close any signal routes leading into its old routing
                    # at the CtrlPoint the old group block routing is shooting to.
                    for r in _curr_shooting_cp.curr_routes_set:
                        if _curr_shooting_port == r[0]:
                            _curr_shooting_cp.close_route(r)
            self._routing = new_routing
            self.set_routing_for_tracks()
        else:
            # Closing the routing by setting the property None, together with its tracks
            self._routing = None
            for t in self.tracks:
                t.routing = None

    @property
    def curr_routing_paths_all(self):
        for i in range(len(self.tracks) - 1):
            assert self.tracks[i].curr_routing_paths_all == self.tracks[i + 1].curr_routing_paths_all
        return self.tracks[0].curr_routing_paths_all

    @property
    def individual_routing_paths_list(self):
        '''
            @return:
                A list of routing objects for the individual tracks within the GroupBlock
        '''
        if self.routing:
            (start_point, start_port) = self.routing[0]
            individual_routing = [
                    getattr(self.tracks[i], 'routing')
                    for i in range(len(self.tracks))
                ]
            reverse = True \
                if start_point in (self.tracks[-1].node1, self.tracks[-1].node2) \
                else False
            return individual_routing if not reverse else list(reversed(individual_routing))
        return []

    def set_routing_for_tracks(self):
        '''
            If a GroupBlock has routing property, this method sets the routing
            property of its tracks by the same routing information.
            If this method is called, the routing is unified among all tracks inside
            plus their parental GroupBlock.
            @return:
                None
        '''
        assert self.routing is not None
        (start_point, start_port) = self.routing[0]
        reverse = True \
            if start_point in (self.tracks[-1].node1, self.tracks[-1].node2) \
            else False
        if not reverse:
            for i in range(len(self.tracks) - 1):
                (next_point, next_port) = ( self.tracks[i].node1,
                                            self.tracks[i].node1_port) \
                    if start_point == self.tracks[i].node2 \
                    else (self.tracks[i].node2, self.tracks[i].node2_port)
                self.tracks[i].routing = ((start_point, start_port),(next_point, next_port))
                start_point, start_port = next_point, self.tracks[i + 1].port_by_node[next_point]
            self.tracks[-1].routing = ((start_point, start_port),self.routing[1])
        else:
            for i in range(len(self.tracks) - 1, 0, -1):
                (next_point, next_port) = ( self.tracks[i].node1,
                                            self.tracks[i].node1_port) \
                    if start_point == self.tracks[i].node2 \
                    else (self.tracks[i].node2, self.tracks[i].node2_port)
                self.tracks[i].routing = ((start_point, start_port),(next_point, next_port))
                start_point, start_port = next_point, self.tracks[i - 1].port_by_node[next_point]
            self.tracks[0].routing = ((start_point, start_port),self.routing[1])