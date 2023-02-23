from ..utils.utils import *
from ..components.waveguide import Waveguide
from ..components.sbend import ASBend, SBend
from ..lumericalcommun.fdtdapi import FDTDSimulation
from ..lumericalcommun.modeapi import MODESimulation
import json

class SimpleAsymmetricDirectionalCoupler:
    """
    Simple Asymmetric Directional Coupler in SPLayout.

    Parameters
    ----------
    start_point : Point
        Start point of the coupler.
    direction : FROM_LEFT_TO_RIGHT or FROM_RIGHT_TO_LEFT or FROM_LOWER_TO_UPPER or FROM_UPPER_TO_LOWER
        The direction of the coupler.
    json_file : String
        Path to the json file that stocks the ADC information.
    coupling_length : float
        Coupling length of the coupler (μm, default: None, only usefule when json_file is not defined).
    bus_width : Float
        Width of the bus waveguide (μm, default: None, only usefule when json_file is not defined).
    bus_coupler_gap : Float
        Gap between the bus waveguide and the coupler waveguide (μm, default: None, only usefule when json_file is not defined).
    coupler_width : Float
        Width of the coupler waveguide (μm, default: None, only usefule when json_file is not defined).
    sbend_length : Float
        Length of the sbends at the ports of the coupler waveguide (μm, default: None, only usefule when json_file is not defined).
    z_start : Float
        The start point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    z_end : Float
        The end point for the structure in z axis (unit: μm, default: None, only useful when draw on CAD).
    material : String or Float
        Material setting for the structure in Lumerical FDTD (SiO2 = "SiO2 (Glass) - Palik", SiO2 = "SiO2 (Glass) - Palik"). When it is a float, the material in FDTD will be
        <Object defined dielectric>, and index will be defined. (default: None, only useful when draw on CAD)
    rename : String
        New name of the structure in Lumerical (default: None, only useful when draw on CAD).
    opposite : Bool or Int
        Whether the coupler is mirrored (default: 0).

    """
    def __init__(self, start_point, direction = FROM_LEFT_TO_RIGHT ,json_file = None,
                 coupling_length = None, bus_width = None, bus_coupler_gap = None,
                 coupler_width = None, sbend_length = None, z_start = None,
                 z_end = None, material = None, rename = None, opposite = 0):
        if json_file is None:
            if (coupling_length is None) or (bus_width is None) or (bus_coupler_gap is None) or (
                coupler_width is None) or (sbend_length is None) :
                raise Exception("json_file or all parameters for the simple ADC should be specified! ")
            else:
                self.coupling_length = coupling_length
                self.bus_width = bus_width
                self.bus_coupler_gap = bus_coupler_gap
                self.coupler_width = coupler_width
                self.sbend_length = sbend_length
        else:
            try:
                with open(json_file) as f:
                    load_params = json.load(f)
            except:
                raise Exception("Can not open the json file!")

            self.coupling_length = load_params['coupling length']
            self.bus_width = load_params['bus width']
            self.bus_coupler_gap = load_params['bus coupler gap']
            self.coupler_width = load_params['coupler width']
            self.sbend_length = load_params['sbend length']
        self.start_point = tuple_to_point(start_point)
        self.direction = direction
        self.z_start = z_start
        self.z_end = z_end
        self.material = material
        self.rename = rename
        self.opposite = opposite
        if (direction == FROM_LEFT_TO_RIGHT):
            self.bus_input_waveguide = Waveguide(self.start_point,
                                               self.start_point + (self.sbend_length, 0),
                                               width=self.bus_width, z_start=self.z_start, z_end=self.z_end, material=self.material,
                                               rename=self.rename)

            self.bus_coupling_waveguide = Waveguide(self.bus_input_waveguide.get_end_point(),
                                               self.bus_input_waveguide.get_end_point() + (self.coupling_length, 0),
                                               width=self.bus_width, z_start=self.z_start, z_end=self.z_end, material=self.material,
                                               rename=self.rename)

            self.bus_output_waveguide = Waveguide(self.bus_coupling_waveguide.get_end_point(),
                                               self.bus_coupling_waveguide.get_end_point() + (self.sbend_length, 0),
                                               width=self.bus_width, z_start=self.z_start, z_end=self.z_end, material=self.material,
                                               rename=self.rename)

            self.through_point = self.bus_output_waveguide.get_end_point()
            if (self.opposite):
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    0, self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width / 2)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                       coupler_coupling_waveguide_start_point + (self.coupling_length, 0),
                                                       width=self.coupler_width,z_start=self.z_start, z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_y = self.bus_input_waveguide.get_end_point().y + self. bus_width / 2 + self.bus_coupler_gap + self.coupler_width + 1
                coupler_sbend_end = Point(coupler_bend_start_point.x + self.sbend_length, output_waveguide_y)
                self.coupler_sbend = ASBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                       z_start=self.z_start, z_end=self.z_end,
                                       material=self.material, rename=self.rename)

                another_sbend_start_point =  self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(another_sbend_start_point.x - self.sbend_length, output_waveguide_y)
                self.another_sbend = SBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

            else:
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    0, - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width / 2)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                            self.coupling_length, 0),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)
                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_y = self.bus_input_waveguide.get_end_point().y - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width - 1
                coupler_sbend_end = Point(coupler_bend_start_point.x + self.sbend_length, output_waveguide_y)
                self.coupler_sbend = SBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(another_sbend_start_point.x - self.sbend_length, output_waveguide_y)
                self.another_sbend = ASBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

        elif (direction == FROM_RIGHT_TO_LEFT):
            self.bus_input_waveguide = Waveguide(self.start_point,
                                                 self.start_point + ( - self.sbend_length, 0),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.bus_coupling_waveguide = Waveguide(self.bus_input_waveguide.get_end_point(),
                                                    self.bus_input_waveguide.get_end_point() + (- self.coupling_length, 0),
                                                    width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                    material=self.material,
                                                    rename=self.rename)

            self.bus_output_waveguide = Waveguide(self.bus_coupling_waveguide.get_end_point(),
                                                 self.bus_coupling_waveguide.get_end_point() + (-self.sbend_length, 0),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.through_point = self.bus_output_waveguide.get_end_point()
            if (self.opposite):
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    0, self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width / 2)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                            - self.coupling_length, 0),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_y = self.bus_coupling_waveguide.get_start_point().y + self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width + 1
                coupler_sbend_end = Point(coupler_bend_start_point.x - self.sbend_length, output_waveguide_y)
                self.coupler_sbend = SBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(another_sbend_start_point.x + self.sbend_length, output_waveguide_y)
                self.another_sbend = ASBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

            else:
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    0, - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width / 2)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                                - self.coupling_length, 0),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)
                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_y = self.bus_coupling_waveguide.get_start_point().y - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width - 1
                coupler_sbend_end = Point(coupler_bend_start_point.x - self.sbend_length, output_waveguide_y)
                self.coupler_sbend = ASBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(another_sbend_start_point.x + self.sbend_length, output_waveguide_y)
                self.another_sbend = SBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)
        elif (direction == FROM_LOWER_TO_UPPER):
            self.bus_input_waveguide = Waveguide(self.start_point,
                                                 self.start_point + (0, self.sbend_length),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.bus_coupling_waveguide = Waveguide(self.bus_input_waveguide.get_end_point(),
                                                    self.bus_input_waveguide.get_end_point() + (0, self.coupling_length),
                                                    width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                    material=self.material,
                                                    rename=self.rename)

            self.bus_output_waveguide = Waveguide(self.bus_coupling_waveguide.get_end_point(),
                                                 self.bus_coupling_waveguide.get_end_point() + (0, self.sbend_length),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.through_point = self.bus_coupling_waveguide.get_end_point()
            if (self.opposite):
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width / 2, 0)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                            0, self.coupling_length),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_x = self.bus_coupling_waveguide.get_start_point().x - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width - 1
                coupler_sbend_end = Point(output_waveguide_x, coupler_bend_start_point.y + self.sbend_length)
                self.coupler_sbend = ASBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(output_waveguide_x, another_sbend_start_point.y - self.sbend_length)
                self.another_sbend = SBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

            else:
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width / 2, 0)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                                0, self.coupling_length),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_x = self.bus_coupling_waveguide.get_start_point().x + self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width + 1
                coupler_sbend_end = Point(output_waveguide_x, coupler_bend_start_point.y + self.sbend_length)
                self.coupler_sbend = SBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(output_waveguide_x, another_sbend_start_point.y - self.sbend_length)
                self.another_sbend = ASBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)
        else: ## direction == FROM_UPPER_TO_LOWER
            self.bus_input_waveguide = Waveguide(self.start_point,
                                                 self.start_point + (0, - self.sbend_length),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.bus_coupling_waveguide = Waveguide(self.bus_input_waveguide.get_end_point(),
                                                    self.bus_input_waveguide.get_end_point() + (0, - self.coupling_length),
                                                    width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                    material=self.material,
                                                    rename=self.rename)

            self.bus_output_waveguide = Waveguide(self.bus_coupling_waveguide.get_end_point(),
                                                 self.bus_coupling_waveguide.get_end_point() + (0, - self.sbend_length),
                                                 width=self.bus_width, z_start=self.z_start, z_end=self.z_end,
                                                 material=self.material,
                                                 rename=self.rename)

            self.through_point = self.bus_output_waveguide.get_end_point()
            if (self.opposite):
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width / 2, 0)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                                0, - self.coupling_length),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_x = self.bus_coupling_waveguide.get_start_point().x - self.bus_width / 2 - self.bus_coupler_gap - self.coupler_width - 1
                coupler_sbend_end = Point(output_waveguide_x, coupler_bend_start_point.y - self.sbend_length)
                self.coupler_sbend = SBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(output_waveguide_x, another_sbend_start_point.y + self.sbend_length)
                self.another_sbend = ASBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

            else:
                coupler_coupling_waveguide_start_point = self.bus_coupling_waveguide.get_start_point() + (
                    self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width / 2, 0)
                self.coupler_coupling_waveguide = Waveguide(coupler_coupling_waveguide_start_point,
                                                            coupler_coupling_waveguide_start_point + (
                                                                0, - self.coupling_length),
                                                            width=self.coupler_width, z_start=self.z_start,
                                                            z_end=self.z_end,
                                                            material=self.material, rename=self.rename)

                coupler_bend_start_point = self.coupler_coupling_waveguide.get_end_point()
                output_waveguide_x = self.bus_coupling_waveguide.get_start_point().x + self.bus_width / 2 + self.bus_coupler_gap + self.coupler_width + 1
                coupler_sbend_end = Point(output_waveguide_x, coupler_bend_start_point.y - self.sbend_length)
                self.coupler_sbend = ASBend(coupler_bend_start_point, coupler_sbend_end, width=self.coupler_width,
                                           z_start=self.z_start, z_end=self.z_end,
                                           material=self.material, rename=self.rename)

                another_sbend_start_point = self.coupler_coupling_waveguide.get_start_point()
                another_sbend_end = Point(output_waveguide_x, another_sbend_start_point.y + self.sbend_length)
                self.another_sbend = SBend(another_sbend_start_point, another_sbend_end, width=self.coupler_width,
                                            z_start=self.z_start, z_end=self.z_end,
                                            material=self.material, rename=self.rename)
        self.drop_point = self.coupler_sbend.get_end_point()

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
        self.bus_input_waveguide.draw(cell, layer)
        self.bus_coupling_waveguide.draw(cell, layer)
        self.bus_output_waveguide.draw(cell, layer)
        self.coupler_coupling_waveguide.draw(cell, layer)
        self.coupler_sbend.draw(cell, layer)
        self.another_sbend.draw(cell, layer)

        return self.start_point, self.through_point, self.drop_point

    def draw_on_lumerical_CAD(self, engine):
        """
        Draw the Component on the lumerical CAD (FDTD or MODE).

        Parameters
        ----------
        engine : FDTDSimulation or MODESimulation
            CAD to draw the component.
        """
        self.bus_input_waveguide.draw_on_lumerical_CAD(engine)
        self.bus_coupling_waveguide.draw_on_lumerical_CAD(engine)
        self.bus_output_waveguide.draw_on_lumerical_CAD(engine)
        self.coupler_coupling_waveguide.draw_on_lumerical_CAD(engine)
        self.coupler_sbend.draw_on_lumerical_CAD(engine)
        self.another_sbend.draw_on_lumerical_CAD(engine)


    def get_start_point(self):
        """
        Derive the start point of the coupler.

        Returns
        -------
        out : Point
            Start point.
        """
        return self.start_point

    def get_through_point(self):
        """
        Derive the through point of the coupler.

        Returns
        -------
        out : Point
            End point.
        """
        return self.through_point

    def get_drop_point(self):
        """
        Derive the drop point of the coupler.

        Returns
        -------
        out : Point
            End point.
        """
        return self.drop_point

    def get_input_width(self):
        """
        Derive the width of input waveguide.

        Returns
        -------
        out : float
            Width.
        """
        return self.bus_width

    def get_output_width(self):
        """
        Derive the width of the output waveguide.

        Returns
        -------
        out : float
            Width.
        """
        return self.bus_width

    def get_drop_width(self):
        """
        Derive the width of the drop port.

        Returns
        -------
        out : float
            Width.
        """
        return self.coupler_width



