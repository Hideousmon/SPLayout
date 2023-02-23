from ..utils.utils import *
from ..components.bend import Bend
from ..components.waveguide import Waveguide
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class Circle:
    """
    Filled Circle Definition in SPLayout.

    Parameters
    ----------
    center_point : Point
        Center point of the circle.
    radius : float
        Radius of the circle.
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.
    """
    def __init__(self, center_point, radius, z_start = None, z_end = None, material = None, rename = None):
        self.center_point = tuple_to_point(center_point)
        self.radius = radius
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        self.bend = Bend(center_point=center_point,start_radian=0,end_radian=2*math.pi,width=radius,radius=radius/2, z_start = self.z_start, z_end = self.z_end, material = self.material, rename = self.rename)

    def draw(self,cell,layer):
        """
        Draw the Component on the layout.

        Parameters
        ----------
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.

        Returns
        -------
        out : Point
            Center point of the circle.
        """
        self.bend.draw(cell,layer)
        return self.center_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
            if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                self.bend.draw_on_lumerical_CAD(engine)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_center_point(self):
        """
        Derive the center point of the circle.

        Returns
        -------
        out : Point
            Center point.
        """
        return self.center_point


class Rectangle:
    """
    Filled Rectangle Definition in SPLayout.

    Parameters
    ----------
    center_point : Point
        Center point of the circle.
    width : float
        Width of the rectangle.
    height : float
        Height of the rectangle(if not specified, height will equal to width).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.
    """
    def __init__(self, center_point, width, height = None, z_start = None, z_end = None, material = None, rename = None):
        self.center_point = tuple_to_point(center_point)
        self.width = width
        if (height == None):
            self.height = width
        else:
            self.height = height

        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        self.waveguide = Waveguide(start_point=self.center_point + (-self.width/2, 0), end_point=self.center_point + (self.width/2, 0),
                                   width=self.height, z_start = self.z_start, z_end = self.z_end, material = self.material, rename = self.rename)

    def draw(self, cell, layer):
        """
        Draw the Component on the layout.

        Parameters
        ----------
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.

        Returns
        -------
        out : Point
            Center point of the rectangle.
        """
        self.waveguide.draw(cell,layer)
        return self.center_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
            if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                self.waveguide.draw_on_lumerical_CAD(engine)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_center_point(self):
        """
        Derive the center point of the rectangle.

        Returns
        -------
        out : Point
            Center point.
        """
        return self.center_point
