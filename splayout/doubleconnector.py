from splayout.utils import *
from splayout.quarbend import AQuarBend,QuarBend

class DoubleBendConnector:
    '''
    Double Bend Connector Definiton in SPLayout with Trible Waveguide and two 90-degree Bends
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    xpercent: the center point position selection in x coordinate
    ypercent: the center point position selection in y coordinate
    '''
    def __init__(self,start_point,end_point,width,radius=5, xpercent = 0.5 , ypercent = 0.5,direction =  HORIZONAL):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.x_percent = xpercent
        self.y_percent = ypercent
        self.direction = direction
        self.center_point = Point(start_point.x + (end_point.x - start_point.x)*self.x_percent, start_point.y + (end_point.y - start_point.y)*self.y_percent)

        if (math.fabs(self.start_point.x - self.center_point.x) < self.radius or math.fabs(self.start_point.y - self.center_point.y) < self.radius
        or math.fabs(self.end_point.x - self.center_point.x) < self.radius or math.fabs(self.end_point.y - self.center_point.y) < self.radius):
            raise Exception("Two Points are too Near to Use DoubleBendConnector Or the Percent Need to be Adjusted!")

        if (self.start_point.x < self.end_point.x and self.start_point.y < self.end_point.y): ## up right type
            if (self.direction == HORIZONAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise  Exception("Wrong direction expression!")
        elif (self.start_point.x < self.end_point.x and self.start_point.y > self.end_point.y): ## down right type
            if (self.direction == HORIZONAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise Exception("Wrong direction expression!")
        elif (self.start_point.x > self.end_point.x and self.start_point.y > self.end_point.y): ## down left type
            if (self.direction == HORIZONAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise Exception("Wrong direction expression!")
        elif (self.start_point.x > self.end_point.x and self.start_point.y < self.end_point.y): ## up left type
            if (self.direction == HORIZONAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise Exception("Wrong direction expression!")
        else:
            raise Exception("Unexpected DoubleBendConnector Error!")

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_bend.draw(cell,layer)
        self.second_bend.draw(cell,layer )
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