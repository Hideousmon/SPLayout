""" https://github.com/Hideousmon/SPLayout """
from splayout import *
import math

#############################################################################################################
########################################### cell and layer define ###########################################
#############################################################################################################
# define cell and layer
cell = Cell("basic")
wg_layer = Layer(1,0)
grating_layer = Layer(2,0)
heater_layer = Layer(3,0)
contact_layer = Layer(4,0)
inv_layer = Layer(50,0)
cover_layer = Layer(51,0)

#############################################################################################################
############################################# components layout #############################################
#############################################################################################################

################################# waveguide example #################################
# start point and end point for the waveguide
wg_start_point = Point(0,0)
wg_end_point = wg_start_point + (10,0)
# make a waveguide
wg = Waveguide(wg_start_point,wg_end_point,width=0.5)
# draw the waveguide on the layout
wg.draw(cell,wg_layer)

################################# taper example #################################
# start point and end point for the taper
tp_start_point = Point(30,0)
tp_end_point = tp_start_point + (0,5)
# make a taper
tp = Taper(tp_start_point,tp_end_point,start_width=0.5,end_width=1)
# draw the taper on the layout
tp.draw(cell,wg_layer)

################################# bend example #################################
# center point and angle for the bend
center_point = Point(60,0)
start_angle = math.pi*0
end_angle = math.pi*3/5
width = 0.5
radius = 5
# make a bend
first_bend = Bend(center_point, start_angle, end_angle, width , radius)
# draw the bend on the layout
first_bend.draw(cell,wg_layer)


################################# clockwise quarbend example #################################
# start point and end point for the quarbend
start_point = Point(90,0)
end_point = start_point + (-7,20)
# make a quarbend
first_QuarBend = QuarBend(start_point,end_point,width=0.5)
# draw the quarbend on the layout
first_QuarBend.draw(cell,wg_layer)

################################# anti-clockwise quarbend example 2 #################################
# start point and end point for the anti-clockwise quarbend
start_point = Point(0,-30)
end_point = start_point + (-7,20)
# make the anti-clockwise quarbend
first_AQuarBend = AQuarBend(start_point,end_point,width=0.5)
# draw the anti-clockwise quarbend on the layout
first_AQuarBend.draw(cell,wg_layer)

################################# polygon example #################################
# points for the polygon
pointlist = [Point(30,-30) ,Point(30,-25),Point(37,-20),Point(33,-27),Point(32,-28),Point(31,-29)] ## or [(30,-30),(30,-25),(37,-20),(33,-27),(32,-28),(31,-29)]
# make the polygon
polygon = Polygon(pointlist)
# draw the polygon on the layout
polygon.draw(cell,wg_layer)

################################# add drop microring example #################################
# start point(input point) for the microring, and radius, gap, waveguide width, coupling length
start_point = Point(50,40)
radius = 5.1973
gap = 0.18
wg_width = 0.45
coupling_length = 5.5
# make the add drop microring
first_ring = AddDropMicroring(start_point,radius,gap,wg_width,coupling_length)
# drawe the microring on the layout
first_ring.draw(cell,wg_layer)
# add heater for the microring
first_ring.add_heater(cell, heater_layer, contact=1, contact_layer=contact_layer)


################################# flat coupling microring example #################################
# start point(input point) for the microring, and radius, gap, waveguide width, coupling length
start_point = Point(50,-300)
radius = 5.1973
gap = 0.18
wg_width = 0.45
coupling_length = 5.5
# make the add drop microring
second_ring = AddDropMicroringFlat(start_point,radius,gap,wg_width,coupling_length)
# draw the microring on the layout
second_ring.draw(cell,wg_layer)
# add heater for the microring
second_ring.add_heater(cell, heater_layer, contact=1, contact_layer=contact_layer)


################################# doubleconnector example #################################
# start point and end point for the doubleconnector
double_connect_start_point = Point(60,-30)
double_connect_end_point = double_connect_start_point + (20,10)
# make the doubleconnector
connector = DoubleBendConnector(double_connect_start_point, double_connect_end_point, width=0.5)
# draw the doubleconnector on the layout
connector.draw(cell,wg_layer)

################################# text example #################################
# start point for the text
text_start_point = Point(0,-60)
# make the text
text = Text(text_start_point,"OTIP2021")
# draw the text on the layout
text.draw(cell,wg_layer)

################################# AEMD grating example #################################
# get a AEMD grating definition
AEMDgrating = MAKE_AEMD_GRATING(port_width=0.5)
# start point for the AEMD grating
grating_point = Point(90,-30)
# make the AEMD grating
right_grating = AEMDgrating(grating_point,RIGHT)
# draw the AEMD grating on the layout
right_grating.draw(cell)

################################# self define component example #################################
# take the "selfdefine.gds" as an example
SelfDefineComponent = MAKE_COMPONENT("selfdefine.gds")
# start point for the component
start_point = Point(0,-90)
# make the component
component = SelfDefineComponent(start_point,RIGHT)
# draw the component on the layout
component.draw(cell)

#############################################################################################################
############################################## make gdsii file ##############################################
#############################################################################################################
# create file and save
make_gdsii_file("basic.gds")
# create file and save the layout with an inverse layer
make_gdsii_file("basic_inverse.gds",inv_source_layer=wg_layer,inv_target_layer=inv_layer)
# create file and save the layout with inverse layer and cover layer
make_gdsii_file("basic_inverse_and_cover.gds",inv_source_layer=wg_layer,inv_target_layer=inv_layer,cover_source_layer=wg_layer,cover_target_layer=cover_layer)