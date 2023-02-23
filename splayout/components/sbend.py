from ..utils.utils import *
from ..components.bend import Bend
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation

class SBend:
    """
    S-Bend Definition with a First Clockwise Bend in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the S-Bend.
    end_point : Point
        End point of the S-Bend.
    width : float
        Width of the waveguides (μm).
    length : float
        Length of the S-Bend (μm).
    radius : float
        Radius of the S-Bend once length is specified (μm).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.

    Notes
    --------
    Once length is specified, the end_point of the S-Bend will be re-calculated.

    """
    def __init__(self,start_point, end_point, width,length=None,radius=5, z_start = None, z_end = None, material = None, rename = None):
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (length != None and radius != None): # overwrite the properties of S-Bend
            self.start_point = tuple_to_point(start_point)
            self.length = length
            self.radius = radius
            self.width = width
            self.radian = self.length/2/self.radius
            if (self.start_point.x > end_point.x and self.start_point.y > end_point.y): ## left down type
                self.delta_y = self.radius * math.sin(self.radian) * 2
                self.delta_x = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (-self.delta_x,-self.delta_y)
            if (self.start_point.x < end_point.x and self.start_point.y > end_point.y):  ## right down type
                self.delta_x = self.radius * math.sin(self.radian) * 2
                self.delta_y = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (self.delta_x, -self.delta_y)
            if (self.start_point.x < end_point.x and self.start_point.y < end_point.y):  ## right up type
                self.delta_y = self.radius * math.sin(self.radian) * 2
                self.delta_x = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (self.delta_x, self.delta_y)
            if (self.start_point.x > end_point.x and self.start_point.y < end_point.y):  ## left up type
                self.delta_x = self.radius * math.sin(self.radian) * 2
                self.delta_y = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (-self.delta_x, self.delta_y)

        else:
            self.start_point = tuple_to_point(start_point)
            self.end_point = tuple_to_point(end_point)
            self.width = width

            ## calculate radius and radian
            self.delta_x = abs(self.start_point.x - end_point.x)
            self.delta_y = abs(self.start_point.y - end_point.y)

            if (self.start_point.x > end_point.x and self.start_point.y > end_point.y) or (self.start_point.x < end_point.x and self.start_point.y < end_point.y):
                self.theta = math.atan(self.delta_y / self.delta_x)
            else:
                self.theta = math.atan(self.delta_x / self.delta_y)
            self.radian = math.pi - 2 * self.theta
            self.radius = math.sin(self.theta) * math.sqrt(
                math.pow(self.delta_x / 2, 2) + math.pow(self.delta_y / 2, 2)) / math.sin(self.radian)
            if (self.radius < 5):
                print("Warning! The radius of the bends in SBend is too small! The radius now is:" + str(
                    self.radius) + "μm.")
            self.length = self.radian * self.radius



        ## identify the type of S-Bend
        if (self.start_point.x > end_point.x and self.start_point.y > end_point.y): ## left down type
            self.first_bend_center_point = self.start_point + (-self.radius,0)
            self.first_bend = Bend(self.first_bend_center_point,-self.radian,0,self.width,self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (self.radius,0)
            self.second_bend = Bend(self.second_bend_center_point,math.pi - self.radian, math.pi,self.width,self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x < end_point.x and self.start_point.y > end_point.y): ## right down type
            self.first_bend_center_point = self.start_point + (0, -self.radius)
            self.first_bend = Bend(self.first_bend_center_point, math.pi/2 - self.radian, math.pi/2, self.width, self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (0, self.radius)
            self.second_bend = Bend(self.second_bend_center_point, math.pi*3/2 - self.radian, math.pi*3/2, self.width,
                                    self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x < end_point.x and self.start_point.y < end_point.y):  ## right up type
            self.first_bend_center_point = self.start_point + (self.radius, 0)
            self.first_bend = Bend(self.first_bend_center_point, math.pi - self.radian, math.pi, self.width, self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (-self.radius, 0)
            self.second_bend = Bend(self.second_bend_center_point, - self.radian, 0, self.width,
                                    self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x > end_point.x and self.start_point.y < end_point.y): ## left up type
            self.first_bend_center_point = self.start_point + (0, self.radius)
            self.first_bend = Bend(self.first_bend_center_point, math.pi*3 / 2 - self.radian, math.pi*3 / 2, self.width,
                                   self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (0, -self.radius)
            self.second_bend = Bend(self.second_bend_center_point, math.pi / 2 - self.radian, math.pi / 2,
                                    self.width,
                                    self.radius, self.z_start, self.z_end, self.material, self.rename)

    def draw(self, cell, layer):
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
        out : Point,Point
            Start point and end point.
        """
        self.first_bend.draw(cell, layer)
        self.second_bend.draw(cell, layer)
        return self.start_point, self.end_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
            if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                self.first_bend.draw_on_lumerical_CAD(engine)
                self.second_bend.draw_on_lumerical_CAD(engine)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_start_point(self):
        """
        Derive the start point of the S-Bend.

        Returns
        -------
        out : Point
            Start point.
        """
        return self.start_point

    def get_end_point(self):
        """
        Derive the end point of the S-Bend.

        Returns
        -------
        out : Point
            End point.
        """
        return self.end_point

    def get_length(self):
        """
        Derive the length of the S-Bend.

        Returns
        -------
        out : Point
            End point.
        """
        return self.length


class ASBend:
    """
    S-Bend Definition with a First Anti-Clockwise Bend in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the S-Bend.
    end_point : Point
        End point of the S-Bend.
    width : float
        Width of the waveguides (μm).
    length : float
        Length of the S-Bend (μm).
    radius : float
        Radius of the S-Bend once length is specified (μm).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : str or float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical.

    Notes
    --------
    Once length is specified, the end_point of the S-Bend will be re-calculated.

    """

    def __init__(self, start_point, end_point, width, length=None, radius=5, z_start = None, z_end = None, material = None, rename = None):
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        if (length != None and radius != None):  # overwrite the properties of S-Bend
            self.start_point = tuple_to_point(start_point)
            self.length = length
            self.radius = radius
            self.width = width
            self.radian = self.length / 2 / self.radius

            if (self.start_point.x > end_point.x and self.start_point.y > end_point.y):  ## left down type
                self.delta_x = self.radius * math.sin(self.radian) * 2
                self.delta_y = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (-self.delta_x, -self.delta_y)
            if (self.start_point.x < end_point.x and self.start_point.y > end_point.y):  ## right down type
                self.delta_y = self.radius * math.sin(self.radian) * 2
                self.delta_x = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (self.delta_x, -self.delta_y)
            if (self.start_point.x < end_point.x and self.start_point.y < end_point.y):  ## right up type
                self.delta_x = self.radius * math.sin(self.radian) * 2
                self.delta_y = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (self.delta_x, self.delta_y)
            if (self.start_point.x > end_point.x and self.start_point.y < end_point.y):  ## left up type
                self.delta_y = self.radius * math.sin(self.radian) * 2
                self.delta_x = (self.radius - self.radius * math.cos(self.radian)) * 2
                self.end_point = self.start_point + (-self.delta_x, self.delta_y)

        else:
            self.start_point = tuple_to_point(start_point)
            self.end_point = tuple_to_point(end_point)
            self.width = width

            ## calculate radius and radian
            self.delta_x = abs(self.start_point.x - end_point.x)
            self.delta_y = abs(self.start_point.y - end_point.y)

            if (self.start_point.x < end_point.x and self.start_point.y > end_point.y) or (
                    self.start_point.x > end_point.x and self.start_point.y < end_point.y):
                self.theta = math.atan(self.delta_y / self.delta_x)
            else:
                self.theta = math.atan(self.delta_x / self.delta_y)
            self.radian = math.pi - 2 * self.theta
            self.radius = math.sin(self.theta) * math.sqrt(
                math.pow(self.delta_x / 2, 2) + math.pow(self.delta_y / 2, 2)) / math.sin(self.radian)
            if (self.radius < 5):
                print("Warning! The radius of the bends in SBend is too small! The radius now is:" + str(
                    self.radius) + "μm.")
            self.length = self.radian * self.radius

        ## identify the type of S-Bend
        if (self.start_point.x > end_point.x and self.start_point.y > end_point.y): ## left down type
            self.first_bend_center_point = self.start_point + (0,-self.radius)
            self.first_bend = Bend(self.first_bend_center_point,math.pi/2,math.pi/2 + self.radian,self.width,self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (0,self.radius)
            self.second_bend = Bend(self.second_bend_center_point,math.pi*3/2 , math.pi*3/2 + self.radian,self.width,self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x < end_point.x and self.start_point.y > end_point.y): ## right down type
            self.first_bend_center_point = self.start_point + (self.radius, 0)
            self.first_bend = Bend(self.first_bend_center_point, math.pi , math.pi + self.radian, self.width,
                                   self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (-self.radius, 0)
            self.second_bend = Bend(self.second_bend_center_point,0,  self.radian,
                                    self.width, self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x < end_point.x and self.start_point.y < end_point.y):  ## right up type
            self.first_bend_center_point = self.start_point + (0, self.radius)
            self.first_bend = Bend(self.first_bend_center_point, math.pi*3 / 2, math.pi*3 / 2 + self.radian, self.width,
                                   self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (0, -self.radius)
            self.second_bend = Bend(self.second_bend_center_point, math.pi / 2, math.pi / 2 + self.radian,
                                    self.width, self.radius, self.z_start, self.z_end, self.material, self.rename)

        if (self.start_point.x > end_point.x and self.start_point.y < end_point.y): ## left up type
            self.first_bend_center_point = self.start_point + (-self.radius, 0)
            self.first_bend = Bend(self.first_bend_center_point, 0 ,  self.radian, self.width,
                                   self.radius, self.z_start, self.z_end, self.material, self.rename)
            self.second_bend_center_point = self.end_point + (self.radius, 0)
            self.second_bend = Bend(self.second_bend_center_point, math.pi,  math.pi + self.radian,
                                    self.width, self.radius, self.z_start, self.z_end, self.material, self.rename)

    def draw(self, cell, layer):
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
        out : Point,Point
            Start point and end point.
        """
        self.first_bend.draw(cell, layer)
        self.second_bend.draw(cell, layer)
        return self.start_point, self.end_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        if ((type(engine) == FDTDSimulation) or (type(engine) == MODESimulation)):
            if (type(self.z_start) != type(None) and type(self.z_end) != type(None) and type(self.material) != type(None) ):
                self.first_bend.draw_on_lumerical_CAD(engine)
                self.second_bend.draw_on_lumerical_CAD(engine)
            else:
                raise Exception("Z-axis specification or material specification is missing!")
        else:
            raise Exception("Wrong CAD engine!")

    def get_start_point(self):
        """
        Derive the start point of the S-Bend.

        Returns
        -------
        out : Point
            Start point.
        """
        return self.start_point

    def get_end_point(self):
        """
        Derive the end point of the S-Bend.

        Returns
        -------
        out : Point
            End point.
        """
        return self.end_point

    def get_length(self):
        """
        Derive the length of the S-Bend.

        Returns
        -------
        out : Point
            End point.
        """
        return self.length

