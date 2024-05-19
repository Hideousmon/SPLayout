SPLayout
========

|GitHub repository| |GitHub license|

SPLayout (**S**\ilicon **P**\hotonics **Layout** Design Tools) is a silicon photonics structures design package. It provides commonly used silicon photonics structures for fast integration and pixelated blocks for inverse design.

The GDSII streaming is based on gdspy(https://github.com/heitzmann/gdspy) and FDTD simulation is executed on Ansys Lumerical.


Dependency
----------

-  Python 3.6+
-  gdspy
-  scipy
-  numpy
-  (Ansys Lumerical for FDTDSimulation and MODESimulation)

Installation
------------

use pip:

::

    pip install splayout

or download from the source and build/install with:

::

    python setup.py install

Documentation
-------------

The documentation can be found
`here <https://splayout.readthedocs.io/en/latest/>`__.


`History (Click Here) <https://github.com/Hideousmon/SPLayout/tree/main/history.md>`__
-------------------------------------------------------------------------------------------


.. |GitHub repository| image:: https://img.shields.io/badge/github-SPLayout-blue
   :target: https://github.com/Hideousmon/SPLayout
.. |GitHub license| image:: https://img.shields.io/badge/lisence-GNU--3.0-green
   :target: https://github.com/Hideousmon/SPLayout/blob/main/LICENSE

