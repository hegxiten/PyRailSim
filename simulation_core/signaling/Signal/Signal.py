from abc import ABC, abstractmethod
#!/usr/bin/python3
# -*- coding: utf-8 -*-
import simulation_core.infrastructure.Track.BigBlock
import simulation_core.infrastructure.Track.Track

"""
    PyRailSim
    Copyright (C) 2019  Zezhou Wang

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from simulation_core.observation_model.observe import Observable, Observer
from simulation_core.signaling.Signal.Aspect import Aspect
from simulation_core.signaling.InterlockingPoint.InterlockingPoint import InterlockingPoint


class Signal(Observable, Observer, ABC):
    '''
    Base class of a Signal object.
    '''

    def __init__(self, port_idx, sigpoint, MP=None):
        super().__init__()
        self.system = None
        self.sigpoint = sigpoint
        self._MP = MP
        self.port_idx = port_idx
        self._aspect = Aspect('r', route=self.route)  # Default aspect is red/r

        self._next_enroute_sigpoint = None

    @property
    def governed_track(self):
        '''
            Concept of "Governed Track" for a signal:
              o-                  o- (<-This signal)   o-
            0:P:1===============0:P:1================0:P:1============
             -o                  -o                   -o
                                  |-> Governed track <-|
            "0:P:1" - port_0:SigPnt:port_1
            @return:
                The track object governed by this signal.
        '''
        return self.sigpoint.track_by_port.get(self.port_idx)

    @property
    def permitted_track(self):
        '''
            Concept of "Permitted Track" for a signal:
              o-                    o- (<-This signal, Aspect 'g')     o-
            0:P:1=================0:P:1==============================0:P:1============
             -o                    -o                                 -o
              |-> Permitted Track <-|-> --------Governed track-------<-|
            "0:P:1" - port_0:SigPnt:port_1

            If there is an active route, there is a track segment to which
            this signal permits movement authority.
            @return:
                The Track object to which the current route of the signal permits.
        '''
        return self.sigpoint.track_by_port.get(self.route[1]) if self.route else None

    @property
    def facing_MP_direction_sign(self):
        '''
            Concept of "Direction" for a signal:
              o-                  o- (<-This signal)   o-
            0:P:1===============0:P:1================0:P:1============
             -o                  -o                   -o
            MP-0              MP-5               MP-10
                               -> Governed track <-
                               Signal direction: <---- (-1)
            "0:P:1" - port_0:SigPnt:port_1
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        if self.governed_track:
            # The signal has a track segment to govern: infer from track milepost
            if max(self.governed_track.MP) == self.MP:
                return 1
            elif min(self.governed_track.MP) == self.MP:
                return -1
            else:
                raise ValueError('Undefined MP direction')
        else:
            # The signal has NO track segment to govern
            # (still has a neighbor signal point)
            # infer from the neighbor signal point on the other side
            return -self.sigpoint.signal_by_port[
                self.sigpoint.opposite_port(self.port_idx)
            ].facing_MP_direction_sign

    @property
    def upwards(self):
        '''
            Concept of "upward traffic stream" for a signal:
             o-                o- (<-This signal) o-
            0:P:1===============0:P:1================0:P:1============
            -o                -o                 -o
            MP-0              MP-5               MP-10
                               Signal direction (-1): <----
                               Traffic stream:        <---- (upwards)
            "0:P:1" - port_0:SigPnt:port_1
            Trains bounding for MP-0 are considered "up-bounding trains".
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        return True if self.facing_MP_direction_sign == -1 else False

    @property
    def downwards(self):
        '''
            Concept of "downward traffic stream" for a signal:
             o-                o-                 o-
            0:P:1===============0:P:1================0:P:1============
            -o                -o (<-This signal) -o
            MP-0              MP-5               MP-10
                               Signal direction (+1): ---->
                               Traffic stream:        ----> (downwards)
            "0:P:1" - port_0:SigPnt:port_1
            Trains bounding for MP-∞ are considered "down-bounding trains".
            @return:
                The sign (+1/-1) of the direction w.r.t. the milepost ascending/descending
        '''
        return True if self.facing_MP_direction_sign == 1 else False

    @property
    def route(self):
        return self.sigpoint.current_route_by_port.get(self.port_idx)

    @property
    def MP(self):
        if not self._MP:
            self._MP = self.sigpoint.MP
        return self._MP

    @MP.setter
    def MP(self, new_MP):
        print('Warning:\n\tSetting MilePost manually for {}!\n\t\
            Changing from old MP {} to new MP {}'
              .format(self, self._MP, new_MP))
        self._MP = new_MP

    @property
    def aspect(self):
        '''
        TODO: Refactoring Under Devo
        '''
        # print('\tcall aspect of {} route {}'.format(self.sigpoint,self.route))
        self._aspect.route = self.route
        if not self.route:
            self._aspect.color = 'r'
        elif self.is_cleared_signal_to_exit_system:  # exiting the system
            self._aspect.color = 'g'
        else:
            if self.number_of_blocks_cleared_ahead == 0:
                self._aspect.color = 'r'
            elif self.number_of_blocks_cleared_ahead == 1:
                if self.next_enroute_signal.is_cleared_signal_to_exit_system:
                    self._aspect.color = 'g'
                else:
                    self._aspect.color = 'y'
            elif self.number_of_blocks_cleared_ahead == 2:
                if self.next_enroute_signal.next_enroute_signal.is_cleared_signal_to_exit_system:
                    self._aspect.color = 'g'
                else:
                    self._aspect.color = 'yy'
            elif self.number_of_blocks_cleared_ahead >= 3:
                self._aspect.color = 'g'
            else:
                raise ValueError(
                    'signal aspect of {}, port: {} not defined ready'.format(
                        self.sigpoint, self.port_idx))
        return self._aspect

    @property
    def next_enroute_sigpoint(self):
        '''
            @return:
                The next sigpoint object of this signal to which
                its current route is leading.
        '''
        return self.permitted_track.get_shooting_point(self.sigpoint) \
            if self.permitted_track else None

    @property
    def next_enroute_signal(self):
        '''
            @return:
                The next Signal object of this signal to which
                its current route is leading.
        '''
        return self.next_enroute_sigpoint.signal_by_port[
            self.next_enroute_sigpoint_port] if self.permitted_track else None

    @property
    def next_enroute_sigpoint_port(self):
        '''
            @return:
                The next signal port of the sigpoint object to which
                its current route is leading.
        '''
        return self.permitted_track.get_shooting_port(point=self.sigpoint) \
            if self.permitted_track else None

    @property
    def is_cleared_signal_to_exit_system(self):
        return True if (self.route and not self.permitted_track) else False

    @property
    def curr_routing_paths(self):
        '''
            @return:
                The list of current routing paths that this signal is part of.
        '''
        _track_rp = []
        if self.permitted_track:
            # Signal has to be permissive to have an active routing path
            return self.permitted_track.curr_routing_paths
        elif self.governed_track:
            _track_rp = self.governed_track.curr_routing_paths
            # Signal has to be permissive to have an active routing path
            if self.governed_track.routing[1][0] == self.sigpoint:
                return _track_rp
        return _track_rp

    @property
    def curr_enroute_tracks(self):
        '''
            @return:
                The list of track segments that consist of the current routing path of this signal.
        '''
        _curr_enroute_tracks = []
        if self.curr_routing_paths:
            for ((p1, p1port), (p2, p2port)) in self.curr_routing_paths:
                _curr_enroute_tracks.append(self.system.get_track_by_point_port_pairs(p1, p1port, p2, p2port))
        return _curr_enroute_tracks

    @property
    def number_of_blocks_cleared_ahead(self):
        '''
            @return:
                The number of empty/unoccupied track segments that ahead of this signal,
                along the given current routing path.
        '''
        _number = 0
        if self.curr_enroute_tracks:
            if self.governed_track:
                _governed_trk_idx = self.curr_routing_paths.index(self.governed_track.routing)
            else:
                _governed_trk_idx = 0
            _tracks_ahead = self.curr_enroute_tracks[_governed_trk_idx + 1:]
            for i in range(len(_tracks_ahead)):
                if _tracks_ahead[i]:
                    if _tracks_ahead[i].is_occupied:
                        return _number
                    elif not _tracks_ahead[i].is_occupied:
                        _number += 1
                        continue
        return _number

    @property
    def tracks_to_enter(self):
        '''
            @return:
                The number of track segments diverging from this Signal that
                are available for a train to enter.
        '''
        return [self.sigpoint.track_by_port[p]
                for p in self.sigpoint.available_ports_by_port[self.port_idx]]

    @property
    def following_sigpoints(self):
        '''
            @return:
                A list of signal points this signal can potentially permit (reach) to.
        '''
        _sigpoints = []
        for t in self.tracks_to_enter:
            for p in [t.L_point, t.R_point]:
                if p != self.sigpoint:
                    _sigpoints.append(p)
        return _sigpoints

    def reachable(self, other):
        '''
            ########################################################
            TODO: Refactoring Under Devo
            ########################################################
            Determine if another signal point/Signal/Track segment is reachable from this signal.
            @return:
                True/False
        '''

        def reachable_sigpoint(p):
            path_generator = all_simple_paths(self.system.G_origin, self.sigpoint, p)
            while True:
                try:
                    if next(path_generator)[1] in self.following_sigpoints:
                        return True
                except:
                    break
            return False

        def reachable_track(t):
            if self.sigpoint in (t.L_point, t.R_point):
                if self.governed_track == t: return False
                for p in self.sigpoint.available_ports_by_port[self.port_idx]:
                    if t == self.sigpoint.track_by_port[p]: return True
            # include AutoPoint's bigblock instance entirely covering the signal
            for p in (t.L_point, t.R_point):
                if reachable_sigpoint(p) is True: return True
            return False

        if isinstance(other, InterlockingPoint):
            return reachable_sigpoint(other)
        if isinstance(other, Signal):
            if other.sigpoint != self.sigpoint:
                return reachable_sigpoint(other.sigpoint)
            else:
                return True \
                    if other.port_idx in \
                       self.sigpoint.available_ports_by_port[self.port_idx] \
                    else False
        if isinstance(other, simulation_core.Infrastructure.Track.Track.Track) \
                or isinstance(other, simulation_core.Infrastructure.Track.BigBlock.BigBlock):
            return reachable_track(other)
        return False

    @property
    @abstractmethod
    def bblks_to_enter(self):
        raise NotImplementedError("Needed to be implemented in AutoSignal or \
            HomeSignal")

    @property
    @abstractmethod
    def ctrl_pnts_to_reach(self):
        raise NotImplementedError("Needed to be implemented in AutoSignal or \
            HomeSignal")

    # ----------------deprecated----------------#
    def update(self, observable, update_message):
        raise NotImplementedError("Old-version function to be refactored")
        if observable.type == 'bigblock':
            self.change_color_to('r', False)
        elif observable.type == 'track':
            self.change_color_to('r', False)
        elif observable.type == 'home' and observable.port_idx != self.port_idx:
            if update_message.color != 'r':
                self.change_color_to('r', False)
        else:
            pass

    def change_color_to(self, color, isNotified=True):
        raise NotImplementedError("Old-version function to be refactored")
        self.aspect = new_aspect
        if isNotified:
            self.listener_updates(obj=self.aspect)