from simulation_test.simulation_helpers import timestamper, string_diagram


def launch(sys, O_D_pair, downtrain=True, same_train_set=True, debug_timestamp=None):
    _exception = None
    if downtrain:
        orgn_pnt, orgn_port, dest_pnt, dest_port = O_D_pair[0][0], O_D_pair[0][1], O_D_pair[1][0], O_D_pair[1][1]
    else:
        orgn_pnt, orgn_port, dest_pnt, dest_port = O_D_pair[1][0], O_D_pair[1][1], O_D_pair[0][0], O_D_pair[0][1]
    orgn_port_opposite = orgn_pnt.opposite_port(orgn_port)
    try:
        spd_list, acc_list, dcc_list = \
            sys.persisted_spd_list.copy(), sys.persisted_acc_list.copy(), sys.persisted_dcc_list.copy()
        while sys.sys_time - sys.init_time <= sys.term_time - sys.init_time:
            if debug_timestamp:
                if sys.sys_time >= debug_timestamp:
                    string_diagram(sys)
                    print('{0} [DEBUG]: Breakpoint'.format(timestamper(debug_timestamp)))
            _semaphore_to_return = False
            for t in sys.trains:
                sys.dispatcher.request_routing(t)
                t.move()
            if sys.sys_time + sys.refresh_time - sys.last_train_init_time >= sys.headway:
                if not orgn_pnt.curr_train_with_route.keys():
                    if all([t.curr_routing_path_segment != ((None, None), (orgn_pnt, orgn_port)) for t in sys.trains]):
                        if not orgn_pnt.track_by_port[orgn_port_opposite].trains:
                            if same_train_set:
                                t = sys.dispatcher.generate_train(
                                    orgn_pnt, orgn_port,
                                    dest_pnt, dest_port,
                                    max_spd=spd_list.pop(0),
                                    max_acc=acc_list.pop(0),
                                    max_dcc=dcc_list.pop(0),
                                    length=1)
                            else:
                                t = sys.dispatcher.generate_train(
                                    orgn_pnt, orgn_port,
                                    dest_pnt, dest_port,
                                    length=1)
            sys.sys_time += sys.refresh_time
    except Exception as e:
        _exception = e
        print('{0} [ERROR]: Timestamp: {1} Exception Details: {2}'.format(timestamper(sys.sys_time), sys.sys_time, e))
        raise e
