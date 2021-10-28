import sys, os
from splayout.utils import *

class MODESimulation:
    """
    MODE Simulation via Lumerical varFDTD API, especially for 2-Dimension structures.

    Parameters
    ----------
    hide : Bool
        Whether the Lumerical window is hidden (default is False).
    fdtd_path : String
        Path to the Lumerical Python API folder.

    """
    def __init__(self,hide=0,fdtd_path = "C:\\Program Files\\Lumerical\\v202\\api\\python\\"):
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
                "Lumerical FDTD is not installed in the default path, please specify the python api path with fdtd_path=***.")
        self.lumapi = lumapi
        self.mode = self.lumapi.MODE(hide=hide)
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


    def add_varfdtd_region(self,bottom_left_corner_point,top_right_corner_point, mode_position, simulation_time = 5000, test_points = None, background_index=1.444,mesh_order =2,height = 1,z_symmetric = 0):
        """
        Add simulation region in Lumerical FDTD.

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
            The level of the mesh grid in Lumerical FDTD (default: 2).
        height : Float
            Height of the simulation region (in z axis, unit: μm, default: 1).
        z_symmetric : Bool
            Whether set symmetric in z-axis (default: 0).
        """
        bottom_left_corner_point = tuple_to_point(bottom_left_corner_point)
        top_right_corner_point = tuple_to_point(top_right_corner_point)
        mode_position = tuple_to_point(mode_position)
        self.mode.eval("addvarfdtd;")
        position = (bottom_left_corner_point + top_right_corner_point)/2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.mode.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.mode.eval("set(\"x span\"," + str(x_span) + "e-6);")
        self.mode.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + str(y_span) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        self.mode.eval("set(\"z span\"," + str(height) + "e-6);")
        self.mode.eval("set(\"x0\"," + str(mode_position.x) + "e-6);")
        self.mode.eval("set(\"y0\"," + str(mode_position.y) + "e-6);")
        if (type(test_points) != type(None)):
            self.mode.eval("set(\"test points\"," + self.lumerical_list(test_points) + ");")
        self.mode.eval("set(\"index\"," + str(background_index) + ");")
        self.mode.eval("set(\"simulation time\"," + str(simulation_time) + "e-15);")
        self.mode.eval("set(\"mesh accuracy\"," + str(mesh_order) + ");")
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
            Name of the source in Lumerical FDTD (default: "source").
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
        self.mode.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.mode.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + str(width) + "e-6);")
        self.mode.eval("set(\"override global source settings\",0);")
        if not self.global_source_set_flag:
            self.mode.setglobalsource('set wavelength', True)
            self.mode.setglobalsource('wavelength start', wavelength_start*1e-6)
            self.mode.setglobalsource('wavelength stop', wavelength_end*1e-6)
            self.wavelength_start = wavelength_start*1e-6
            self.wavelength_end = wavelength_end*1e-6
            self.global_source_set_flag = 1
        self.mode.eval("set(\"amplitude\"," + str(amplitude) + ");")
        self.mode.eval("set(\"phase\"," + str(phase) + ");")
        self.mode.eval("set(\"waist radius w0\"," + str(waist_radius) + "e-6);")


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
            Name of the structure in Lumerical FDTD (default: "powermonitor").
        points : Int
            The number of the frequency points that will be monitored (default: 1001).
        """
        position = tuple_to_point(position)
        self.mode.eval("addpower;")
        self.mode.eval("set(\"name\",\"" + monitor_name+"\");")
        self.mode.eval("set(\"monitor type\",5);")
        self.mode.eval("set(\"x\","+ str(position.x) +"e-6);")
        self.mode.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.mode.eval("set(\"y span\"," + str(width) + "e-6);")
        self.mode.eval("set(\"z\",0);")
        self.mode.eval("set(\"z span\"," + str(height) + "e-6);")
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
            Material setting for the structure in Lumerical FDTD (Si = "Si (Silicon) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: Si).
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical FDTD.
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
                string += str(item[0]) + "e-6," + str(item[1]) + "e-6;"
            string += str(tuple_list[-1][0]) + "e-6," + str(tuple_list[-1][1]) + "e-6]"
        return string

    def put_rectangle(self, bottom_left_corner_point, top_right_corner_point, z_start, z_end, material):
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
            Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in FDTD will be
            <Object defined dielectric>, and index will be defined.
        '''
        bottom_left_corner_point = tuple_to_point(bottom_left_corner_point)
        top_right_corner_point = tuple_to_point(top_right_corner_point)
        self.mode.eval("addrect;")
        self.mode.eval("set(\"x min\"," + str(bottom_left_corner_point.x) + "e-6);")
        self.mode.eval("set(\"x max\"," + str(top_right_corner_point.x) + "e-6);")
        self.mode.eval("set(\"y min\"," + str(bottom_left_corner_point.y) + "e-6);")
        self.mode.eval("set(\"y max\"," + str(top_right_corner_point.y) + "e-6);")
        self.mode.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material == str):
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material == float):
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def put_polygon(self, tuple_list, z_start, z_end, material):
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
            Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in FDTD will be
            <Object defined dielectric>, and index will be defined.
        '''
        lumerical_list = self.lumerical_list(tuple_list)
        self.mode.eval("addpoly;")
        self.mode.eval("set(\"vertices\"," + lumerical_list + ");")
        self.mode.eval("set(\"x\",0);")
        self.mode.eval("set(\"y\",0);")
        self.mode.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material == str):
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material == float):
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def put_round(self, center_point, inner_radius, outer_radius, start_radian, end_radian, z_start, z_end, material):
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
            Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in FDTD will be
            <Object defined dielectric>, and index will be defined.
        '''
        center_point = tuple_to_point(center_point)
        self.mode.eval("addring;")
        self.mode.eval("\"x\"," + str(center_point.x) + "e-6);")
        self.mode.eval("\"y\"," + str(center_point.y) + "e-6);")
        self.mode.eval("\"inner radius\"," + str(inner_radius) + "e-6);")
        self.mode.eval("\"outer radius\"," + str(outer_radius) + "e-6);")
        self.mode.eval("\"theta start\"," + str(180 * start_radian / math.pi) + "e-6);")
        self.mode.eval("\"theta stop\"," + str(180 * end_radian / math.pi) + "e-6);")
        self.mode.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.mode.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material == str):
            self.mode.eval("set(\"material\",\"" + material + "\");")
        elif type(material == float):
            self.mode.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.mode.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def eval(self, command):
        '''
        Execute the command on the MODE.

        Parameters
        ----------
        command : str
            Command that can be evaluated in fdtd.
        '''
        self.mode.eval(command)