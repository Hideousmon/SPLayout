from splayout.utils import *
from splayout.waveguide import Waveguide

class Bend:
    """
    Bend Definiton in SPLayout
    center point: center point of the based ring
    start angle: start angle
    end angle: end angle
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
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
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
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
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point


