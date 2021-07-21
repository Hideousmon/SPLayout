#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

with open("README.md") as fin:
    long_description = fin.read()

setup(name='SPLayout',
      version='0.0.4',
      description='Silicon Photonics Design Tools for GDSII Files.',
      # long_description=long_description,
      author='Zhenyu ZHAO',
      author_email='mailtozyzhao@163.com',
      install_requires=['gdspy'],
      url="https://github.com/Hideousmon/SPLayout",
      packages=['splayout']
      )