import random
import simpy

RANDOM_SEED = 42
NEW_TRAINS = 5  # Total number of trains
INTERVAL_TRAINS = 15.0  # Generate new trains roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience


def source(env, number, interval, counter):
    """Source generates customers randomly"""
    for i in range(number):
        c = customer(env, '%02d' % i, counter, time_in_station=12.0)
        env.process(c)
        t = random.expovariate(1.0 / interval)
        yield env.timeout(t)


def customer(env, name, counter, time_in_station):
    """Customer arrives, is served and leaves."""
    arrive = env.now
    print('train%s arrive %7.4f' % (name, arrive))

    with counter.request() as req:
        # patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
        # Wait for the counter or abort at the end of our tether
        # results = yield req | env.timeout(patience)

        wait = env.now - arrive

        print('train%s waited %7.4f in station' % (name, wait))

        tib = random.expovariate(1.0 / time_in_station)
        yield env.timeout(tib)
        print('train%s depart %7.4f' % (name, env.now))

# Setup and start the simulation
print('Station renege')
random.seed(RANDOM_SEED)
env = simpy.Environment()

# Start processes and run
counter = simpy.Resource(env, capacity=1)
env.process(source(env, NEW_TRAINS, INTERVAL_TRAINS, counter))
env.run()