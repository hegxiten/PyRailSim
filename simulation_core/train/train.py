from simulation_core.network.network_utils import all_simple_paths
from simulation_core.signaling.node.control_point import CtrlPoint
from simulation_test.simulation_helpers import timestamper


class Train():
    """
        Constructor Parameters
        ----------
        :network: Network instance
            Network the train is operating at. Must be registered when initialize.
        :length: (**kw), miles
            train length that can occupy multiple tracks. 0 by default.
        :init_segment: 2-element-tuple: ((Node, Port), (Node, Port))
            Describes the initial direction and section of track of the train.
    """

    @staticmethod
    def abs_brake_distance(curr_spd, tgt_spd, brake_dcc):
        """
            :curr_spd:  Current speed in miles/sec.
            :tgt_spd:   Current target speed in miles/sec.
            :brake_dcc: Maximum deceleration in miles/(sec)^2.
            @return:
                Absolute value of brake distance in miles at input status.
        """
        if brake_dcc == 0:
            return 0
        else:
            return abs((tgt_spd) ** 2 - (curr_spd) ** 2) / (2 * abs(brake_dcc)) \
                if abs(tgt_spd) < abs(curr_spd) \
                else 0

    @staticmethod
    def directional_sign(rp_seg):
        """
            :rp_seg: 2-element-tuple: ((Node, Port),(Node, Port))
                Routing path segment of a train, describing its direction.
            @return:
                The sign (+1/-1) of train's direction (speed).
        """
        if rp_seg[0][0] and rp_seg[1][0]:
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP > rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP < rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        elif not rp_seg[0][0]:  # initiating
            if rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == min(
                    rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return 1
            elif rp_seg[1][0].signal_by_port[rp_seg[1][1]].MP == max(
                    rp_seg[1][0].track_by_port[rp_seg[1][0].opposite_port(rp_seg[1][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')
        elif not rp_seg[1][0]:  # terminating
            if rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == max(
                    rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
                return 1
            elif rp_seg[0][0].signal_by_port[rp_seg[0][1]].MP == min(
                    rp_seg[0][0].track_by_port[rp_seg[0][0].opposite_port(rp_seg[0][1])].MP):
                return -1
            else:
                raise ValueError('Undefined MP direction')

    def __init__(self,
                 network,
                 init_segment,
                 dest_segment,
                 max_spd,
                 max_acc,
                 max_dcc,
                 **kwargs):

        self.network = network
        self.time_pos_list = []
        self.rear_time_pos_list = []
        self.time_spd_list = []
        self.pos_spd_list = []
        self.init_time = self.network.sys_time
        self.init_segment, self.dest_segment = init_segment, dest_segment
        self.init_node_port = init_segment[1]
        self.dest_node_port = dest_segment[0]
        self.max_spd = max_spd
        self.max_acc = max_acc
        self.max_dcc = max_dcc
        # Default length of train is 1 (mile).
        self.length = 1 if kwargs.get('length') is None else kwargs.get('length')

        # Spawning routing path configs.
        self._curr_routing_path_segment = self.init_segment
        self._curr_occupying_routing_path = [self._curr_routing_path_segment]
        # Spawning head MP is the signal MP. Spawning rear MP is projected by train length.
        self._curr_MP = self.curr_sig.MP
        self._rear_curr_MP = self.curr_MP - self.length * self.directional_sign(self.curr_routing_path_segment)
        # Spawning speed and acceleration -> zero
        self._curr_speed = 0
        self._curr_acc = 0
        # Spawning speed limit is zero:
        self._curr_spd_lmt_abs = 0
        self._stopped = True
        # Spawning on a track/spawning outside the network
        if self.curr_track:
            if self not in self.curr_track.trains:
                if self.curr_track.trains:
                    print('{0} [WARNING]: adding new train to a track already occupied!'
                          .format(timestamper(self.network.sys_time)))
                self.curr_track.trains.append(self)

        # Auto-generated train index.
        self.train_idx = len(self.network.train_list)
        # Auto-generated train symbol.
        self.symbol = 2 * self.train_idx if self.is_uptrain else 2 * self.train_idx + 1
        # Construction complete. Update network properties.
        self.network.last_train_init_time = self.network.sys_time
        self.network.train_list.append(self)

    def __repr__(self):
        return 'Train uuid:{0} occupying:{1} head MP:{2} rear MP:{3}' \
            .format(str(self.train_idx).rjust(2, ' '),
                    self.curr_occupying_routing_path,
                    str("%.2f" % round(self.curr_MP, 2)).rjust(5, ' '),
                    str("%.2f" % round(self.rear_curr_MP, 2)).rjust(5, ' '))

    @property
    def same_way_trains(self):
        """
            @return: The sorted list of trains traveling the same direction as self.
        """
        if self.is_uptrain:
            return self.network.train_list.uptrains
        elif self.is_downtrain:
            return self.network.train_list.downtrains
        else:
            raise ValueError("Unable to get all the same-way-trains.")

    @property
    def rank(self):
        """
            Rank of the train starting from the first train to the last.
            First: 0; Last: len(self.network.trains) - 1
            TODO: Implement rank for both directions.
            @return: int
        """
        return self.same_way_trains.index(self)

    @property
    def curr_sign(self):
        return self.directional_sign(self.curr_routing_path_segment)

    @property
    def is_uptrain(self):
        return True if self.curr_sign == -1 else False

    @property
    def is_downtrain(self):
        return True if self.curr_sign == +1 else False

    @property
    def terminated(self):
        """
            Status property shows if the train has exited the rail network.
            @return: True or False
        """
        if not self.curr_routing_path_segment[1][0]:  # The head has exited the network (no upcoming ports)
            if not self.rear_curr_track:  # The end has exited the network (the rear ran off the tracks)
                return True
        return False

    @property
    def stopped(self):
        """
            Status property shows if the train is stopped because of:
                1. terminated out of the network;
                2. no and awating for signal to clear;
            @return: True or False
        """
        if self.terminated:
            # terminated trains are stopped trains
            self._stopped = True
        elif self.curr_speed == 0 and self.curr_target_spd_abs == 0:
            if self.can_acc_before_dcc:
                # Trains with 0 speed and 0 target speed may not be stopped trains:
                # Corner case: a train just logically crossed a HomeSig with 0 speed
                # and the upcoming signal aspect is red
                self._stopped = False
            else:
                # Note: 0 speed trains with non-zero target speed (clear signal ahead) are not stopped.
                # Therefore, trains with non-zero acceleration are not stopped trains.
                self._stopped = True
        else:
            self._stopped = False
        return self._stopped

    @property
    def curr_track(self):
        """
            The current TrackSegment instance the head of the train is moving upon.
        """
        return self.network.get_track_by_node_port_pairs(
            self.curr_prev_node, self.curr_prev_port,
            self.curr_node, self.curr_port)

    @property
    def rear_curr_track(self):
        """
            The current TrackSegment instance the rear of the train is moving upon.
        """
        return self.network.get_track_by_node_port_pairs(
            self.rear_curr_prev_node, self.rear_curr_prev_port,
            self.rear_curr_node, self.rear_curr_port)

    @property
    def curr_occupying_routing_path(self):
        """
            A list of routing path tuples being occupied by the train.
            The routing path tuples are in order from train head to rear.
        """
        return self._curr_occupying_routing_path if self.length != 0 else [self.curr_routing_path_segment]

    @property
    def curr_tracks(self):
        """
            A list of TrackSegment instances being occupied by the train.
            The TrackSegment instances are in order from train head to rear.
        """
        _curr_tracks = []
        for r in self.curr_occupying_routing_path:
            _track = self.network.get_track_by_node_port_pairs(r[0][0], r[0][1], r[1][0], r[1][1])
            if _track:
                _curr_tracks.append(_track)
        return _curr_tracks

    @property
    def curr_grpblk_routing(self):
        """
            The routing tuple of the group block where the train head is moving on.
        """
        return self.curr_track.group_block.routing

    @property
    def curr_routing_paths_all(self):
        """
            A list of tuples describing the current routing of the train.
            Routing segments tuples include both ahead and behind the train.
            The tuples starts from the head of its movement authority limit
            shooting to the end of the limit.
            Each tuple is a routing path segment.
        """
        return self.curr_track.curr_routing_paths_all if self.curr_track else None

    @property
    def curr_routing_path_ahead(self):
        """
            A list of tuples describing the current routing ahead of the train.
            The routing tuples (movement authority limits), even granted behind
            the train, are ignored because of no effects to itself.
        """
        return self.curr_routing_paths_all[self.curr_routing_paths_all.index(self.curr_routing_path_segment):] \
            if self.curr_routing_paths_all else None

    @property
    def curr_routing_path_segment(self):
        """
            Return a tuple of the current segment the train head is moving upon;
            expressed in a 2-element-tuple: ((Point1, Port1), (Point2, Port2)).
                Point2/Port2: SignalPoint/Port the train head is operating to.
                Point1/Port1: the opposite SignalPoint/Port of the track segment.
            None: undefined SignalPoint/Port in the network.
                Mostly appears when initialing or terminating.
            When a train exists, it has a True curr_routing_path_segment even if
                the train is not granted for any routing paths.
            With no routing paths granted: the tuple describes the position
                and its potential of movement (moving direction) of the train;
            With routing paths granted: the tuple describes the position with
                a valid routing paths.
        """
        return self._curr_routing_path_segment

    @curr_routing_path_segment.setter
    def curr_routing_path_segment(self, new_segment):
        """
            Setter for curr_routing_path_segment.
            Once set, the direction of the train & occupied track are confined.
        """
        self._curr_routing_path_segment = new_segment

    @property
    def all_paths_ahead(self):
        """
            All the simple paths ahead with banned path filtered out, given the current destination node/port tuple.
            @return:
                A list of signal points from self.curr_node to current destination signal node.
        """
        return list(all_simple_paths(self.network.G_origin, self.curr_node, self.dest_node_port[0]))

    @property
    def curr_node(self):
        """
            The SignalPoint instance the train head is moving towards currently.
        """
        return self.curr_routing_path_segment[1][0]

    @property
    def curr_prev_node(self):
        """
            The SignalPoint instance train head has just passed.
        """
        return self.curr_routing_path_segment[0][0]

    @property
    def curr_port(self):
        """
            The port of curr_node train head is moving towards.
        """
        return self.curr_routing_path_segment[1][1]

    @property
    def curr_prev_port(self):
        """
            The port of curr_prev_node that facing towards the train head.
            Note:
                this is not the port that the train head has just passed.
                It is rather the port on the BACK of the port of the signal the
                train head has just passed/acquired aspect from.
        """
        return self.curr_routing_path_segment[0][1]

    @property
    def rear_curr_node(self):
        """
            The SignalPoint instance the train rear is moving towards currently.
        """
        return self.curr_occupying_routing_path[-1][1][0]

    @property
    def rear_curr_prev_node(self):
        """
            The SignalPoint instance the train rear has just passed.
        """
        return self.curr_occupying_routing_path[-1][0][0]

    @property
    def rear_curr_port(self):
        """
            The port of rear_curr_node the train rear is moving towards.
        """
        return self.curr_occupying_routing_path[-1][1][1]

    @property
    def rear_curr_prev_port(self):
        """
            The port of rear_curr_prev_node that facing towards the rear of the train.
            Note:
                this is not the port that the train rear has just passed. It is rather the
                port on the BACK of the port the train rear has just passed/cleared signal.
        """
        return self.curr_occupying_routing_path[-1][0][1]

    @property
    def curr_ctrl_point(self):
        """
            The closest CtrlPoint instance the train head is moving towards.
            TODO: Determine if else return None or self.curr_node
        """
        return self.curr_track.group_block.get_shooting_node(
            directional_sign=self.directional_sign(self.curr_routing_path_segment)
        ) if self.curr_track else self.curr_node

    @property
    def curr_ctrl_point_port(self):
        """
            The port of curr_ctrl_point the train head is moving towards.
            TODO: Determine if else return None or self.curr_sigport
        """
        return self.curr_track.group_block.get_shooting_port(
            directional_sign=self.directional_sign(self.curr_routing_path_segment)
        ) if self.curr_track else self.curr_port

    @property
    def curr_home_sig(self):
        """
            The closest HomeSignal instance the train head is moving towards.
        """
        return self.curr_ctrl_point.signal_by_port[self.curr_ctrl_point_port] if self.curr_ctrl_point else None

    @property
    def curr_route_cancelable(self):
        """
            TODO: Explain and exhaust all the scenarios
        """
        if not self.curr_home_sig:
            return True
        if not self.curr_home_sig.route:
            return True
        if self.curr_target_spd_abs == 0:
            return True
        # TODO: The following logics are not complete.
        if self.abs_brake_distance(self.curr_speed, 0, self.max_dcc) < self.curr_dis_to_curr_sig_abs:
            return True
        return False

    @property
    def curr_sig(self):
        """
            The Signal instance the train head is moving towards.
        """
        return self.curr_node.signal_by_port[self.curr_port] if self.curr_node else None

    @property
    def rear_curr_sig(self):
        """
            The Signal instance the train rear is moving towards.
        """
        return self.rear_curr_node.signal_by_port[self.rear_curr_port] if self.rear_curr_node else None

    @property
    def curr_MP(self):  # in miles
        """
            The current MilePost of the train head, in miles.
        """
        if self.curr_track:
            assert min(self.curr_track.MP) <= self._curr_MP <= max(self.curr_track.MP)
        return self._curr_MP

    @curr_MP.setter
    def curr_MP(self, new_MP):
        """
            Setter for the curr_MP.
            Setting under different conditions with actions to trigger.
            TODO: groom for improvement
        """
        _delta_s = new_MP - self._curr_MP
        # since the intended new_MP to set is based on distance delta, back-calculate the delta_s
        if self.curr_node:
            # 1 the train head is not out of the network (has a current SignalPoint)
            if self.curr_track:
                # 1.1 the train head is within the network (has a occupied track)
                if min(self.curr_track.MP) < new_MP < max(self.curr_track.MP):
                    # 1.1.1 train head is confined in the same track after the update
                    self._curr_MP = self._curr_MP + _delta_s
                else:
                    # 1.1.2 train head entering a new track (crossing current SignalPoint)
                    # Note: new track may have a separate MP network (switching corridors)
                    _new_prev_sig_MP = self.curr_node.signal_by_port[
                        self.curr_sig.route[1]].MP
                    _curr_sig_MP = self.curr_node.signal_by_port[
                        self.curr_sig.route[0]].MP
                    self.cross_node(self.curr_node, self._curr_MP,
                                    new_MP)
                    self._curr_MP = _new_prev_sig_MP + (new_MP - _curr_sig_MP)
                    # if entering a separate MP TrackSegment, interpolate distance at MP changing node
            else:
                # 1.2 the train head is initiating, crossing the entry SignalPoint (CtrlPoint)
                _new_prev_sig_MP = self.curr_node.signal_by_port[
                    self.curr_sig.route[1]].MP
                _curr_sig_MP = self.curr_node.signal_by_port[
                    self.curr_sig.route[0]].MP
                self.cross_node(self.curr_node, self._curr_MP, new_MP)
                self._curr_MP = _new_prev_sig_MP + (new_MP - _curr_sig_MP)
                # if entering a separate MP TrackSegment, interpolate distance at MP changing node
        else:
            # 2 the train head is out of the network (going to terminate)
            self._curr_MP = self._curr_MP + _delta_s
        self.rear_curr_MP = self.rear_curr_MP + _delta_s
        # set the new rear MP using the same delta_s
        self.time_pos_list.append([self.network.sys_time, self.curr_MP])

    @property
    def rear_curr_MP(self):  # in miles
        """
            The current MilePost of the train rear, in miles.
        """
        return self._rear_curr_MP

    @rear_curr_MP.setter
    def rear_curr_MP(self, new_rear_MP):
        """
            Setter for the rear_curr_MP.
            Setting under different conditions with actions to trigger.
            TODO: groom for improvement
        """
        if not self.length:
            # 1 if the train is simplified with 0 length, set rear_curr_MP the same as curr_MP
            self._rear_curr_MP = self.curr_MP
        else:
            # 2 the train has non-zero length
            _delta_s = new_rear_MP - self._rear_curr_MP
            # since the intended new_MP to set is based on distance delta, back-calculate the delta_s
            if self.rear_curr_node:
                # 2.1 the train rear is not out of the network (rear has a current SignalPoint)
                if self.rear_curr_track:
                    # 2.1.1 not initiating
                    if min(self.rear_curr_track.MP) < new_rear_MP < max(
                            self.rear_curr_track.MP):
                        # 2.1.1.1 train rear is confined in the same track after the update
                        self._rear_curr_MP = self._rear_curr_MP + _delta_s
                    else:
                        # 2.1.1.2 train rear is entering a new track (crossing its current SignalPoint)
                        # Note: new track of the train rear may have a separate MP network
                        assert len(self.curr_occupying_routing_path) >= 2
                        _rear_route = (
                            self.curr_occupying_routing_path[-1][1][1],
                            self.curr_occupying_routing_path[-2][0][1])
                        _new_rear_prev_sig_MP = self.rear_curr_node.signal_by_port[
                            _rear_route[1]].MP
                        _rear_curr_sig_MP = self.rear_curr_node.signal_by_port[
                            _rear_route[0]].MP
                        self.rear_cross_node(self.rear_curr_node,
                                             self._rear_curr_MP,
                                             new_rear_MP)
                        self._rear_curr_MP = _new_rear_prev_sig_MP + \
                                             (new_rear_MP - _rear_curr_sig_MP)
                        # if entering a separate MP TrackSegment, interpolate distance at MP changing node
                else:
                    # 2.2 initiating, train rear is going to cross the entry CtrlPoint
                    assert len(self.curr_occupying_routing_path) >= 2
                    if (new_rear_MP - self.rear_curr_sig.MP) * (
                            self._rear_curr_MP - self.rear_curr_sig.MP) < 0:
                        # 2.2.1 rear entering the new track (crossing entry CP)
                        # Note: the train rear is sure to acquire a new MP network
                        _rear_route = \
                            (self.curr_occupying_routing_path[-1][1][1],
                             self.curr_occupying_routing_path[-2][0][1])
                        _new_rear_prev_sig_MP = self.rear_curr_node.signal_by_port[
                            _rear_route[1]].MP
                        _rear_curr_sig_MP = self.rear_curr_node.signal_by_port[
                            _rear_route[0]].MP
                        self.rear_cross_node(self.rear_curr_node,
                                             self._rear_curr_MP,
                                             new_rear_MP)
                        self._rear_curr_MP = _new_rear_prev_sig_MP + \
                                             (new_rear_MP - _rear_curr_sig_MP)
                        # interpolate distance at the MP changing node
                    else:
                        # 2.2.2 not crossing the entry CtrlPoint; train rear not in the network yet
                        self._rear_curr_MP += _delta_s
            else:
                raise ValueError(
                    'Setting Undefined rear MP: original:{0}, new:{1}, \
                        rear track:{2}'
                    .format(self._rear_curr_MP,
                            new_rear_MP,
                            self.rear_curr_track))
        self.rear_time_pos_list.append([self.network.sys_time, self.rear_curr_MP])

    @property
    def curr_speed(self):
        """
            The current speed of the train. Consistant for the whole length.
            @return: float, in miles/sec, with (+/-)
        """
        return self._curr_speed

    @curr_speed.setter
    def curr_speed(self, new_speed):
        """
            Setter for curr_speed. Setting the speed value under different conditions:
            ----------
            1: new speed after update maintains the same sign as old speed.
                1.1: the train is accelerating:
                    1.1.1: the train is accelerating into its current speed limit.
                        current speed value crossing the absolute value of its current speed limit
                        set the new current speed as the speed limit with sign.
                    1.1.2: the train is undergoing normal acceleration and not reaching its speed limit.
                1.2: the train is decelerating:
                    1.2.1: the train is decelerating into its current target speed.
                        current speed value crossing the absolute value of its current target speed.
                        stop deceleration, maintain current speed (with sign) at its target speed value.
                    1.2.2: the train is undergoing normal deceleration and not reaching its target speed.
                1.3: the train is neither accelerating nor decelerating. new_speed == _old_speed.
            2: new speed after update has the opposite sign to old_speed (speed value crossing zero):
                the train is decelerating into a complete stop, setting the speed as 0.
            TODO: groom for improvement
        """
        assert self.curr_brake_distance_abs <= self.curr_dis_to_curr_sig_abs, \
            '\n\tAssertion Error: braking distance {0} at {1} ' \
            '\n\tis greater than distance ({2}) to current signal {3}' \
            '\n\t{4}' \
            '\n\tCurrent accel: {5:.2f} mph/sec/sec' \
            '\n\tCurrent speed: {6:.2f} mph' \
            '\n\tWill overshoot by {7:.2f} ft'.format(self.curr_brake_distance_abs, self.curr_MP,
                                                      self.curr_dis_to_curr_sig_abs, self.curr_sig,
                                                      self,
                                                      self.curr_acc * 3600,
                                                      self.curr_speed * 3600,
                                                      (self.curr_brake_distance_abs - self.curr_dis_to_curr_sig_abs) * 5280)
        assert abs(self.curr_speed) <= self.curr_spd_lmt_abs
        # assert always-on braking distance/speed limit satisfaction to find bugs
        _old_speed = self._curr_speed
        # store the old speed value internally for logical processing
        # the intended new_speed to set is based on speed delta acquired by its
        # current acceleration
        if new_speed * _old_speed >= 0:  # 1
            if abs(new_speed) > abs(_old_speed):  # 1.1
                if (self.curr_spd_lmt_abs - abs(new_speed)) * (
                        self.curr_spd_lmt_abs - abs(_old_speed)) < 0:
                    # 1.1.1
                    self._curr_speed = self.curr_spd_lmt_abs if _old_speed >= 0 else -self.curr_spd_lmt_abs
                else:  # 1.1.2
                    self._curr_speed = new_speed
            elif abs(new_speed) < abs(_old_speed):  # 1.2
                if (self.curr_target_spd_abs - abs(new_speed)) * (
                        self.curr_target_spd_abs - abs(_old_speed)) < 0:
                    # 1.2.1
                    self._curr_speed = self.curr_target_spd_abs if _old_speed >= 0 else - \
                        self.curr_target_spd_abs
                else:  # 1.2.2
                    self._curr_speed = new_speed
            else:  # 1.3
                self._curr_speed = new_speed
        elif new_speed * _old_speed < 0:  # 2
            self._curr_speed = 0
        else:
            raise ValueError(
                'Setting Undefined speed value: original:{0}, new:{1}'
                .format(_old_speed, new_speed))
        assert self.curr_brake_distance_abs <= self.curr_dis_to_curr_sig_abs, \
            '\n\tAssertion Error: braking distance {0} at {1} ' \
            '\n\tis greater than distance ({2}) to current signal {3}' \
            '\n\t{4}' \
            '\n\tCurrent accel: {5:.2f} mph/sec/sec' \
            '\n\tCurrent speed: {6:.2f} mph' \
            '\n\tWill overshoot by {7:.2f} ft'.format(self.curr_brake_distance_abs, self.curr_MP,
                                                      self.curr_dis_to_curr_sig_abs, self.curr_sig,
                                                      self,
                                                      self.curr_acc * 3600,
                                                      self.curr_speed * 3600,
                                                      (self.curr_brake_distance_abs - self.curr_dis_to_curr_sig_abs) * 5280)
        assert abs(self.curr_speed) <= self.curr_spd_lmt_abs
        # assert always-on braking distance/speed limit satisfaction (after newly set speed value) to find bugs

    @property
    def curr_acc(self):  # acceleration in miles/(second)^2, with (+/-)
        """
            The current acceleration value of the train, assumed consistant acceleration for its whole length.
            The acceleration value is fully determined by its current status with different conditions:
            ----------
            1: stopped trains has to maintain 0 acceleration, otherwise it is not stopped.
            2: the train is running, not stopped.
                2.1: if the train is running at its speed limit.
                    2.1.1: if the train's current target speed is higher than its current speed limit,
                        the train shall neither accelerate nor decelerate.
                    2.1.2: if the train's current target speed is not higher than its current speed limit,
                        at every refreshing cycle, the train needs to determine if it needs to brake or not.
                        2.1.2.1: if it is ok to maintain current speed for the next refreshing cycle without
                            any violations, maintain its speed.
                        2.1.2.2: if it is not ok to maintain current speed for the next refreshing cycle period,
                            (some violations may happen if speed maintained), start to brake at its maximum effort
                2.2: if the train is running below its current speed limit.
                    2.2.1: if the train is not crossing its current signal if it maintains its current acceleration:
                        either accelerating or decelerating.
                        2.2.1.1: if the train's target speed >= its current speed limit > its current speed,
                            accelerate at its maximum acceleration effort.
                        2.2.1.2: if the train's current speed < its target speed < its current speed limit,
                            accelerate at its maximum acceleration effort.
                        2.2.1.3: if both the train's target speed and its current speed are less than (<) speed limit
                            the train has to determine whether to accelerate of decelerate at every refreshing cycle:
                            2.2.1.3.1: accelerate at maximum effort if it is ok to do so in the next refreshing cycle.
                            2.2.1.3.2: if it is not ok to accelerate at maximum effort for the next refreshing cycle,
                                maintain its current speed if it is okay to not to brake for the next refreshing cycle.
                            2.2.1.3.3: brake at maximum effort if cannot maintain speed for the next refreshing cycle.
                    2.2.2: if the train will cross its current signal if it maintains current acceleration (acc/dcc):
                        2.2.2.1 accelerate at maximum effort to cross the signal if target speed > current speed limit.
                        2.2.2.2 if target speed > current speed and the target speed < current speed limit,
                            accelerate at maximum effort to cross the signal.
                        2.2.2.3 if target speed <= current speed and the target speed < current speed limit,
                            decelerate at maximum effort to cross the signal.
                        TODO: groom for improvement
        """
        _direction_sign = self.directional_sign(self.curr_routing_path_segment)
        # sign of traveling direction (MP increment)
        _delta_s = self.curr_speed * self.network.refresh_time + 0.5 * self._curr_acc * self.network.refresh_time ** 2
        # *intended* MP increment with current acceleration value after the next refreshing cycle
        _tgt_MP = self.curr_sig.MP if self.curr_sig else _direction_sign * float('inf')
        # MilePost of its current signal. If no current signal, set the milepost as infinite.
        if self.stopped:  # 1
            self._curr_acc = 0
        else:  # 2
            if abs(self.curr_speed) == self.curr_spd_lmt_abs:  # 2.1
                if self.curr_target_spd_abs >= self.curr_spd_lmt_abs:  # 2.1.1
                    self._curr_acc = 0
                else:  # 2.1.2
                    if self.can_hold_speed_before_dcc:
                        self._curr_acc = 0  # 2.1.2.1
                    else:
                        self._curr_acc = self.max_dcc * \
                                         (-1) * _direction_sign  # 2.1.2.2
            elif abs(self.curr_speed) < self.curr_spd_lmt_abs:  # 2.2
                if (_tgt_MP - self.curr_MP) * (_tgt_MP - (self.curr_MP + _delta_s)) >= 0:  # 2.2.1
                    if self.curr_target_spd_abs >= self.curr_spd_lmt_abs:  # 2.2.1.1
                        self._curr_acc = self.max_acc * _direction_sign
                    # 2.2.1.2
                    elif self.curr_target_spd_abs > abs(self.curr_speed):
                        self._curr_acc = self.max_acc * _direction_sign
                    # 2.2.1.3
                    elif self.curr_target_spd_abs <= abs(self.curr_speed):
                        if self.can_acc_before_dcc:
                            self._curr_acc = self.max_acc * _direction_sign  # 2.2.1.3.1
                        elif self.can_hold_speed_before_dcc:
                            self._curr_acc = 0  # 2.2.1.3.2
                        else:  # 2.2.1.3.3
                            self._curr_acc = self.max_dcc * \
                                             (-1) * _direction_sign
                else:  # 2.2.2
                    if self.curr_target_spd_abs >= self.curr_spd_lmt_abs:  # 2.2.2.1
                        self._curr_acc = self.max_acc * _direction_sign
                    # 2.2.2.2
                    elif self.curr_target_spd_abs > abs(self.curr_speed):
                        # Note 1: speed setter guarantees not to violate speed limit albeit the acceleration value
                        # Note 2: current speed limit is the limit before crossing the signal. The speed limit will
                        # be updated as the train acquires the new signal aspect by crossing over it.
                        self._curr_acc = self.max_acc * _direction_sign
                    # 2.2.2.3
                    elif self.curr_target_spd_abs <= abs(self.curr_speed):
                        self._curr_acc = self.max_dcc * (-1) * _direction_sign
        return self._curr_acc

    @property
    def curr_target_spd_abs(self):  # in miles/sec, + only
        """
            The current target speed of the train in aboslute value.
            Corresponding to its current siganling speed and track allowable speeds.
        """
        if self.is_during_dos:
            return 0
        _curr_sig_trgt_speed_abs = float('inf')
        _curr_track_allow_spd_abs = getattr(self.curr_track, 'allow_spd', float('inf'))
        _curr_sig_permit_track_allow_spd = float('inf')
        # if exit the network, target speed is infinite (not defined).
        if self.curr_sig:  # waiting to initiate
            _curr_sig_trgt_speed_abs = self.curr_sig.aspect.target_speed
            if self.curr_sig.permitted_track:  # initiating
                _curr_sig_permit_track_allow_spd = self.curr_sig.permitted_track.allow_spd
        _tgt_spd = min(_curr_sig_trgt_speed_abs, _curr_track_allow_spd_abs, _curr_sig_permit_track_allow_spd)
        # both current track allowable speed and permit track allowable speed are considered.
        assert _tgt_spd >= 0.0
        return _tgt_spd

    @property
    def curr_spd_lmt_abs(self):  # in miles/sec, + only
        """
            The current speed limit in absolute value of the train.
        """
        return self._curr_spd_lmt_abs

    @curr_spd_lmt_abs.setter
    def curr_spd_lmt_abs(self, spd_lmt):
        """
            Setter for the current speed limit.
            To be called only by the other methods/functions, not directly.
        """
        if self.curr_track:
            self._curr_spd_lmt_abs = self.curr_track.allow_spd \
                if spd_lmt > self.curr_track.allow_spd \
                else spd_lmt
        else:
            self._curr_spd_lmt_abs = spd_lmt

    @property
    def curr_brake_distance_abs(self):  # in miles, + only
        """
            The current braking distance in absolute value of the train if
            engaging maximum brake effort.
            @return: float
        """
        return self.abs_brake_distance(self.curr_speed, self.curr_target_spd_abs, self.max_dcc)

    @property
    def curr_dis_to_curr_sig_abs(self):  # in miles, + only
        """
            The current distance to its curr_sig instance in absolute value
            from the train head.
        """
        return abs(self.curr_sig.MP - self.curr_MP) if self.curr_sig else float('inf')

    @property
    def trains_ahead_same_dir(self):
        """
            A list of other trains ahead of the train with the same direction.
            The lower the list index, the closer with the train.
        """
        return self.network.get_trains_between_points(self.curr_node, self.dest_node_port[0], obv=True)

    @property
    def trains_behind_same_dir(self):
        """
            A list of other trains behind the train with the same direction.
            The lower the list index, the closer with the train.
        """
        return self.network.get_trains_between_points(self.rear_curr_prev_node, self.init_node_port[0], rev=True)

    @property
    def trains_ahead_oppo_dir(self):
        """
            A list of other trains ahead of the train with the opposite direction.
            The lower the list index, the closer with the train.
        """
        return self.network.get_trains_between_points(self.curr_node, self.dest_node_port[0], rev=True)

    @property
    def trains_behind_oppo_dir(self):
        """
            A list of other trains behind the train with the opposite direction.
            The lower the list index, the closer with the train.
        """
        return self.network.get_trains_between_points(self.rear_curr_prev_node, self.init_node_port[0], obv=True)

    @property
    def trn_follow_behind(self):
        return self.same_way_trains[self.rank + 1]

    @property
    def dist_to_trn_behind(self):
        return abs(self.rear_curr_MP - self.trn_follow_behind.curr_MP)

    @property
    def is_waiting_route_at_curr_cp(self):
        """
            Status property shows if the train is pending a route at its current CtrlPoint for further proceeding.
            @return: bool
        """
        if not self.curr_node:
            return False
        elif self.curr_node == self.curr_ctrl_point:
            if not self.curr_sig.route:
                return True
        elif not self.network.get_trains_between_points(self.curr_node, self.curr_ctrl_point, obv=True):
            if not self.curr_ctrl_point.signal_by_port[self.curr_ctrl_point_port].route:
                return True
        return False

    @property
    def is_during_dos(self):
        """
            Whether the train is during the dos pos and time period
            @return: True or False
        """
        if self.curr_track:
            return min(self.curr_track.MP) == min(self.network.dos_pos) and \
                   max(self.curr_track.MP) == max(self.network.dos_pos) and \
                   self.network.dos_period[0] <= self.network.sys_time <= self.network.dos_period[1]
        return False

    @property
    def can_hold_speed_before_dcc(self):
        """
            Method to determine if the train can hold its current speed
            for another refreshing cycle at its concurrent properties:
                MP, target speed, current speed, and target speed
            @return: True or False
        """
        MP, tgt_MP, spd, tgt_spd = self.curr_MP, self.curr_sig.MP, self.curr_speed, self.curr_target_spd_abs
        delta_s = spd * self.network.refresh_time
        if abs(tgt_MP - MP) >= abs(delta_s):
            if abs(tgt_spd) >= abs(spd):
                return True
            else:
                if abs(tgt_MP - (MP + delta_s)) > self.abs_brake_distance(spd, tgt_spd, self.max_dcc):
                    return True
        else:
            if abs(tgt_spd) >= abs(spd):
                return True
            else:
                return False
        return False

    @property
    def can_acc_before_dcc(self):
        """
            Method to determine if the train can accelerate at maximum acceleration
            for another refreshing cycle at its concurrent properties:
                MP, target speed, current speed, and target speed
            @return: True or False
        """
        MP, tgt_MP, spd, tgt_spd = self.curr_MP, self.curr_sig.MP, self.curr_speed, self.curr_target_spd_abs
        assert self.curr_sig
        _direction_sign = self.directional_sign(self.curr_routing_path_segment)
        delta_spd = (_direction_sign * self.max_acc) * self.network.refresh_time
        delta_s = spd * self.network.refresh_time + 0.5 * (
                _direction_sign * self.max_acc) * self.network.refresh_time ** 2
        # prerequisite: the train can hold its current speed for another refreshing cycle (timestep).
        if not self.can_hold_speed_before_dcc:
            return False

        if abs(tgt_MP - MP) >= abs(delta_s):
            if abs(tgt_spd) >= abs(spd + delta_spd):
                return True
            else:
                if abs(tgt_MP - (MP + delta_s)) > self.abs_brake_distance(spd + delta_spd, tgt_spd, self.max_dcc):
                    return True
        else:
            if abs(tgt_spd) >= abs(spd + delta_spd):
                return True
            else:
                return False
        return False

    def cross_node(self, node, curr_MP, new_MP):
        """
            Method to update attributes and properties when the train's head
            crosses an interlocking signal node.
            @return: None
        """
        # TODO: implement geographical spans within interlocking points
        assert self.curr_sig.route in node.curr_routes_set
        assert self.curr_sig in [
            sig for p, sig in node.signal_by_port.items()
        ]
        assert min(curr_MP, new_MP) <= self.curr_sig.MP <= max(curr_MP, new_MP)
        assert not self.stopped

        _route = getattr(self.curr_sig, 'route')
        _permit_track = getattr(self.curr_sig, 'permitted_track')
        _next_enroute_node = getattr(self.curr_sig, 'next_enroute_node')
        _next_enroute_port = getattr(self.curr_sig, 'next_enroute_node_port')
        terminate = False if _next_enroute_node else True
        initiate = False if self.curr_prev_node else True

        # if self.curr_speed != 0:
        #     timestamp = self.network.sys_time + abs(curr_MP - self.curr_sig.MP)/abs(self.curr_speed)
        # else:
        #     timestamp = self.network.sys_time
        # # record the time when the train crosses an interlocking node for God's sake
        # self.time_pos_list.append([timestamp, self.curr_sig.MP])

        if initiate:
            assert isinstance(node, CtrlPoint)
            assert len(self.curr_sig.permitted_track.trains) == 0
            print('{0} [INFO]: {1} initiated, \n\tentering into {2}'
                  .format(timestamper(self.network.sys_time), self, _permit_track))
            self.curr_spd_lmt_abs = self.curr_target_spd_abs  # update current speed limit
            self.curr_sig.permitted_track.trains.append(self)  # occupy the track to enter
            # occupy the route of interlocking node
            node.curr_train_with_route[self] = _route
            # close the route to protect interlocking
            node.close_route(_route)
            self.curr_routing_path_segment = ((node, _route[1]),
                                              (_next_enroute_node, _next_enroute_port))
            self.curr_occupying_routing_path.insert(0, self.curr_routing_path_segment)
            # record the time of entering the network, serving train generation's time separation
            self.entry_time = self.network.sys_time

        elif not initiate and not terminate:
            assert len(self.curr_sig.permitted_track.trains) == 0
            self.curr_spd_lmt_abs = self.curr_target_spd_abs  # update current speed limit
            self.curr_sig.permitted_track.trains.append(self)  # occupy the track to enter
            # occupy the route of interlocking node
            node.curr_train_with_route[self] = _route
            # only close the route of CtrlPoint along the way
            if isinstance(node, CtrlPoint):
                # AutoPoints have no method to close route
                node.close_route(_route)
            self.curr_routing_path_segment = ((node, _route[1]),
                                              (_next_enroute_node, _next_enroute_port))
            self.curr_occupying_routing_path.insert(0, self.curr_routing_path_segment)

        elif terminate:
            # no track to occupy because of terminating
            assert isinstance(node, CtrlPoint)
            self.curr_spd_lmt_abs = self.curr_target_spd_abs  # update current speed limit
            # occupy the route of interlocking node
            node.curr_train_with_route[self] = _route
            # close the route to protect interlocking
            node.close_route(_route)
            self.curr_routing_path_segment = ((node, _route[1]), (None, None))
            self.curr_occupying_routing_path.insert(0, self.curr_routing_path_segment)

        else:
            raise Exception('{} crossing {} failed unexpectedly'
                            .format(self, node))

    def rear_cross_node(self, node, rear_curr_MP, new_rear_MP):
        """
            Method to update attributes and properties when the train's rear end
            crosses an interlocking signal node.
            @return: None
        """
        # TODO: implement geographical spans within interlocking points
        assert self in node.curr_train_with_route.keys()
        assert self.rear_curr_sig in [
            sig for p, sig in node.signal_by_port.items()
        ]
        assert min(rear_curr_MP, new_rear_MP) <= self.rear_curr_sig.MP <= max(
            rear_curr_MP, new_rear_MP)
        assert not self.stopped

        # if self.curr_speed != 0:
        #     timestamp = self.network.sys_time + abs(rear_curr_MP - self.rear_curr_sig.MP)/abs(self.curr_speed)
        # else:
        #     timestamp = self.network.sys_time
        # self.rear_time_pos_list.append([timestamp, self.rear_curr_sig.MP])

        del node.curr_train_with_route[self]
        if self.rear_curr_track:
            self.rear_curr_track.trains.remove(self)
        self.curr_occupying_routing_path.pop(-1)
        # TODO:----dispatching logic may need to modify here
        # ---------to determine if further group block actions are needed

    def move(self):
        """
            Method to be called by a simulator/network, updating the train's MP,
            speed & acceleration properties at each refreshing cycle.
            Update properties under different conditions and status.
            @return: None
        """
        if not self.stopped:
            self.curr_speed = self.curr_speed + self.curr_acc * self.network.refresh_time
            delta_s = self.curr_speed * self.network.refresh_time + 0.5 * self.curr_acc * self.network.refresh_time ** 2
            self.curr_MP += delta_s
            self.pos_spd_list.append([
                self.curr_MP,
                self._curr_speed,
                self.curr_spd_lmt_abs,
                self.curr_target_spd_abs
            ])
            self.time_spd_list.append([
                self.network.sys_time + self.network.refresh_time,
                self.curr_speed,
                self.curr_spd_lmt_abs,
                self.curr_target_spd_abs
            ])
        elif not self.terminated:
            self.time_pos_list.append([self.network.sys_time + self.network.refresh_time, self.curr_MP])
            self.time_spd_list.append([
                self.network.sys_time + self.network.refresh_time,
                self.curr_speed,
                self.curr_spd_lmt_abs,
                self.curr_target_spd_abs
            ])
            self.rear_time_pos_list.append([self.network.sys_time + self.network.refresh_time, self.rear_curr_MP])
        else:
            pass

    def __lt__(self, other):
        """
            implement __lt__ to sort trains based on their current MilePost.
            If MilePosts are the same, compare max_spd.
            TODO: implement better algorithms to compare train priority.
        """
        if not self.terminated:
            if self.curr_MP > other.curr_MP:
                return True if self.is_downtrain else False
            elif self.curr_MP < other.curr_MP:
                return False if self.is_downtrain else True
            # when MP is the same, compare max speed as a priority indicator
            elif self.curr_MP == other.curr_MP:
                if self.max_spd > other.max_spd:
                    return True if self.is_downtrain else False
                elif self.max_spd < other.max_spd:
                    return False if self.is_downtrain else True
        if self.terminated and other.terminated:
            _self_term_time = max([time for [time, _] in self.time_pos_list])
            _other_term_time = max([time for [time, _] in other.time_pos_list])
            if _self_term_time < _other_term_time:
                return True
        if self.terminated and not other.terminated:
            return True
