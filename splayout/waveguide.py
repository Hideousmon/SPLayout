from splayout.utils import *

class Waveguide:
    """
    Waveguide Definition in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the waveguide.
    end_point : Point
        End point of the waveguide.
    width : float
        Width of the waveguide (μm).

    Notes
    -----
    The waveguide should be vertical or horizontal, which means the x-axis value or the y-axis value
    of the start_point and the end_point should be the same.
    """

    def __init__(self, start_point, end_point, width):
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Waveguide Parameter!")
        self.start_point = start_point
        self.end_point = end_point
        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical waveguide
            self.down_left_x = start_point.x - width / 2
            self.down_left_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.up_right_x = end_point.x + width / 2
            self.up_right_y = end_point.y if (start_point.y < end_point.y) else start_point.y
            self.waveguide_type = VERTICAL
        else:  ## parallel waveguide
            self.down_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.down_left_y = start_point.y - width / 2
            self.up_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.up_right_y = end_point.y + width / 2
            self.waveguide_type = HORIZONTAL

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
        if (self.ifexist):
            waveguide = gdspy.Rectangle((self.down_left_x, self.down_left_y), (self.up_right_x, self.up_right_y),
                                        layer=layer.layer, datatype=layer.datatype)
            cell.cell.add(waveguide)
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