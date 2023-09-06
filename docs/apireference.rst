#############
API Reference
#############


*********************
Basic Class
*********************

Point
=============

.. autoclass:: splayout.Point
   :members:
   :inherited-members:
   :show-inheritance:

Cell
=============

.. autoclass:: splayout.Cell
   :members:
   :inherited-members:
   :show-inheritance:

Layer
=============

.. autoclass:: splayout.Layer
   :members:
   :inherited-members:
   :show-inheritance:

*********************
Components
*********************

Waveguide
=============

.. autoclass:: splayout.Waveguide
   :members:
   :inherited-members:
   :show-inheritance:

ArbitraryAngleWaveguide
=============

.. autoclass:: splayout.ArbitraryAngleWaveguide
   :members:
   :inherited-members:
   :show-inheritance:

Taper
=============

.. autoclass:: splayout.Taper
   :members:
   :inherited-members:
   :show-inheritance:

SlowlyVaryingTaper
=============

.. autoclass:: splayout.SlowlyVaryingTaper
   :members:
   :inherited-members:
   :show-inheritance:

Bend
=============

.. autoclass:: splayout.Bend
   :members:
   :inherited-members:
   :show-inheritance:

SBend
=============

.. autoclass:: splayout.SBend
   :members:
   :inherited-members:
   :show-inheritance:


ASBend
=============

.. autoclass:: splayout.ASBend
   :members:
   :inherited-members:
   :show-inheritance:

QuarBend
=============

.. autoclass:: splayout.QuarBend
   :members:
   :inherited-members:
   :show-inheritance:


AQuarBend
=============

.. autoclass:: splayout.AQuarBend
   :members:
   :inherited-members:
   :show-inheritance:

Polygon
=============

.. autoclass:: splayout.Polygon
   :members:
   :inherited-members:
   :show-inheritance:

DoubleBendConnector
===================

.. autoclass:: splayout.DoubleBendConnector
   :members:
   :inherited-members:
   :show-inheritance:

SimpleAsymmetricDirectionalCoupler
===================

.. autoclass:: splayout.SimpleAsymmetricDirectionalCoupler
   :members:
   :inherited-members:
   :show-inheritance:

AddDropMicroring
===================

.. autoclass:: splayout.AddDropMicroring
   :members:
   :inherited-members:
   :show-inheritance:



AddDropMicroringFlat
===================

.. autoclass:: splayout.AddDropMicroringFlat
   :members:
   :inherited-members:
   :show-inheritance:

Text
===================

.. autoclass:: splayout.Text
   :members:
   :inherited-members:
   :show-inheritance:

Circle
===================

.. autoclass:: splayout.Circle
   :members:
   :inherited-members:
   :show-inheritance:


Rectangle
===================

.. autoclass:: splayout.Rectangle
   :members:
   :inherited-members:
   :show-inheritance:

******************************************
Functions for Self-define Components
******************************************

MAKE_AEMD_GRATING
=================

.. autofunction:: splayout.MAKE_AEMD_GRATING


MAKE_COMPONENT
==============

.. autofunction:: splayout.MAKE_COMPONENT


******************************************
Make File and Generate Specifical Layer
******************************************

make_gdsii_file
================

.. autofunction:: splayout.make_gdsii_file

remove_cell
================

.. autofunction:: splayout.remove_cell

******************************************
FDTD API
******************************************

FDTDSimulation
=============

.. autoclass:: splayout.FDTDSimulation
   :members:
   :inherited-members:
   :show-inheritance:

MODESimulation
=============

.. autoclass:: splayout.MODESimulation
   :members:
   :inherited-members:
   :show-inheritance:


******************************************
Inverse Design Algorithms
******************************************

BinaryBatAlgorithm
===================

.. autoclass:: splayout.BinaryBatAlgorithm
   :members:
   :inherited-members:
   :show-inheritance:

DirectBinarySearchAlgorithm
============================

.. autoclass:: splayout.DirectBinarySearchAlgorithm
   :members:
   :inherited-members:
   :show-inheritance:

ParticleSwarmAlgorithm
============================

.. autoclass:: splayout.ParticleSwarmAlgorithm
   :members:
   :inherited-members:
   :show-inheritance:

BinaryParticleSwarmAlgorithm
============================

.. autoclass:: splayout.BinaryParticleSwarmAlgorithm
   :members:
   :inherited-members:
   :show-inheritance:

BinaryGeneticAlgorithm
============================

.. autoclass:: splayout.BinaryGeneticAlgorithm
   :members:
   :inherited-members:
   :show-inheritance:

******************************************
Inverse Design Blocks for Adjoint Method
******************************************

ShapeOptRegion2D
============================
.. autoclass:: splayout.ShapeOptRegion2D
   :members:
   :inherited-members:
   :show-inheritance:

ShapeOptRegion3D
============================
.. autoclass:: splayout.ShapeOptRegion3D
   :members:
   :inherited-members:
   :show-inheritance:

TopologyOptRegion2D
============================
.. autoclass:: splayout.TopologyOptRegion2D
   :members:
   :inherited-members:
   :show-inheritance:

TopologyOptRegion3D
============================
.. autoclass:: splayout.TopologyOptRegion3D
   :members:
   :inherited-members:
   :show-inheritance:

ScalableToOptRegion3D
============================
.. autoclass:: splayout.ScalableToOptRegion3D
   :members:
   :inherited-members:
   :show-inheritance:

AdjointForShapeOpt
============================
.. autoclass:: splayout.AdjointForShapeOpt
   :members:
   :inherited-members:
   :show-inheritance:

AdjointForTO
============================
.. autoclass:: splayout.AdjointForTO
   :members:
   :inherited-members:
   :show-inheritance:

AdjointForMultiTO
============================
.. autoclass:: splayout.AdjointForMultiTO
   :members:
   :inherited-members:
   :show-inheritance:

