from splayout.utils import *
from splayout.quarbend import AQuarBend,QuarBend

class DoubleBendConnector:
    """
    Double Bend Connector Definition in SPLayout with Triple Waveguide and two 90-degree Bends.

    Parameters
    ----------
    start_point : Point
        Start point of the DoubleBendConnector.
    end_point : Point
        End point of the DoubleBendConnector.
    width : float
        Width of the waveguide (μm).
    radius : float
        Radius of the bends (μm).
    xpercent : float
        The center point location between start point and end point in the x axis (0~1).
    ypercent : float
        The center point location between start point and end point in the y axis (0~1).
    direction : HORIZONAL or VERTICAL
        HORIZONAL means the DoubleBendConnector will connect start point and end point
        in the horizontal direction. VERTICAL means the DoubleBendConnector will connect
        start point and end point in the vertical direction

    """
    def __init__(self,start_point,end_point,width,radius=5, xpercent = 0.5 , ypercent = 0.5,direction =  HORIZONTAL):
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
            if (self.direction == HORIZONTAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise  Exception("Wrong direction expression!")
        elif (self.start_point.x < self.end_point.x and self.start_point.y > self.end_point.y): ## down right type
            if (self.direction == HORIZONTAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise Exception("Wrong direction expression!")
        elif (self.start_point.x > self.end_point.x and self.start_point.y > self.end_point.y): ## down left type
            if (self.direction == HORIZONTAL):
                self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
                self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
            elif (self.direction == VERTICAL):
                self.first_bend = QuarBend(self.start_point, self.center_point, width, self.radius)
                self.second_bend = AQuarBend(self.center_point, self.end_point, width, self.radius)
            else:
                raise Exception("Wrong direction expression!")
        elif (self.start_point.x > self.end_point.x and self.start_point.y < self.end_point.y): ## up left type
            if (self.direction == HORIZONTAL):
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
        self.first_bend.draw(cell,layer)
        self.second_bend.draw(cell,layer )
        return self.start_point, self.end_point

    def get_start_point(self):
        """
        Derive the start point of the connector.

        Returns
        -------
        out : Point
            Start point.
        """
        return  self.start_point

    def get_end_point(self):
        """
        Derive the end point of the connector.

        Returns
        -------
        out : Point
            End point.
        """
        return  self.end_point