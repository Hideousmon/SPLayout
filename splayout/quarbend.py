from splayout.utils import *
from splayout.waveguide import Waveguide
from splayout.bend import Bend

## anticlockwise
class AQuarBend:
    '''
    Anticlockwise Connector Definiton in SPLayout with Dual Waveguide and a 90-degree Bend
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    '''
    def __init__(self,start_point,end_point,width,radius=5):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.width = width

        if (start_point.x < end_point.x and start_point.y > end_point.y): ## left down type
            if (end_point.x - start_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y + self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x + self.radius, end_point.y + self.radius), math.pi, math.pi*3/2, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x + self.radius,end_point.y),end_point ,self.width)

        if (start_point.x < end_point.x and start_point.y < end_point.y): ## right down type
            if (end_point.x - start_point.x < self.radius) or (end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x - self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x - self.radius, start_point.y + self.radius), -math.pi/2, 0 , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y + self.radius),end_point ,self.width)

        if (start_point.x > end_point.x and start_point.y < end_point.y):  ## right up type
            if (start_point.x - end_point.x < self.radius) or (
                    end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point, Point(start_point.x, end_point.y - self.radius), self.width)
            self.center_bend = Bend(Point(start_point.x - self.radius, end_point.y - self.radius), 0 , math.pi / 2,
                                    self.width, self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x - self.radius, end_point.y), end_point, self.width)


        if (start_point.x > end_point.x and start_point.y > end_point.y): ## left up type
            if (start_point.x - end_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x + self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x + self.radius, start_point.y - self.radius), math.pi/2, math.pi, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y - self.radius),end_point ,self.width)

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_waveguide.draw(cell,layer)
        self.center_bend.draw(cell,layer)
        self.second_waveguide.draw(cell,layer)
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


class QuarBend:
    '''
    Clockwise Connector Definiton in SPLayout with Dual Waveguide and a 90-degree Bend
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    '''
    def __init__(self,start_point,end_point,width,radius=5):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.width = width

        if (start_point.x < end_point.x and start_point.y > end_point.y): ## right up type
            if (end_point.x - start_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x - self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x - self.radius, start_point.y - self.radius), 0, math.pi/2, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y - self.radius),end_point ,self.width)

        if (start_point.x < end_point.x and start_point.y < end_point.y): ## left up type
            if (end_point.x - start_point.x < self.radius) or (end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y - self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x + self.radius, end_point.y - self.radius), math.pi/2, math.pi , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x + self.radius,end_point.y),end_point ,self.width)

        if (start_point.x > end_point.x and start_point.y < end_point.y):  ## down left type
            if (start_point.x - end_point.x < self.radius) or (
                    end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point, Point(end_point.x + self.radius, start_point.y), self.width)
            self.center_bend = Bend(Point(end_point.x + self.radius, start_point.y + self.radius), math.pi , math.pi*3 / 2,
                                    self.width, self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x, start_point.y + self.radius), end_point, self.width)


        if (start_point.x > end_point.x and start_point.y > end_point.y): ## right down type
            if (start_point.x - end_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y + self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x - self.radius, end_point.y + self.radius),  - math.pi/2, 0 , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x - self.radius,end_point.y),end_point ,self.width)

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_waveguide.draw(cell,layer)
        self.center_bend.draw(cell,layer)
        self.second_waveguide.draw(cell,layer)
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