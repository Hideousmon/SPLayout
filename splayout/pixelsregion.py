from splayout.utils import *
import numpy as np

class RectanglePixelsRegion:
    """
    Rectangle pixels region for FDTD simulation. It will create a region with etched blocks that can be updated by a two-dimensional matrix.

    Parameters
    ----------
    bottom_left_corner_point : Point
        Lower left corner of the region.
    top_right_corner_point : Point
        Upper right corner of the region.
    pixel_x_length : float
        Length of the pixel(etched block) in axis-x.
    pixel_y_length : float
        Length of the pixel(etched block) in axis-y.
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    material : String
        Material setting for the pixels in Lumerical FDTD (Si = "Si (Silicon) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: -0.11).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: 0.11).
    unique_name : String
        Unique name of the pixels for distinguishing different pixel region.
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_x_length, pixel_y_length, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11, unique_name = "p"):
        self.left_down_point = bottom_left_corner_point
        self.right_up_point = top_right_corner_point
        self.pixel_x_length = pixel_x_length
        self.pixel_y_length = pixel_y_length
        self.__last_array = None
        self.__lastest_array = None
        self.fdtd_engine = fdtd_engine
        self.material = material
        self.z_start = z_start
        self.z_end = z_end
        self.unique_name = unique_name

    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[1]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[0]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2
        for row in range(0, self.__lastest_array.shape[0]):
            for col in range(0, self.__lastest_array.shape[1]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                self.fdtd_engine.add_structure_rectangle(center_point,self.pixel_x_length,self.pixel_y_length,material=self.material, z_start = self.z_start, z_end = self.z_end ,rename =self.unique_name +  str(row)+"_"+str(col))
        disable_positions = np.where(self.__lastest_array == 0)
        for position in np.transpose(disable_positions):
            self.fdtd_engine.set_disable(self.unique_name + str(position[0]) + "_" + str(position[1]))

    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            A two-dimensional binary array that represent the pixels in the region.
        '''
        self.fdtd_engine.switch_to_layout()
        if (len(matrix.shape) != 2):
            raise Exception("The input matrix should be two-dimensional!")
        if (type(self.__lastest_array) == type(None)):
            self.__lastest_array = np.array(matrix,dtype=np.int32)
            self.__last_array = np.array(matrix,dtype=np.int32)
            self.__initialize()
        else:
            self.__lastest_array = np.array(matrix,dtype=np.int32)
            self.__diff = self.__lastest_array - self.__last_array
            self.__last_array = np.array(matrix,dtype=np.int32)
            enable_positions = np.where(self.__diff == 1)
            disable_positions = np.where(self.__diff == -1)
            for position in np.transpose(enable_positions):
                self.fdtd_engine.set_enable(self.unique_name + str(position[0])+"_"+str(position[1]))
            for position in np.transpose(disable_positions):
                self.fdtd_engine.set_disable(self.unique_name + str(position[0])+"_"+str(position[1]))

class CirclePixelsRegion:
    """
    Rectangle pixels region for FDTD simulation. It will create a region with etched blocks that can be updated by a two-dimensional matrix.

    Parameters
    ----------
    bottom_left_corner_point : Point
        Lower left corner of the region.
    top_right_corner_point : Point
        Upper right corner of the region.
    pixel_radius : float
        Radius of the pixel(etched block).
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    material : String
        Material setting for the pixels in Lumerical FDTD (Si = "Si (Silicon) - Palik", SiO2 = "SiO2 (Glass) - Palik", default: SiO2).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: -0.11).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: 0.11).
    unique_name : String
        Unique name of the pixels for distinguishing different pixel region.
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_radius, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11, unique_name = "p"):
        self.left_down_point = bottom_left_corner_point
        self.right_up_point = top_right_corner_point
        self.pixel_radius = pixel_radius
        self.__last_array = None
        self.__lastest_array = None
        self.fdtd_engine = fdtd_engine
        self.material = material
        self.z_start = z_start
        self.z_end = z_end
        self.unique_name = unique_name

    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[1]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[0]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2
        for row in range(0, self.__lastest_array.shape[0]):
            for col in range(0, self.__lastest_array.shape[1]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                self.fdtd_engine.add_structure_circle(center_point,self.pixel_radius,material=self.material, z_start = self.z_start, z_end = self.z_end ,rename = self.unique_name + str(row)+"_"+str(col))
        disable_positions = np.where(self.__lastest_array == 0)
        for position in np.transpose(disable_positions):
            self.fdtd_engine.set_disable(self.unique_name + str(position[0]) + "_" + str(position[1]))

    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            A two-dimensional binary array that represent the pixels in the region.
        '''
        self.fdtd_engine.switch_to_layout()
        if (len(matrix.shape) != 2):
            raise Exception("The input matrix should be two-dimensional!")
        if (type(self.__lastest_array) == type(None)):
            self.__lastest_array = np.array(matrix,dtype=np.int32)
            self.__last_array = np.array(matrix,dtype=np.int32)
            self.__initialize()
        else:
            self.__lastest_array = np.array(matrix,dtype=np.int32)
            self.__diff = self.__lastest_array - self.__last_array
            self.__last_array = np.array(matrix,dtype=np.int32)
            enable_positions = np.where(self.__diff == 1)
            disable_positions = np.where(self.__diff == -1)
            for position in np.transpose(enable_positions):
                self.fdtd_engine.set_enable(self.unique_name + str(position[0])+"_"+str(position[1]))
            for position in np.transpose(disable_positions):
                self.fdtd_engine.set_disable(self.unique_name + str(position[0])+"_"+str(position[1]))