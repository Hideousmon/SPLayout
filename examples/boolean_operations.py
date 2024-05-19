""" https://github.com/Hideousmon/SPLayout """
from splayout import *

if __name__ == "__main__":
    # prepare the initial pattern
    cell = Cell("Boolean")
    layer1 = Layer(1, 0)
    layer2 = Layer(2, 0)
    result_layer = Layer(31,0)

    circle1 = Circle(Point(-1, 0), radius=2)
    circle1.draw(cell, layer1)
    circle2 = Circle(Point(1, 0), radius=2)
    circle2.draw(cell, layer2)

    make_gdsii_file("boolean_before.gds")

    # cut operation
    layer1.cut(layer2, output_layer=result_layer)
    make_gdsii_file("boolean_cut.gds")

    # add operation
    layer1.add(layer2, output_layer=result_layer)
    make_gdsii_file("boolean_add.gds")

    # common operation
    layer1.common(layer2, output_layer=result_layer)
    make_gdsii_file("boolean_common.gds")

    # dilation operation
    layer1.dilation(distance=2, output_layer=result_layer)
    make_gdsii_file("boolean_dilation.gds")

    # inversion operation
    layer1.inversion(distance=2, output_layer=result_layer)
    make_gdsii_file("boolean_inversion.gds")