from ..utils.utils import *
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class Bend:
    """
    Bend Definition in SPLayout.

    Parameters
    ----------
    center_point : Point
        Center point of the based ring.
    start_radian : float
        Start radian (radian) [can be easily defined by math.pi].
    end_radian : float
        End radian (radian) [can be easily defined by math.pi].
    width : float
        Width of the waveguide (μm).
    radius : float
        Radius of the bend (μm).
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
    def __init__(self,center_point, start_radian, end_radian, width , radius, z_start = None, z_end = None, material = None, rename = None):
        self.center_point = tuple_to_point(center_point)
        self.start_radian = start_radian
        self.end_radian = end_radian
        self.width = width
        self.radius = radius
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        self.start_point = Point(self.center_point.x + radius*math.cos(start_radian),
                                 self.center_point.y + radius*math.sin(start_radian))
        self.end_point = Point(self.center_point.x + radius * math.cos(end_radian),
                                 self.center_point.y + radius * math.sin(end_radian))

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
        out : Point,Point
            Start point and end point.
        """
        round = gdspy.Round(
            (self.center_point.x, self.center_point.y),
            self.radius + self.width/2,
            inner_radius=self.radius - self.width/2,
            initial_angle=self.start_radian,
            final_angle=self.end_radian,
            tolerance=0.0001,
            max_points = 100000,
            layer=layer.layer,
            datatype=layer.datatype,
        )
        cell.cell.add(round)
        return self.start_point, self.end_point

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
                engine.put_round(self.center_point, inner_radius = self.radius - self.width/2,
                                 outer_radius = self.radius + self.width/2,
                                 start_radian = self.start_radian,
                                 end_radian = self.end_radian, z_start=self.z_start, z_end= self.z_end, material= self.material, rename = self.rename)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_start_point(self):
        """
        Derive the start point of the bend.

        Returns
        -------
        out : Point
            Start point.
        """
        return  self.start_point

    def get_end_point(self):
        """
        Derive the end point of the bend.

        Returns
        -------
        out : Point
            End point.
        """
        return  self.end_point


