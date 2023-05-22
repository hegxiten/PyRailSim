from simulation_core.observation_model.observe import Observable


class TrackSegment(Observable):
    @staticmethod
    def sign_routing(rp_seg):
        """
            :rp_seg: 2-element-tuple: ((Node, Port),(Node, Port))
                Routing path segment of a train, describing its direction.
            @return:
                The sign (+1/-1) of traffic when input with a legal routing
                path segment of a track/group block (describing traffic direction)
        """
        if not rp_seg:  # no routing information (dormant track/group block)
            return 0
        elif rp_seg[0][0] and rp_seg[1][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP > rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP < rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')

        # initiating
        elif not rp_seg[0][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    min(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == \
                    max(rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')
        # terminating
        elif not rp_seg[1][0]:
            if rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    max(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
                return 1
            elif rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == \
                    min(rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')

    def __init__(self,
                 system,
                 node1,
                 node1_port,
                 node2,
                 node2_port,
                 edge_key=0,
                 allow_spd=65,  # speed as mph
                 yard=None,
                 **kwargs):
        super().__init__()
        self._trains = []
        self._routing = None
        self.type = 'track'
        self.edge_key = edge_key
        self.allow_spd = allow_spd / 3600

        self.node1, self.node2 = node1, node2
        self.node1_port, self.node2_port = node1_port, node2_port
        self.port_by_node = {node1: node1_port, node2: node2_port}
        self.add_observer(node1)
        self.add_observer(node2)

        self.system = system
        self.yard = yard
        if self.yard:
            if self not in self.yard.tracks:
                self.yard.tracks.append(self)
        lambda_defaultmainline = lambda l_port, r_port: True if l_port == 1 and r_port == 0 else False
        self.mainline = lambda_defaultmainline(self.node1_port, self.node2_port) \
            if kwargs.get('mainline') is None \
            else kwargs.get('mainline')

        self.mainline_weight = float('inf') if self.mainline == False else 1
        self.tracks = []
        self.__group_block = None
        self.__curr_routing_path = None

    def __repr__(self):
        return 'TrackSegment <MP:{0}~{1}> <{2} port:{3}~{4} port:{5}> key:{6}'\
            .format(str("%.1f" % round(self.MP[0], 1)).rjust(5, ' '),
                    str("%.1f" % round(self.MP[1], 1)).ljust(5, ' '),
                    self.node1,
                    str(self.node1_port).rjust(2, ' '),
                    self.node2,
                    str(self.node2_port).rjust(2, ' '),
                    str(self.edge_key).rjust(2, ' '),)

    @property
    def MP(self):
        return (self.node1.signal_by_port[self.node1_port].MP,
                self.node2.signal_by_port[self.node2_port].MP)

    @property
    def length(self):
        return abs(self.MP[1] - self.MP[0])

    @property
    def trains(self):
        return self._trains

    @property
    def is_occupied(self):
        return False if not self.trains else True

    @property
    def group_block(self):
        return self.__group_block

    @group_block.setter
    def group_block(self, grpblk):
        self.__group_block = grpblk

    @property
    def routing(self):
        assert self.sign_routing(self._routing) == self.group_block.sign_routing(
            self.group_block.routing)
        return self._routing

    @routing.setter
    def routing(self, new_routing):
        """
            WARNING:
                Setting a routing property directly from a track in normal
                dispatching mode is NOT RECOMMENDED.
                Please set routing property by track's parental group block instance.
        """
        if new_routing:
            for (p, pport) in new_routing:
                assert p in [self.node1, self.node2]
                assert pport in [self.node1_port, self.node2_port]
            self._routing = new_routing
        else:
            self._routing = None

    @property
    def curr_routing_paths_all(self):
        for rp in self.system.curr_routing_paths_all:
            if self.routing in rp:
                return rp
        return []

    def __lt__(self, other):
        """
            Implement __lt__ to sort yards based on their MilePost.
            If MilePosts are the same, compare key in Graphs.
            MP system of self and other has to be the same: same corridor.
        """
        if getattr(self, 'mainline', False) is True:
            if getattr(self, 'mainline', False) is False:
                return True
        if self.MP == other.MP:
            if self.edge_key < other.edge_key:
                return True
        if self.length == other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
        if self.length < other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
            if min(other.MP) <= min(self.MP):
                if min(self.MP) - min(other.MP) < max(other.MP) - max(self.MP):
                    return True
        if self.length > other.length:
            if max(self.MP) <= min(other.MP): return True
            if min(other.MP) < max(self.MP) < max(other.MP): return True
            if min(self.MP) < min(other.MP):
                if min(other.MP) - min(self.MP) > max(self.MP) - max(other.MP):
                    return True

    def purge_trains(self):
        self._trains = []

    def get_shooting_node(self, node=None, port=None, directional_sign=None):
        """
            Example:
                [port_0:CP_A:port_1 ----> port_0:CP_B:port_1]
            Given CP_A or port_1,
            @return:
                CP_B
        """
        if node is not None:
            return self.node1 if node == self.node2 else self.node2
        if port is not None:
            return self.node1 if port == self.node2_port else self.node2
        if directional_sign is not None:
            return self.node1 if directional_sign == -1 else self.node2
        return None

    def get_shooting_port(self, node=None, port=None, directional_sign=None):
        """
            Example:
                [port_0:CP_A:port_1 ----> port_0:CP_B:port_1]
            Given CP_A or port_1,
            @return:
                port_0
        """
        if node is not None:
            return self.node1_port if node == self.node2 else self.node2_port
        if port is not None:
            return self.node1_port if port == self.node2_port else self.node2_port
        if directional_sign is not None:
            return self.node1_port if directional_sign == -1 else self.node2_port
        return None