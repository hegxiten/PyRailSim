#!/usr/bin/python3
# -*- coding: utf-8 -*-
from simulation_test.configs import *
from simulation_test.launcher import launch
from simulation_test.simulation_helpers import *
import threading
import queue


class SimulationLauncherThread(threading.Thread):

    def __init__(self, exception_queue, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon)
        self.exception_queue = exception_queue
        self.ret_val = None

    def run(self):
        try:
            if self._target is not None:
                self.ret_val = self._target(*self._args, **self._kwargs)
        except Exception as e:
            import sys
            self.exception_queue.put(e)
        finally:
            del self._target, self._args, self._kwargs


if __name__ == '__main__':
    exception_queue = queue.Queue()
    sim_sys = System(sim_init_time, spd_container, acc_container, dcc_container,
                     term_time=sim_term_time,
                     dos_period=dos_period,
                     dos_pos=dos_pos,
                     headway=headway,
                     refresh_time=refresh_time,
                     persisted_spd_list=max_spd_list,
                     persisted_acc_list=max_acc_list,
                     persisted_dcc_list=max_dcc_list
                     )
    # Init Launch
    simulator_thread = SimulationLauncherThread(target=launch,
                                                kwargs={
                                                    'sys': sim_sys,
                                                    'O_D_pair': ((sim_sys.signal_points[0], 0),
                                                                 (sim_sys.signal_points[10], 1)),
                                                    'downtrain': True,
                                                    'same_train_set': True,
                                                },
                                                name="Simulation Main Thread",
                                                daemon=False,
                                                exception_queue=exception_queue)
    simulator_thread.start()
    simulator_thread.join()
    string_diagram(sim_sys)
    e = exception_queue.get(block=False)
    if e:
        raise e
