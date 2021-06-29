from splayout.utils import *

class Waveguide:
    """
    Waveguide Definiton in SPLayout
    start_point: start point
    end_point: end point
    width: width of the waveguide, unit: μm
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
            self.waveguide_type = HORIZONAL

    def draw(self, cell, layer):
        '''
        Draw the Component on Layout
        :param cell:
        :param layer:
        :return:
        '''
        if (self.ifexist):
            waveguide = gdspy.Rectangle((self.down_left_x, self.down_left_y), (self.up_right_x, self.up_right_y),
                                        layer=layer.layer, datatype=layer.datatype)
            cell.cell.add(waveguide)
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