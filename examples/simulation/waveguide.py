"""
https://github.com/Hideousmon/SPLayout (Version >= 0.4.0)
waveguide simulation example with Lumerical FDTD.
"""

from splayout import *
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # initialize the simulation frame
    fdtd = FDTDSimulation()

    # draw waveguides on Lumerical
    waveguide = Waveguide(start_point=Point(-3,0), end_point=Point(3,0), width=1, z_start=-0.11, z_end=0.11, material=Si)
    waveguide.draw_on_lumerical_CAD(fdtd)

    # add simulation region, source, and monitor
    fdtd.add_fdtd_region(bottom_left_corner_point=Point(-2, -1.5), top_right_corner_point=Point(2, 1.5), background_index=1.444,dimension=3, height=0.8, use_gpu=0)

    fdtd.add_mode_source(position=Point(-1.5,0), width=1.5, height=0.8, wavelength_start=1.54, wavelength_end=1.57, mode_number=1)

    fdtd.add_mode_expansion(position=Point(1.5, 0), width=1.5, height=0.8, points=101, mode_list=[1])

    # run simulation
    fdtd.run("./temp")

    # get result return: (number of modes, 2, frequency points)
    # where (number of modes, 0, frequency points) are wavelengths,
    #       (number of modes, 1, frequency points) are transmissions
    transmission = fdtd.get_mode_transmission(expansion_name="expansion")

    # plot figure
    plt.figure()
    plt.plot(transmission[0, 0, :]*1e9, transmission[0, 1, :])
    plt.xlabel("Wavelength(nm)")
    plt.ylabel("Transmission")
    plt.show()