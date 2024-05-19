""" Components

A collection of basic components for layouts and simulations.

"""


from .AEMDgrating import MAKE_AEMD_GRATING
from .bend import Bend
from .doubleconnector import DoubleBendConnector
from .simpleasymmetricdirectionalcoupler import SimpleAsymmetricDirectionalCoupler
from .microring import AddDropMicroring,AddDropMicroringFlat
from .polygon import Polygon
from .quarbend import QuarBend,AQuarBend
from .selfdefinecomponent import MAKE_COMPONENT
from .taper import Taper
from .slowlyvaryingtaper import SlowlyVaryingTaper
from .text import Text
from .waveguide import Waveguide, ArbitraryAngleWaveguide
from .sbend import SBend,ASBend
from .filledpattern import Circle, Rectangle