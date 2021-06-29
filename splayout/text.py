from splayout.utils import *

class Text:
    def __init__(self,start_point,text,size=20,horizontal=True):
        self.start_point = start_point
        self.text = text
        self.size = size
        self.horizontal=horizontal
        self.angle = 0

    def draw(self,cell,layer):
        text = gdspy.Text(self.text,size = self.size, position=(self.start_point.x,self.start_point.y),horizontal=self.horizontal,angle=self.angle,
                              layer=layer.layer, datatype=layer.datatype)
        cell.cell.add(text)
        return self.start_point
