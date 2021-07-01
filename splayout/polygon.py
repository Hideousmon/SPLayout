from splayout.utils import *

class Polygon:
    """
    Polygon Definition in SPLayout.

    Parameters
    ----------
    point_list : List of Point or List of Tuple
        Points for the polygon.
    """
    def __init__(self,point_list):
        self.point_list = []
        self.tuple_list = []
        for item in point_list:
            if type(item) == Point:
                self.tuple_list.append(item.to_tuple())
                self.point_list.append(item)
            elif type(item) == tuple:
                self.tuple_list.append(item)
                self.point_list.append(Point(item[0],item[1]))
            else:
                raise Exception("Polygon Wrong Type Input!")

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