#!/usr/bin/env python


from setuptools import setup


with open("splayout/__init__.py") as fin:
    for line in fin:
        if line.startswith("__version__ ="):
            version = eval(line[14:])
            break

setup(name='SPLayout',
      version=version,
      description='Silicon Photonics Design Tools for GDSII Files.',
      author='Zhenyu ZHAO',
      author_email='mailtozyzhao@163.com',
      install_requires=['gdspy','numpy','scipy'],
      url="https://github.com/Hideousmon/SPLayout",
      packages=['splayout']
      )