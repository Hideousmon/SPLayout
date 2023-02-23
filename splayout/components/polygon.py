from ..utils.utils import *
import numpy as np
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class Polygon:
    """
    Polygon Definition in SPLayout.

    Parameters
    ----------
    point_list : List of Point or List of Tuple
        Points for the polygon.
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.
    start_point : Point
        Start point definition for the Polygon, it can be used by "self.get_start_point()".
    end_point : Point
        End point definition for the Polygon, it can be used by "self.get_end_point()".
    input_point : Point
        Input point definition for the Polygon, it can be used by "self.get_input_point()".
    through_point : Point
        Through point definition for the Polygon, it can be used by "self.get_through_point()".
    drop_point : Point
        Drop point definition for the Polygon, it can be used by "self.get_drop_point()".
    add_point : Point
        Add point definition for the Polygon, it can be used by "self.get_add_point()".
    """
    def __init__(self,point_list, z_start = None, z_end = None, material = None, rename = None, start_point = None, end_point = None, input_point = None, through_point = None, drop_point = None, add_point = None):
        self.point_list = []
        self.tuple_list = []
        if (type(point_list) == np.ndarray):
            point_list = point_list.tolist()
        for item in point_list:
            if type(item) == Point:
                self.tuple_list.append(item.to_tuple())
                self.point_list.append(item)
            elif type(item) == tuple:
                self.tuple_list.append(item)
                self.point_list.append(Point(item[0],item[1]))
            elif type(item) == list:
                self.tuple_list.append(tuple(item))
                self.point_list.append(Point(item[0], item[1]))
            elif type(item) == np.ndarray:
                self.tuple_list.append(tuple(item))
                self.point_list.append(Point(item[0], item[1]))
            else:
                raise Exception("Polygon Wrong Type Input!")
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        self.start_point = tuple_to_point(start_point)
        self.end_point = tuple_to_point(end_point)
        self.input_point = tuple_to_point(input_point)
        self.through_point = tuple_to_point(through_point)
        self.drop_point = tuple_to_point(drop_point)
        self.add_point = tuple_to_point(add_point)

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
        out : List of Point
            Points for the polygon.
        """
        polygon = gdspy.Polygon(self.tuple_list,layer=layer.layer,datatype = layer.datatype)
        cell.cell.add(polygon)
        return self.point_list

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
                engine.put_polygon(tuple_list = self.tuple_list,
                                   z_start = self.z_start,
                                   z_end = self.z_end,
                                   material= self.material,
                                   rename = self.rename)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_the_point_at_number(self,i):
        """
        Draw the Component on the layout.

        Parameters
        ----------
        i : int
            The number of the point you want.

        Returns
        -------
        out : Point
            The ith Point in List.
        """
        if (i >= len(self.point_list)):
            raise Exception("The Request Polygon Point not Exist!")
        return self.point_list[i]

    def get_start_point(self):
        """
        Derive the start point of the Polygon.

        Returns
        -------
        out : Point
            Start point.
        """
        if (type(self.start_point) == type(None)):
            raise Exception("\"start_point\" is not specified in this Polygon!")
        else:
            return self.start_point

    def get_end_point(self):
        """
        Derive the end point of the Polygon.

        Returns
        -------
        out : Point
            End point.
        """
        if (type(self.end_point) == type(None)):
            raise Exception("\"end_point\" is not specified in this Polygon!")
        else:
            return self.end_point

    def get_input_point(self):
        """
        Derive the input port point of the Polygon.

        Returns
        -------
        out : Point
            Input point.
        """
        if (type(self.input_point) == type(None)):
            raise Exception("\"input_point\" is not specified in this Polygon!")
        else:
            return self.input_point

    def get_through_point(self):
        """
        Derive the through port point of the Polygon.

        Returns
        -------
        out : Point
            Through point.
        """
        if (type(self.through_point) == type(None)):
            raise Exception("\"through_point\" is not specified in this Polygon!")
        else:
            return self.through_point

    def get_drop_point(self):
        """
        Derive the drop port point of the Polygon.

        Returns
        -------
        out : Point
            Drop point.
        """
        if (type(self.drop_point) == type(None)):
            raise Exception("\"drop_point\" is not specified in this Polygon!")
        else:
            return self.drop_point

    def get_add_point(self):
        """
        Derive the add port point of the Polygon.

        Returns
        -------
        out : Point
            Add point.
        """
        if (type(self.add_point) == type(None)):
            raise Exception("\"add_point\" is not specified in this Polygon!")
        else:
            return self.add_point