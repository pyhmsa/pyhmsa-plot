#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(BASEDIR, 'VERSION')) as version_file:
    version = version_file.read().strip()

# Get the long description from the relevant file
with open('README.rst', 'r') as f:
    long_description = f.read()

setup(name='pyHMSA-plot',
      version=version,
      description='Plot data from HMSA specification',
      long_description=long_description,

      author='Philippe Pinard',
      author_email='philippe.pinard@gmail.com',
      maintainer='Philippe Pinard',
      maintainer_email='philippe.pinard@gmail.com',

      url='http://pyhmsa.readthedocs.org',
      license='MIT',
      keywords='microscopy microanalysis hmsa file format',

      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Scientific/Engineering :: Physics',
        ],

      packages=find_packages(),
      package_data={},

      install_requires=['pyHMSA', 'matplotlib', 'matplotlib_colorbar',
                        'matplotlib_scalebar'],

      zip_safe=True,

      entry_points={},

     )
