# build.py
import sys
from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy
# Simulate command-line arguments
sys.argv += ["build_ext", "--inplace"]

extensions = [
    Extension(
        name="TKSFastCode",
        sources=["TKSFastCode.pyx"],
        include_dirs=[numpy.get_include()],  # <- here
    )
]

setup(
    ext_modules=cythonize(
        extensions,
        compiler_directives={'language_level': "3"},
    ),
)