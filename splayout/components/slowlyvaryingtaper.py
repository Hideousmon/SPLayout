from ..utils.utils import *
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class SlowlyVaryingTaper:
    """
    Slowly Varying (Default 1.8°) Taper Definition in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the taper.
    start_width : float
        Start width of the taper (μm).
    end_width : float
        End width of the taper (μm).
    direction : FROM_LEFT_TO_RIGHT or FROM_RIGHT_TO_LEFT or FROM_LOWER_TO_UPPER or FROM_UPPER_TO_LOWER
        The direction of the taper.
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : String or Float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.
    varying_angle : Float
        Varying angle of the taper.
    """
    def __init__(self, start_point, start_width,end_width, direction = FROM_LEFT_TO_RIGHT,
                 z_start = None, z_end = None, material = None, rename = None, varying_angle = 1.8):
        if direction not in [FROM_LEFT_TO_RIGHT, FROM_RIGHT_TO_LEFT,
                             FROM_LOWER_TO_UPPER, FROM_UPPER_TO_LOWER]:
            raise Exception("Invalid Direction for SlowlyVaryingTaper!")
        self.start_point = tuple_to_point(start_point)
        self.direction = direction
        self.start_width = start_width
        self.end_width = end_width
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (start_width == end_width):
            self.ifexist = 0
            self.length = 0
        else:
            self.ifexist = 1
            self.length = abs(start_width - end_width)/2/math.tan(varying_angle*math.pi/180)
        if self.direction == FROM_LEFT_TO_RIGHT:
            self.lower_left_x = self.start_point.x
            self.lower_left_y = self.start_point.y - start_width/2
            self.lower_right_x = self.start_point.x + self.length
            self.lower_right_y = self.start_point.y - end_width/2
            self.upper_right_x = self.start_point.x + self.length
            self.upper_right_y = self.start_point.y + end_width/2
            self.upper_left_x = self.start_point.x
            self.upper_left_y = self.start_point.y + start_width/2
            self.end_point = self.start_point + (self.length, 0)
        elif self.direction == FROM_RIGHT_TO_LEFT:
            self.lower_left_x = self.start_point.x - self.length
            self.lower_left_y = self.start_point.y - end_width / 2
            self.lower_right_x = self.start_point.x
            self.lower_right_y = self.start_point.y - start_width / 2
            self.upper_right_x = self.start_point.x
            self.upper_right_y = self.start_point.y + start_width / 2
            self.upper_left_x = self.start_point.x - self.length
            self.upper_left_y = self.start_point.y + end_width / 2
            self.end_point = self.start_point + (-self.length, 0)
        elif self.direction == FROM_LOWER_TO_UPPER:
            self.lower_left_x = self.start_point.x - start_width/2
            self.lower_left_y = self.start_point.y
            self.lower_right_x = self.start_point.x + start_width/2
            self.lower_right_y = self.start_point.y
            self.upper_right_x = self.start_point.x + end_width/2
            self.upper_right_y = self.start_point.y + self.length
            self.upper_left_x = self.start_point.x - end_width/2
            self.upper_left_y = self.start_point.y + self.length
            self.end_point = self.start_point + (0, self.length)
        else: ## FROM_UPPER_TO_LOWER
            self.lower_left_x = self.start_point.x - end_width / 2
            self.lower_left_y = self.start_point.y - self.length
            self.lower_right_x = self.start_point.x + end_width / 2
            self.lower_right_y = self.start_point.y - self.length
            self.upper_right_x = self.start_point.x + start_width / 2
            self.upper_right_y = self.start_point.y
            self.upper_left_x = self.start_point.x - start_width / 2
            self.upper_left_y = self.start_point.y
            self.end_point = self.start_point + (0, -self.length)

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
        taper_pts = [(self.lower_left_x, self.lower_left_y), (self.lower_right_x, self.lower_right_y),
                     (self.upper_right_x, self.upper_right_y), (self.upper_left_x, self.upper_left_y)]
        if (self.ifexist):
            taper = gdspy.Polygon(taper_pts,
                                  layer=layer.layer, datatype=layer.datatype)
            cell.cell.add(taper)

        return self.start_point, self.end_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        taper_pts = [(self.lower_left_x, self.lower_left_y), (self.lower_right_x, self.lower_right_y),
                     (self.upper_right_x, self.upper_right_y), (self.upper_left_x, self.upper_left_y)]
        if (self.ifexist):
            if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
                if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(
                        None)):
                    engine.put_polygon(tuple_list=taper_pts,
                                       z_start=self.z_start,
                                       z_end=self.z_end,
                                       material=self.material,
                                       rename=self.rename)
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
