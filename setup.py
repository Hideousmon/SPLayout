#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(name='SPLayout',
      version='0.0.3',
      description='Silicon Photonics Design Tools for GDSII Files.',
      author='Zhenyu ZHAO',
      author_email='mailtozyzhao@163.com',
      install_requires=['gdspy'],
      url="https://github.com/Hideousmon/SPLayout",
      packages=['splayout']
      )