
from setuptools import setup, find_packages

setup(name='pyGTEx',
      version='0.1.1',
      url='https://github.com/mystical-Rose/pyGTEx',
      install_requires=[
          'numpy',
          'pandas',
          'matplotlib',
          'seaborn',
          'biopython'
      ],
      py_modules=['pygtex', 'GTExVisuals', 'tests']
      )
