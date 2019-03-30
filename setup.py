#!/usr/bin/env python

# Standard library modules.
import os

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the relevant file
with open(os.path.join(BASEDIR, 'README.rst'), 'r') as f:
    long_description = f.read()

PACKAGES = find_packages()

CMDCLASS = versioneer.get_cmdclass()

INSTALL_REQUIRES = ['pyHMSA', 'matplotlib', 'matplotlib_colorbar',
                    'matplotlib_scalebar', 'scipy']
EXTRAS_REQUIRE = {'develop': ['nose', 'coverage']}

setup(name='pyHMSA-plot',
      version=versioneer.get_version(),
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
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Physics',
        ],

      packages=PACKAGES,

      install_requires=INSTALL_REQUIRES,
      extras_require=EXTRAS_REQUIRE,

      zip_safe=True,

      test_suite='nose.collector',

      cmdclass=CMDCLASS,

     )
