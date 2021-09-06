#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

with open("README.md") as fin:
    long_description = fin.read()

with open("splayout/__init__.py") as fin:
    for line in fin:
        if line.startswith("__version__ ="):
            version = eval(line[14:])
            break

setup(name='SPLayout',
      version=version,
      description='Silicon Photonics Design Tools for GDSII Files.',
      # long_description=long_description,
      author='Zhenyu ZHAO',
      author_email='mailtozyzhao@163.com',
      install_requires=['gdspy'],
      url="https://github.com/Hideousmon/SPLayout",
      packages=['splayout']
      )