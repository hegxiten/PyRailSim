import logging
import random
import networkx as nx
from datetime import datetime

from simulation_core.dispatching.Dispatcher import Dispatcher
from simulation_core.infrastructure.Track.BigBlock import BigBlock
from simulation_core.infrastructure.Track.Track import Track
from simulation_core.infrastructure.Yard.Yard import Yard
from simulation_core.network.network_utils import shortest_path, all_simple_paths, collect_banned_paths
from simulation_core.signaling.InterlockingPoint.AutoPoint import AutoPoint
from simulation_core.signaling.InterlockingPoint.CtrlPoint import CtrlPoint
from simulation_core.signaling.Signal.Aspect import Aspect
from simulation_core.train.TrainList import TrainList
from simulation_core.train.Train import Train


class System():
    """
        Parameters
        ----------
        :headway: (**kw), seconds
            Traffic headway in seconds for unidirectional trains. 500 by default.
        :dos_pos: (MP1, MP2) (**kw)
            Tuple of MPs to be attacked by DoS. (None,None) by default (no DoS).
        :refresh_time: int (**kw), seconds
            Seconds between two consecutive traverse calculations of the simulation.
        :spd_container: list (**kw), mph
            A list of randomized speed values for trains to initialize by.
        :acc_container: list (**kw), miles/(sec)^2
            A list of randomized acceleration values for trains to initialize by.
        :dcc_container: list (**kw), miles/(sec)^2
            A list of randomized deceleration values for trains to brake by.
    """

    def __init__(self, init_time, *args, **kwargs):
        super().__init__()

        self.sys_time = init_time.timestamp()
        # CPU format time in sec, transferable to numerical value or str values
        self.init_time = init_time.timestamp()
        self.term_time = float('inf') \
            if kwargs.get('term_time') is None \
            else kwargs.get('term_time').timestamp()
        self.G_origin = self.graph_constructor()
        self.G_skeleton = self.graph_extractor(self.G_origin)

        # list of all SignalPoints, including AutoPoints and CtrlPoints
        self.signal_points = list(self.G_origin.nodes())
        # list of all CtrlPoints. Indices are different from signal_points.
        self.ctrl_points = list(self.G_skeleton.nodes())
        # list of all vertex CtrlPoints where trains can initiate/terminate.
        self.vertex_points = [cp for cp in self.ctrl_points if cp.is_vertex == True]
        # list of all Tracks.
        self.tracks = [data['instance'] for (u, v, data) in list(self.G_origin.edges(data=True))]
        # list of all BigBlocks.
        self.bigblocks = [data['instance'] for (u, v, data) in list(self.G_skeleton.edges(data=True))]

        self.dos_period = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S").timestamp() for t in kwargs.get('dos_period') if
                           type(t) == str]
        self.dos_pos = (None, None) if kwargs.get('dos_pos') is None else kwargs.get('dos_pos')

        self._trains = TrainList()
        _min_spd, _max_spd, _min_acc, _max_acc = \
            0.01, 0.02, 2.78e-05 * 0.85, 2.78e-05 * 1.15
        self.headway = 500 if kwargs.get('headway') is None \
            else kwargs.get('headway')
        self.last_train_init_time = self.sys_time
        self.spd_container = args[0] \
            if args else [random.uniform(_min_spd, _max_spd) for i in range(20)]
        self.acc_container = args[1] \
            if args else [random.uniform(_min_acc, _max_acc) for i in range(20)]
        self.dcc_container = args[2] \
            if args else [random.uniform(self.sys_min_dcc * 1.15, self.sys_min_dcc * 1.25) for i in range(20)]
        self.dcc_container = [i if i >= self.sys_min_dcc else self.sys_min_dcc
                              for i in self.dcc_container]
        self.refresh_time = 1 if kwargs.get('refresh_time') is None \
            else kwargs.get('refresh_time')
        self.dispatcher = Dispatcher(self)
        # self.register(self.blocks)
        # register method links the observation relationships

    @property
    def sys_min_dcc(self):
        '''
            Absolute value, minimum brake acceleration of all trains required by
            the system setup. If train's maximum braking deceleration is smaller
            than this value, it may violate some signal/speed limits at extreme
            scenarios. When violated, the program will throw AssertionErrors at
            braking distance/speed limit check.'''
        _signal_speeds = sorted(
            [spd for _, spd in Aspect.COLOR_SPD_MAP.items()])
        _speed_diff_pairs = [(_signal_speeds[i], _signal_speeds[i + 1])
                             for i in range(len(_signal_speeds) - 1)]
        _max_diff_square_of_spd = max(
            [abs(i[0] ** 2 - i[1] ** 2) for i in _speed_diff_pairs])
        _min_track_length = min([t.length for t in self.tracks])
        return _max_diff_square_of_spd / (2 * _min_track_length)

    @property
    def trains(self):
        '''
            List of all trains inside the system.'''
        return self._trains

    @property
    def train_num(self):
        return len(self.trains)

    @property
    def curr_routing_paths(self):
        '''
            A list of all currently cleared routing path lists inside the system.
            Each routing path list has the direction and segments information of
            the limit of movement authority cleared for a certain train.
            Each routing path list consists of routing tuples (2-element-tuple)'''

        def has_repeating_routing_paths(rplist, traversed):
            '''
                local function to determine if routing path list has repeating
                elements.'''
            for i in traversed:
                if i in rplist:
                    rplist.remove(i)
            rplist_copy = rplist
            for rp in rplist_copy:
                for _rp in rplist:
                    if connectable(rp, _rp) or connectable(_rp, rp):
                        return True
            return False

        def connectable(rp1, rp2):
            '''
                local function to determine if two lists of routing paths can be
                connected together: linking two joint movement authorities.'''
            if rp1 and rp2:
                rp1_head, rp1_tail = rp1[0][0][0], rp1[-1][-1][0]
                rp2_head, rp2_tail = rp2[0][0][0], rp2[-1][-1][0]
                rp1_head_port, rp1_tail_port = rp1[0][0][1], rp1[-1][-1][1]
                rp2_head_port, rp2_tail_port = rp2[0][0][1], rp2[-1][-1][1]
                if rp1_tail == None or rp2_head == None:
                    return False
                elif rp1_tail == rp2_head:
                    assert rp1_tail.current_routes == rp2_head.current_routes
                    if (rp1_tail_port,
                        rp2_head_port) in rp1_tail.current_routes:
                        return True
            return False

        def add_cleared_routing_external_virtual_bblk():
            '''
                Add routing of initiating/terminalting routing path without a
                materialized bigblock outside the vertex CtrlPoints.'''
            for cp in self.vertex_points:
                if cp.current_routes:
                    for r in cp.current_routes:
                        if cp.track_by_port.get(r[0]):
                            _routing_list.append([((cp, r[1]), (None, None))])
                        if cp.track_by_port.get(r[1]):
                            _routing_list.append([((None, None), (cp, r[0]))])

        _routing_list = [i for i in [getattr(_bblk, 'individual_routing_paths_list')
                                     for _bblk in self.bigblocks] if i]
        add_cleared_routing_external_virtual_bblk()
        _traversed = []
        while has_repeating_routing_paths(_routing_list, _traversed):
            for i in range(len(_routing_list)):
                for j in range(len(_routing_list)):
                    if connectable(_routing_list[i], _routing_list[j]):
                        _routing_list[i].extend(_routing_list[j])
                        _traversed.append(_routing_list[j])
                    elif connectable(_routing_list[j], _routing_list[i]):
                        _routing_list[j].extend(_routing_list[i])
                        _traversed.append(_routing_list[i])
        return _routing_list

    @property
    def curr_routing_paths_cp(self):
        _routing_paths_cp = []
        for rp in self.curr_routing_paths:
            _cp_rp = []
            for ((p1, port1), (p2, port2)) in rp:
                if p1 is None or isinstance(p1, CtrlPoint):
                    _cp_rp.append([(p1, port1), None])
                if p2 is None or isinstance(p2, CtrlPoint):
                    _cp_rp[-1][1] = (p2, port2)
                    _cp_rp[-1] = tuple(_cp_rp[-1])
            _routing_paths_cp.append(_cp_rp)
        return _routing_paths_cp

    @property
    def topo(self):
        _topolist = []
        for t in self.tracks:
            if t.yard not in _topolist:
                pass

    @property
    def statelist(self):
        _statelist = []
        pass

    def get_track_by_point_port_pairs(self, p1, p1_port, p2, p2_port):
        return p1.track_by_port.get(p1_port, None) if p1 and p2 else None

    def graph_constructor(self, node={}, track={}):
        """
            Initialize the MultiGraph object with railroad components
            (CP, AT as nodes, Tracks as edges)
        """
        # TODO: construct the nbunch and ebunch list for Graph in network_constructor.py
        # TODO: automation of port connecting and index assignment
        # TODO: to be achieved in network_constructor.py
        TEST_SIDINGS = [Yard(self), Yard(self), Yard(self), Yard(self)]

        TEST_NODE = {0: CtrlPoint(self, idx=0, ports=[0, 1], MP=0.0),
                     1: AutoPoint(self, idx=1, MP=5.0),
                     2: AutoPoint(self, idx=2, MP=10.0),
                     3: CtrlPoint(self, idx=3, ports=[0, 1, 3], banned_ports_by_port={0: [0], 1: [1, 3], 3: [3, 1]},
                                  MP=15.0),
                     4: CtrlPoint(self, idx=4, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0], 1: [1]},
                                  MP=20.0),
                     5: AutoPoint(self, idx=5, MP=25.0),
                     6: CtrlPoint(self, idx=6, ports=[0, 1, 3], banned_ports_by_port={0: [0], 1: [1, 3], 3: [3, 1]},
                                  MP=30.0),
                     7: CtrlPoint(self, idx=7, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0], 1: [1]},
                                  MP=35.0),
                     8: AutoPoint(self, idx=8, MP=40.0),
                     9: AutoPoint(self, idx=9, MP=45.0),
                     10: CtrlPoint(self, idx=10, ports=[0, 1], MP=50.0)
                     }  # yapf: disable

        TEST_TRACK = [
            Track(self, TEST_NODE[0], 1, TEST_NODE[1], 0),
            Track(self, TEST_NODE[1], 1, TEST_NODE[2], 0),
            Track(self, TEST_NODE[2], 1, TEST_NODE[3], 0),
            Track(self, TEST_NODE[3], 1, TEST_NODE[4], 0, edge_key=0, yard=TEST_SIDINGS[1]),
            Track(self, TEST_NODE[3], 3, TEST_NODE[4], 2, edge_key=1, yard=TEST_SIDINGS[1]),
            Track(self, TEST_NODE[4], 1, TEST_NODE[5], 0),
            Track(self, TEST_NODE[5], 1, TEST_NODE[6], 0),
            Track(self, TEST_NODE[6], 1, TEST_NODE[7], 0, edge_key=0, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[6], 3, TEST_NODE[7], 2, edge_key=1, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[7], 1, TEST_NODE[8], 0),
            Track(self, TEST_NODE[8], 1, TEST_NODE[9], 0),
            Track(self, TEST_NODE[9], 1, TEST_NODE[10], 0)
        ]  # yapf: disable

        TEST_SIDINGS = [Yard(self), Yard(self), Yard(self), Yard(self), Yard(self), Yard(self)]

        TEST_NODE = {0: CtrlPoint(self, idx=0, ports=[0, 1], banned_ports_by_port={0: [0], 1: [1]}, MP=0.0),
                     1: AutoPoint(self, idx=1, MP=5.0),
                     2: CtrlPoint(self, idx=2, ports=[0, 1, 3], banned_ports_by_port={1: [1, 3], 3: [3, 1]}, MP=10.0),
                     3: CtrlPoint(self, idx=3, ports=[0, 1, 3], banned_ports_by_port={1: [1, 3], 3: [3, 1]}, MP=15.0),
                     4: CtrlPoint(self, idx=4, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0]}, MP=20.0),
                     5: CtrlPoint(self, idx=5, ports=[0, 1, 3], banned_ports_by_port={1: [1, 3], 3: [3, 1]}, MP=25.0),
                     6: CtrlPoint(self, idx=6, ports=[0, 1, 3], banned_ports_by_port={1: [1, 3], 3: [3, 1]}, MP=30.0),
                     7: CtrlPoint(self, idx=7, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0]}, MP=35.0),
                     8: CtrlPoint(self, idx=8, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0]}, MP=40.0),
                     9: AutoPoint(self, idx=9, MP=45.0),
                     10: CtrlPoint(self, idx=10, ports=[0, 1], banned_ports_by_port={0: [0], 1: [1]}, MP=50.0),
                     11: AutoPoint(self, idx=11, MP=30.0),
                     12: AutoPoint(self, idx=12, MP=35.0),
                     13: CtrlPoint(self, idx=13, ports=[0, 1], banned_ports_by_port={0: [0], 1: [1]}, MP=20.0),
                     14: CtrlPoint(self, idx=14, ports=[0, 1, 3], banned_ports_by_port={1: [1, 3], 3: [3, 1]}, MP=5.0),
                     15: AutoPoint(self, idx=15, MP=10.0),
                     16: CtrlPoint(self, idx=16, ports=[0, 2, 1], banned_ports_by_port={0: [0, 2], 2: [2, 0]}, MP=15.0),
                     }  # yapf: disable

        TEST_TRACK = [
            Track(self, TEST_NODE[0], 1, TEST_NODE[1], 0, mainline=True),
            Track(self, TEST_NODE[1], 1, TEST_NODE[2], 0, mainline=True),
            Track(self, TEST_NODE[2], 1, TEST_NODE[3], 0, mainline=True),
            Track(self, TEST_NODE[3], 1, TEST_NODE[4], 0, edge_key=0, yard=TEST_SIDINGS[1], mainline=True),
            Track(self, TEST_NODE[3], 3, TEST_NODE[4], 2, edge_key=1, yard=TEST_SIDINGS[1]),
            Track(self, TEST_NODE[4], 1, TEST_NODE[5], 0, mainline=True),
            Track(self, TEST_NODE[5], 1, TEST_NODE[6], 0, mainline=True),
            Track(self, TEST_NODE[6], 1, TEST_NODE[7], 0, edge_key=0, yard=TEST_SIDINGS[2], mainline=True),
            Track(self, TEST_NODE[6], 3, TEST_NODE[7], 2, edge_key=1, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[7], 1, TEST_NODE[8], 0, mainline=True),
            Track(self, TEST_NODE[8], 1, TEST_NODE[9], 0, mainline=True),
            Track(self, TEST_NODE[9], 1, TEST_NODE[10], 0, mainline=True),
            Track(self, TEST_NODE[5], 3, TEST_NODE[11], 0, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[11], 1, TEST_NODE[12], 0, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[12], 1, TEST_NODE[8], 2, yard=TEST_SIDINGS[2]),
            Track(self, TEST_NODE[2], 3, TEST_NODE[14], 0, mainline=True),
            Track(self, TEST_NODE[14], 3, TEST_NODE[15], 0, yard=TEST_SIDINGS[3]),
            Track(self, TEST_NODE[15], 1, TEST_NODE[16], 2, yard=TEST_SIDINGS[3]),
            Track(self, TEST_NODE[14], 1, TEST_NODE[16], 0, yard=TEST_SIDINGS[3], mainline=True),
            Track(self, TEST_NODE[16], 1, TEST_NODE[13], 0, mainline=True),
        ]  # yapf: disable

        _node = TEST_NODE if not node else node
        nbunch = [_node[i] for i in range(len(_node))]
        _track = TEST_TRACK if not track else track
        ebunch = [_track[i] for i in range(len(_track))]

        # _node and _track will be parameters passed from outside in the future development
        G = nx.MultiGraph()
        for n in nbunch:
            G.add_node(n, attr=n.__dict__, instance=n)
            # __dict__ of instances (CPs, ATs, Tracks) is pointing the same
            # attribute dictionary as the node in the MultiGraph

        for t in ebunch:
            G.add_edge(t.L_point,
                       t.R_point,
                       key=t.edge_key,
                       attr=t.__dict__,
                       instance=t)
            # __dict__ of instances (CPs, ATs, Tracks) is pointing the same
            # attribute dictionary as the edge in the MultiGraph
            # key is the index of parallel edges between two nodes
            t.tracks.append(t)
            t.L_point.track_by_port[t.L_point_port] = t.R_point.track_by_port[
                t.R_point_port] = t
            G[t.L_point][t.R_point][t.edge_key]['weight_mainline'] \
                = t.mainline_weight

        for i in G.nodes():  # register neighbor nodes as observers to each node
            i.neighbor_nodes.extend([n for n in G.neighbors(i)])
            for n in G.neighbors(i):
                i.add_observer(n)
        return G

    def graph_extractor(self, G):
        """
        Extract the skeletion MultiGraph with only CtrlPoints and Bigblocks
        ----------
        Parameter:
            G: MultiGraph instance of the raw network with Track as edges.
        ----------
        Return:
            F: MultiGraph instance with BigBlock as edges.
        """
        F = G.copy()

        # F is a shallow copy of G: attrbutes of G/F components
        # are pointing at the same memory.
        def _node_vars(node):
            at_neighbor = [j for j in F.neighbors(node)]
            assert len(at_neighbor) == len(F.edges(node)) == 2
            edgetrk_L_points = [
                F[at_neighbor[0]][node][0]['instance'].L_point,
                F[node][at_neighbor[1]][0]['instance'].L_point
            ]
            edgetrk_R_points = [
                F[at_neighbor[0]][node][0]['instance'].R_point,
                F[node][at_neighbor[1]][0]['instance'].R_point
            ]
            edgetrk_L_points.remove(node)
            edgetrk_R_points.remove(node)
            new_L_point, new_R_point = edgetrk_L_points[0], edgetrk_R_points[0]
            old_L_trk = F[new_L_point][node][0]['instance']
            old_R_trk = F[node][new_R_point][0]['instance']
            return new_L_point, new_R_point, old_L_trk, old_R_trk

        for i in G.nodes():
            # only use G.nodes() instead of F.nodes() to get original nodes
            # to avoid dictionary size changing issues.
            # all the following graph updates are targeted on F
            if i.type == 'at':
                new_L_point, new_R_point, old_L_trk, old_R_trk = _node_vars(i)
                new_track = Track(self,
                                  new_L_point,
                                  F[new_L_point][i][0]['instance'].L_point_port,
                                  new_R_point,
                                  F[i][new_R_point][0]['instance'].R_point_port,
                                  edge_key=0)
                if len(old_L_trk.tracks) == 1 and old_L_trk in old_L_trk.tracks:
                    new_track.tracks.append(old_L_trk)
                else:
                    new_track.tracks.extend([t for t in old_L_trk.tracks
                                             if t not in new_track.tracks])
                if len(old_R_trk.tracks) == 1 and old_R_trk in old_R_trk.tracks:
                    new_track.tracks.append(old_R_trk)
                else:
                    new_track.tracks.extend([t for t in old_R_trk.tracks
                                             if t not in new_track.tracks])
                F.remove_node(i)
                F.add_edge(new_L_point,
                           new_R_point,
                           attr=new_track.__dict__,
                           instance=new_track)
                # MultiGraph parallel edges are auto-keyed (0, 1, 2...)
                # default 0 as mainline, idx as track number

        for (u, v, k) in F.edges(keys=True):
            _L_point, _R_point = \
                F[u][v][k]['instance'].L_point, F[u][v][k]['instance'].R_point
            big_block_instance = BigBlock(self,
                                          _L_point,
                                          F[u][v][k]['instance'].L_point_port,
                                          _R_point,
                                          F[u][v][k]['instance'].R_point_port,
                                          edge_key=k,
                                          raw_graph=G,
                                          cp_graph=F)
            _L_point.bigblock_by_port[F[u][v][k]
            ['instance'].L_point_port] = big_block_instance
            _R_point.bigblock_by_port[F[u][v][k]
            ['instance'].R_point_port] = big_block_instance
            for t in F[u][v][k]['instance'].tracks:
                t.bigblock = big_block_instance
                if t not in big_block_instance.tracks:
                    big_block_instance.tracks.append(t)
            # get the list of track unit components of a bigblock,
            # and record in the instance
            for t in big_block_instance.tracks:
                t.bigblock = big_block_instance
            big_block_instance.mainline = True if all([t.mainline
                                                       for t in big_block_instance.tracks]) else False
            F[u][v][k]['attr'] = big_block_instance.__dict__
            F[u][v][k]['instance'] = big_block_instance
            F[u][v][k]['weight_mainline'] = big_block_instance.mainline_weight

        return F

    def num_occupied_parallel_tracks(self, init_point, dest_point):
        """
            Determine the number of occupied routing paths from init_point towards dest_point.
            @return: int
            TODO: refactor and revise - not suitable for bi-directional traffic
        """
        _all_trains = self.get_trains_between_points(from_point=init_point, to_point=dest_point, obv=True, rev=True)
        count = 0
        test_G = self.G_origin.copy()  # generate a dummy copy of graph
        for trn in _all_trains:
            for trk in trn.curr_tracks:  # remove all the track/edges from the graph that are occupied by trains
                if trk:
                    try:
                        test_G.remove_edge(trk.L_point, trk.R_point, key=trk.edge_key)
                    except BaseException as e:
                        pass
            if nx.has_path(test_G, init_point, dest_point):  # if a train does not
                count += 1
        return count

    def get_trains_between_points(self,
                                  from_point,
                                  to_point,
                                  obv=False,
                                  rev=False):
        """
            Given a pair of O-D in the system, return all trains running between
            this pair of O-D nodes.
            @option: filter trains running at the obversed/reversed direction
            compared with the from-to path.
            @return: list of trains, differentiated by input conditions.
        """
        _trains_all = []
        _trains_obv_dir = []
        _trains_rev_dir = []
        for path in all_simple_paths(self.G_origin, from_point, to_point):
            for node_idx in range(len(path) - 1):
                for edge_idx in list(self.G_origin[path[node_idx]][path[node_idx + 1]]):
                    trk = self.G_origin[path[node_idx]][path[node_idx + 1]][edge_idx]['instance']
                    for trn in trk.trains:
                        if trn.curr_routing_path_segment[0][0] in (path[node_idx], path[node_idx + 1]) \
                                and trn.curr_routing_path_segment[1][0] in (path[node_idx], path[node_idx + 1]):
                            if trn not in _trains_all:
                                _trains_all.append(trn)
                            if (trn.curr_routing_path_segment[0][0], trn.curr_routing_path_segment[1][0]) == (
                            path[node_idx], path[node_idx + 1]):
                                if trn not in _trains_obv_dir:
                                    _trains_obv_dir.append(trn)
                            if (trn.curr_routing_path_segment[0][0], trn.curr_routing_path_segment[1][0]) == (
                            path[node_idx + 1], path[node_idx]):
                                if trn not in _trains_rev_dir:
                                    _trains_rev_dir.append(trn)
        if obv == True and rev == True:
            return _trains_all
        elif obv == True:
            return _trains_obv_dir
        elif rev == True:
            return _trains_rev_dir
        return []

    def launch(self, launch_duration, auto_generate_train=False):
        logging.info("Thread %s: starting", 'simulator')
        while self.sys_time - self.init_time <= launch_duration:
            for t in self.trains:
                try:
                    self.dispatcher.request_routing(t)
                    t.move()
                except:
                    print(t)
                    raise (ValueError('Raise Error to Stop Simulation'))
            if auto_generate_train:
                if self.sys_time + self.refresh_time - self.last_train_init_time \
                        >= self.headway:
                    if not self.signal_points[0].curr_train_with_route.keys():
                        if all([t.curr_routing_path_segment != ((None, None), (self.signal_points[0], 0)) for t in self.trains.all_trains]):
                            if not self.tracks[0].trains:
                                t = self.dispatcher.generate_train(self.signal_points[0],0,self.signal_points[10],1,length=1)
            self.sys_time += self.refresh_time
        logging.info("Thread %s: finishing", 'simulator')

    def refresh(self):
        """
            TODO: Combine dispatcher actions; routing update actions.
        """
        # self.generate_train()
        self.dispatcher.update_routing()
        for t in self.trains.all_trains:
            t.move()
        for i, tr in enumerate(self.trains):
            tr.rank = i
        self.sys_time += self.refresh_time


sim_init_time = datetime.strptime('2018-01-10 10:00:00', "%Y-%m-%d %H:%M:%S")
sim_term_time = datetime.strptime('2018-01-10 15:30:00', "%Y-%m-%d %H:%M:%S")
spd_container = [random.uniform(0.01, 0.02) for i in range(20)]
acc_container = [0.5 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15)
                 for i in range(20)]
dcc_container = [0.2 * random.uniform(2.78e-05 * 0.85, 2.78e-05 * 1.15)
                 for i in range(20)]
headway = 300 + random.random() * 400
sys = System(sim_init_time, spd_container, acc_container, dcc_container,
             term_time=sim_term_time,
             dos_period=['2018-01-10 11:30:00', '2018-01-10 12:30:00'],
             dos_pos=(15, 20),
             headway=headway,
             refresh_time=50)
