from splayout.utils import *
from splayout.bend import Bend
from splayout.waveguide import Waveguide

class Circle:
    """
    Filled Circle Definition in SPLayout.

    Parameters
    ----------
    center_point : Point
        Center point of the circle.
    radius : float
        Radius of the circle.
    """
    def __init__(self, center_point, radius):
        self.center_point = center_point
        self.radius = radius
        self.bend = Bend(center_point=center_point,start_radian=0,end_radian=2*math.pi,width=radius,radius=radius/2)

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
    """
    def __init__(self, center_point, width, height = None):
        self.center_point = center_point
        self.width = width
        if (height == None):
            self.height = width
        else:
            self.height = height
        self.waveguide = Waveguide(start_point=self.center_point + (-self.width/2, 0), end_point=self.center_point + (self.width/2, 0), width=self.height)

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

    def get_center_point(self):
        """
        Derive the center point of the rectangle.

        Returns
        -------
        out : Point
            Center point.
        """
        return self.center_point
