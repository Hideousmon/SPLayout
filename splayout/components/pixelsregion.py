from ..utils.utils import *
from ..components.filledpattern import Circle,Rectangle
import numpy as np
import os
import time

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
    matrix_mask : Array
        Mask array for the matrix in update function (default: None).
    relaxing_time : Float
        Relaxing time for eval in Lumerical FDTD (unit: s, default: 0).
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_radius, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11 , group_name = "pixels", matrix_mask = None, relaxing_time = 0):
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
        self.relaxing_time = relaxing_time
        if (type(matrix_mask) != type(None)):
            self.matrix_mask = np.array(matrix_mask, dtype=np.int32)
        else:
            self.matrix_mask = matrix_mask


    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[0]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[1]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2
        command = ""
        for row in range(0, self.__lastest_array.shape[1]):
            for col in range(0, self.__lastest_array.shape[0]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                radius = self.pixel_radius * self.__lastest_array[col,row]
                disable_flag = 0
                if ( radius <= 0.001):
                    radius = 0
                    disable_flag = 1
                if (np.isclose(radius, self.pixel_radius) or radius > self.pixel_radius):
                    radius = self.pixel_radius

                ## replace add structure circle
                command +="addcircle;"
                command +="set(\"x\"," + "%.6f" % (center_point.x) + "e-6);"
                command +="set(\"y\"," + "%.6f" % (center_point.y) + "e-6);"
                command +="set(\"radius\"," + "%.6f" % (radius) + "e-6);"
                command +="set(\"z min\"," + "%.6f" % (self.z_start) + "e-6);"
                command +="set(\"z max\"," + "%.6f" % (self.z_end) + "e-6);"
                command +="set(\"name\",\"" + self.group_name + str(col) + "_" + str(row) + "\");"
                if type(self.material) == str:
                    command +="set(\"material\",\"" + self.material + "\");"
                elif type(self.material) == float:
                    command +="set(\"material\",\"" + "<Object defined dielectric>" + "\");"
                    command +="set(\"index\"," + str(self.material) + ");"
                else:
                    raise Exception("Wrong material specification!")
                if (disable_flag):
                    command += 'set("enabled", 0);'
                else:
                    command += 'set("enabled", 1);'

        command_list = command.split(";")[:-1]
        block_length = int(len(command_list) / 10000) + 1
        for i in range(0, block_length):
            command_block = ";".join(command_list[i * 10000: (i + 1) * 10000])
            if (command_block != ""):
                command_block += ";"
                time.sleep(self.relaxing_time)
                self.fdtd_engine.fdtd.eval(command_block)




    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            Array (values:0~1) that represent the pixels in the region.
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
            command = ""
            for position in np.transpose(reconfig_positions):
                radius = self.pixel_radius * self.__lastest_array[position[0], position[1]]
                disable_flag = 0
                if ( radius <= 0.001):
                    radius = 0
                    disable_flag = 1
                if ( radius > self.pixel_radius):
                    radius = self.pixel_radius

                command += 'select("{}");'.format(self.group_name + str(position[0]) + "_" + str(position[1]))
                command += 'set("radius", %.6fe-6);' % (radius)
                if (disable_flag):
                    command += 'set("enabled", 0);'
                else:
                    command += 'set("enabled", 1);'

            self.fdtd_engine.fdtd.eval("clear;")
            command_list = command.split(";")[:-1]
            block_length = int(len(command_list) / 10000) + 1
            for i in range(0, block_length):
                command_block = ";".join(command_list[i * 10000: (i + 1) * 10000])
                if (command_block != ""):
                    command_block += ";"
                    time.sleep(self.relaxing_time)
                    self.fdtd_engine.fdtd.eval(command_block)


    def draw_layout(self, matrix, cell, layer):
        '''
        Draw pixels on layout.

        Parameters
        ----------
        matrix : numpy.array
            Array (values:0~1) that represent the pixels in the region.
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.
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

        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / masked_matrix.shape[0]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / masked_matrix.shape[1]
        self.x_start_point = self.left_down_point.x + self.block_x_length / 2
        self.y_start_point = self.right_up_point.y - self.block_y_length / 2

        for row in range(0, masked_matrix.shape[1]):
            for col in range(0, masked_matrix.shape[0]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                radius = self.pixel_radius * masked_matrix[col,row]
                if (radius <= 0.001):
                    radius = 0
                if (np.isclose(radius, self.pixel_radius) or radius > self.pixel_radius):
                    radius = self.pixel_radius
                if (~np.isclose(radius, 0)):
                    circle = Circle(center_point=center_point, radius=radius)
                    circle.draw(cell,layer)





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
    matrix_mask : Array
        Mask array for the matrix in update function (default: None).
    relaxing_time : Float
        Relaxing time for eval in Lumerical FDTD (unit: s, default: 0).
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, pixel_x_length, pixel_y_length, fdtd_engine, material=SiO2, z_start=-0.11, z_end=0.11, group_name = "p", matrix_mask = None, relaxing_time = 0):
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
        self.relaxing_time = relaxing_time
        if (type(matrix_mask) != type(None)):
            self.matrix_mask = np.array(matrix_mask, dtype=np.int32)
        else:
            self.matrix_mask = matrix_mask

    def __initialize(self):
        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / self.__lastest_array.shape[0]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / self.__lastest_array.shape[1]
        self.x_start_point = self.left_down_point.x + self.block_x_length/2
        self.y_start_point = self.right_up_point.y - self.block_y_length/2
        command = ""
        for row in range(0, self.__lastest_array.shape[1]):
            for col in range(0, self.__lastest_array.shape[0]):
                center_point = Point(self.x_start_point+col*self.block_x_length,self.y_start_point-row*self.block_y_length)
                x_length = self.pixel_x_length * self.__lastest_array[col,row]
                y_length = self.pixel_y_length * self.__lastest_array[col,row]
                disable_flag = 0
                if ( x_length < 0.001):
                    x_length = 0
                    disable_flag = 1
                if ( y_length < 0.001):
                    y_length = 0
                    disable_flag = 1
                if (np.isclose(x_length, self.pixel_x_length) or x_length > self.pixel_x_length):
                    x_length = self.pixel_x_length
                if (np.isclose(y_length, self.pixel_y_length) or y_length > self.pixel_y_length):
                    y_length = self.pixel_y_length

                command += "addrect;"
                command += "set(\"x\"," + "%.6f" % (center_point.x) + "e-6);"
                command += "set(\"x span\"," + "%.6f" % (x_length) + "e-6);"
                command += "set(\"y\"," + "%.6f" % (center_point.y) + "e-6);"
                command += "set(\"y span\"," + "%.6f" % (y_length) + "e-6);"
                command += "set(\"z min\"," + "%.6f" % (self.z_start) + "e-6);"
                command += "set(\"z max\"," + "%.6f" % (self.z_end) + "e-6);"
                command += "set(\"name\",\"" + self.group_name +  str(col)+"_"+str(row) + "\");"
                if type(self.material) == str:
                    command += "set(\"material\",\"" + self.material + "\");"
                elif type(self.material) == float:
                    command += "set(\"material\",\"" + "<Object defined dielectric>" + "\");"
                    command += "set(\"index\"," + str(self.material) + ");"
                else:
                    raise Exception("Wrong material specification!")

                if (disable_flag):
                    command += 'set("enabled", 0);'
                else:
                    command += 'set("enabled", 1);'

        command_list = command.split(";")[:-1]
        block_length = int(len(command_list) / 10000) + 1
        for i in range(0, block_length):
            command_block = ";".join(command_list[i * 10000: (i + 1) * 10000])
            if (command_block != ""):
                command_block += ";"
                time.sleep(self.relaxing_time)
                self.fdtd_engine.fdtd.eval(command_block)






    def update(self, matrix):
        '''
        Update pixel region according to the new matrix. For the first time it is called, the pixels will be created in the FDTD simulation CAD. In the following update process, it will enable/disable correspoinding pixels.

        Parameters
        ----------
        matrix : numpy.array
            Array (values:0~1) that represent the pixels in the region.
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
            command = ""
            for position in np.transpose(reconfig_positions):
                x_length = self.pixel_x_length * self.__lastest_array[position[0], position[1]]
                y_length = self.pixel_y_length * self.__lastest_array[position[0], position[1]]
                disable_flag = 0
                if (x_length < 0.001):
                    x_length = 0
                    disable_flag = 1
                if (y_length < 0.001):
                    y_length = 0
                    disable_flag = 1
                if (np.isclose(x_length, self.pixel_x_length) or x_length > self.pixel_x_length):
                    x_length = self.pixel_x_length
                if (np.isclose(y_length, self.pixel_y_length) or y_length > self.pixel_y_length):
                    y_length = self.pixel_y_length

                command += 'select("{}");'.format(self.group_name + str(position[0]) + "_" + str(position[1]))
                command += 'set("x span", {:.6f}e-6);'.format(x_length)
                command += 'set("y span", {:.6f}e-6);'.format(y_length)
                if (disable_flag):
                    command += 'set("enabled", 0);'
                else:
                    command += 'set("enabled", 1);'

            self.fdtd_engine.fdtd.eval("clear;")
            command_list = command.split(";")[:-1]
            block_length = int(len(command_list) / 10000) + 1
            for i in range(0, block_length):
                command_block = ";".join(command_list[i * 10000: (i + 1) * 10000])
                if (command_block != ""):
                    command_block += ";"
                    time.sleep(self.relaxing_time)
                    self.fdtd_engine.fdtd.eval(command_block)

    def draw_layout(self, matrix, cell, layer):
        '''
        Draw pixels on layout.

        Parameters
        ----------
        matrix : numpy.array
            Array (values:0~1) that represent the pixels in the region.
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.
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

        self.block_x_length = np.abs(self.left_down_point.x - self.right_up_point.x) / masked_matrix.shape[0]
        self.block_y_length = np.abs(self.left_down_point.y - self.right_up_point.y) / masked_matrix.shape[1]
        self.x_start_point = self.left_down_point.x + self.block_x_length / 2
        self.y_start_point = self.right_up_point.y - self.block_y_length / 2

        for row in range(0, masked_matrix.shape[1]):
            for col in range(0, masked_matrix.shape[0]):
                center_point = Point(self.x_start_point + col * self.block_x_length,
                                     self.y_start_point - row * self.block_y_length)
                x_length = self.pixel_x_length * masked_matrix[col, row]
                y_length = self.pixel_y_length * masked_matrix[col, row]
                if (x_length < 0.001):
                    x_length = 0
                if (y_length < 0.001):
                    y_length = 0
                if (np.isclose(x_length, self.pixel_x_length) or x_length > self.pixel_x_length):
                    x_length = self.pixel_x_length
                if (np.isclose(y_length, self.pixel_y_length) or y_length > self.pixel_y_length):
                    y_length = self.pixel_y_length
                if (~np.isclose(x_length, 0) and ~np.isclose(y_length, 0)):
                    rectangle = Rectangle(center_point=center_point, width=x_length, height=y_length)
                    rectangle.draw(cell,layer)


