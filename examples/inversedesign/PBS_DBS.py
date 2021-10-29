"""
https://github.com/Hideousmon/SPLayout
contributor: Yichen Pan(https://github.com/xiling1204)
polarization beam splitter inverse design example.
(Reference: Shen, B., Wang, P., Polson, R. et al.
An integrated-nanophotonics polarization beamsplitter with 2.4 × 2.4 μm2 footprint.
Nature Photon 9, 378–382 (2015). https://doi.org/10.1038/nphoton.2015.80)
"""

from splayout import *
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
    ## definitions for gdsii file creation
    cell = Cell("PBS")
    wg_layer = Layer(1, 0)
    etch_layer = Layer(2, 0)
    oxide_layer = Layer(3, 0)

    ## parameters for structures
    waveguide_width = 0.44
    waveguide_length =3
    waveguide_gap = 1
    design_region_width = 2.4
    design_region_length = 2.4
    oxide_thickness = 2
    Air = "etch"

    ## initialize the simulation frame
    fdtd = FDTDSimulation(fdtd_path="C:\\Program Files\\Lumerical\\v202\\api\\python")

    ## draw the silicon-oxide substrate and waveguides into the gdsii file
    waveguide_input = Waveguide(Point(-design_region_length / 2 - waveguide_length, 0),
                                Point(-design_region_length / 2, 0),
                                width=waveguide_width)
    waveguide_input.draw(cell, wg_layer)
    waveguide_output1 = Waveguide(Point(design_region_length / 2, waveguide_gap / 2),
                                  Point(design_region_length / 2 + waveguide_length, waveguide_gap / 2),
                                  width=waveguide_width)
    waveguide_output1.draw(cell, wg_layer)
    waveguide_output2 = Waveguide(Point(design_region_length / 2, -waveguide_gap / 2),
                                  Point(design_region_length / 2 + waveguide_length, -waveguide_gap / 2),
                                  width=waveguide_width)
    waveguide_output2.draw(cell, wg_layer)
    design_region = Rectangle(Point(0, 0), width=design_region_length, height=design_region_width)
    design_region.draw(cell, wg_layer)
    substrate = Rectangle(Point(0, 0), width=design_region_length + 2 * waveguide_length + 2,
                          height=design_region_width + 1)
    substrate.draw(cell, oxide_layer)

    ## make the gdsii file
    make_gdsii_file("PBS.gds")

    ## add sources and monitors for the FDTD simulation
    fdtd.add_source(waveguide_input.get_start_point() + (2, 0), source_name="source_TE", width=1, mode_number=1,
                    wavelength_start=1.525, wavelength_end=1.575)
    fdtd.add_source(waveguide_input.get_start_point() + (2, 0), source_name="source_TM", width=1, mode_number=2,
                    wavelength_start=1.525, wavelength_end=1.575)
    fdtd.add_mode_expansion(waveguide_output1.get_end_point() - (2, 0), mode_list=[1, 2], width=1,
                            expansion_name="mode1", points=101)
    fdtd.add_mode_expansion(waveguide_output2.get_end_point() - (2, 0), mode_list=[1, 2], width=1,
                            expansion_name="mode2", points=101)
    fdtd.add_fdtd_region(waveguide_input.get_start_point() + (1, -1.5), waveguide_output1.get_end_point() + (-1, 1),
                         z_symmetric=0, background_index=1)
    fdtd.add_mesh_region(waveguide_input.get_start_point() + (1.5, -1.5), waveguide_output1.get_end_point() + (-1.5, 1),
                         x_mesh=0.03, y_mesh=0.03, z_mesh=0.03, height=1)

    ## add structures from the gdsii file to the FDTD simulation
    fdtd.add_structure_from_gdsii("PBS.gds", "PBS", layer=wg_layer.layer,
                                  datatype=wg_layer.datatype, material=Si, z_start=-0.15, z_end=0.15,
                                  rename="WG")
    fdtd.add_structure_from_gdsii("PBS.gds", "PBS", layer=oxide_layer.layer,
                                  datatype=oxide_layer.datatype, material=SiO2, z_start=-2.15, z_end=-0.15,
                                  rename="OXIDE")

    ## pixels region definition
    pixels = RectanglePixelsRegion(Point(-design_region_length/2,-design_region_width/2),Point(design_region_length/2,design_region_width/2),pixel_x_length=0.12,pixel_y_length=0.12,fdtd_engine=fdtd,material=Air,z_start=-0.15,z_end=0.15)

    ## Define Optimization
    max_iteration = 3
    loS = 400
    FoMTE_list = np.zeros((max_iteration * loS + 1))
    FoMTM_list = np.zeros((max_iteration * loS + 1))
    list_counter = 0

    def cost_function(based_matrix):
        based_matrix = based_matrix.reshape(20, 20)
        pixels.update(based_matrix)
        ## TE
        fdtd.switch_to_layout()
        fdtd.set_enable("source_TE")
        fdtd.set_disable("source_TM")
        fdtd.run("PBS")
        FoMTE = np.mean(fdtd.get_mode_transmission("mode1")[0, 1, :])
        ## TM
        fdtd.switch_to_layout()
        fdtd.set_enable("source_TM")
        fdtd.set_disable("source_TE")
        fdtd.run("PBS")
        FoMTM = np.mean(fdtd.get_mode_transmission("mode2")[1, 1, :])

        global list_counter
        FoMTE_list[list_counter] = FoMTE
        FoMTM_list[list_counter] = FoMTM
        list_counter += 1

        return -FoMTE - FoMTM

    def call_back():
        print("Size of remained:", DBS.get_remained_size())
        print("Number of iteration:", DBS.get_iteration_number())
        print("The minimum fitness:", DBS.get_fitness())
        print("Best Solution:", DBS.get_best_solution())

    DBS = DirectBianrySearchAlgorithm(loS, cost_function, max_iteration, call_back)

    ## save initial solution into the file
    np.save("init_solution", DBS.best_solution)

    ## start DBS optimization
    DBS.run()

    ## save results into files
    np.save("solution", DBS.best_solution)
    np.save("cg_curve", DBS.cg_curve)
    np.save("FoMTE", np.array(FoMTE_list))
    np.save("FoMTM", np.array(FoMTM_list))

    ## plot for the cost
    x = range(0, DBS.cg_curve.shape[0])
    y = DBS.cg_curve
    xlabel = "Operation Times"
    ylabel = "Cost (Lower Better)"
    plt.figure()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.plot(x, y)
    plt.savefig("PBS", dpi=600)
    plt.show()
    plt.close()
    plt.clf()

