from ..utils.utils import *
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation
from ..components.polygon import Polygon

class Waveguide:
    """
    Waveguide Definition in SPLayout.

    Parameters
    ----------
    start_point : Point or Tuple
        Start point of the waveguide.
    end_point : Point or Tuple
        End point of the waveguide.
    width : float
        Width of the waveguide (μm).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.
    Notes
    -----
    The waveguide should be vertical or horizontal, which means the x-axis value or the y-axis value
    of the start_point and the end_point should be the same. For arbitrary angle waveguide, please use ArbitraryAngleWaveguide.
    """

    def __init__(self, start_point, end_point, width, z_start = None, z_end = None, material = None, rename = None):
        start_point = tuple_to_point(start_point)
        end_point = tuple_to_point(end_point)
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Waveguide Parameter!")
        self.start_point = start_point
        self.end_point = end_point
        self.width = width
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical waveguide
            self.down_left_x = start_point.x - width / 2
            self.down_left_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.up_right_x = end_point.x + width / 2
            self.up_right_y = end_point.y if (start_point.y < end_point.y) else start_point.y
            self.waveguide_type = VERTICAL
        else:  ## parallel waveguide
            self.down_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.down_left_y = start_point.y - width / 2
            self.up_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.up_right_y = end_point.y + width / 2
            self.waveguide_type = HORIZONTAL

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
        out : Point,Point
            Start point and end point.
        """
        if (self.ifexist):
            waveguide = gdspy.Rectangle((self.down_left_x, self.down_left_y), (self.up_right_x, self.up_right_y),
                                        layer=layer.layer, datatype=layer.datatype)
            cell.cell.add(waveguide)
        return self.start_point, self.end_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if (self.ifexist):
            if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
                if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                    engine.put_rectangle((self.down_left_x, self.down_left_y), (self.up_right_x, self.up_right_y), self.z_start, self.z_end, self.material, self.rename)
                else:
                    raise Exception("Z-axis specification or material specification is missing!")
            else:
                raise Exception("Wrong CAD engine!")


    def get_start_point(self):
        """
        Derive the start point of the taper.

        Returns
        -------
        out : Point
            Start point.
        """
        return self.start_point

    def get_end_point(self):
        """
        Derive the end point of the taper.

        Returns
        -------
        out : Point
            End point.
        """
        return self.end_point


class ArbitraryAngleWaveguide:
    """
    Arbitrary Waveguide Definition in SPLayout.

    Parameters
    ----------
    start_point : Point or Tuple
        Start point of the waveguide.
    end_point : Point or Tuple
        End point of the waveguide.
    width : float
        Width of the waveguide (μm).
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
    def __init__(self,start_point, end_point, width, z_start = None, z_end = None, material = None, rename = None):
        self.start_point = tuple_to_point(start_point)
        self.end_point = tuple_to_point(end_point)
        self.width = width
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
            self.theta = self.end_point.get_relative_radian(self.start_point)
            self.point_1 = self.start_point + (
                self.width / 2 * math.sin(self.theta), -self.width / 2 * math.cos(self.theta))
            self.point_2 = self.start_point + (
                -self.width / 2 * math.sin(self.theta), self.width / 2 * math.cos(self.theta))
            self.point_3 = self.end_point + (
                -self.width / 2 * math.sin(self.theta), self.width / 2 * math.cos(self.theta))
            self.point_4 = self.end_point + (
                self.width / 2 * math.sin(self.theta), -self.width / 2 * math.cos(self.theta))
            self.waveguide = Polygon([self.point_1, self.point_2, self.point_3, self.point_4], z_start = self.z_start, z_end = self.z_end, material = self.material, rename = self.rename)

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
        out : Point,Point
            Start point and end point.
        """
        if (self.ifexist):
            self.waveguide.draw(cell,layer)
        return self.start_point, self.end_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if (self.ifexist):
            if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
                if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                    self.waveguide.draw_on_lumerical_CAD(engine)
                else:
                    raise Exception("Z-axis specification or material specification is missing!")
            else:
                raise Exception("Wrong CAD engine!")

    def get_start_point(self):
        """
        Derive the start point of the waveguide.

        Returns
        -------
        out : Point
            Start point.
        """
        return self.start_point

    def get_end_point(self):
        """
        Derive the end point of the waveguide.

        Returns
        -------
        out : Point
            End point.
        """
        return self.end_point