"""
https://github.com/Hideousmon/SPLayout (Version >= 0.5.2)
generate gdsii file with the result from polarization beam splitter inverse design example.
(Reference: Shen, B., Wang, P., Polson, R. et al.
An integrated-nanophotonics polarization beamsplitter with 2.4 × 2.4 μm2 footprint.
Nature Photon 9, 378–382 (2015). https://doi.org/10.1038/nphoton.2015.80)
"""

from splayout import *
import numpy as np

if __name__ == "__main__":
    # result import
    solution = np.load("./solution.npy")

    # definitions for gdsii file creation
    cell = Cell("PBS")
    wg_layer = Layer(1, 0)
    etch_layer = Layer(2, 0)

    # parameters for structures
    waveguide_width = 0.44
    waveguide_length = 3
    waveguide_gap = 1
    design_region_width = 2.4
    design_region_length = 2.4
    oxide_thickness = 2

    # draw waveguides into the gdsii file
    waveguide_input = Waveguide(Point(-design_region_length / 2 - waveguide_length, 0),
                                Point(-design_region_length / 2, 0),
                                width=waveguide_width, z_start=-0.15, z_end=0.15, material=Si)
    waveguide_input.draw(cell, wg_layer)
    waveguide_output1 = Waveguide(Point(design_region_length / 2, waveguide_gap / 2),
                                  Point(design_region_length / 2 + waveguide_length, waveguide_gap / 2),
                                  width=waveguide_width, z_start=-0.15, z_end=0.15, material=Si)
    waveguide_output1.draw(cell, wg_layer)
    waveguide_output2 = Waveguide(Point(design_region_length / 2, -waveguide_gap / 2),
                                  Point(design_region_length / 2 + waveguide_length, -waveguide_gap / 2),
                                  width=waveguide_width, z_start=-0.15, z_end=0.15, material=Si)
    waveguide_output2.draw(cell, wg_layer)
    design_region = Rectangle(Point(0, 0), width=design_region_length, height=design_region_width,
                              z_start=-0.15, z_end=0.15, material=Si)
    design_region.draw(cell, wg_layer)

    # pixels region definition
    pixels = RectanglePixelsRegion(Point(-design_region_length/2,-design_region_width/2),
                                   Point(design_region_length/2,design_region_width/2),
                                   pixel_x_length=0.12, pixel_y_length=0.12, fdtd_engine=None,
                                   material=None, z_start=-0.15, z_end=0.15)

    # etch pixels to gdsii
    solution = solution.reshape(20, 20)
    pixels.draw_layout(solution, cell, etch_layer)

    # boolean operation to get the silicon pattern on wg_layer (optional)
    wg_layer.cut(etch_layer)

    # make gdsii file
    make_gdsii_file("./PBS")
