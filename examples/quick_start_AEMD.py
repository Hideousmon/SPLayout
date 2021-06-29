""" https://github.com/Hideousmon/SPLayout """
# A simple microring filter design example

## import
from splayout import *
import math

## define main cell
filterCell = Cell("filter")

## define layers
WG_LAYER = Layer(5,0)
HEATER_LAYER = Layer(3,0)
CONTACT_LAYER = Layer(4,0)
INV_LAYER = Layer(1,0)

## make the AEMD grating definition
AEMDgrating = MAKE_AEMD_GRATING(port_width=0.45,waveguide_layer=WG_LAYER)

## firstly, draw a waveguide before the filter
start_point = Point(0,0)
input_waveguide = Waveguide(start_point,start_point + (300,0),width=0.45)
input_waveguide.draw(filterCell,WG_LAYER)

## draw an AEMD grating on the left of the waveguide
grating = AEMDgrating(input_waveguide.get_start_point(),LEFT)
grating.draw(filterCell)

## draw a microring with heater after the waveguide
ring = AddDropMicroring(input_waveguide.get_end_point(),radius=5,gap=0.18,wg_width=0.45,coupling_length=0)
ring.draw(filterCell,WG_LAYER)
ring.add_heater(filterCell,heater_layer=HEATER_LAYER,contact=1,contact_layer=CONTACT_LAYER)

# draw the through port waveguide
through_waveguide = Waveguide(ring.get_through_point(),ring.get_through_point()+(300,0),width=0.45)
through_waveguide.draw(filterCell,WG_LAYER)

# draw an AEMD grating for the through port
grating = AEMDgrating(through_waveguide.get_end_point(),RIGHT)
grating.draw(filterCell)

# draw the add port connectors and make the output aligns with the through port
add_port_connector = QuarBend(ring.get_add_point(), ring.get_input_point() + (20, -100), width=0.45)
add_port_connector.draw(filterCell, WG_LAYER)
add_port_connector = AQuarBend(add_port_connector.get_end_point(), through_waveguide.get_end_point() + (0, -127 * 1),
                               width=0.45)
add_port_connector.draw(filterCell, WG_LAYER)

# draw an AEMD grating for the add port
grating = AEMDgrating(add_port_connector.get_end_point(),RIGHT)
grating.draw(filterCell)

# draw the drop port connectors and make the output aligns with the through port
drop_port_connector = AQuarBend(ring.get_drop_point(), ring.get_input_point() + (-10, -100),
                                width=0.45)
drop_port_connector.draw(filterCell, WG_LAYER)
drop_port_connector = AQuarBend(drop_port_connector.get_end_point(),
                                through_waveguide.get_end_point() + (0, -127 * 2),
                                width=0.45)
drop_port_connector.draw(filterCell, WG_LAYER)

# draw an AEMD grating for the drop port
grating = AEMDgrating(drop_port_connector.get_end_point(),RIGHT)
grating.draw(filterCell)

# make the gdsii file and invert the WG_LAYER to INV_LAYER for positive photoresist
make_gdsii_file("quick_start_AEMD.gds",inv_source_layer=WG_LAYER,inv_target_layer=INV_LAYER)




