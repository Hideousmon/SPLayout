## History

### Version 0.0.1 (Jun 29, 2021)

* Initial release

### Version 0.0.2 (Jun 30, 2021)

* Fix a fatal bug in version 0.0.1 that Selfdefinecomponent can not work with multi-components.

### Version 0.0.3 (Jul 1, 2021)

* Add document.
* Fix a bug that the microring can not return the right pad point when it is rotated.
* Fix a bug horizonal -> horizontal.
* Fix a bug Point.\__eq__ will return False when other==None.

### Version 0.0.4 (Jul 21, 2021)

* Lift restrictions on taper length.
* Support coordinate transfer for MAKE_COMPONENT.

### Version 0.0.5 (Jul 24, 2021)

* Add self.get_start_point() for AEMD_grating.
* New Class: SBend & ASBend.
* Add a constant: pi = math.pi.

### Version 0.0.6 (Jul 27,2021) & Version 0.0.7 (Jul 28, 2021)

* SBend docs update.
* Variable names: angle -> radian.
* AEMD gratings can have multiple definitions in a file.
* AEMD Grating default relative position: RIGHT.
* New cell function: self.remove_components().
* If the input filename of "make_gdsii_file" is not "*.gds", it will automatically add ".gds" to the tail.
* New class: Circle, Rectangle.
* Add port points definition for Polygon.

### Version 0.1.4 & Version 0.1.5 (Sep 6, 2021)

* FDTD API added.
* Binary Bat Algorithm & Direct Binary Search Algorithm for inverse design.

### Version 0.1.6 (Sep 17, 2021)

* README.rst for pypi ducumentation.
* Support numpy array for Polygon definition.
* Annotation for DBS run.
* Support cell flatten.
* Fix a bug: initial_solution in DirectBianrySearchAlgorithm can not be properly defined.


### Version 0.1.8 (Sep 25, 2021)

* Able to derive phase information from monitor.
* Able to create rectangle&circle pixels with fdtd functions.


### Version 0.1.9 (Sep 29, 2021)

* Pixels region for inverse design.
* Variable names: point1 -> bottom_left_corner_point, point2 -> top_right_corner_point.

### Version 0.2.0 (Oct 29, 2021)

* Component drawing functions on fdtd_engine with z_start, z_end and material. .
* Tuple support for definitions.
* Float index to define material in fdtd (object defined dielectric).
* Lumerical script eval for fdtd.
* ArbitraryAngleWaveguide class.
* Example for DBS.
* Width property for waveguides.
* Fix a bug for unexpected rotation in SelfDefineComponent.
* Self.start_point -> self.start_point_for_return in func:get_start_point of SelfDefineComponent.
* Able to get backward transmission from mode expansion monitor.

### Version 0.2.1 (Nov 3, 2021)

* ASBend & SBend bugs fixed for 'z_start' attribute missing.
* AQuarBend & QuarBend bugs fixed for unacceptable 'tuple' parameters.
* DoubleBendConnector bugs fixed for wrong type definition. 

### Version 0.2.2 (Nov 9, 2021)

* Fix bugs for MAKE_COMPONENT rotation errors.
* Microring add_heater should generate conductor layer on the heater layer.
* More functions for MODE varFDTD simulation tools. 
* Rename a function in fdtdapi: add_source -> add_mode_source.
* Function for removing cells.
* Function for renaming all drawing on Lumerical CAD.

### Version 0.2.3 (Nov 10, 2021)

* Anti-Symmetry boundary condition choice for FDTD simulation region.
* Fix bugs for material definition with float type parameter.
* Fix bugs for putting round on Lumerical CAD.
* Support Fundamental TE mode for add_mode_source in fdtdapi.

### Version 0.2.4 (Nov 13, 2021)

* Anti-Symmetry boundary condition choice for FDTD simulation region.
* Fix bugs for material definition with float type parameters.
* Fix bugs for putting round on Lumerical CAD.
* Support fundamental TE mode for add_mode_source in fdtdapi.


### Version 0.2.5 (Nov 26, 2021)

* add_index_region, add_field_region, add_mesh_region can be defined by z_min&z_max.
* Support Fundamental TE mode for add_mode_expansion in fdtdapi.
* Fix a bug for get_transmission error.

### Version 0.2.6 (Dec 13, 2021)

* Fix a bug for mismatching axises in pixelsregion.
* Fix a bug for wrong data-pass with  Scientific notation.
* Able to set amplitude and phase for mode source.
* New Function for fdtdapi: reset_source_amplitude and reset_source_phase.
* Fix a bug for wrong SelfMadeComponent rotation.

### Version 0.2.7 (Dec 16, 2021)
* New Classes for Inverse Design with Adjoint Method: ShapeOptRegion2D, ShapeOptRegion3D, TopologyOptRegion2D, TopologyOptRegion3D, AdjointForShapeOpt, AdjointForTO. 

### Version 0.2.8 (Dec 21, 2021)
* Fix a bug for mesh region error in FDTDSimulation.
* Add draw functions for CirclePixelsRegion&RectanglePixelsRegion.
* *load_file* param for FDTDSimulation & MODESimulation.

### Version 0.2.9 (Dec 22, 2021)
* Periodic boundary condition in y-axis direction for FDTD region.
* Fix a bug for wrong SelfMadeComponent rotation.

### Version 0.3.1 (Dec 28, 2021)
* Fix a bug for wrong field region definition in z-axis.
* Fix a bug for wrong initialization of RectanglePixelsRegion.

### Version 0.3.2 (Jan 4, 2022)
* New heuristic algorithms for inverse design: BPSO & BGA.
* Refine variable names for cost functions in heuristic methods.
* Optimize pixels regions for faster updating.

### Version 0.3.4 (Jan 13, 2022)
* Able to save the fdtdfile without changing working path.
* Able to create inexistent folders to save figures.

### Version 0.3.5 (Jan 18, 2022)
* Alternative show for figure plot. 
* Able to reset targets for adjoint methods.
* Add use('AGG') for matplotlib.
* Enhance reliability for executing simulations.

### Version 0.3.6 (Feb 12, 2022)
* Able to get eigenmode distribution from mode monitor.
* Enhance reliability for executing simulations.
* Figures can be shown when it is required in the inverse design regions.
* Able to get magnetic field intensity from field regions.
* Able to get power of the sources with specific wavelengths.

### Version 0.3.7 (Feb 21, 2022)
* Able to set items enable/disable for those saved in list or numpy.ndarray.
* Optimize pixels regions for faster creating.

### Version 0.3.8 (Mar 15, 2022)
* Support vertical sources and monitors.
* 2D index monitor regions and 2D field monitor regions.
* Support custom source distribution.

### Version 0.3.9 (Mar 21, 2022)
* FDTD regions can be defined with z_min&z_max.

### Version 0.4.3 (Feb 24, 2023)
* Topology optimization without filters.
* New components: SimpleAsymmetricDirectionalCoupler, SlowlyVaryingTaper.
* Add algorithm: ParticleSwarmAlgorithm.
* Reorganize the submodules.
* Rename the class: DirectBianrySearchAlgorithm -> DirectBinarySearchAlgorithm.
* Fix bug for setting the vertical mode expansions.

### Version 0.4.4 (April 14, 2023)
* Support for setting background  material with name for FDTD regions.

### Version 0.4.5 (April 15, 2023)
* Support for resetting simulation wavelengths when the sources are added.
* Support for resetting wavelength points when the monitors are added.