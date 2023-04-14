__version__ = "0.4.4"

## Submodules
from . import utils
from . import components
from . import algorithms
from . import lumericalcommun
from . import adjointmethod

## Components
from .components.AEMDgrating import MAKE_AEMD_GRATING
from .components.bend import Bend
from .components.doubleconnector import DoubleBendConnector
from .components.simpleasymmetricdirectionalcoupler import SimpleAsymmetricDirectionalCoupler
from .components.microring import AddDropMicroring,AddDropMicroringFlat
from .components.polygon import Polygon
from .components.quarbend import QuarBend,AQuarBend
from .components.selfdefinecomponent import MAKE_COMPONENT
from .components.taper import Taper
from .components.slowlyvaryingtaper import SlowlyVaryingTaper
from .components.text import Text
from .components.waveguide import Waveguide, ArbitraryAngleWaveguide
from .components.sbend import SBend,ASBend
from .components.filledpattern import Circle,Rectangle
from .components.pixelsregion import RectanglePixelsRegion,CirclePixelsRegion

## Lumerical Commun
from .lumericalcommun.fdtdapi import FDTDSimulation
from .lumericalcommun.modeapi import MODESimulation

## Adjoint Method
from .adjointmethod.shaperegion2d import ShapeOptRegion2D
from .adjointmethod.shaperegion3d import ShapeOptRegion3D
from .adjointmethod.topologyregion2d import TopologyOptRegion2D
from .adjointmethod.topologyregion3d import TopologyOptRegion3D
from .adjointmethod.adjointshapeopt import AdjointForShapeOpt
from .adjointmethod.adjointtopologyopt import AdjointForTO

## Algorithms
from .algorithms.binarybatalgorithm import BinaryBatAlgorithm
from .algorithms.directbinarysearchalgorithm import  DirectBinarySearchAlgorithm
from .algorithms.particleswarmalgorithm import ParitcleSwarmAlgorithm
from .algorithms.binaryparticleswarmalgorithm import BinaryParitcleSwarmAlgorithm
from .algorithms.binarygeneticalgorithm import BinaryGeneticAlgorithm

## Utils
from .utils import *