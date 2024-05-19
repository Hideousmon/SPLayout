from ..utils.utils import *
import numpy as np
import os


class ScalableToOptRegion3D:
    """
    Scalable 3D Optimization region for topology optimization method.

    Parameters
    ----------
    bottom_left_corner_point : Point
        Lower left corner of the region.
    top_right_corner_point : Point
        Upper right corner of the region.
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    x_mesh : Float
        The grid unit in x-axis (unit: μm, default: 0.02).
    y_mesh : Float
        The grid unit in y-axis (unit: μm, default: 0.02).
    z_mesh : Float
        The grid unit in z-axis (unit: μm, default: 0.0071).
    x_scale : Float
        The scale size in x-axis (default: 1)
    y_scale : Float
        The scale size in y-axis (default: 1)
    lower_index : Float
        Lower boundary for refractive index (default: 1.444).
    higher_index : Float
        Higher boundary for refractive index (default: 3.478).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: -0.11).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: 0.11).
    rename : String
        New name for the components in Lumerical.
    filter_R : Float
        The radius of smoothing filter (unit: μm, default: 0.5)
    eta : Float
        Eta for the smoothing filter (default: 0.5)
    beta : Float
        Beta fort hte smoothing filter (default: 1)
    """
    def __init__(self, bottom_left_corner_point, top_right_corner_point, fdtd_engine, x_mesh = 0.02,y_mesh = 0.02,z_mesh = 0.02,
                 x_scale=1, y_scale=1, lower_index = 1.444, higher_index = 3.478, z_start=-0.11, z_end=0.11, rename = "ToOptRegion"):
        self.left_down_point = tuple_to_point(bottom_left_corner_point)
        self.right_up_point = tuple_to_point(top_right_corner_point)
        self.__last_params = None
        self.__lastest_params = None
        self.fdtd_engine = fdtd_engine
        self.x_mesh = x_mesh
        self.y_mesh = y_mesh
        self.z_mesh = z_mesh
        self.x_scale = int(x_scale)
        self.y_scale = int(y_scale)
        self.x_min = self.left_down_point.x
        self.x_max = self.right_up_point.x
        self.y_min = self.left_down_point.y
        self.y_max = self.right_up_point.y
        self.z_min = z_start
        self.z_max = z_end
        self.x_size = int((self.x_max - self.x_min)/self.x_mesh) + 1
        self.y_size = int((self.y_max - self.y_min)/self.y_mesh) + 1
        self.z_size = int((self.z_max - self.z_min)/self.z_mesh) + 1
        self.x_positions = np.linspace(self.x_min, self.x_max, self.x_size)
        self.y_positions = np.linspace(self.y_min, self.y_max, self.y_size)
        self.z_positions = np.linspace(self.z_min, self.z_max, self.z_size)
        # check scaling possible
        if (self.x_size - 1) % self.x_scale != 0:
            raise Exception("The scale on x axis is not possible.")
        if (self.y_size - 1) % self.y_scale != 0:
            raise Exception("THe scale on y axis is not possible.")
        self.scaled_x_size = int((self.x_size - 1) / self.x_scale) + 1
        self.scaled_y_size = int((self.y_size - 1) / self.y_scale) + 1
        self.lower_epsilon = lower_index**2
        self.higher_epsilon = higher_index**2
        self.z_start = z_start
        self.z_end = z_end
        self.rename = rename
        self.index_region_name = self.rename + "_index"
        self.field_region_name = self.rename + "_field"
        if not (self.fdtd_engine is None):
            self.__initialize()
        self.epsilon_figure = None
        self.field_figure = None

    def __initialize(self):
        self.fdtd_engine.add_index_region(self.left_down_point, self.right_up_point, z_min=self.z_min, z_max=self.z_max, dimension=3, index_monitor_name= self.index_region_name)
        self.fdtd_engine.fdtd.eval( 'select("{}");set("spatial interpolation","specified position");'.format(self.index_region_name))
        self.fdtd_engine.add_field_region(self.left_down_point, self.right_up_point, z_min=self.z_min, z_max=self.z_max, dimension=3, field_monitor_name= self.field_region_name)
        self.fdtd_engine.fdtd.eval(
            'select("{}");set("spatial interpolation","specified position");'.format(self.field_region_name))
        self.fdtd_engine.add_mesh_region(self.left_down_point, self.right_up_point, x_mesh=self.x_mesh, y_mesh=self.y_mesh,
                             z_mesh=self.z_mesh, z_min=self.z_min, z_max=self.z_max)
        self.fdtd_engine.fdtd.eval('addimport;')
        self.fdtd_engine.fdtd.eval('set("detail",1);')
        self.fdtd_engine.fdtd.eval('set("name","{}");'.format(self.rename))

    def get_x_size(self):
        """
        Return x-axis size of the region.

        Returns
        -------
        self.x_size : Int
            x-axis size.
        """
        return self.scaled_x_size

    def get_y_size(self):
        """
        Return y-axis size of the region.

        Returns
        -------
        self.y_size : Int
            y-axis size.
        """
        return self.scaled_y_size

    def scaling(self, original_matrix):
        '''
        Scaling the original matrix to a scaled matrix.

        Returns
        -------
        scaled_matrix : Array.
            (scaled_x_size, scaled_y_size).
        '''
        scaled_matrix = np.zeros((self.scaled_x_size, self.scaled_y_size), dtype=original_matrix.dtype)
        for i in range(0, scaled_matrix.shape[0]):
            for j in range(0, scaled_matrix.shape[1]):
                lower_x_index = i * self.x_scale - int(self.x_scale / 2)
                if lower_x_index < 0:
                    lower_x_index = 0
                lower_y_index = j * self.y_scale - int(self.y_scale / 2)
                if lower_y_index < 0:
                    lower_y_index = 0
                scaled_matrix[i, j] = np.mean(original_matrix[lower_x_index:
                                                              i * self.x_scale + int(self.x_scale / 2) + 1,
                                              lower_y_index:
                                              j * self.y_scale + int(self.y_scale / 2) + 1])
        return scaled_matrix


    def descaling(self, scaled_matrix):
        '''
        Scaling the scaled matrix to an original-size matrix.

        Returns
        -------
        original-size matrix: Array.
            (x_size, y_size).
        '''
        original_matrix = np.zeros((self.x_size, self.y_size))
        for i in range(0, scaled_matrix.shape[0]):
            for j in range(0, scaled_matrix.shape[1]):
                if self.x_scale == 1:
                    lower_x_index = i * self.x_scale
                    upper_x_index = i * self.x_scale + 1
                else:
                    lower_x_index = i * self.x_scale - int(self.x_scale / 2) + 1
                    upper_x_index = i * self.x_scale + int(self.x_scale / 2)
                    if lower_x_index < 0:
                        lower_x_index = 0
                if self.y_scale == 1:
                    lower_y_index = j * self.y_scale
                    upper_y_index = j * self.y_scale + 1
                else:
                    lower_y_index = j * self.y_scale - int(self.y_scale / 2) + 1
                    upper_y_index = j * self.y_scale + int(self.y_scale / 2)
                    if lower_y_index < 0:
                        lower_y_index = 0
                # central part
                original_matrix[lower_x_index:upper_x_index,
                lower_y_index: upper_y_index] = scaled_matrix[i, j]
                # edge parts
                # left edge
                if self.x_scale != 1 and i != 0:
                    original_matrix[lower_x_index - 1, lower_y_index:
                                                       upper_y_index] = (scaled_matrix[i - 1, j] + scaled_matrix[
                        i, j]) / 2
                # upper edge
                if self.y_scale != 1 and j != 0:
                    original_matrix[lower_x_index:
                                    upper_x_index, lower_y_index - 1] = (scaled_matrix[i, j - 1] + scaled_matrix[
                        i, j]) / 2
                # corner parts
                # lower left corner
                if self.x_scale != 1 and self.y_scale != 1 and i != 0 and j != 0:
                    original_matrix[lower_x_index - 1, lower_y_index - 1] = (
                                                                                    scaled_matrix[i - 1, j - 1] +
                                                                                    scaled_matrix[i - 1, j] +
                                                                                    scaled_matrix[i, j - 1] +
                                                                                    scaled_matrix[i, j]
                                                                            ) / 4
        return original_matrix


    def update(self, params_matrix):
        '''
        Update Toopology Optimization Region according to the new matrix.

        Parameters
        ----------
        params_matrix : numpy.array
            A two-dimensional array in [0,1].
        '''

        original_params_matrix = self.descaling(params_matrix)

        epsilon = original_params_matrix * (self.higher_epsilon - self.lower_epsilon) + self.lower_epsilon
        full_epsilon = np.broadcast_to(epsilon[:, :, None], (self.x_size, self.y_size, self.z_size))
        self.fdtd_engine.fdtd.putv('eps_geo', full_epsilon)
        self.fdtd_engine.fdtd.putv('x_geo', self.x_positions*1e-6)
        self.fdtd_engine.fdtd.putv('y_geo', self.y_positions*1e-6)
        self.fdtd_engine.fdtd.putv('z_geo', self.z_positions*1e-6)

        self.fdtd_engine.fdtd.eval('select("{}");'.format(self.rename) +
                  'delete;' +
                  'addimport;' +
                  'set("name","{}");'.format(self.rename) +
                  'importnk2(sqrt(eps_geo),x_geo,y_geo,z_geo);')

    def reset_index(self, lower_index, higher_index):

        self.lower_epsilon = lower_index ** 2
        self.higher_epsilon = higher_index ** 2

    def get_E_distribution(self, if_get_spatial = 0):
        """
        Get electric field distribution from the region.

        Parameters
        ----------
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
        if (if_get_spatial == 0):
            self.field_figure = self.fdtd_engine.get_E_distribution(field_monitor_name=self.field_region_name,
                                                                    if_get_spatial=if_get_spatial)
            return self.field_figure
        else:
            return self.fdtd_engine.get_E_distribution(field_monitor_name=self.field_region_name,
                                                       if_get_spatial=if_get_spatial)

    def get_epsilon_distribution(self):
        """
        Get epsilon distribution from the region.

        Returns
        -------
        out : Array
            Spectrum, size: (x mesh, y mesh, z mesh, 1).
        """
        return self.fdtd_engine.get_epsilon_distribution(index_monitor_name=self.index_region_name)

    def plot_epsilon_figure(self, filename = None, display = 0):
        """
        Plot epsilon distribution as a heatmap and save it as a file if filename is specified.

        Parameters
        ----------
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).
        display : Int or Bool
            Whether to show the figure (default: 0).

        """
        if (display):
            import matplotlib
            matplotlib.use('module://backend_interagg')
            import matplotlib.pyplot as plt
        else:
            import matplotlib
            matplotlib.use('AGG')
            import matplotlib.pyplot as plt

        epsilon = np.real(np.mean(self.epsilon_figure[:,:,int(self.z_size/2),:] if type(self.epsilon_figure)!=type(None) else self.get_epsilon_distribution()[:,:,int(self.z_size/2),:], axis=-1))
        xx, yy = np.meshgrid(np.linspace(self.x_positions[0], self.x_positions[-1], epsilon.shape[0]),
                                         np.linspace(self.y_positions[0], self.y_positions[-1], epsilon.shape[1]))
        bar = plt.pcolormesh(xx, yy, epsilon.T , cmap="gray", vmin=self.lower_epsilon, vmax=self.higher_epsilon)
        plt.colorbar(bar)
        plt.xlabel('x (μm)')
        plt.ylabel('y (μm)')
        if (type(filename) != type(None)):
            if (filename[0:2] == './'):
                filepath = os.path.abspath('./') + '/' + filename[2:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            elif (filename[0:3] == '../'):
                filepath = os.path.abspath('../') + '/' + filename[3:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            else:
                plt.savefig(filename)
        if (display):
            plt.show()
        plt.close()



    def plot_field_figure(self, filename = None, display = 0):
        """
        Plot electric distribution as a heatmap and save it as a file if filename is specified.

        Parameters
        ----------
        datafile : String
            The name of the file for saving the data, None means no saving (default: None).
        display : Int or Bool
            Whether to show the figure (default: 0).

        """
        if (display):
            import matplotlib
            matplotlib.use('module://backend_interagg')
            import matplotlib.pyplot as plt
        else:
            import matplotlib
            matplotlib.use('AGG')
            import matplotlib.pyplot as plt

        field = np.abs(np.mean(self.field_figure[:, :, int(self.z_size/2), 0, :], axis=-1) if type(self.field_figure) != type(
            None) else np.mean(self.get_E_distribution()[:, :, int(self.z_size/2), 0, :], axis=-1))
        xx, yy = np.meshgrid(np.linspace(self.x_positions[0], self.x_positions[-1], field.shape[0]),
                             np.linspace(self.y_positions[0], self.y_positions[-1], field.shape[1]))
        bar = plt.pcolormesh(xx, yy, field.T, cmap="jet")
        plt.colorbar(bar)
        plt.xlabel('x (μm)')
        plt.ylabel('y (μm)')
        if (type(filename) != type(None)):
            if (filename[0:2] == './'):
                filepath = os.path.abspath('./') + '/' + filename[2:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            elif (filename[0:3] == '../'):
                filepath = os.path.abspath('../') + '/' + filename[3:]
                filedir = os.path.split(filepath)[0]
                if not os.path.isdir(filedir):
                    os.makedirs(filedir)
                plt.savefig(filepath)
            else:
                plt.savefig(filename)
        if (display):
            plt.show()
        plt.close()