""" https://github.com/Hideousmon/SPLayout """
# A simple microring filter design example

## import
from splayout import *
import math

## define main cell
filterCell = Cell("filter")

## define layers
WG_LAYER = Layer(31,1)
COVER_LAYER = Layer(31,2)
HEATER_LAYER = Layer(19,0)
CONTACT_LAYER = Layer(11,1)
TOUCH_LAYER = Layer(50,0)
OPEN_LAYER = Layer(60,0)

## make the CUMEC grating definition (GC_TE_1550.gds can be gotten from the pdk of CUMEC)
CUMECgrating = MAKE_COMPONENT("GC_TE_1550.gds","Fixed_GC_TE_1550",initial_relative_position=LEFT)

## firstly, draw a waveguide before the filter
start_point = Point(0,0)
input_waveguide = Waveguide(start_point,start_point + (300,0),width=0.45)
input_waveguide.draw(filterCell,WG_LAYER)

## draw an AEMD grating on the left of the waveguide
grating = CUMECgrating(input_waveguide.get_start_point(),LEFT)
grating.draw(filterCell)

## draw a microring with heater after the waveguide
ring = AddDropMicroring(input_waveguide.get_end_point(),radius=5,gap=0.18,wg_width=0.45,coupling_length=0)
ring.draw(filterCell,WG_LAYER)
ring.add_heater(filterCell,heater_layer=HEATER_LAYER,contact=1,contact_layer=CONTACT_LAYER,touch=1,touch_layer=TOUCH_LAYER,open=1,open_layer=OPEN_LAYER)

# draw the through port waveguide
through_waveguide = Waveguide(ring.get_through_point(),ring.get_through_point()+(300,0),width=0.45)
through_waveguide.draw(filterCell,WG_LAYER)

# draw an AEMD grating for the through port
grating = CUMECgrating(through_waveguide.get_end_point(),RIGHT)
grating.draw(filterCell)

# draw the add port connectors and make the output aligns with the through port
add_port_connector = QuarBend(ring.get_add_point(), ring.get_input_point() + (20, -100), width=0.45)
add_port_connector.draw(filterCell, WG_LAYER)
add_port_connector = AQuarBend(add_port_connector.get_end_point(), through_waveguide.get_end_point() + (0, -127 * 1),
                               width=0.45)
add_port_connector.draw(filterCell, WG_LAYER)

# draw an AEMD grating for the add port
grating = CUMECgrating(add_port_connector.get_end_point(),RIGHT)
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
grating = CUMECgrating(drop_port_connector.get_end_point(),RIGHT)
grating.draw(filterCell)

# make the gdsii file and invert the WG_LAYER to INV_LAYER for positive photoresist
make_gdsii_file("quick_start_CUMEC.gds",cover_source_layer=WG_LAYER,cover_target_layer=COVER_LAYER)
