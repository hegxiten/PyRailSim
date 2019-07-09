"""
Useful links:
https://www.oschina.net/translate/parallelising-python-with-threading-and-multiprocessing
https://morvanzhou.github.io/tutorials/python-basic/multiprocessing/4-comparison/
https://stackoverflow.com/questions/28269157/plotting-in-a-non-blocking-way-with-matplotlib/42674363
https://pythonprogramming.net/live-graphs-matplotlib-tutorial/
https://codeday.me/bug/20180420/155369.html
https://scipy-cookbook.readthedocs.io/#head-3d51654b8306b1585664e7fe060a60fc76e5aa08
https://stackoverflow.com/questions/11874767/how-do-i-plot-in-real-time-in-a-while-loop-using-matplotlib
https://stackoverflow.com/questions/34764535/why-cant-matplotlib-plot-in-a-different-thread
https://linuxeye.com/334.html

multithreading:
https://realpython.com/intro-to-python-threading/

"""

import matplotlib.pyplot as plt
import numpy as np
import time
import multiprocessing
#multiprocessing.freeze_support() # <- may be required on windows

def plot(datax, datay, name):
    x = datax
    y = datay**2
    plt.scatter(x, y, label=name)
    plt.legend()
    # plt.pause()
    plt.show(block=False)
""" Source Code Of plt.pause()
def pause(interval):
    Pause for *interval* seconds.

    If there is an active figure, it will be updated and displayed before the
    pause, and the GUI event loop (if any) will run during the pause.

    This can be used for crude animation.  For more complex animation, see
    :mod:`matplotlib.animation`.

    Notes
    -----
    This function is experimental; its behavior may be changed or extended in a
    future release.
    manager = _pylab_helpers.Gcf.get_active()
    if manager is not None:
        canvas = manager.canvas
        if canvas.figure.stale:
            canvas.draw_idle()
        show(block=False)
        canvas.start_event_loop(interval)
    else:
        time.sleep(interval)

"""

def multiP():
    processes = []
    for i in range(5):
        p = multiprocessing.Process(target=plot, args=(i, i, i))
        processes.append(p)
        p.start()
    # for p in processes:
    #     time.sleep(processes.index(p))
    #     p.join()

if __name__ == "__main__": 
    input('Value: ') 
    multiP()