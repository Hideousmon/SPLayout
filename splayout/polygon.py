from splayout.utils import *

class Polygon:
    '''
    Polygon Definiton in SPLayout
    point_list:  point list of the polygon, type: tuple list or Point list
    '''
    def __init__(self,point_list):
        self.point_list = []
        self.tuple_list = []
        for item in point_list:
            if type(item) == Point:
                self.tuple_list.append(item.to_tuple())
                self.point_list.append(item)
            elif type(item) == tuple:
                self.tuple_list.append(item)
                self.point_list.append(Point(item[0],item[1]))
            else:
                raise Exception("Polygon Wrong Type Input!")

    def draw(self, cell, layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        polygon = gdspy.Polygon(self.tuple_list,layer=layer.layer,datatype = layer.datatype)
        cell.cell.add(polygon)
        return self.point_list

    def get_the_point_at_number(self,i):
        '''
        Derive the ith point of the polygon
        :param i:
        :return: the ith Point
        '''
        if (i >= len(self.point_list)):
            raise Exception("The Request Polygon Point not Exist!")
        return self.point_list[i]