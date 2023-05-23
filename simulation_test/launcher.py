from simulation_test.simulation_helpers import timestamper, string_diagram


def launch(network, O_D_pair, downtrain=True, same_train_set=True, debug_timestamp=None):
    _exception = None
    if downtrain:
        orgn_pnt, orgn_port, dest_pnt, dest_port = O_D_pair[0][0], O_D_pair[0][1], O_D_pair[1][0], O_D_pair[1][1]
    else:
        orgn_pnt, orgn_port, dest_pnt, dest_port = O_D_pair[1][0], O_D_pair[1][1], O_D_pair[0][0], O_D_pair[0][1]
    orgn_port_opposite = orgn_pnt.opposite_port(orgn_port)
    try:
        spd_list, acc_list, dcc_list, init_time_list = \
            network.persisted_spd_list.copy(), network.persisted_acc_list.copy(), network.persisted_dcc_list.copy(), network.persisted_init_time_list.copy()
        while network.sys_time - network.init_time <= network.term_time - network.init_time:
        # while not network.trains or max([t.train_idx for t in network.trains]) < 70:
            if debug_timestamp:
                if network.sys_time >= debug_timestamp:
                    string_diagram(network)
                    print('{0} [DEBUG]: Breakpoint'.format(timestamper(debug_timestamp)))
            _semaphore_to_return = False
            for t in network.train_list:
                if not t.terminated:
                    network.dispatcher.request_routing(t)
                    t.move()
            if network.sys_time + network.refresh_time - network.last_train_init_time >= network.headway:
                if same_train_set:
                    if network.sys_time == init_time_list[0]:
                        _init_t = init_time_list.pop(0)
                        t = network.dispatcher.generate_train(
                            orgn_pnt, orgn_port,
                            dest_pnt, dest_port,
                            max_spd=spd_list.pop(0),
                            max_acc=acc_list.pop(0),
                            max_dcc=dcc_list.pop(0),
                            length=1)
                else:
                    if not orgn_pnt.curr_train_with_route.keys():
                        if all([t.curr_routing_path_segment != ((None, None), (orgn_pnt, orgn_port)) for t in network.train_list]):
                            if not orgn_pnt.track_by_port[orgn_port_opposite].trains:
                                t = network.dispatcher.generate_train(
                                    orgn_pnt, orgn_port,
                                    dest_pnt, dest_port,
                                    length=1)
            network.sys_time += network.refresh_time
    except Exception as e:
        _exception = e
        trace = network.exc_info()
        print('{0} [ERROR]: Timestamp: {1} Exception Details: {2} Trace: {3}'.format(timestamper(network.sys_time), network.sys_time, e, trace))
        raise e
