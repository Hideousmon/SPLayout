from splayout.utils import *
import numpy as np

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
    group_name : String
        Unique name of the pixels for distinguishing different pixel region(default: "pixels").
    pixel_radius_th : float
        Lower boundary for the radius (default: 0).
    matrix_mask : Array
        Mask array for the matrix in update function (default: None).
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_radius, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11 , group_name = "pixels",  pixel_radius_th = 0, matrix_mask = None):
        self.left_down_point = tuple_to_point(bottom_left_corner_point)
        self.right_up_point = tuple_to_point(top_right_corner_point)
        self.pixel_radius = pixel_radius
        self.__last_array = None
        self.__lastest_array = None
        self.fdtd_engine = fdtd_engine
        self.material = material
        self.z_start = z_start
        self.z_end = z_end
        self.group_name = group_name
        self.pixel_radius_th = pixel_radius_th
        if (type(matrix_mask) != type(None)):
            self.matrix_mask = np.array(matrix_mask, dtype=np.int32)
        else:
            self.matrix_mask = matrix_mask


    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[0]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[1]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2
        for row in range(0, self.__lastest_array.shape[1]):
            for col in range(0, self.__lastest_array.shape[0]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                radius = self.pixel_radius * self.__lastest_array[col,row]
                if (np.isclose(radius, self.pixel_radius_th) or radius < self.pixel_radius_th):
                    radius = 0
                if (np.isclose(radius, self.pixel_radius) or radius > self.pixel_radius):
                    radius = self.pixel_radius
                self.fdtd_engine.add_structure_circle(center_point,radius,material=self.material, z_start = self.z_start, z_end = self.z_end ,rename = self.group_name + str(col)+"_"+str(row))


    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            A two-dimensional binary array that represent the pixels in the region.
        '''
        if (type(self.matrix_mask) != type(None)):
            enable_positions = np.where(np.transpose(self.matrix_mask) == 1)
            if (len(np.transpose(enable_positions)) != len(matrix)):
                raise Exception("The input matrix can not match the matrix_mask!")
            masked_matrix = self.matrix_mask.copy().astype(np.double)
            for i,position in enumerate(np.transpose(enable_positions)):
                masked_matrix[position[1], position[0]] = matrix[i]
        elif (len(matrix.shape) != 2):
            raise Exception("The input matrix should be two-dimensional when matrix_mask not specified!")
        else:
            masked_matrix = matrix

        self.fdtd_engine.switch_to_layout()
        if (type(self.__lastest_array) == type(None)):
            self.__lastest_array = np.array(masked_matrix,dtype=np.double)
            self.__last_array = np.array(masked_matrix,dtype=np.double)
            self.__initialize()
        else:
            self.__lastest_array = np.array(masked_matrix,dtype=np.double)
            self.__diff = self.__lastest_array - self.__last_array
            self.__last_array = np.array(masked_matrix,dtype=np.double)
            reconfig_positions = np.where(~np.isclose(np.abs(self.__diff), 0))
            for position in np.transpose(reconfig_positions):
                radius = self.pixel_radius * self.__lastest_array[position[0], position[1]]
                if (np.isclose(radius, self.pixel_radius_th) or (radius < self.pixel_radius_th)):
                    radius = 0
                if (np.isclose(radius, self.pixel_radius) or radius > self.pixel_radius):
                    radius = self.pixel_radius
                self.fdtd_engine.fdtd.eval('select("{}");'.format(self.group_name + str(position[0])+"_"+str(position[1])))
                self.fdtd_engine.fdtd.eval('set("radius", {:.12f});'.format(radius*1e-6))


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
    group_name : String
        Unique name of the pixels for distinguishing different pixel region.
    pixel_x_length_th : float
        Lower boundary for the pixel_x_length (default: 0).
    pixel_y_length_th : float
        Lower boundary for the pixel_y_length (default: 0).
    matrix_mask : Array
        Mask array for the matrix in update function (default: None).
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_x_length, pixel_y_length, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11, group_name = "p", pixel_x_length_th = 0, pixel_y_length_th = 0, matrix_mask = None):
        self.left_down_point = tuple_to_point(bottom_left_corner_point)
        self.right_up_point = tuple_to_point(top_right_corner_point)
        self.pixel_x_length = pixel_x_length
        self.pixel_y_length = pixel_y_length
        self.__last_array = None
        self.__lastest_array = None
        self.fdtd_engine = fdtd_engine
        self.material = material
        self.z_start = z_start
        self.z_end = z_end
        self.group_name = group_name
        self.pixel_x_length_th = pixel_x_length_th
        self.pixel_y_length_th = pixel_y_length_th
        if (type(matrix_mask) != type(None)):
            self.matrix_mask = np.array(matrix_mask, dtype=np.int32)
        else:
            self.matrix_mask = matrix_mask

    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[1]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[0]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2

        for row in range(0, self.__lastest_array.shape[1]):
            for col in range(0, self.__lastest_array.shape[0]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                x_length = self.pixel_x_length * self.__lastest_array[col,row]
                y_length = self.pixel_y_length * self.__lastest_array[col,row]
                if (np.isclose(x_length, self.pixel_x_length_th) or x_length < self.pixel_x_length_th):
                    x_length = 0
                if (np.isclose(y_length, self.pixel_y_length_th) or y_length < self.pixel_y_length_th):
                    y_length = 0
                if (np.isclose(x_length, self.pixel_x_length) or x_length > self.pixel_x_length):
                    x_length = self.pixel_x_length
                if (np.isclose(y_length, self.pixel_y_length) or y_length > self.pixel_y_length):
                    y_length = self.pixel_y_length

                self.fdtd_engine.add_structure_rectangle(center_point,x_length,y_length,material=self.material, z_start = self.z_start, z_end = self.z_end ,rename =self.group_name +  str(col)+"_"+str(row))


    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            A two-dimensional binary array that represent the pixels in the region.
        '''
        if (type(self.matrix_mask) != type(None)):
            enable_positions = np.where(np.transpose(self.matrix_mask) == 1)
            if (len(np.transpose(enable_positions)) != len(matrix)):
                raise Exception("The input matrix can not match the matrix_mask!")
            masked_matrix = self.matrix_mask.copy().astype(np.double)
            for i,position in enumerate(np.transpose(enable_positions)):
                masked_matrix[position[1], position[0]] = matrix[i]
        elif (len(matrix.shape) != 2):
            raise Exception("The input matrix should be two-dimensional when matrix_mask not specified!")
        else:
            masked_matrix = matrix

        self.fdtd_engine.switch_to_layout()
        if (len(masked_matrix.shape) != 2):
            raise Exception("The input matrix should be two-dimensional!")
        if (type(self.__lastest_array) == type(None)):
            self.__lastest_array = np.array(masked_matrix,dtype=np.double)
            self.__last_array = np.array(masked_matrix,dtype=np.double)
            self.__initialize()
        else:
            self.__lastest_array = np.array(masked_matrix,dtype=np.double)
            self.__diff = self.__lastest_array - self.__last_array
            self.__last_array = np.array(masked_matrix,dtype=np.double)
            reconfig_positions = np.where(~np.isclose(np.abs(self.__diff), 0))
            for position in np.transpose(reconfig_positions):
                x_length = self.pixel_x_length * self.__lastest_array[position[0], position[1]]
                y_length = self.pixel_y_length * self.__lastest_array[position[0], position[1]]
                if (np.isclose(x_length, self.pixel_x_length_th) or x_length < self.pixel_x_length_th):
                    x_length = 0
                if (np.isclose(y_length, self.pixel_y_length_th) or y_length < self.pixel_y_length_th):
                    y_length = 0
                if (np.isclose(x_length, self.pixel_x_length) or x_length > self.pixel_x_length):
                    x_length = self.pixel_x_length
                if (np.isclose(y_length, self.pixel_y_length) or y_length > self.pixel_y_length):
                    y_length = self.pixel_y_length
                self.fdtd_engine.fdtd.eval(
                    'select("{}");'.format(self.group_name + str(position[0]) + "_" + str(position[1])))
                self.fdtd_engine.fdtd.eval('set("x span", {:.12f});'.format(x_length * 1e-6))
                self.fdtd_engine.fdtd.eval('set("y span", {:.12f});'.format(y_length * 1e-6))


