import gdspy
import math

## "macros"
RIGHT = 0
UP = 90
LEFT = 180
DOWN = 270
VERTICAL = 0
HORIZONTAL = 1
FROM_LEFT_TO_RIGHT = 0
FROM_RIGHT_TO_LEFT = 1
FROM_LOWER_TO_UPPER = 2
FROM_UPPER_TO_LOWER = 3
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

    def __mul__(self, num):
        return Point(self.x * num, self.y * num)

    def __str__(self):
        return ("({},{})".format(self.x, self.y))



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

    def cut(self, another_layer, output_layer = None):
        """
        Cut the components in this layer with the components from another_layer, which means generate components 'in
        this layer but not in another_layer'. If output_layer is not specified the result will replace the components
        in this layer.

        Parameters
        ----------
        another_layer : Layer
            The layer for cutting.
        output_layer : Layer
            The layer for output (default: None).

        Notes
        -----
        The sub-cells will be taken into calculation but will not be revised.
        """
        if output_layer is None:
            output_layer = self
        top_cell = common_lib.top_level()[0]
        polygons = top_cell.get_polygons(by_spec=True)
        cutted_components = gdspy.boolean(polygons[(self.layer, self.datatype)],
                                          polygons[(another_layer.layer, another_layer.datatype)],
                                          "not", layer = output_layer.layer, datatype=output_layer.datatype,
                                          max_points=100000)
        top_cell.remove_polygons(lambda p, l, d:(l==output_layer.layer and d==output_layer.datatype))
        top_cell.add(cutted_components)

    def add(self, another_layer, output_layer = None):
        """
        Add the components in this layer with the components from another_layer, which means generate components 'in
        this layer or in another_layer'. If output_layer is not specified the result will replace the components
        in this layer.

        Parameters
        ----------
        another_layer : Layer
            The layer for adding.
        output_layer : Layer
            The layer for output (default: None).

        Notes
        -----
        The sub-cells will be taken into calculation but will not be revised.
        """
        if output_layer is None:
            output_layer = self
        top_cell = common_lib.top_level()[0]
        polygons = top_cell.get_polygons(by_spec=True)
        added_components = gdspy.boolean(polygons[(self.layer, self.datatype)],
                                          polygons[(another_layer.layer, another_layer.datatype)],
                                          "or", layer = output_layer.layer, datatype=output_layer.datatype,
                                          max_points=100000)
        top_cell.remove_polygons(lambda p, l, d:(l==output_layer.layer and d==output_layer.datatype))
        top_cell.add(added_components)

    def common(self, another_layer, output_layer = None):
        """
        Find the common part of the components in this layer and the components from another_layer, which means
        generate components 'in this layer and in another_layer'. If output_layer is not specified the result will
        replace the components in this layer.

        Parameters
        ----------
        another_layer : Layer
            The layer for finding the common part.
        output_layer : Layer
            The layer for output (default: None).

        Notes
        -----
        The sub-cells will be taken into calculation but will not be revised.
        """
        if output_layer is None:
            output_layer = self
        top_cell = common_lib.top_level()[0]
        polygons = top_cell.get_polygons(by_spec=True)
        common_components = gdspy.boolean(polygons[(self.layer, self.datatype)],
                                          polygons[(another_layer.layer, another_layer.datatype)],
                                          "and", layer = output_layer.layer, datatype=output_layer.datatype,
                                          max_points=100000)
        top_cell.remove_polygons(lambda p, l, d:(l==output_layer.layer and d==output_layer.datatype))
        top_cell.add(common_components)

    def dilation(self, distance = 2, output_layer = None ):
        """
        Dilate the components in this layer. If output_layer is not specified the result will
        replace the components in this layer.

        Parameters
        ----------
        distance : Int or Float
            The distance for dilation.
        output_layer : Layer
            The layer for output (default: None).

        Notes
        -----
        The sub-cells will be taken into calculation but will not be revised.
        """
        if output_layer is None:
            output_layer = self
        top_cell = common_lib.top_level()[0]
        polygons = top_cell.get_polygons(by_spec=True)
        dilation_components = gdspy.offset(polygons[(self.layer, self.datatype)], distance=distance,
                             join_first=True, layer=output_layer.layer, datatype=output_layer.datatype,
                             tolerance=0.0001, max_points=100000)
        top_cell.remove_polygons(lambda p, l, d: (l == output_layer.layer and d == output_layer.datatype))
        top_cell.add(dilation_components)

    def inversion(self, distance = 2, output_layer = None):
        """
        Make inversion for the components in this layer. If output_layer is not specified the result will
        replace the components in this layer.

        Parameters
        ----------
        distance : Int or Float
            The distance for inversion.
        output_layer : Layer
            The layer for output (default: None).

        Notes
        -----
        The sub-cells will be taken into calculation but will not be revised.s
        """
        if output_layer is None:
            output_layer = self
        top_cell = common_lib.top_level()[0]
        polygons = top_cell.get_polygons(by_spec=True)
        dilation_components = gdspy.offset(polygons[(self.layer, self.datatype)], distance=distance, join_first=True,
                             layer=output_layer.layer, datatype=output_layer.datatype, tolerance=0.0001, max_points=100000)
        inversion_components = gdspy.boolean(dilation_components, polygons[(self.layer, self.datatype)], "not",
                            layer=output_layer.layer, datatype=output_layer.datatype, max_points=100000)
        top_cell.remove_polygons(lambda p, l, d: (l == output_layer.layer and d == output_layer.datatype))
        top_cell.add(inversion_components)

        


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

    def remove_layer(self, layer):
        """
        Remove the components of the cell on a specified layer.

        Parameters
        ----------
        layer : Layer
            The layer for removing components.
        """
        self.cell.remove_polygons(lambda p, l, d:(l==layer.layer and d==layer.datatype))


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