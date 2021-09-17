

# SPLayout
[![GitHub repository](https://img.shields.io/badge/github-SPLayout-blue)](https://github.com/Hideousmon/SPLayout) [![GitHub license](https://img.shields.io/badge/lisence-GNU--3.0-green)](https://github.com/Hideousmon/SPLayout/blob/main/LICENSE) [![Language](https://img.shields.io/badge/make%20with-Python-red)]()

 Silicon Photonics Design Tools for GDSII Files. It is based on **gdspy**([heitzmann/gdspy: Python module for creating GDSII stream files, usually CAD layouts. (github.com)](https://github.com/heitzmann/gdspy)) and can interact with it.

## Dependency
* Python3 (3.6, 3.7, 3.8)
* gdspy
* scipy
* numpy

## Installation

use pip:

```
pip install splayout
```

or download from the source and build/install with:

```
python setup.py install
```

## Documentation

The documentation can be found [here](https://splayout.readthedocs.io/en/latest/).

## References for Inverse Design Methods

[1] Mirjalili, S., Mirjalili, S.M. & Yang, XS. Binary bat algorithm. Neural Comput &Applic 25, 663–681 (2014). https://doi.org/10.1007/s00521-013-1525-5

[2] Shen, B., Wang, P., Polson, R. et al. An integrated-nanophotonics polarization beamsplitter with 2.4 × 2.4 μm2 footprint. Nature Photon 9, 378–382 (2015). https://doi.org/10.1038/nphoton.2015.80


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

