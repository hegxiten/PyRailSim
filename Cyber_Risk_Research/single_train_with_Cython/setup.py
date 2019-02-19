from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='integrate',
    ext_modules=cythonize('integ2.pyx')
)
