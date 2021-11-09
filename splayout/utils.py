import gdspy
import math


## "macros"
RIGHT = 0
UP = 90
LEFT = 180
DOWN = 270
VERTICAL = 0
HORIZONTAL = 1
pi = math.pi
Si = "Si (Silicon) - Palik"
SiO2 = "SiO2 (Glass) - Palik"
ETCH = "etch"
FORWARD = 1
BACKWARD = 0

## global library
common_lib = gdspy.GdsLibrary(unit=1.0e-6, precision=1.0e-9)

def remove_cell(cell):
    """
    Remove a cell.

    Parameters
    ----------
    cell : str or Cell
        Cell to be removed.
    """
    if type(cell) == str:
        common_lib.remove(cell)
    elif type(cell) == Cell:
        common_lib.remove(cell.cell)


class Point:
    """
    Point Definition in SPLayout. Point is the basic unit that describe the locations of all the
    components in SPLayout.

    Parameters
    ----------
    x : float
        The x coordinate of a point.
    y : float
        The y coordinate of a point.

    Notes
    -----
    By overloading operators, the Point object can do calculations with Point object and Tuples, the available operations are:
    Point == Point
    Point + Point
    Point + Tuple
    Point - Point
    Point - Tuple
    Point / float
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):

        if (type(other) != Point):
            return False
        else:
            return (self.x == other.x) and (self.y == other.y)

    def to_tuple(self):
        """
        Convert Point into Tuple.

        Returns
        -------
        out : Tuple
            (x,y).
        """
        return (self.x, self.y)

    def get_percent_point(self,others,percent = 0.5):
        """
        Derive the point on the connection line of the point and the other point.

        Parameters
        ----------
        others : Point
            Another end of the line.
        percent : float
            The percent from the original point to the end of the line (0~1).

        Returns
        -------
        out : Point
            The desired point.
        """
        return Point( self.x + (others.x - self.x)*percent,  self.y+ (others.y - self.y)*percent)

    def get_relative_radian(self,other): ## ! -pi to pi
        """
        Derive the relative radian with another point as a circle center point.

        Parameters
        ----------
        others : Point
            The center of the circle.

        Returns
        -------
        out : float
            The desired radian (radian,  -pi to pi).
        """
        radian = math.atan( (self.y - other.y)/(self.x - other.x))
        return radian

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
    """
    Layer Definition in SPLayout. The object of Layer can be used to "***.draw(*,layer)" functions of the components.

    Parameters
    ----------
    layer : int
        The layer index.
    datatype : int
        The datatype index.
    """
    def __init__(self,layer,datatype = 0):
        self.layer = layer
        self.datatype = datatype

class Cell():
    """
    Cell Definition in SPLayout. The object of Cell can be used to "***.draw(cell,*)" functions of the components.

    Parameters
    ----------
    name : string
        The name of the cell.
    lib : gdspy.GdsLibrary
        The library that the cell will belong to (Normally, no need to specify it).
    """
    def __init__(self,name,lib=common_lib):
        if type(name) != str :
            raise Exception("The name of a cell should be a string!")
        self.cell = lib.new_cell(name,  overwrite_duplicate=True)

    def remove_components(self):
        """
        Remove all the polygons and sub-cells in the cell.
        """
        self.cell.flatten()
        self.cell.remove_polygons(lambda pts, layer, datatype:any)

    def flatten(self):
        """
        Flatten all the polygons in the cell.
        """
        self.cell.flatten()


def tuple_to_point(input_tuple):
    """
    Automatically convert tuple to Point.

    Parameters
    ----------
    input_tuple : tuple or Point
        The data to be converted.

    Returns
    -------
    output_point : Point
        Converted Point.
    """
    if type(input_tuple) == tuple and len(input_tuple) == 2:
        output_point = Point(input_tuple[0],input_tuple[1])
    elif type(input_tuple) == Point:
        output_point = input_tuple
    elif type(input_tuple) == type(None):
        output_point = None
    else:
        raise Exception("Wrong data type input!")
    return output_point

def make_gdsii_file(filename,cover_source_layer=None,cover_target_layer=None,inv_source_layer=None,inv_target_layer=None,lib = common_lib):
    """
    Make gdsii file based on all the drawn component before the function is called.

    Parameters
    ----------
    filename : string
        The name of the target file (can include the path to the file, e.g. "./output/test.gds").
    cover_source_layer : Layer
        The layer based on which the cover layer will be generated.
    cover_target_layer : Layer
        The layer that will contain the generated cover layer.
    inv_source_layer : Layer
        The layer based on which the inverse layer will be generated.
    cover_target_layer : Layer
        The layer that will contain the generated inverse layer.
    """
    if (type(inv_source_layer) == Layer ):
        if (type(inv_target_layer) != Layer):
            raise  Exception("The target layer should be the same type (Layer or List) with source layer")
        top_cell = lib.top_level()[0]
        # polygon_set = top_cell.get_polygonsets()
        polygons =  top_cell.get_polygons(by_spec=True)
        # print(polygons[(inv_source_layer.layer,inv_source_layer.datatype)])
        outer = gdspy.offset(polygons[(inv_source_layer.layer,inv_source_layer.datatype)],distance=2,join_first=True, layer=inv_source_layer.layer,tolerance=0.0001,max_points = 100000)
        # top_cell.remove_polygons(lambda pts, layer, datatype:layer == inv_layer.layer)
        inv = gdspy.boolean(outer, polygons[(inv_source_layer.layer,inv_source_layer.datatype)], "not",layer=inv_target_layer.layer,datatype=inv_target_layer.datatype,max_points = 100000)
        top_cell.add(inv)

    if (type(cover_source_layer) == Layer ):
        if (type(cover_target_layer) != Layer):
            raise  Exception("The target layer should be the same type (Layer or List) with source layer")
        top_cell = lib.top_level()[0]
        # polygon_set = top_cell.get_polygonsets()
        polygons =  top_cell.get_polygons(by_spec=True)
        # print(polygons[(inv_source_layer.layer,inv_source_layer.datatype)])
        cover = gdspy.offset(polygons[(cover_source_layer.layer,cover_source_layer.datatype)],distance=2,join_first=True, layer=cover_target_layer.layer,datatype=cover_target_layer.datatype,tolerance=0.0001,max_points = 100000)
        top_cell.add(cover)

    if (filename[-4:] != ".gds"):
        filename += ".gds"

    lib.write_gds(filename)