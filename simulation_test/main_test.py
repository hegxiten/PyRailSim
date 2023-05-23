from matplotlib import pyplot as plt

from simulation_core.network.network import Network
from simulation_test.configs import *
from simulation_test.simulation_helpers import string_diagram, timestamper, speed_curve
from simulation_test.launcher import launch

if __name__ == '__main__':
    sim_network = Network(sim_init_time, spd_container, acc_container, dcc_container,
                          term_time=sim_term_time,
                          dos_period=dos_period,
                          dos_pos=dos_pos,
                          headway=headway,
                          refresh_time=refresh_time,
                          persisted_spd_list=max_spd_list,
                          persisted_acc_list=max_acc_list,
                          persisted_dcc_list=max_dcc_list,
                          persisted_init_time_list=init_time_list
                          )
    print('{0} [INFO]: Simulation Launched, aim to terminate at timestamp {1}'.format(timestamper(sim_network.init_time), sim_network.term_time))
    try:
        launch(sim_network, downtrain=True, same_train_set=False,
               O_D_pair=((sim_network.signal_points[0], 0), (sim_network.signal_points[10], 1)))
        # launch(sim_network, downtrain=True, same_train_set=False,
        #        O_D_pair=((sim_network.signal_points[0], 0), (sim_network.signal_points[10], 1)),
        #        debug_timestamp=1515615000)
        string_diagram(sim_network)
        speed_curve(sim_network, marker='o')
        plt.show()
    except Exception as e:
        string_diagram(sim_network)
        speed_curve(sim_network, marker='o')
        plt.show()

        raise e
    print('max speed:\n\t', [t.max_spd for t in sim_network.train_list])
    print('max accel:\n\t', [t.max_acc for t in sim_network.train_list])
    print('max decel:\n\t', [t.max_dcc for t in sim_network.train_list])
    print('init time:\n\t', [t.init_time for t in sim_network.train_list])