from ..utils.utils import *

class Text:
    """
    Text Definition in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the DoubleBendConnector.
    text : string
        Characters that you want to put on the layout.
    size : int
        The size of the characters.
    horizontal : bool
        If the text will be put horizontally.

    """
    def __init__(self,start_point,text,size=20,horizontal=True):
        self.start_point = tuple_to_point(start_point)
        self.text = text
        self.size = size
        self.horizontal=horizontal
        self.radian = 0

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
        out : Point
            Start point.
        """
        text = gdspy.Text(self.text,size = self.size, position=(self.start_point.x,self.start_point.y),horizontal=self.horizontal,angle = self.radian,
                              layer=layer.layer, datatype=layer.datatype)
        cell.cell.add(text)
        return self.start_point
