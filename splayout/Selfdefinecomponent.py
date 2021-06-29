from splayout.utils import *

def MAKE_COMPONENT(filename,rename=None,relative_start_point=None,relative_end_point=None,relative_input_point=None,relative_through_point=None,relative_drop_point=None,relative_add_point=None,initial_relative_position = RIGHT):
    global SelfDefineComponent_cell
    if (filename[-4:] != ".gds"):
        raise Exception("The input of the AdditionalCell should be a GDSII file!")
    if rename == None:
        rename = filename[:-4]
    temp_lib = gdspy.GdsLibrary(infile=filename, rename_template=rename)
    SelfDefineComponent_cell = Cell(rename)
    SelfDefineComponent_cell.cell.add(temp_lib.top_level()[0])

    class SelfDefineComponent():
        def __init__(self,start_point,relative_position=RIGHT):
            self.start_point = start_point
            self.rotate_angle = relative_position - initial_relative_position
            if (relative_start_point != None):
                self.start_point_for_return = self.start_point + relative_start_point
            else:
                self.start_point_for_return = None
            if (relative_end_point != None):
                self.end_point_for_return = self.start_point + relative_end_point
            else:
                self.end_point_for_return = None
            if (relative_input_point != None):
                self.input_point_for_return = self.start_point + relative_input_point
            else:
                self.input_point_for_return = None
            if (relative_through_point != None):
                self.through_point_for_return = self.start_point + relative_through_point
            else:
                self.through_point_for_return = None
            if (relative_drop_point != None):
                self.drop_point_for_return = self.start_point + relative_drop_point
            else:
                self.drop_point_for_return = None
            if (relative_add_point != None):
                self.add_point_for_return = self.start_point + relative_add_point
            else:
                self.add_point_for_return = None

        def draw(self,cell):
            global SelfDefineComponent_cell
            cell.cell.add(gdspy.CellReference(SelfDefineComponent_cell.cell, (self.start_point.x, self.start_point.y),rotation=self.rotate_angle))

        def get_start_point(self):
            return self.start_point

        def get_end_point(self):
            if (self.end_point_for_return == None):
                raise Exception("You did not define a relative end point for your component!")
            else:
                return self.end_point_for_return

        def get_input_point(self):
            if (self.input_point_for_return == None):
                raise Exception("You did not define a relative input point for your component!")
            else:
                return self.input_point_for_return

        def get_through_point(self):
            if (self.through_point_for_return == None):
                raise Exception("You did not define a relative through point for your component!")
            else:
                return self.through_point_for_return

        def get_drop_point(self):
            if (self.drop_point_for_return == None):
                raise Exception("You did not define a relative drop point for your component!")
            else:
                return self.drop_point_for_return

        def get_add_point(self):
            if (self.add_point_for_return == None):
                raise Exception("You did not define a relative drop point for your component!")
            else:
                return  self.add_point_for_return

    return SelfDefineComponent