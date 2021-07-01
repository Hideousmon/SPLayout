from splayout.utils import *
from splayout.waveguide import Waveguide

class Bend:
    """
    Bend Definition in SPLayout.

    Parameters
    ----------
    center_point : Point
        Center point of the based ring.
    start_angle : float
        Start angle (radian) [can be easily defined by math.pi].
    end_angle : float
        End angle (radian) [can be easily defined by math.pi].
    width : float
        Width of the waveguide (μm).
    radius : float
        Radius of the bend (μm).
    """
    def __init__(self,center_point, start_angle, end_angle, width , radius):
        self.center_point = center_point
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.width = width
        self.radius = radius
        self.start_point = Point(self.center_point.x + radius*math.cos(start_angle),
                                 self.center_point.y + radius*math.sin(start_angle))
        self.end_point = Point(self.center_point.x + radius * math.cos(end_angle),
                                 self.center_point.y + radius * math.sin(end_angle))

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
            initial_angle=self.start_angle,
            final_angle=self.end_angle,
            tolerance=0.0001,
            max_points = 100000,
            layer=layer.layer,
            datatype=layer.datatype,
        )
        cell.cell.add(round)
        return self.start_point, self.end_point

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


