SPLayout
========

|GitHub repository| |GitHub license|

Silicon Photonics Design Tools for GDSII Files. It is based on
**gdspy**\ (`heitzmann/gdspy: Python module for creating GDSII stream
files, usually CAD layouts.
(github.com) <https://github.com/heitzmann/gdspy>`__) and can interact
with it.

Dependency
----------

-  Python3 (3.6, 3.7, 3.8)
-  gdspy
-  scipy
-  numpy

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


History
-------

Version 0.0.1 (Jun 29, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Initial release

Version 0.0.2 (Jun 30, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Fix a fatal bug in version 0.0.1 that Selfdefinecomponent can not
   work with multi-components.

Version 0.0.3 (Jul 1, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Add document.
-  Fix a bug that the microring can not return the right pad point when
   it is rotated.
-  Fix a bug horizonal -> horizontal.
-  Fix a bug Point.\_\_eq\_\_ will return False when other==None.

Version 0.0.4 (Jul 21, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Lift restrictions on taper length.
-  Support coordinate transfer for MAKE\_COMPONENT.

Version 0.0.5 (Jul 24, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Add self.get\_start\_point() for AEMD\_grating.
-  New Class: SBend & ASBend.
-  Add a constant: pi = math.pi.

Version 0.0.6 (Jul 27,2021) & Version 0.0.7 (Jul 28, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  SBend docs update.
-  Variable names: angle -> radian.
-  AEMD gratings can have multiple definitions in a file.
-  AEMD Grating default relative position\: RIGHT.
-  New cell function: self.remove\_components().
-  If the input filename of "make\_gdsii\_file" is not "\*.gds", it will
   automatically add ".gds" to the tail.
-  New class: Circle, Rectangle.
-  Add port points definition for Polygon.

Version 0.1.4 & Version 0.1.5 (Sep 6, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  FDTD API added.
-  Binary Bat Algorithm & Direct Binary Search Algorithm for inverse
   design.

Version 0.1.6 (Sep 17, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
-  README.rst for pypi ducumentation.
-  Support numpy array for Polygon definition.
-  Annotation for DBS run.
-  Support cell flatten.
-  Fix a bug: initial_solution in DirectBianrySearchAlgorithm can not be properly defined.

Version 0.1.8 (Sep 25, 2021)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

-  Able to derive phase information from monitor.
-  Able to create rectangle&circle pixels with fdtd functions.


.. |GitHub repository| image:: https://img.shields.io/badge/github-SPLayout-blue
   :target: https://github.com/Hideousmon/SPLayout
.. |GitHub license| image:: https://img.shields.io/badge/lisence-GNU--3.0-green
   :target: https://github.com/Hideousmon/SPLayout/blob/main/LICENSE

