from ..utils.utils import *
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class Taper():
    """
    Bend Definition in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the taper.
    end_point : Point
        End point of the taper.
    start_width : float
        Start width of the taper (μm).
    end_width : float
        End width of the taper (μm).
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
    The taper should be vertical or horizontal, which means the x-axis value or the y-axis value
    of the start_point and the end_point should be the same.
    """
    def __init__(self, start_point, end_point, start_width,end_width, z_start = None, z_end = None, material = None, rename = None):
        self.start_point = tuple_to_point(start_point)
        self.end_point = tuple_to_point(end_point)
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Taper Parameter!")
        self.start_width = start_width
        self.end_width = end_width
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical taper
            # if (math.fabs(start_point.y - end_point.y) < 5):
            #     raise Exception("Taper Too Short!")
            self.down_left_x = start_point.x - start_width / 2 if (start_point.y < end_point.y) else start_point.x - end_width / 2
            self.down_left_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.down_right_x = start_point.x + start_width / 2 if (start_point.y < end_point.y) else start_point.x + end_width / 2
            self.down_right_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.up_right_x = end_point.x + end_width / 2 if (start_point.y < end_point.y) else start_point.x + start_width / 2
            self.up_right_y = end_point.y if (start_point.y < end_point.y) else start_point.y
            self.up_left_x = end_point.x - end_width / 2 if (start_point.y < end_point.y) else start_point.x - start_width / 2
            self.up_left_y = end_point.y if (start_point.y < end_point.y) else start_point.y
            self.taper_type = VERTICAL
        else:  ## parallel waveguide
            # if (math.fabs(start_point.x - end_point.x) < 5):
            #     raise Exception("Taper Too Short!")
            self.down_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.down_left_y = start_point.y - start_width / 2 if (start_point.x < end_point.x) else end_point.y - end_width / 2
            self.down_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.down_right_y = end_point.y - end_width / 2  if (start_point.x < end_point.x) else start_point.y - start_width / 2
            self.up_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.up_right_y = end_point.y + end_width / 2 if (start_point.x < end_point.x) else start_point.y + start_width / 2
            self.up_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.up_left_y = start_point.y + start_width / 2 if (start_point.x < end_point.x) else end_point.y + end_width / 2
            self.taper_type =   HORIZONTAL

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
        taper_pts = [(self.down_left_x,self.down_left_y),(self.down_right_x,self.down_right_y),
                     (self.up_right_x,self.up_right_y),(self.up_left_x,self.up_left_y)]
        if (self.ifexist):
            taper = gdspy.Polygon(taper_pts,
                                layer=layer.layer,datatype=layer.datatype)
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
        taper_pts = [(self.down_left_x, self.down_left_y), (self.down_right_x, self.down_right_y),
                     (self.up_right_x, self.up_right_y), (self.up_left_x, self.up_left_y)]
        if (self.ifexist):
            if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
                if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                    engine.put_polygon(tuple_list = taper_pts,
                                       z_start = self.z_start,
                                       z_end = self.z_end,
                                       material = self.material,
                                       rename = self.rename)
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