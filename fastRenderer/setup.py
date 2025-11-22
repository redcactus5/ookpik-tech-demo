# build.py
import sys
from setuptools import setup
from Cython.Build import cythonize

# Simulate command-line arguments
sys.argv += ["build_ext", "--inplace"]

setup(
    ext_modules=cythonize(
        ["generateDisplayList.pyx"],  # your .pyx files
        compiler_directives={'language_level': "3"}
    ),
)