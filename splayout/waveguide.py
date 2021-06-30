from splayout.utils import *

class Waveguide:
    """
    Set of polygonal objects.
    Parameters
    ----------
    polygons : iterable of array-like[N][2]
        List containing the coordinates of the vertices of each polygon.
    layer : integer
        The GDSII layer number for this element.
    datatype : integer
        The GDSII datatype for this element (between 0 and 255).
    Attributes
    ----------
    polygons : list of numpy array[N][2]
        Coordinates of the vertices of each polygon.
    layers : list of integer
        The GDSII layer number for each element.
    datatypes : list of integer
        The GDSII datatype for each element (between 0 and 255).
    properties : {integer: string} dictionary
        Properties for these elements.
    Notes
    -----
    The last point should not be equal to the first (polygons are
    automatically closed).
    The original GDSII specification supports only a maximum of 199
    vertices per polygon.
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
        """
        Rotate this object.
        Parameters
        ----------
        angle : number
            The angle of rotation (in *radians*).
        center : array-like[2]
            Center point for the rotation.
        Returns
        -------
        out : `PolygonSet`
            This object.
        """
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