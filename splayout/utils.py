import gdspy
import math

## "macros"
RIGHT = 0
UP = 90
LEFT = 180
DOWN = 270
VERTICAL = 0
HORIZONAL = 1

## global library
common_lib = gdspy.GdsLibrary(unit=1.0e-6, precision=1.0e-9)


class Point:
    '''
    Point Definiton in SPLayout
    Points descript the 2D coordinate in a layout.
    x: x-coordinate, unit: μm
    y: y-coordinate, unit: μm
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def to_tuple(self):
        '''
        Convert Point into Tuple
        :return: a tuple
        '''
        return (self.x, self.y)

    def get_percent_point(self,others,percent = 0.5):
        '''
        Derive the point on the connection line of the point and the other point
        :param others: another point
        :param percent: the distance rate from the start point compared with the whole distance
        :return: the center point
        '''
        return Point( self.x + (others.x - self.x)*percent,  self.y+ (others.y - self.y)*percent)

    def get_relative_angle(self,other): ## ! -pi to pi
        '''
        Derive the relative angle with another point as a ring center point
        :param other: the reference center point
        :return: the relative point
        '''
        angle = math.atan( (self.y - other.y)/(self.x - other.x))
        return angle

    def __add__(self, other):
        if (type(other) == Point):
            return Point(self.x + other.x,self.y + other.y)
        elif (type(other) == tuple):
            return Point(self.x + other[0],self.y + other[1])
        else:
            raise Exception("Wrong data type!")

    def __sub__(self, other):
        if (type(other) == Point):
            return Point(self.x - other.x,self.y - other.y)
        elif (type(other) == tuple):
            return Point(self.x - other[0],self.y - other[1])
        else:
            raise Exception("Wrong data type!")

    def __truediv__(self, num):
        return Point(self.x /num, self.y/num)


class Layer():
    def __init__(self,layer,datatype = 0):
        self.layer = layer
        self.datatype = datatype

class Cell():
    def __init__(self,name,lib=common_lib):
        if type(name) != str :
            raise Exception("The name of a cell should be a string!")
        self.cell = lib.new_cell(name,  overwrite_duplicate=True)


def make_gdsii_file(filename,cover_souce_layer=None,cover_target_layer=None,inv_source_layer=None,inv_target_layer=None):
    if (type(inv_source_layer) == Layer ):
        if (type(inv_target_layer) != Layer):
            raise  Exception("The target layer should be the same type (Layer or List) with source layer")
        top_cell = common_lib.top_level()[0]
        # polygon_set = top_cell.get_polygonsets()
        polygons =  top_cell.get_polygons(by_spec=True)
        # print(polygons[(inv_source_layer.layer,inv_source_layer.datatype)])
        outer = gdspy.offset(polygons[(inv_source_layer.layer,inv_source_layer.datatype)],distance=2,join_first=True, layer=inv_source_layer.layer,tolerance=0.0001,max_points = 100000)
        # top_cell.remove_polygons(lambda pts, layer, datatype:layer == inv_layer.layer)
        inv = gdspy.boolean(outer, polygons[(inv_source_layer.layer,inv_source_layer.datatype)], "not",layer=inv_target_layer.layer,datatype=inv_target_layer.datatype,max_points = 100000)
        top_cell.add(inv)

    if (type(cover_souce_layer) == Layer ):
        if (type(cover_target_layer) != Layer):
            raise  Exception("The target layer should be the same type (Layer or List) with source layer")
        top_cell = common_lib.top_level()[0]
        # polygon_set = top_cell.get_polygonsets()
        polygons =  top_cell.get_polygons(by_spec=True)
        # print(polygons[(inv_source_layer.layer,inv_source_layer.datatype)])
        cover = gdspy.offset(polygons[(cover_souce_layer.layer,cover_souce_layer.datatype)],distance=2,join_first=True, layer=cover_target_layer.layer,datatype=cover_target_layer.datatype,tolerance=0.0001,max_points = 100000)
        top_cell.add(cover)

    common_lib.write_gds(filename)