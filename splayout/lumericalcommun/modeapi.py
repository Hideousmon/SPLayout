import sys, os
from ..utils.utils import *
import numpy as np
import scipy.constants

class MODESimulation:
    """
    MODE Simulation via Lumerical varFDTD API, especially for 2-Dimension structures.

    Parameters
    ----------
    hide : Bool
        Whether the Lumerical window is hidden (default: False).
    fdtd_path : String
        Path to the Lumerical Python API folder.
    load_file : String
        Path to the .lms file that what want to be loaded (default: None).

    """
    def __init__(self,hide=0,fdtd_path = "C:\\Program Files\\Lumerical\\v202\\api\\python\\", load_file = None):
        sys.path.append(fdtd_path)
        sys.path.append(os.path.dirname(__file__))
        try:
            os.add_dll_directory(fdtd_path)
        except:
            pass
        try:
            import lumapi
        except:
            raise Exception(
                "Lumerical MODE is not installed in the default path, please specify the python api path with fdtd_path=***.")
        self.lumapi = lumapi
        self.mode = self.lumapi.MODE(hide=hide)
        if (type(load_file) != type(None)):
            self.mode.eval("load(\"" + load_file + "\");")
        self.global_source_set_flag = 0
        self.global_monitor_set_flag = 0

    def save(self,filename="temp"):
        """
        Save the simulation as a ".lms" file.

        Parameters
        ----------
        filename : String
            File name or File path (default: "temp").
        """
        self.mode.save(filename)

    def run(self,filename="temp"):
        """
        Save the simulation as a ".lms" file and run.

        Parameters
        ----------
        filename : String
            File name or File path (default: "temp").
        """
        self.save(filename)
        self.mode.eval("switchtolayout;")
        self.mode.eval("run;")


    def add_varfdtd_region(self,bottom_left_corner_point,top_right_corner_point, mode_position, simulation_time = 5000, test_points = None, background_index = 1.444,mesh_order = 2,height = 1,z_symmetric = 0):
        """
        Add varFDTD simulation region in Lumerical MODE.

        Parameters
        ----------
        bottom_left_corner_point : Point or tuple
            Lower left corner of the region.
        top_right_corner_point : Point or tuple
            Upper right corner of the region.
        mode_position : Point or tuple
            The point for slab mode calculation.
        simulation_time : int
            Total simulation time (unit: fs, default: 5000).
        test_points : List of tuple
            Four test point for effective index  (default: None).
        background_index : float
            Background refractive index in the simualtion region  (default: 1.444).
        mesh_order :  int
            The level of the mesh grid in Lumerical MODE (default: 2).
        height : Float
            Height of the simulation region (in z axis, unit: μm, default: 1).
        z_symmetric : Bool
            Whether set symmetric in z-axis (default: 0).
        """
        bottom_left_corner_point = tuple_to_point(bottom_left_corner_point)
        top_right_corner_point = tuple_to_point(top_right_corner_point)
        mode_position = tuple_to_point(mode_position)
        mode_position = mode_position - (bottom_left_corner_point + top_right_corner_point)/2
        self.mode.eval("addvarfdtd;")
        position = (bottom_left_corner_point + top_right_corner_point)/2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"x span\"," + "%.6f"%(x_span) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(y_span) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        self.mode.eval("set(\"z span\"," + "%.6f"%(height) + "e-6);")
        self.mode.eval("set(\"x0\"," + "%.6f"%(mode_position.x) + "e-6);")
        self.mode.eval("set(\"y0\"," + "%.6f"%(mode_position.y) + "e-6);")
        if (type(test_points) != type(None)):
            self.mode.eval("set(\"test points\"," + self.lumerical_list(test_points) + ");")
        self.mode.eval("set(\"index\"," + str(background_index) + ");")
        self.mode.eval("set(\"simulation time\"," + str(simulation_time) + "e-15);")
        self.mode.eval("set(\"mesh accuracy\"," + str(mesh_order) + ");")
        if (z_symmetric == 1):
            self.mode.eval("set(\"z min bc\", \"Symmetric\");")


    def add_gaussian_source(self,position, width=2,source_name="gauss", amplitude = 1, phase = 0, waist_radius = 2.45 , wavelength_start=1.540,wavelength_end=1.570,direction = FORWARD):
        """
        Add gaussian source in Lumerical MODE.

        Parameters
        ----------
        position : Point or tuple
            Center point of the source.
        width : Float
            Width of the source (in y axis, unit: μm, default: 2).
        source_name : String
            Name of the source in Lumerical MODE (default: "source").
        amplitude : float
            Amplitude of the source.
        phase : float
            Phase of the source (unit: radian).
        waist_radius : float
            Waist radius of the gauss source (unit: μm).
        wavelength_start : Float
            The start wavelength of the source (unit: μm, default: 1.540).
        wavelength_end : Float
            The end wavelength of the source (unit: μm, default: 1.570).
        direction : Int
            The light propagation direction 1: the positive direction of x-axis, 0: the negative direction of x-axis(FORWARD:1, BACKWARD:0 , default: FORWARD).
        """
        position = tuple_to_point(position)
        self.mode.eval("addgaussian;")
        self.mode.eval("set(\"name\",\"" + source_name + "\");")
        self.mode.eval("set(\"injection axis\",\"x-axis\");")
        if (direction == FORWARD):
            self.mode.eval("set(\"direction\",\"Forward\");")
        elif (direction == BACKWARD):
            self.mode.eval("set(\"direction\",\"Backward\");")
        else:
            raise Exception("Wrong source direction!")
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(width) + "e-6);")
        self.mode.eval("set(\"override global source settings\",0);")
        if not self.global_source_set_flag:
            self.mode.setglobalsource('set wavelength', True)
            self.mode.setglobalsource('wavelength start', wavelength_start*1e-6)
            self.mode.setglobalsource('wavelength stop', wavelength_end*1e-6)
            self.wavelength_start = wavelength_start*1e-6
            self.wavelength_end = wavelength_end*1e-6
            self.global_source_set_flag = 1
        self.mode.eval("set(\"amplitude\"," + "%.6f"%(amplitude) + ");")
        self.mode.eval("set(\"phase\"," + "%.6f"%(phase) + ");")
        self.mode.eval("set(\"waist radius w0\"," + "%.6f"%(waist_radius) + "e-6);")


    def add_power_monitor(self,position,width=2,height=0.8,monitor_name="powermonitor",points=101):
        """
        Add power monitor in Lumerical MODE.

        Parameters
        ----------
        position : Point or tuple
           Center point of the monitor.
        width : Float
           Width of the monitor (in y axis, unit: μm, default: 2).
        height :  Float
            Height of the monitor (in z axis, unit: μm, default: 0.8).
        monitor_name : String
            Name of the structure in Lumerical MODE (default: "powermonitor").
        points : Int
            The number of the frequency points that will be monitored (default: 1001).
        """
        position = tuple_to_point(position)
        self.mode.eval("addpower;")
        self.mode.eval("set(\"name\",\"" + monitor_name+"\");")
        self.mode.eval("set(\"monitor type\",5);")
        self.mode.eval("set(\"x\","+ "%.6f"%(position.x) +"e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(width) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        self.mode.eval("set(\"z span\"," + "%.6f"%(height) + "e-6);")
        self.mode.eval("set(\"override global monitor settings\",0);")
        if not self.global_monitor_set_flag:
            self.mode.setglobalmonitor('use source limits', True)
            self.mode.setglobalmonitor('use wavelength spacing', True)
            self.mode.setglobalmonitor('frequency points', points)
            self.frequency_points = points
            self.global_monitor_set_flag = 1



    def add_structure_from_gdsii(self,filename,cellname,layer=1,datatype=0,material=Si, z_start = -0.11, z_end = 0.11,rename = None):
        """
        Draw the structure to the simulation CAD from gdsii file.

        Parameters
        ----------
        filename : String
           GDSII file path.
        cellname : String
           The name of the cell that contains the structure.
        layer :  Int
            The number of the layer that contains the structure (default: 1).
        datatype : Int
            The datatype of the layer that contains the structure (default: 0).
        material : String
            Material setting for the structure in Lumerical MODE (Si = "Si (Silicon) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: Si).
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical MODE.
        """
        self.mode.redrawoff()
        self.mode.eval("n = gdsimport(\"" + filename + "\",\"" + cellname + "\",\"" +str(layer) +":"+ str(datatype) +"\",\"" + material +"\", "+str(z_start)+"e-6," +str(z_end)+"e-6);")
        self.mode.redrawon()
        if (rename != None):
            self.mode.eval("select(\"GDS_LAYER_" + str(layer) +":" + str(datatype) + "\");")
            self.mode.eval("set(\"name\",\"" + rename + "\");")


    @staticmethod
    def lumerical_list(tuple_list):
        """
        Convert a tuple list to Lumerical list String expression.

        Parameters
        ----------
        tuple_list : List
            The List for conversion.

        Returns
        -------
        out : String
            The Lumerical list String expression of the input List.
        """
        if len(tuple_list) == 0:
            string = "[]"
        else:
            string = "["
            for item in tuple_list[:-1]:
                string += "%.6f"%(item[0]) + "e-6," + "%.6f"%(item[1]) + "e-6;"
            string += "%.6f"%(tuple_list[-1][0]) + "e-6," + "%.6f"%(tuple_list[-1][1]) + "e-6]"
        return string

    def put_rectangle(self, bottom_left_corner_point, top_right_corner_point, z_start, z_end, material, rename):
        '''
        Draw a rectangle on the varFDTD simulation CAD.

        Parameters
        ----------
        bottom_left_corner_point : tuple or Point
            Bottom left corner point of the rectangle.
        top_right_corner_point : tuple or Point
            Top right corner point of the rectangle.
        z_start : Float
            The start point for the structure in z axis (unit: μm).
        z_end : Float
            The end point for the structure in z axis (unit: μm).
        material : str or float
            Material setting for the structure in Lumerical MODE (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in MODE will be
            <Object defined dielectric>, and index will be defined.
        rename : String
            New name of the structure in Lumerical.
        '''
        bottom_left_corner_point = tuple_to_point(bottom_left_corner_point)
        top_right_corner_point = tuple_to_point(top_right_corner_point)
        self.mode.eval("addrect;")
        self.mode.eval("set(\"x min\"," + "%.6f"%(bottom_left_corner_point.x) + "e-6);")
        self.mode.eval("set(\"x max\"," + "%.6f"%(top_right_corner_point.x) + "e-6);")
        self.mode.eval("set(\"y min\"," + "%.6f"%(bottom_left_corner_point.y) + "e-6);")
        self.mode.eval("set(\"y max\"," + "%.6f"%(top_right_corner_point.y) + "e-6);")
        self.mode.eval("set(\"z min\"," + "%.6f"%(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + "%.6f"%(z_end) + "e-6);")
        if type(material) == str:
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.mode.eval("set(\"name\",\"" + rename + "\");")

    def put_polygon(self, tuple_list, z_start, z_end, material, rename):
        '''
        Draw a polygon on the varFDTD simulation CAD.

        Parameters
        ----------
        point_list : List of Tuple
            Points for the polygon.
        z_start : Float
            The start point for the structure in z axis (unit: μm).
        z_end : Float
            The end point for the structure in z axis (unit: μm).
        material : str or float
            Material setting for the structure in Lumerical MODE (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in MODE will be
            <Object defined dielectric>, and index will be defined.
        rename : String
            New name of the structure in Lumerical.
        '''
        lumerical_list = self.lumerical_list(tuple_list)
        self.mode.eval("addpoly;")
        self.mode.eval("set(\"vertices\"," + lumerical_list + ");")
        self.mode.eval("set(\"x\",0);")
        self.mode.eval("set(\"y\",0);")
        self.mode.eval("set(\"z min\"," + "%.6f"%(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + "%.6f"%(z_end) + "e-6);")
        if type(material) == str:
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.mode.eval("set(\"name\",\"" + rename + "\");")

    def put_round(self, center_point, inner_radius, outer_radius, start_radian, end_radian, z_start, z_end, material, rename):
        '''
        Draw a round on the varFDTD simulation CAD.

        Parameters
        ----------
        center_point : Point
            Points for the center of the round.
        inner_radius : float
            Inner radius of the round.
        outer_radius : float
            Outer radius of the round.
        start_radian : float
            The start radian of the round (unit: radian).
        end_radian : float
            The end radian of the round (unit: radian).
        z_start : Float
            The start point for the structure in z axis (unit: μm).
        z_end : Float
            The end point for the structure in z axis (unit: μm).
        material : str or float
            Material setting for the structure in Lumerical MODE (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in MODE will be
            <Object defined dielectric>, and index will be defined.
        rename : String
            New name of the structure in Lumerical.
        '''
        center_point = tuple_to_point(center_point)
        self.mode.eval("addring;")
        self.mode.eval("set(\"x\"," + "%.6f"%(center_point.x) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(center_point.y) + "e-6);")
        self.mode.eval("set(\"inner radius\"," + "%.6f"%(inner_radius) + "e-6);")
        self.mode.eval("set(\"outer radius\"," + "%.6f"%(outer_radius) + "e-6);")
        self.mode.eval("set(\"theta start\"," + "%.6f"%(180 * start_radian / math.pi) + ");")
        self.mode.eval("set(\"theta stop\"," + "%.6f"%(180 * end_radian / math.pi) + ");")
        self.mode.eval("set(\"z min\"," + "%.6f"%(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + "%.6f"%(z_end) + "e-6);")
        if  type(material) == str:
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.mode.eval("set(\"name\",\"" + rename + "\");")

    def eval(self, command):
        '''
        Execute the command on the MODE.

        Parameters
        ----------
        command : str
            Command that can be evaluated in MODE.
        '''
        self.mode.eval(command)

    def add_structure_circle(self, center_point, radius, material=SiO2, z_start = -0.11, z_end = 0.11,rename = "circle"):
        '''
        Draw the a circle on the simulation CAD.

        Parameters
        ----------
        center_point : Point
            Center point of the circle.
        radius : float
            Radius of the circle (unit: μm).
        material : str or float
            Material setting for the structure in Lumerical MODE (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in MODE will be
            <Object defined dielectric>, and index will be defined.
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical MODE (default: "circle").
        '''
        self.mode.eval("addcircle;")
        self.mode.eval("set(\"x\"," + "%.6f"%(center_point.x) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(center_point.y) + "e-6);")
        self.mode.eval("set(\"radius\"," + "%.6f"%(radius) + "e-6);")
        self.mode.eval("set(\"z min\"," + "%.6f"%(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + "%.6f"%(z_end) + "e-6);")
        self.mode.eval("set(\"name\",\"" + rename + "\");")
        if  type(material) == str:
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def add_structure_rectangle(self, center_point, x_length, y_length, material=SiO2, z_start=-0.11, z_end=0.11, rename="rect"):
        '''
        Draw the a rectangle on the simulation CAD.

        Parameters
        ----------
        center_point : Point
            Center point of the rectangle.
        x_length : float
            Length in the x axis (unit: μm).
        y_length : float
            Length in the y axis (unit: μm).
        material : str or float
            Material setting for the structure in Lumerical MODE (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in MODE will be
            <Object defined dielectric>, and index will be defined.
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical MODE (default: "rect").
        '''
        self.mode.eval("addrect;")
        self.mode.eval("set(\"x\"," + "%.6f"%(center_point.x) + "e-6);")
        self.mode.eval("set(\"x span\"," + "%.6f"%(x_length) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(center_point.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(y_length) + "e-6);")
        self.mode.eval("set(\"z min\"," + "%.6f"%(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + "%.6f"%(z_end) + "e-6);")
        self.mode.eval("set(\"name\",\"" + rename + "\");")
        if  type(material) == str:
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def add_mode_source(self, position, width=2, source_name="source", mode_number=1, wavelength_start=1.540, wavelength_end=1.570, direction = FORWARD):
        """
        Add eigen mode source in Lumerical MODE.

        Parameters
        ----------
        position : Point or tuple
            Center point of the source.
        width : Float
            Width of the source (in y axis, unit: μm, default: 2).
        height :  Float
            Height of the source (in z axis, unit: μm, default: 0.8).
        source_name : String
            Name of the source in Lumerical MODE (default: "source").
        mode_number : Int
            The selected mode index (start from 1).
        wavelength_start : Float
            The start wavelength of the source (unit: μm, default: 1.540).
        wavelength_end : Float
            The end wavelength of the source (unit: μm, default: 1.570).
        direction : Int
            The light propagation direction 1: the positive direction of x-axis, 0: the negative direction of x-axis(FORWARD:1, BACKWARD:0 , default: FORWARD).
        """
        position = tuple_to_point(position)
        self.mode.eval("addmodesource;")
        self.mode.eval("set(\"name\",\"" + source_name + "\");")
        self.mode.eval("set(\"injection axis\",\"x-axis\");")
        self.mode.eval("set(\"mode selection\",\"user select\");")
        self.mode.eval("set(\"selected mode number\"," + str(mode_number) + ");")
        if (direction == FORWARD):
            self.mode.eval("set(\"direction\",\"Forward\");")
        elif (direction == BACKWARD):
            self.mode.eval("set(\"direction\",\"Backward\");")
        else:
            raise Exception("Wrong source direction!")
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(width) + "e-6);")
        self.mode.eval("set(\"override global source settings\",0);")
        if not self.global_source_set_flag:
            self.mode.setglobalsource('set wavelength', True)
            self.mode.setglobalsource('wavelength start', wavelength_start*1e-6)
            self.mode.setglobalsource('wavelength stop', wavelength_end*1e-6)
            self.wavelength_start = wavelength_start*1e-6
            self.wavelength_end = wavelength_end*1e-6
            self.global_source_set_flag = 1

    def switch_to_layout(self):
        """
        Switch the Lumerical MODE simulation to "Layout" mode.
        """
        self.mode.eval("switchtolayout;")

    def add_mode_expansion(self,position, mode_list, width=2, height=0.8, expansion_name="expansion",points = 251):
        """
        Add mode expansion monitor in Lumerical MODE.

        Parameters
        ----------
        position : Point or tuple
            Center point of the monitor.
        mode_list : List
            List that contains the index of desired mode (start from 1).
        width : Float
            Width of the monitor (in y axis, unit: μm, default: 2).
        height :  Float
            Height of the monitor (in z axis, unit: μm, default: 0.8).
        expansion_name : String
            Name of the mode expansion monitor in Lumerical MODE (default: "expansion").
        points : Int
            The number of the frequency points that will be monitored (default: 251).

        Notes
        -----
        This function will automatically add a power monitor at the same position with same shape.
        """
        position = tuple_to_point(position)
        power_monitor_name = expansion_name + "_expansion"
        self.add_power_monitor(position,width = width,height=height,monitor_name=power_monitor_name ,points=points)
        self.mode.eval("addmodeexpansion;")
        self.mode.eval("set(\"name\",\"" + expansion_name + "\");")
        self.mode.eval("set(\"monitor type\",2);")
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(width) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        self.mode.eval("setexpansion(\"Output\",\""+power_monitor_name+"\");")
        self.mode.eval("set(\"mode selection\",\"user select\");")
        self.mode.eval("set(\"selected mode numbers\","+self.str_list(mode_list)+");")
        self.mode.eval("set(\"override global monitor settings\",0);")

    @staticmethod
    def str_list(list):
        """
        Convert a list to String expression.

        Parameters
        ----------
        list : List
            The List for conversion.

        Returns
        -------
        out : String
            The String expression of the input List.
        """
        if len(list) == 0:
            string = "[]"
        else:
            string = "["
            for item in list[:-1]:
                string += str(item) + ","
            string += str(list[-1]) + "]"
        return string

    def set_disable(self,item_name):
        """
        Set an item of the simulation to "disable" state.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical MODE simulaiton.
        """
        self.mode.eval("select(\""+item_name+"\");")
        self.mode.eval("set(\"enabled\",0);")

    def set_enable(self,item_name):
        """
        Set an item of the simulation to "enable" state.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical MODE simulaiton.
        """
        self.mode.eval("select(\"" + item_name + "\");")
        self.mode.eval("set(\"enabled\",1);")

    def remove(self, item_name):
        """
        Remove an item of the simulation.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical MODE simulaiton.
        """
        self.mode.eval("select(\"" + item_name + "\");")
        self.mode.eval("delete;")

    def get_transmission(self,monitor_name,datafile = None):
        """
        Get data from power monitor after running the simulation.

        Parameters
        ----------
        monitor_name : String
            Name of the power monitor.
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum [wavelength,transmission], size: (2,frequency points).
        """
        self.mode.eval("data = getresult(\"" + monitor_name + "\",\"T\");")
        data = self.lumapi.getVar(self.mode.handle, varname="data")
        wavelength = np.reshape(data["lambda"],(data["lambda"].shape[0]))
        transmission = data["T"]
        spectrum = np.zeros((2,data["T"].shape[0]))
        spectrum[0,:] = wavelength.flatten()
        spectrum[1,:] = transmission.flatten
        if (datafile != None):
            np.save(datafile,spectrum)
        return spectrum

    def get_mode_transmission(self, expansion_name, direction=FORWARD, datafile=None):
        """
        Get data from mode expansion monitor after running the simulation.

        Parameters
        ----------
        expansion_name : String
            Name of the mode expansion monitor.
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum [[wavelength,transmission],...], size: (number of modes,2,frequency points).
        """
        self.mode.eval("data = getresult(\"" + expansion_name + "\",\"expansion for Output\");")
        self.mode.eval("wavelength = data.lambda;")
        if (direction == FORWARD):
            self.mode.eval("mode_transmission = data.T_forward;")
        elif (direction == BACKWARD):
            self.mode.eval("mode_transmission = data.T_backward;")
        wavelength = self.lumapi.getVar(self.mode.handle, varname="wavelength")
        wavelength = np.reshape(wavelength, (wavelength.shape[0]))
        transmission = self.lumapi.getVar(self.mode.handle, varname="mode_transmission").T
        spectrum = np.zeros((transmission.shape[0], 2, transmission.shape[1]))
        for i in range(0, transmission.shape[0]):
            spectrum[i, 0, :] = wavelength
            spectrum[i, 1, :] = transmission[i, :]
        if (datafile != None):
            np.save(datafile, spectrum)
        return spectrum

    def get_mode_phase(self, expansion_name, direction = FORWARD, datafile = None):
        """
        Get data and calculate phase vs wavelength from mode expansion monitor after running the simulation.

        Parameters
        ----------
        expansion_name : String
            Name of the mode expansion monitor.
        direction : Int
            The light propagation direction 1: the positive direction of x-axis, 0: the negative direction of x-axis(FORWARD:1, BACKWARD:0 , default: FORWARD).
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Phase, size: (1,frequency points).
        """
        mode_exp_data_set = self.mode.getresult(expansion_name, 'expansion for Output')
        fwd_trans_coeff = mode_exp_data_set['a'] * np.sqrt(mode_exp_data_set['N'].real)
        back_trans_coeff = mode_exp_data_set['b'] * np.sqrt(mode_exp_data_set['N'].real)
        if direction == FORWARD:
            mode_phase = np.angle(fwd_trans_coeff)
        elif direction == BACKWARD:
            mode_phase = np.angle(back_trans_coeff)
        else:
            raise Exception("Wrong direction setting!")
        if (datafile != None):
            np.save(datafile, mode_phase.flatten())
        return mode_phase.flatten()

    def get_mode_coefficient(self, expansion_name , direction = FORWARD,  datafile = None):
        """
        Get data and calculate coefficient from mode expansion monitor after running the simulation.

        Parameters
        ----------
        expansion_name : String
            Name of the mode expansion monitor.
        direction : Int
            The light propagation direction 1: the positive direction of x-axis, 0: the negative direction of x-axis(FORWARD:1, BACKWARD:0 , default: FORWARD).
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum, size: (1,frequency points).
        """
        mode_exp_data_set = self.mode.getresult(expansion_name, 'expansion for Output')
        fwd_trans_coeff = mode_exp_data_set['a'] * np.sqrt(mode_exp_data_set['N'].real)
        back_trans_coeff = mode_exp_data_set['b'] * np.sqrt(mode_exp_data_set['N'].real)
        if direction == FORWARD:
            mode_coefficient = fwd_trans_coeff
        elif direction == BACKWARD:
            mode_coefficient = back_trans_coeff
        else:
            raise Exception("Wrong direction setting!")
        if (datafile != None):
            np.save(datafile, mode_coefficient.flatten())
        return mode_coefficient.flatten()

    def get_source_power(self, source_name="source", datafile = None):
        """
        Get source power spectrum from source.

        Parameters
        ----------
        source_name : String
            Name of the source.
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum, size: (1,frequency points).

        Notes
        -----
        This function should be called after setting the frequency points in any frequency domain monitor.
        """
        if self.global_source_set_flag  and self.global_monitor_set_flag:
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points,endpoint=True)
            frequency = scipy.constants.speed_of_light / wavelength
            self.lumapi.putMatrix(self.mode.handle, "frequency", frequency)
            self.mode.eval("data = sourcepower(frequency,2,\""+source_name+"\");")
            source_power = self.lumapi.getVar(self.mode.handle, varname="data")
        else:
            raise Exception("The source is not well defined!")
        if (datafile != None):
            np.save(datafile, source_power.flatten())
        return source_power.flatten()

    def get_wavelength(self):
        """
        Get wavelength points from Lumerical simulation.

        Returns
        -------
        out : Array
            Wavelength points, size: (1,frequency points).

        Notes
        -----
        This function should be called after setting the wavelength range in source and the frequency points in any frequency domain monitor.
        """
        if self.global_source_set_flag  and self.global_monitor_set_flag:
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points,endpoint=True)
        else:
            raise Exception("The source is not well defined!")
        return wavelength

    def get_frequency(self):
        """
        Get frequency points from Lumerical simulation.

        Returns
        -------
        out : Array
            Frequency points, size: (1,frequency points).

        Notes
        -----
        This function should be called after setting the wavelength range in source and the frequency points in any frequency domain monitor.
        """
        if self.global_source_set_flag  and self.global_monitor_set_flag:
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points,endpoint=True)
            frequency = scipy.constants.speed_of_light / wavelength
        else:
            raise Exception("The source is not well defined!")
        return frequency

    def get_omega(self):
        """
        Get omega points from Lumerical simulation (omega = 2*pi*frequency).

        Returns
        -------
        out : Array
            Omega points, size: (1,frequency points).

        Notes
        -----
        This function should be called after setting the wavelength range in source and the frequency points in any frequency domain monitor.
        """
        if self.global_source_set_flag  and self.global_monitor_set_flag:
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points,endpoint=True)
            omega = 2.0 * np.pi * scipy.constants.speed_of_light / wavelength
        else:
            raise Exception("The source is not well defined!")
        return omega


    def get_epsilon_distribution(self,index_monitor_name="index", data_name = "index_data",  datafile = None):
        """
        Get epsilon distribution from index monitor.

        Parameters
        ----------
        index_monitor_name : String
            Name of the index monitor (default: "index").
        data_name : String
            Name of the data in Lumeircal MODE (default: "index_data").
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum, size: (x mesh, y mesh, z mesh, 1).
        """
        self.mode.eval("{0} = getresult(\"".format(data_name) + index_monitor_name + "\",\"index\");")
        index = self.lumapi.getVar(self.mode.handle, "{0}".format(data_name))
        fields_eps = np.stack((np.power(index['index_x'], 2),
                               np.power(index['index_y'], 2),
                               np.power(index['index_z'], 2)),
                              axis=-1)
        fields_eps = np.squeeze(fields_eps,axis = -2)
        if (datafile != None):
            np.save(datafile, fields_eps)
        return fields_eps

    def get_E_distribution(self, field_monitor_name = "field", data_name = "field_data",datafile = None, if_get_spatial = 0):
        """
        Get electric field distribution from field monitor.

        Parameters
        ----------
        field_monitor_name : String
            Name of the field monitor (default: "field").
        data_name : String
            Name of the data in Lumeircal MODE (default: "field_data").
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).
        if_get_spatial : Bool
            Whether get spatial information as return (default: 0).

        Returns
        -------
        out : Array
            if if_get_spatial == 0: field
                size: (x mesh, y mesh, z mesh, frequency points, 3).
            if if_get_spatial == 1: field, x mesh, y mesh, z mesh
                size: (x mesh, y mesh, z mesh, frequency points, 3), (x mesh,), (y mesh,), (z mesh,)
        """
        self.mode.eval("{0} = getresult(\"".format(data_name) + field_monitor_name + "\",\"E\");")
        field = self.lumapi.getVar(self.mode.handle, "{0}".format(data_name))
        if (datafile != None):
            np.save(datafile, field['E'])
        if if_get_spatial:
            return field['E'],field['x'].flatten(),field['y'].flatten(),field['z'].flatten()
        else:
            return field['E']

    def add_index_region(self, bottom_left_corner_point, top_right_corner_point, height = 1, z_min = None, z_max = None, index_monitor_name="index",dimension = 2):
        """
        Add index monitor (x-y plane) in Lumerical MODE.

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        height : Float
            Height of the monitor (in z axis, unit: μm, default: 1).
        index_monitor_name : String
            Name of the monitor in Lumerical MODE (default: "index").
        dimension : Int
            Dimension of monitor (default: 2).
        """
        self.mode.eval("addindex;")
        self.mode.eval("set(\"name\",\"" + index_monitor_name + "\");")

        position = (bottom_left_corner_point + top_right_corner_point) / 2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"x span\"," + "%.6f"%(x_span) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(y_span) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        if (dimension == 2):
            self.mode.eval("set(\"monitor type\",3);")
        elif (dimension == 3):
            self.mode.eval("set(\"monitor type\",4);")
            if (type(z_min) != type(None) and type(z_max) != type(None)):
                self.mode.eval("set(\"z min\"," + "%.6f"%(z_min) + "e-6);")
                self.mode.eval("set(\"z max\"," + "%.6f"%(z_max) + "e-6);")
            else:
                self.mode.eval("set(\"z span\"," + "%.6f"%(height) + "e-6);")
        else:
            raise Exception("Wrong dimension for index region!")
        self.mode.eval("set(\"use wavelength spacing\",1);")
        self.mode.eval("set(\"override global monitor settings\",1);")
        self.mode.eval("set(\"frequency points\",1);")
        self.mode.eval("set(\"record conformal mesh when possible\",1);")
        self.mode.eval("set(\"spatial interpolation\",\"none\");")

    def add_field_region(self, bottom_left_corner_point, top_right_corner_point, height = 1, z_min = None, z_max = None, field_monitor_name="field",dimension = 2):
        """
        Add field monitor (x-y plane) in Lumerical MODE (DFT Frequency monitor).

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        height : Float
            Height of the monitor (in z axis, unit: μm, default: 1).
        field_monitor_name : String
            Name of the monitor in Lumerical MODE (default: "field").
        dimension : Int
            Dimension of monitor (default: 2).
        """
        self.mode.eval("addpower;")
        self.mode.eval("set(\"name\",\"" + field_monitor_name + "\");")

        position = (bottom_left_corner_point + top_right_corner_point) / 2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.mode.eval("set(\"x\"," + "%.6f"%(position.x) + "e-6);")
        self.mode.eval("set(\"x span\"," + "%.6f"%(x_span) + "e-6);")
        self.mode.eval("set(\"y\"," + "%.6f"%(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + "%.6f"%(y_span) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        if (dimension == 2):
            self.mode.eval("set(\"monitor type\",7);")
        elif (dimension == 3):
            self.mode.eval("set(\"monitor type\",8);")
            if (type(z_min) != type(None) and type(z_max) != type(None)):
                self.mode.eval("set(\"z min\"," + "%.6f"%(z_min) + "e-6);")
                self.mode.eval("set(\"z max\"," + "%.6f"%(z_max) + "e-6);")
            else:
                self.mode.eval("set(\"z span\"," + "%.6f"%(height) + "e-6);")
        else:
            raise Exception("Wrong dimension for index region!")
        self.mode.eval("set(\"override global monitor settings\",0);")
        self.mode.eval("set(\"spatial interpolation\",\"none\");")



