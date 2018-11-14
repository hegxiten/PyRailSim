import matplotlib
from numpy import *
import numpy as np
import matplotlib.pyplot as plt

fig = plt.figure()
def f(x1, c):
     m1 = sin(2*pi*x1)
     m2 = exp(-c*x1)
     return multiply(m1, m2)
x = linspace(0,4,100)
sigma = 0.5
plt.plot(x, f(x, sigma), 'r', linewidth=2)
plt.xlabel(r'$\rm{time}  \  t$', fontsize=16)
plt.ylabel(r'$\rm{Amplitude} \ f(x)$', fontsize=16)
plt.title(r'$f(x) \ \rm{is \ damping  \ with} \ x$', fontsize=16)
plt.text(2.0, 0.5, r'$f(x) = \rm{sin}(2 \pi  x^2) e^{\sigma x}$', fontsize=20)
plt.savefig('latex.png', dpi=75)
plt.show()