from splayout.utils import *

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

    Notes
    -----
    There is a physical constrain that the taper should be longer than 5μm for reducing loss.
    The taper should be vertical or horizontal, which means the x-axis value or the y-axis value
    of the start_point and the end_point should be the same.
    """
    def __init__(self, start_point, end_point, start_width,end_width):
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Taper Parameter!")
        self.start_point = start_point
        self.end_point = end_point

        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical taper
            if (math.fabs(start_point.y - end_point.y) < 5):
                raise Exception("Taper Too Short!")
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
            if (math.fabs(start_point.x - end_point.x) < 5):
                raise Exception("Taper Too Short!")
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