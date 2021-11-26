from splayout.utils import *
import sys, os
import numpy as np
import scipy.constants


class FDTDSimulation:
    """
    FDTD Simulation via Lumerical FDTD API, especially for 2-Dimension structures.

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
        self.fdtd = self.lumapi.FDTD(hide=hide)
        self.global_monitor_set_flag = 0
        self.global_source_set_flag = 0

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
        self.fdtd.redrawoff()
        self.fdtd.eval("n = gdsimport(\"" + filename + "\",\"" + cellname + "\",\"" +str(layer) +":"+ str(datatype) +"\",\"" + material +"\", "+str(z_start)+"e-6," +str(z_end)+"e-6);")
        self.fdtd.redrawon()
        if (rename != None):
            self.fdtd.eval("select(\"GDS_LAYER_" + str(layer) +":" + str(datatype) + "\");")
            self.fdtd.eval("set(\"name\",\"" + rename + "\");")

    def add_power_monitor(self,position,width=2,height=0.8,monitor_name="powermonitor",points=1001):
        """
        Add power monitor in Lumerical FDTD (DFT Frequency monitor).

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
        self.fdtd.eval("addpower;")
        self.fdtd.eval("set(\"name\",\"" + monitor_name+"\");")
        self.fdtd.eval("set(\"monitor type\",5);")
        self.fdtd.eval("set(\"x\","+ str(position.x) +"e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(width) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        self.fdtd.eval("set(\"override global monitor settings\",0);")
        if not self.global_monitor_set_flag:
            self.fdtd.setglobalmonitor('use source limits', True)
            self.fdtd.setglobalmonitor('use wavelength spacing', True)
            self.fdtd.setglobalmonitor('frequency points', points)
            self.frequency_points = points
            self.global_monitor_set_flag = 1

    def add_mode_expansion(self,position, mode_list, width=2, height=0.8, expansion_name="expansion", points = 251, update_mode = 0):
        """
        Add mode expansion monitor in Lumerical FDTD.
        Add mode expansion monitor in Lumerical FDTD.

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
            Name of the mode expansion monitor in Lumerical FDTD (default: "expansion").
        points : Int
            The number of the frequency points that will be monitored (default: 251).
        update_mode : Int or bool
            Whether update the mode after defining FDTD and mesh (default: 0).

        Notes
        -----
        This function will automatically add a power monitor at the same position with same shape.
        If use update_mode the monitor should be put after adding fdtd region and mesh region.
        """
        position = tuple_to_point(position)
        power_monitor_name = expansion_name + "_expansion"
        self.add_power_monitor(position,width = width,height=height,monitor_name=power_monitor_name ,points=points)
        self.fdtd.eval("addmodeexpansion;")
        self.fdtd.eval("set(\"name\",\"" + expansion_name + "\");")
        self.fdtd.eval("set(\"monitor type\",1);")
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(width) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        self.fdtd.eval("setexpansion(\"Output\",\""+power_monitor_name+"\");")
        if (type(mode_list) == str):
            self.fdtd.eval("set(\"mode selection\",\""+mode_list+"\");")
        else:
            self.fdtd.eval("set(\"mode selection\",\"user select\");")
            self.fdtd.eval("set(\"selected mode numbers\"," + self.str_list(mode_list) + ");")

        if (update_mode):
            self.fdtd.updatemodes()
        self.fdtd.eval("set(\"override global monitor settings\",0);")
        self.fdtd.eval("set(\"auto update\",1);")

    def reset_mode_expansion_modes(self, expansion_name, mode_list):
        """
        Reset mode list for mode expansion monitor.

        Parameters
        ----------
        expansion_name : String
            Name of the mode expansion monitor in Lumerical FDTD.
        mode_list : List
            List that contains the index of desired mode (start from 1).

        Notes
        -----
        This function should be called after setting a mode expansion.
        """
        self.fdtd.eval("select(\"" + expansion_name + "\");")
        self.fdtd.eval("set(\"selected mode numbers\","+self.str_list(mode_list)+");")



    def add_mode_source(self,position, width=2,height=0.8,source_name="source",mode_number=1,wavelength_start=1.540,wavelength_end=1.570,direction = FORWARD, update_mode = 0):
        """
        Add source in Lumerical FDTD.

        Parameters
        ----------
        position : Point or tuple
            Center point of the source.
        width : Float
            Width of the source (in y axis, unit: μm, default: 2).
        height :  Float
            Height of the source (in z axis, unit: μm, default: 0.8).
        source_name : String
            Name of the source in Lumerical FDTD (default: "source").
        mode_number : Int
            The selected mode index (start from 1).
        wavelength_start : Float
            The start wavelength of the source (unit: μm, default: 1.540).
        wavelength_end : Float
            The end wavelength of the source (unit: μm, default: 1.570).
        direction : Int
            The light propagation direction 1: the positive direction of x-axis, 0: the negative direction of x-axis(FORWARD:1, BACKWARD:0 , default: FORWARD).
        update_mode : Int or bool
            Whether update the mode after defining FDTD and mesh (default: 0).

        Notes
        -----
        If use update_mode the monitor should be put after adding fdtd region and mesh region.

        """
        position = tuple_to_point(position)
        self.fdtd.eval("addmode;")
        self.fdtd.eval("set(\"name\",\"" + source_name + "\");")
        self.fdtd.eval("set(\"injection axis\",\"x-axis\");")
        if (type(mode_number) == str):
            self.fdtd.eval("set(\"mode selection\",\""+mode_number+"\");")
        else:
            self.fdtd.eval("set(\"mode selection\",\"user select\");")
            self.fdtd.eval("set(\"selected mode number\"," + str(mode_number) + ");")
        if (direction == FORWARD):
            self.fdtd.eval("set(\"direction\",\"Forward\");")
        elif (direction == BACKWARD):
            self.fdtd.eval("set(\"direction\",\"Backward\");")
        else:
            raise Exception("Wrong source direction!")
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(width) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        self.fdtd.eval("set(\"override global source settings\",0);")
        if (update_mode and (type(mode_number) != str)):
            self.fdtd.updatesourcemode(int(mode_number))
        if not self.global_source_set_flag:
            self.fdtd.setglobalsource('set wavelength', True)
            self.fdtd.setglobalsource('wavelength start', wavelength_start*1e-6)
            self.fdtd.setglobalsource('wavelength stop', wavelength_end*1e-6)
            self.wavelength_start = wavelength_start*1e-6
            self.wavelength_end = wavelength_end*1e-6
            self.global_source_set_flag = 1

    def reset_source_mode(self, source_name,mode_number):
        """
        Reset mode for source.

        Parameters
        ----------
        source_name : String
            Name of the source in Lumerical FDTD.
        mode_number : Int
            The selected mode index (start from 1).

        Notes
        -----
        This function should be called after setting a source.
        """
        self.fdtd.eval("select(\"" + source_name + "\");")
        self.fdtd.eval("set(\"selected mode number\","+str(mode_number)+");")



    def add_fdtd_region(self,bottom_left_corner_point,top_right_corner_point,simulation_time=5000,background_index=1.444,mesh_order =2,dimension=3,height = 1, z_symmetric = 0, y_antisymmetric = 0, pml_layers = 8):
        """
        Add simulation region in Lumerical FDTD.

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        simulation_time : int
            Total simulation time (unit: fs, default: 5000).
        background_index : float
            Background refractive index in the simualtion region  (default: 1.444).
        mesh_order :  int
            The level of the mesh grid in Lumerical FDTD (default: 2).
        dimension : Int
            Dimension of FDTD simulation (default: 3).
        height : Float
            Height of the simulation region (in z axis, unit: μm, default: 1).
        z_symmetric : Bool
            Whether set symmetric in z-axis (default: 0).
        """
        self.fdtd.eval("addfdtd;")
        self.fdtd.eval("set(\"dimension\"," + str(dimension-1) + ");")
        position = (bottom_left_corner_point + top_right_corner_point)/2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"x span\"," + str(x_span) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(y_span) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        self.fdtd.eval("set(\"simulation time\"," + str(simulation_time) + "e-15);")
        self.fdtd.eval("set(\"index\"," + str(background_index) + ");")
        self.fdtd.eval("set(\"mesh accuracy\"," + str(mesh_order) + ");")
        self.fdtd.eval("set(\"pml layers\"," +str(pml_layers) +");")

        if (dimension == 3 and z_symmetric == 1):
            self.fdtd.eval("set(\"z min bc\", \"Symmetric\");")

        if (y_antisymmetric == 1):
            self.fdtd.eval("set(\"y min bc\", \"Anti-Symmetric\");")
            self.fdtd.eval("set(\"force symmetric y mesh\", 1);")

    def add_index_region(self, bottom_left_corner_point, top_right_corner_point, height = 1, z_min = None, z_max = None, index_monitor_name="index",dimension = 2):
        """
        Add index monitor (x-y plane) in Lumerical FDTD.

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        height : Float
            Height of the monitor (in z axis, unit: μm, default: 1).
        index_monitor_name : String
            Name of the monitor in Lumerical FDTD (default: "index").
        dimension : Int
            Dimension of monitor (default: 2).
        """
        self.fdtd.eval("addindex;")
        self.fdtd.eval("set(\"name\",\"" + index_monitor_name + "\");")

        position = (bottom_left_corner_point + top_right_corner_point) / 2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"x span\"," + str(x_span) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(y_span) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        if (dimension == 2):
            self.fdtd.eval("set(\"monitor type\",3);")
        elif (dimension == 3):
            self.fdtd.eval("set(\"monitor type\",4);")
            if (type(z_min) != type(None) and type(z_max) != type(None)):
                self.fdtd.eval("set(\"z min\"," + str(z_min) + "e-6);")
                self.fdtd.eval("set(\"z max\"," + str(z_max) + "e-6);")
            else:
                self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        else:
            raise Exception("Wrong dimension for index region!")
        self.fdtd.eval("set(\"override global monitor settings\",1);")
        self.fdtd.eval("set(\"frequency points\",1);")
        self.fdtd.eval("set(\"record conformal mesh when possible\",1);")
        self.fdtd.eval("set(\"spatial interpolation\",\"none\");")


    def add_field_region(self, bottom_left_corner_point, top_right_corner_point, height = 1, z_min = None, z_max = None, field_monitor_name="field",dimension = 2):
        """
        Add field monitor (x-y plane) in Lumerical FDTD (DFT Frequency monitor).

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        height : Float
            Height of the monitor (in z axis, unit: μm, default: 1).
        field_monitor_name : String
            Name of the monitor in Lumerical FDTD (default: "field").
        dimension : Int
            Dimension of monitor (default: 2).
        """
        self.fdtd.eval("addpower;")
        self.fdtd.eval("set(\"name\",\"" + field_monitor_name + "\");")

        position = (bottom_left_corner_point + top_right_corner_point) / 2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        if (dimension == 2):
            self.fdtd.eval("set(\"monitor type\",7);")
        elif (dimension == 3):
            self.fdtd.eval("set(\"monitor type\",8);")
            if (type(z_min) != type(None) and type(z_max) != type(None)):
                self.fdtd.eval("set(\"z min\"," + str(z_min) + "e-6);")
                self.fdtd.eval("set(\"z max\"," + str(z_max) + "e-6);")
            else:
                self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        else:
            raise Exception("Wrong dimension for index region!")
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"x span\"," + str(x_span) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(y_span) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        self.fdtd.eval("set(\"override global monitor settings\",0);")
        self.fdtd.eval("set(\"spatial interpolation\",\"none\");")

    def add_mesh_region(self,bottom_left_corner_point,top_right_corner_point,x_mesh,y_mesh,z_mesh = 0.0025,height = 1, z_min = None, z_max = None):
        """
        Reset the mesh grid in Lumerical FDTD.

        Parameters
        ----------
        bottom_left_corner_point : Point
            Lower left corner of the region.
        top_right_corner_point : Point
            Upper right corner of the region.
        x_mesh : Float
            The grid unit in x-axis (unit: μm).
        y_mesh : Float
            The grid unit in y-axis (unit: μm).
        z_mesh : Float
            The grid unit in z-axis (unit: μm, default: 0.0025).
        height : Float
            Height of the region (in z axis, unit: μm, default: 1).
        """
        self.fdtd.eval("addmesh;")
        position = (bottom_left_corner_point + top_right_corner_point) / 2
        x_span = abs(bottom_left_corner_point.x - top_right_corner_point.x)
        y_span = abs(bottom_left_corner_point.y - top_right_corner_point.y)
        self.fdtd.eval("set(\"x\"," + str(position.x) + "e-6);")
        self.fdtd.eval("set(\"x span\"," + str(x_span) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(position.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(y_span) + "e-6);")
        self.fdtd.eval("set(\"z\",0);")
        if (type(z_min) != type(None) and type(z_max) != type(None)):
            self.fdtd.eval("set(\"z min\"," + str(z_min) + "e-6);")
            self.fdtd.eval("set(\"z max\"," + str(z_max) + "e-6);")
        else:
            self.fdtd.eval("set(\"z span\"," + str(height) + "e-6);")
        self.fdtd.eval("set(\"dx\"," + str(x_mesh) + "e-6);")
        self.fdtd.eval("set(\"dy\"," + str(y_mesh) + "e-6);")
        self.fdtd.eval("set(\"dz\"," + str(z_mesh) + "e-6);")


    def save(self,filename="temp"):
        """
        Save the simulation as a ".fsp" file.

        Parameters
        ----------
        filename : String
            File name or File path (default: "temp").
        """
        self.fdtd.save(filename)

    def run(self,filename="temp"):
        """
        Save the simulation as a ".fsp" file and run.

        Parameters
        ----------
        filename : String
            File name or File path (default: "temp").
        """
        self.save(filename)
        self.fdtd.eval("switchtolayout;")
        self.fdtd.eval("run;")

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
        self.fdtd.eval("data = getresult(\"" + monitor_name + "\",\"T\");")
        data = self.lumapi.getVar(self.fdtd.handle, varname="data")
        wavelength = np.reshape(data["lambda"],(data["lambda"].shape[0]))
        transmission = data["T"]
        spectrum = np.zeros((2,data["T"].shape[0]))
        spectrum[0,:] = wavelength.flatten()
        spectrum[1,:] = transmission.flatten()
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
        self.fdtd.eval("data = getresult(\"" + expansion_name + "\",\"expansion for Output\");")
        self.fdtd.eval("wavelength = data.lambda;")
        if (direction == FORWARD):
            self.fdtd.eval("mode_transmission = data.T_forward;")
        elif (direction == BACKWARD):
            self.fdtd.eval("mode_transmission = data.T_backward;")
        wavelength = self.lumapi.getVar(self.fdtd.handle, varname="wavelength")
        wavelength = np.reshape(wavelength, (wavelength.shape[0]))
        transmission = self.lumapi.getVar(self.fdtd.handle, varname="mode_transmission").T
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
        mode_exp_data_set = self.fdtd.getresult(expansion_name, 'expansion for Output')
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
        mode_exp_data_set = self.fdtd.getresult(expansion_name, 'expansion for Output')
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

    def get_source_power(self, source_name=None, datafile = None):
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
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points)
            frequency = scipy.constants.speed_of_light / wavelength
            if (type(source_name) == type(None)):
                source_power = self.fdtd.sourcepower(frequency)
            else:
                self.lumapi.putMatrix(self.fdtd.handle, "frequency", frequency)
                self.fdtd.eval("data = sourcepower(frequency,2,\""+source_name+"\");")
                source_power = self.lumapi.getVar(self.fdtd.handle, varname="data")
        else:
            raise Exception("The source is not well defined!")
        if (datafile != None):
            np.save(datafile, source_power.flatten())
        return np.asarray(source_power).flatten()

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
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points)
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
            wavelength = np.linspace(self.wavelength_start, self.wavelength_end, self.frequency_points)
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
            Name of the data in Lumeircal FDTD (default: "index_data").
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).

        Returns
        -------
        out : Array
            Spectrum, size: (x mesh, y mesh, z mesh, 1).
        """
        self.fdtd.eval("{0} = getresult(\"".format(data_name) + index_monitor_name + "\",\"index\");")
        index = self.lumapi.getVar(self.fdtd.handle, "{0}".format(data_name))
        fields_eps = np.stack((np.power(index['index_x'], 2),
                               np.power(index['index_y'], 2),
                               np.power(index['index_z'], 2)),
                              axis=-1)
        fields_eps = np.squeeze(fields_eps,axis = -2)
        if (datafile != None):
            np.save(datafile, fields_eps)
        return fields_eps

    def get_epsilon_distribution_in_CAD(self,index_monitor_name="index", data_name = "index_data"):
        """
        Get epsilon distribution from index monitor and save the data in CAD.
        (From: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        index_monitor_name : String
            Name of the index monitor (default: "index").
        data_name : String
            Name of the data in Lumeircal FDTD (default: "index_data").

        Returns
        -------
        data_name : String
            The name of the data in Lumerical.
        """
        self.fdtd.eval("{0}_data_set = getresult('{0}','index');".format(index_monitor_name) +
                  "{0} = matrix(length({1}_data_set.x), length({1}_data_set.y), length({1}_data_set.z), length({1}_data_set.f), 3);".format(
                      data_name, index_monitor_name) +
                  "{0}(:, :, :, :, 1) = {1}_data_set.index_x^2;".format(data_name, index_monitor_name) +
                  "{0}(:, :, :, :, 2) = {1}_data_set.index_y^2;".format(data_name, index_monitor_name) +
                  "{0}(:, :, :, :, 3) = {1}_data_set.index_z^2;".format(data_name, index_monitor_name) +
                  "clear({0}_data_set);".format(index_monitor_name))
        return data_name

    def get_E_distribution(self, field_monitor_name = "field", data_name = "field_data",datafile = None, if_get_spatial = 0):
        """
        Get electric field distribution from field monitor.

        Parameters
        ----------
        field_monitor_name : String
            Name of the field monitor (default: "field").
        data_name : String
            Name of the data in Lumeircal FDTD (default: "field_data").
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
        self.fdtd.eval("{0} = getresult(\"".format(data_name) + field_monitor_name + "\",\"E\");")
        field = self.lumapi.getVar(self.fdtd.handle, "{0}".format(data_name))
        if (datafile != None):
            np.save(datafile, field['E'])
        if if_get_spatial:
            return field['E'],field['x'].flatten(),field['y'].flatten(),field['z'].flatten()
        else:
            return field['E']

    def get_E_distribution_in_CAD(self, field_monitor_name = "field", data_name = "field_data"):
        """
        Get electric field distribution from field monitor and save the data in CAD.

        Parameters
        ----------
        field_monitor_name : String
            Name of the field monitor (default: "field").
        data_name : String
            Name of the data in Lumeircal FDTD (default: "field_data").

        Returns
        -------
        data_name : String
            The name of the data in Lumerical.

        """
        self.fdtd.eval("options=struct; options.unfold=true;"+
            "{0} = getresult(\"".format(data_name) + field_monitor_name + "\",\"E\",options);")

        return data_name

    def clear_data_in_CAD(self):
        """
        Clear the pre-saved data in CAD.
        """
        self.fdtd.eval("clear;")



    def switch_to_layout(self):
        """
        Switch the Lumerical FDTD simulation to "Layout" mode.
        """
        self.fdtd.eval("switchtolayout;")

    def set_disable(self,item_name):
        """
        Set an item of the simulation to "disable" state.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical FDTD simulaiton.
        """
        self.fdtd.eval("select(\""+item_name+"\");")
        self.fdtd.eval("set(\"enabled\",0);")

    def set_enable(self,item_name):
        """
        Set an item of the simulation to "enable" state.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical FDTD simulaiton.
        """
        self.fdtd.eval("select(\"" + item_name + "\");")
        self.fdtd.eval("set(\"enabled\",1);")

    def remove(self, item_name):
        """
        Remove an item of the simulation.

        Parameters
        ----------
        item_name : String
            Name of the item.

        Notes
        -----
        This function should be called in "Layout" mode for the Lumerical FDTD simulaiton.
        """
        self.fdtd.eval("select(\"" + item_name + "\");")
        self.fdtd.eval("delete;")

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
                string += str(item[0])+"e-6,"+ str(item[1])+ "e-6;"
            string += str(tuple_list[-1][0])+"e-6,"+ str(tuple_list[-1][1]) + "e-6]"
        return string

    def put_rectangle(self, bottom_left_corner_point, top_right_corner_point, z_start, z_end, material, rename):
        '''
        Draw a rectangle on the fdtd simulation CAD.

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
        rename : String
            New name of the structure in Lumerical.
        '''
        bottom_left_corner_point = tuple_to_point(bottom_left_corner_point)
        top_right_corner_point = tuple_to_point(top_right_corner_point)
        self.fdtd.eval("addrect;")
        self.fdtd.eval("set(\"x min\"," + str(bottom_left_corner_point.x) + "e-6);")
        self.fdtd.eval("set(\"x max\"," + str(top_right_corner_point.x) + "e-6);")
        self.fdtd.eval("set(\"y min\"," + str(bottom_left_corner_point.y) + "e-6);")
        self.fdtd.eval("set(\"y max\"," + str(top_right_corner_point.y) + "e-6);")
        self.fdtd.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.fdtd.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material) == str:
            self.fdtd.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.fdtd.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.fdtd.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.fdtd.eval("set(\"name\",\"" + rename + "\");")

    def put_polygon(self, tuple_list, z_start, z_end, material, rename):
        '''
        Draw a polygon on the fdtd simulation CAD.

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
        rename : String
            New name of the structure in Lumerical.
        '''
        lumerical_list = self.lumerical_list(tuple_list)
        self.fdtd.eval("addpoly;")
        self.fdtd.eval("set(\"vertices\","+lumerical_list+");")
        self.fdtd.eval("set(\"x\",0);")
        self.fdtd.eval("set(\"y\",0);")
        self.fdtd.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.fdtd.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material) == str:
            self.fdtd.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.fdtd.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.fdtd.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.fdtd.eval("set(\"name\",\"" + rename + "\");")

    def update_polygon(self, polygon_name, point_list):
        '''
        Update a polygon on the fdtd simulation CAD.

        Parameters
        ----------
        polygon_name : str
            Name of the polygon.
        point_list : List of Point
            Points for the polygon.

        '''
        tuple_list = []
        if (type(point_list) == np.ndarray):
            point_list = point_list.tolist()
        for item in point_list:
            if type(item) == Point:
                tuple_list.append(item.to_tuple())
            elif type(item) == tuple:
                tuple_list.append(item)
            elif type(item) == list:
                tuple_list.append(tuple(item))
            elif type(item) == np.ndarray:
                tuple_list.append(tuple(item))
            else:
                raise Exception("Polygon Wrong Type Input!")
        self.fdtd.eval("select(\"{0}\");".format(polygon_name))
        lumerical_list = self.lumerical_list(tuple_list)
        self.fdtd.eval("set(\"vertices\"," + lumerical_list + ");")


    def put_round(self, center_point, inner_radius, outer_radius, start_radian, end_radian, z_start, z_end, material, rename):
        '''
        Draw a round on the fdtd simulation CAD.

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
        rename : String
            New name of the structure in Lumerical.
        '''
        center_point = tuple_to_point(center_point)
        self.fdtd.eval("addring;")
        self.fdtd.eval("set(\"x\","+str(center_point.x)+"e-6);")
        self.fdtd.eval("set(\"y\"," + str(center_point.y) + "e-6);")
        self.fdtd.eval("set(\"inner radius\"," + str(inner_radius) + "e-6);")
        self.fdtd.eval("set(\"outer radius\"," + str(outer_radius) + "e-6);")
        self.fdtd.eval("set(\"theta start\"," + str(180 * start_radian / math.pi) + ");")
        self.fdtd.eval("set(\"theta stop\"," + str(180 * end_radian / math.pi) + ");")
        self.fdtd.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.fdtd.eval("set(\"z max\"," + str(z_end) + "e-6);")
        if type(material) == str:
            self.fdtd.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.fdtd.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.fdtd.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")
        if (type(rename) == str):
            self.fdtd.eval("set(\"name\",\"" + rename + "\");")


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
            Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in FDTD will be
            <Object defined dielectric>, and index will be defined.
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical FDTD (default: "circle").
        '''
        self.fdtd.eval("addcircle;")
        self.fdtd.eval("set(\"x\"," + str(center_point.x) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(center_point.y) + "e-6);")
        self.fdtd.eval("set(\"radius\"," + str(radius) + "e-6);")
        self.fdtd.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.fdtd.eval("set(\"z max\"," + str(z_end) + "e-6);")
        self.fdtd.eval("set(\"name\",\"" + rename + "\");")
        if type(material) == str:
            self.fdtd.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.fdtd.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.fdtd.eval("set(\"index\"," + str(material) + ");")
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
            Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2). When it is a float, the material in FDTD will be
            <Object defined dielectric>, and index will be defined.
        z_start : Float
            The start point for the structure in z axis (unit: μm, default: -0.11).
        z_end : Float
            The end point for the structure in z axis (unit: μm, default: 0.11).
        rename : String
            New name of the structure in Lumerical FDTD (default: "rect").
        '''
        self.fdtd.eval("addrect;")
        self.fdtd.eval("set(\"x\"," + str(center_point.x) + "e-6);")
        self.fdtd.eval("set(\"x span\"," + str(x_length) + "e-6);")
        self.fdtd.eval("set(\"y\"," + str(center_point.y) + "e-6);")
        self.fdtd.eval("set(\"y span\"," + str(y_length) + "e-6);")
        self.fdtd.eval("set(\"z min\"," + str(z_start) + "e-6);")
        self.fdtd.eval("set(\"z max\"," + str(z_end) + "e-6);")
        self.fdtd.eval("set(\"name\",\"" + rename + "\");")
        if type(material) == str:
            self.fdtd.eval("set(\"material\",\"" + material + "\");")
        elif type(material) == float:
            self.fdtd.eval("set(\"material\",\"" + "<Object defined dielectric>" + "\");")
            self.fdtd.eval("set(\"index\"," + str(material) + ");")
        else:
            raise Exception("Wrong material specification!")

    def eval(self, command):
        '''
        Execute the command on the fdtd.

        Parameters
        ----------
        command : str
            Command that can be evaluated in fdtd.
        '''
        self.fdtd.eval(command)






