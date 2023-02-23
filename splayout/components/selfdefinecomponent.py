from ..utils.utils import *

## global parameters
SelfDefineCount = -1
SelfDefineComponent_cell_list = []

def MAKE_COMPONENT(filename,rename=None,relative_start_point=Point(0,0),relative_end_point=None,relative_input_point=None,relative_through_point=None,relative_drop_point=None,relative_add_point=None,initial_relative_position = RIGHT):
    """
    Make an self-defined Class with another gdsii file.

    Parameters
    ----------
    filename : string
        The name of the file that contains your component.
    rename : string
        Name of the cell (default: the filename).
    relative_start_point : Point
        The start point in the file that contains your component (can be missing).
    relative_end_point : Point
        The end point in the file that contains your component (can be missing).
    relative_input_point : Point
        The input point in the file that contains your component (can be missing).
    relative_through_point : Point
        The through point in the file that contains your component (can be missing).
    relative_drop_point : Point
        The drop point in the file that contains your component (can be missing).
    relative_add_point : Point
        The add point in the file that contains your component (can be missing).
    initial_relative_position : RIGHT or UP or LEFT or DOWN
        The relative position of the component that is contained in the file with 'filename'.

    Returns
    -------
    out : ‘Class’
        Can be used to define your own component that is contained in the file with 'filename'.

    Notes
    --------
    The returned Class has two parameters: start_point,relative_position.
    It can be drawn on the cell with:  object.draw(cell).
    If the relative_***_point is specified, then you can use: object.get_***_point() to drive the corresponding point in the cell.

    Examples
    --------
    >>> # take the "selfdefine.gds" as an example
    >>> SelfDefineComponent = MAKE_COMPONENT("selfdefine.gds")
    >>> # start point for the component
    >>> start_point = Point(0,-90)
    >>> # make the component
    >>> component = SelfDefineComponent(start_point,RIGHT)
    >>> # draw the component on the layout
    >>> component.draw(cell)
    """
    global SelfDefineComponent_cell_list
    global SelfDefineCount
    if (filename[-4:] != ".gds"):
        raise Exception("The input of the AdditionalCell should be a GDSII file!")
    if rename == None:
        rename = filename[:-4]
    temp_lib = gdspy.GdsLibrary(infile=filename, rename_template=rename)
    SelfDefineComponent_cell = Cell(rename)
    SelfDefineComponent_cell.cell.add(temp_lib.top_level()[0])
    SelfDefineComponent_cell_list.append(SelfDefineComponent_cell)
    SelfDefineCount += 1
    SelfDefineCount_local = SelfDefineCount

    relative_start_point = tuple_to_point(relative_start_point)
    relative_end_point = tuple_to_point(relative_end_point)
    relative_input_point =tuple_to_point(relative_input_point)
    relative_through_point =tuple_to_point(relative_through_point)
    relative_drop_point =tuple_to_point(relative_drop_point)
    relative_add_point = tuple_to_point(relative_add_point)

    class SelfDefineComponent():
        def __init__(self, start_point, relative_position=RIGHT):
            self.rotate_radian = int(relative_position - initial_relative_position + 360) % 360
            self.count = SelfDefineCount_local
            if (type(relative_start_point) != type(None)):
                if (self.rotate_radian == RIGHT):
                    self.start_point = tuple_to_point(start_point) - relative_start_point
                    self.start_point_for_return = self.start_point + relative_start_point
                elif (self.rotate_radian == UP):
                    self.start_point = tuple_to_point(start_point) - relative_start_point - Point(
                        -relative_start_point.y - relative_start_point.x,
                        -relative_start_point.y + relative_start_point.x)
                    self.start_point_for_return = self.start_point + Point(-relative_start_point.y,
                                                                           relative_start_point.x)
                elif (self.rotate_radian == LEFT):
                    self.start_point = tuple_to_point(start_point) - relative_start_point - Point(
                        -relative_start_point.x,
                        -relative_start_point.y) * 2
                    self.start_point_for_return = self.start_point + Point(-relative_start_point.x,
                                                                           -relative_start_point.y)
                elif (self.rotate_radian == DOWN):
                    self.start_point = tuple_to_point(start_point) - relative_start_point - Point(
                        relative_start_point.y - relative_start_point.x,
                        -relative_start_point.y - relative_start_point.x)
                    self.start_point_for_return = self.start_point + Point(relative_start_point.y,
                                                                           -relative_start_point.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.start_point_for_return = None
            if (type(relative_end_point) != type(None)):
                relative_end_point_transfer = relative_end_point
                if (self.rotate_radian == RIGHT):
                    self.end_point_for_return = self.start_point + relative_end_point_transfer
                elif (self.rotate_radian == UP):
                    self.end_point_for_return = self.start_point + Point(-relative_end_point_transfer.y,
                                                          relative_end_point_transfer.x)
                elif (self.rotate_radian == LEFT):
                    self.end_point_for_return = self.start_point + Point(-relative_end_point_transfer.x,
                                                                  - relative_end_point_transfer.y)
                elif (self.rotate_radian == DOWN):
                    self.end_point_for_return = self.start_point + Point(relative_end_point_transfer.y,
                                                          -relative_end_point_transfer.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.end_point_for_return = None
            if (type(relative_input_point) != type(None)):
                relative_input_point_transfer = relative_input_point
                if (self.rotate_radian == RIGHT):
                    self.input_point_for_return = self.start_point + relative_input_point_transfer
                elif (self.rotate_radian == UP):
                    self.input_point_for_return = self.start_point + Point(-relative_input_point_transfer.y,
                                                          relative_input_point_transfer.x)
                elif (self.rotate_radian == LEFT):
                    self.input_point_for_return = self.start_point + Point(-relative_input_point_transfer.x,
                                                                  -relative_input_point_transfer.y)
                elif (self.rotate_radian == DOWN):
                    self.input_point_for_return = self.start_point + Point(relative_input_point_transfer.y,
                                                          -relative_input_point_transfer.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.input_point_for_return = None
            if (type(relative_through_point) != type(None)):
                relative_through_point_transfer = relative_through_point
                if (self.rotate_radian == RIGHT):
                    self.through_point_for_return = self.start_point + relative_through_point_transfer
                elif (self.rotate_radian == UP):
                    self.through_point_for_return = self.start_point + Point(-relative_through_point_transfer.y,
                                                          relative_through_point_transfer.x)
                elif (self.rotate_radian == LEFT):
                    self.through_point_for_return = self.start_point + Point(-relative_through_point_transfer.x,
                                                                  -relative_through_point_transfer.y)
                elif (self.rotate_radian == DOWN):
                    self.through_point_for_return = self.start_point + Point(relative_through_point_transfer.y,
                                                          -relative_through_point_transfer.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.through_point_for_return = None
            if (type(relative_drop_point) != type(None)):
                relative_drop_point_transfer = relative_drop_point
                if (self.rotate_radian == RIGHT):
                    self.drop_point_for_return = self.start_point + relative_drop_point_transfer
                elif (self.rotate_radian == UP):
                    self.drop_point_for_return = self.start_point + Point(-relative_drop_point_transfer.y,
                                                          relative_drop_point_transfer.x)
                elif (self.rotate_radian == LEFT):
                    self.drop_point_for_return = self.start_point + Point(-relative_drop_point_transfer.x,
                                                                  -relative_drop_point_transfer.y)
                elif (self.rotate_radian == DOWN):
                    self.drop_point_for_return = self.start_point + Point(relative_drop_point_transfer.y,
                                                          -relative_drop_point_transfer.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.drop_point_for_return = None
            if (type(relative_add_point) != type(None)):
                relative_add_point_transfer = relative_add_point
                if (self.rotate_radian == RIGHT):
                    self.add_point_for_return = self.start_point + relative_add_point_transfer
                elif (self.rotate_radian == UP):
                    self.add_point_for_return = self.start_point + Point(-relative_add_point_transfer.y,
                                                          relative_add_point_transfer.x)
                elif (self.rotate_radian == LEFT):
                    self.add_point_for_return = self.start_point + Point(-relative_add_point_transfer.x,
                                                                  -relative_add_point_transfer.y)
                elif (self.rotate_radian == DOWN):
                    self.add_point_for_return = self.start_point + Point(relative_add_point_transfer.y,
                                                          -relative_add_point_transfer.x)
                else:
                    raise Exception("Wrong relative position!")
            else:
                self.add_point_for_return = None

        def draw(self,cell):
            global SelfDefineComponent_cell_list
            cell.cell.add(gdspy.CellReference(SelfDefineComponent_cell_list[self.count].cell, (self.start_point.x, self.start_point.y),rotation=self.rotate_radian))

        def get_start_point(self):
            return self.start_point_for_return

        def get_end_point(self):
            if (type(self.end_point_for_return) == type(None)):
                raise Exception("You did not define a relative end point for your component!")
            else:
                return self.end_point_for_return

        def get_input_point(self):
            if (type(self.input_point_for_return) == type(None)):
                raise Exception("You did not define a relative input point for your component!")
            else:
                return self.input_point_for_return

        def get_through_point(self):
            if (type(self.through_point_for_return) == type(None)):
                raise Exception("You did not define a relative through point for your component!")
            else:
                return self.through_point_for_return

        def get_drop_point(self):
            if (type(self.drop_point_for_return) == type(None)):
                raise Exception("You did not define a relative drop point for your component!")
            else:
                return self.drop_point_for_return

        def get_add_point(self):
            if (type(self.add_point_for_return) == type(None)):
                raise Exception("You did not define a relative drop point for your component!")
            else:
                return  self.add_point_for_return

    return SelfDefineComponent