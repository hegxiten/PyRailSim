# Rutgers PyRailSim Scheduling Engine

This is an ongoing Python-based real-time scheduling and dispatching rail simulator. 

Recommended runtime environment: 

`Python3` by Anaconda

Dependencies: `./environment.yml`

To config the simulation, edit values in: 

`./simulation_test/configs.py`

To change the network topology, edit the props in System class in 

`./simulation_core/network/System/System.py`

To debug: find the intended debug timestamps and add the `debug_timestamp` input argument in launch(), such as `debug_timestamp=1515615000` and add breakpoint at `line #19`

To launch a simulation, do

`python3 ./simulation_test/main_test.py`
