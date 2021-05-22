######################################################################################################################
## File Name: utils.py
## Author: Zhenyu ZHAO
## Date: 2021.05.22
## Description: Basic Definitions for SPLayout(Silicon Photonics Layout Design Tools)
######################################################################################################################
import gdspy
import math

## "macros"
FROM_LEFT_TO_RIGHT = 0
FROM_UP_TO_DOWN = 1
LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

## global parameters
grating_number = 1

class Point:
    '''
    Point Definiton in SPLayout
    Points descript the 2D coordinate in a layout.
    x: x-coordinate, unit: μm
    y: y-coordinate, unit: μm
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def to_tuple(self):
        '''
        Convert Point into Tuple
        :return: a tuple
        '''
        return (self.x, self.y)

    def get_percent_point(self,others,percent = 0.5):
        '''
        Derive the point on the connection line of the point and the other point
        :param others: another point
        :param percent: the distance rate from the start point compared with the whole distance
        :return: the center point
        '''
        return Point((others.x + self.x)*percent, (others.y + self.y)*percent)

    def get_relative_angle(self,other): ## ! -pi to pi
        '''
        Derive the relative angle with another point as a ring center point
        :param other: the reference center point
        :return: the relative point
        '''
        angle = math.atan( (self.y - other.y)/(self.x - other.x))
        return angle


class Waveguide:
    """
    Waveguide Definiton in SPLayout
    start_point: start point
    end_point: end point
    width: width of the waveguide, unit: μm
    """
    def __init__(self, start_point, end_point, width):
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Waveguide Parameter!")
        self.start_point = start_point
        self.end_point = end_point
        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical waveguide
            self.down_left_x = start_point.x - width / 2
            self.down_left_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.up_right_x = end_point.x + width / 2
            self.up_right_y = end_point.y if (start_point.y < end_point.y) else start_point.y
        else:  ## parallel waveguide
            self.down_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.down_left_y = start_point.y - width / 2
            self.up_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.up_right_y = end_point.y + width / 2

    def draw(self, cell, layer):
        '''
        Draw the Component on Layout
        :param cell:
        :param layer:
        :return:
        '''
        if (self.ifexist):
            cell.add(
                gdspy.Rectangle((self.down_left_x, self.down_left_y), (self.up_right_x, self.up_right_y),
                                layer=layer))
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point



class Bend:
    """
    Bend Definiton in SPLayout
    center point: center point of the based ring
    start angle: start angle
    end angle: end angle
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    """
    def __init__(self,center_point, start_angle, end_angle, width , radius):
        self.center_point = center_point
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.width = width
        self.radius = radius
        self.start_point = Point(self.center_point.x + radius*math.cos(start_angle),
                                 self.center_point.y + radius*math.sin(start_angle))
        self.end_point = Point(self.center_point.x + radius * math.cos(end_angle),
                                 self.center_point.y + radius * math.sin(end_angle))

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        cell.add(gdspy.Round(
            (self.center_point.x, self.center_point.y),
            self.radius + self.width/2,
            inner_radius=self.radius - self.width/2,
            initial_angle=self.start_angle,
            final_angle=self.end_angle,
            tolerance=0.01,
            number_of_points = 1000,
            layer=layer,
        ))
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point


## anticlockwise
class AQuarBend:
    '''
    Anticlockwise Connector Definiton in SPLayout with Dual Waveguide and a 90-degree Bend
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    '''
    def __init__(self,start_point,end_point,width,radius=5):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.width = width

        if (start_point.x < end_point.x and start_point.y > end_point.y): ## left down type
            if (end_point.x - start_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y + self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x + self.radius, end_point.y + self.radius), math.pi, math.pi*3/2, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x + self.radius,end_point.y),end_point ,self.width)

        if (start_point.x < end_point.x and start_point.y < end_point.y): ## right down type
            if (end_point.x - start_point.x < self.radius) or (end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x - self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x - self.radius, start_point.y + self.radius), -math.pi/2, 0 , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y + self.radius),end_point ,self.width)

        if (start_point.x > end_point.x and start_point.y < end_point.y):  ## right up type
            if (start_point.x - end_point.x < self.radius) or (
                    end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point, Point(start_point.x, end_point.y - self.radius), self.width)
            self.center_bend = Bend(Point(start_point.x - self.radius, end_point.y - self.radius), 0 , math.pi / 2,
                                    self.width, self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x - self.radius, end_point.y), end_point, self.width)


        if (start_point.x > end_point.x and start_point.y > end_point.y): ## left up type
            if (start_point.x - end_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x + self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x + self.radius, start_point.y - self.radius), math.pi/2, math.pi, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y - self.radius),end_point ,self.width)

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_waveguide.draw(cell,layer)
        self.center_bend.draw(cell,layer)
        self.second_waveguide.draw(cell,layer)
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point


class QuarBend:
    '''
    Clockwise Connector Definiton in SPLayout with Dual Waveguide and a 90-degree Bend
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    '''
    def __init__(self,start_point,end_point,width,radius=5):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.width = width

        if (start_point.x < end_point.x and start_point.y > end_point.y): ## right up type
            if (end_point.x - start_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(end_point.x - self.radius,start_point.y),self.width)
            self.center_bend = Bend(Point(end_point.x - self.radius, start_point.y - self.radius), 0, math.pi/2, self.width , self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x,start_point.y - self.radius),end_point ,self.width)

        if (start_point.x < end_point.x and start_point.y < end_point.y): ## left up type
            if (end_point.x - start_point.x < self.radius) or (end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y - self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x + self.radius, end_point.y - self.radius), math.pi/2, math.pi , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x + self.radius,end_point.y),end_point ,self.width)

        if (start_point.x > end_point.x and start_point.y < end_point.y):  ## down left type
            if (start_point.x - end_point.x < self.radius) or (
                    end_point.y - start_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point, Point(end_point.x + self.radius, start_point.y), self.width)
            self.center_bend = Bend(Point(end_point.x + self.radius, start_point.y + self.radius), math.pi , math.pi*3 / 2,
                                    self.width, self.radius)
            self.second_waveguide = Waveguide(Point(end_point.x, start_point.y + self.radius), end_point, self.width)


        if (start_point.x > end_point.x and start_point.y > end_point.y): ## right down type
            if (start_point.x - end_point.x < self.radius) or (start_point.y - end_point.y < self.radius):
                raise Exception("Distance between two point is too short!")
            self.first_waveguide = Waveguide(start_point,Point(start_point.x,end_point.y + self.radius),self.width)
            self.center_bend = Bend(Point(start_point.x - self.radius, end_point.y + self.radius),  - math.pi/2, 0 , self.width , self.radius)
            self.second_waveguide = Waveguide(Point(start_point.x - self.radius,end_point.y),end_point ,self.width)

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_waveguide.draw(cell,layer)
        self.center_bend.draw(cell,layer)
        self.second_waveguide.draw(cell,layer)
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point

class AddDropMicroring:
    '''
    AddDropMicroring Definiton in SPLayout with Dual Coupling Waveguide and a Microring
    start point: the input port point of the microring
    radius: radius of the bend, unit: μm
    gap: the gap between microring and coupling waveguide, unit: μm
    wg_width: width of the waveguide, unit: μm
    coupling_length: the coupling length between coupling waveguide and the microring, unit: μm
    dirction: the component direction
    '''
    def __init__(self,start_point,radius,gap,wg_width,coupling_length,direction = FROM_LEFT_TO_RIGHT):
        self.start_point = start_point
        self.radius = radius
        self.gap = gap
        self.width = wg_width
        self.coupling_length = coupling_length
        ## force limit
        if (self.coupling_length == 0):
            self.coupling_length = 0.001
        self.direction = direction
        self.default_bend_radius = 5

        if self.direction == FROM_LEFT_TO_RIGHT:
            self.coupling_angle = self.coupling_length / self.radius
            # print("coupling angle degree:",self.coupling_angle * 180 / math.pi) ## for test
            if (self.coupling_angle >= math.pi*2/3):
                raise Exception("Coupling Length Too Long!")

            ## input bend
            self.input_bend = Bend(Point(start_point.x,start_point.y + self.default_bend_radius), - math.pi / 2 , - math.pi / 2 + self.coupling_angle/2,
                                    self.width, self.default_bend_radius)
            self.input_point = self.start_point

            # print("input bend end:", self.input_bend.get_end_point().x) ## for test


            ## up coupling bend
            ring_center_x = self.start_point.x + self.default_bend_radius*math.sin(self.coupling_angle/2) + (self.radius + self.width + self.gap)*math.sin(self.coupling_angle/2)
            ring_center_y = self.start_point.y + self.default_bend_radius*( 1- math.cos(self.coupling_angle/2) ) - (self.radius + self.width + self.gap)*math.cos(self.coupling_angle/2)
            self.ring_center = Point(ring_center_x,ring_center_y)
            self.up_coupling_bend = Bend(self.ring_center,  math.pi / 2 - self.coupling_angle/2,  math.pi / 2 + self.coupling_angle/2,
                                    self.width, (self.radius + self.width + self.gap))

            # print("up coupling bend end:", self.up_coupling_bend.get_end_point().y)  ## for test
            # print("up coupling bend start:", self.up_coupling_bend.get_end_point().x)  ## for test

            ## through bend
            up_coupling_bend_right_point = self.up_coupling_bend.get_start_point()
            self.through_bend = Bend(Point(up_coupling_bend_right_point.x + self.default_bend_radius*math.sin(self.coupling_angle/2), start_point.y + self.default_bend_radius), - math.pi / 2- self.coupling_angle / 2,
                                   - math.pi / 2 ,
                                   self.width, self.default_bend_radius)

            self.through_point = self.through_bend.get_end_point()

            ## Ring
            self.ring = Bend(self.ring_center, 0 ,
                                    math.pi * 2,
                                   self.width, self.radius)

            ## down coupling bend
            self.down_coupling_bend = Bend(self.ring_center, -math.pi / 2 - self.coupling_angle / 2,
                                         -math.pi / 2 + self.coupling_angle / 2,
                                         self.width, (self.radius + self.width + self.gap))

            ## drop bend
            down_coupling_bend_left_point = self.down_coupling_bend.get_start_point()
            self.drop_bend = Bend(Point(down_coupling_bend_left_point.x - self.default_bend_radius*math.sin(self.coupling_angle/2), down_coupling_bend_left_point.y - self.default_bend_radius*math.cos(self.coupling_angle/2)), math.pi / 2 -  self.coupling_angle / 2,
                                    math.pi / 2 ,
                                   self.width, self.default_bend_radius)

            self.drop_point = self.drop_bend.get_end_point()

            ## add bend
            down_coupling_bend_right_point = self.down_coupling_bend.get_end_point()
            self.add_bend = Bend(
                Point(down_coupling_bend_right_point.x + self.default_bend_radius * math.sin(self.coupling_angle / 2),
                      down_coupling_bend_right_point.y - self.default_bend_radius * math.cos(self.coupling_angle / 2)),
                math.pi / 2,
                math.pi / 2 + self.coupling_angle / 2,
                self.width, self.default_bend_radius)

            self.add_point = self.add_bend.get_start_point()

        elif self.direction == FROM_UP_TO_DOWN:
            raise Exception("Unfinished Function!")
        else:
            raise Exception("Unfinished Function!")

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.input_bend.draw(cell,layer)
        self.up_coupling_bend.draw(cell,layer)
        self.through_bend.draw(cell,layer)
        self.ring.draw(cell, layer)
        self.down_coupling_bend.draw(cell, layer)
        self.drop_bend.draw(cell, layer)
        self.add_bend.draw(cell, layer)
        return self.input_point, self.through_point,self.drop_point,self.add_point

    def add_heater(self,cell,heater_layer,heater_angle = math.pi/2, heater_width = 2, connect_pad_width = 14, bus_width = 4 , contact = 1 , contact_layer = 4,contact_width = 150,contact_bus_width = 10,contact_position = UP):
        '''
        Add a heater for the microring
        :param cell:
        :param heater_layer:
        :param heater_angle:
        :param heater_width:
        :param connect_pad_width:
        :param bus_width:
        :param contact:
        :param contact_layer:
        :param contact_width:
        :param contact_bus_width:
        :param contact_position:
        :return:
        '''
        if self.direction != FROM_LEFT_TO_RIGHT:
            raise Exception("Unfinished Function!")


        left_connect_start_point = Point(self.start_point.x - 5,self.start_point.y + 10)
        coupling_start_point = Point(self.start_point.x - 5,self.start_point.y)
        right_connect_start_point = Point(self.through_point.x + 5,self.through_point.y + 10)
        coupling_end_point = Point(self.through_point.x + 5, self.through_point.y)

        ## heater left connector
        relative_angle_left_up = coupling_start_point.get_relative_angle(self.ring_center) + math.pi
        heater_left_bend = Bend(self.ring_center, relative_angle_left_up, math.pi + heater_angle / 2, heater_width,
                                self.radius)
        heater_left_bend.draw(cell, heater_layer)

        pass_point = [left_connect_start_point.to_tuple(), coupling_start_point.to_tuple(),heater_left_bend.get_start_point().to_tuple()]
        heater_left_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True , layer=heater_layer
        )
        cell.add(heater_left_connector)

        ## left PAD
        left_PAD_center_x = left_connect_start_point.x
        left_PAD_center_y = left_connect_start_point.y
        left_pad = Waveguide(Point(left_PAD_center_x ,left_PAD_center_y- connect_pad_width/2),Point(left_PAD_center_x ,left_PAD_center_y + connect_pad_width/2),connect_pad_width)
        left_pad.draw(cell, heater_layer)
        # if (contact):
        #     left_pad.draw(cell, contact_layer)
        left_pad.draw(cell, contact_layer)

        ## link to contact
        if (contact):
            left_contact_point_x = left_PAD_center_x - 150 if contact_position == UP else left_PAD_center_x - 150
            left_contact_point_y = left_PAD_center_y + 150 if contact_position == UP else left_PAD_center_y - 150
            left_contact = Waveguide(Point(left_contact_point_x, left_contact_point_y - contact_width / 2),
                                 Point(left_contact_point_x, left_contact_point_y + contact_width / 2), contact_width)
            left_contact.draw(cell, contact_layer)

            contact_link = QuarBend(Point(left_PAD_center_x ,left_PAD_center_y),Point(left_contact_point_x,left_contact_point_y),contact_bus_width)
            contact_link.draw(cell, contact_layer)


        ## right PAD
        right_PAD_center_x = right_connect_start_point.x
        right_PAD_center_y = right_connect_start_point.y
        right_pad = Waveguide(Point(right_PAD_center_x, right_PAD_center_y - connect_pad_width / 2),
                             Point(right_PAD_center_x, right_PAD_center_y + connect_pad_width / 2), connect_pad_width)
        right_pad.draw(cell, heater_layer)
        # if (contact):
        #     right_pad.draw(cell, contact_layer)
        right_pad.draw(cell, contact_layer)

        ## link to contact
        if (contact):
            right_contact_point_x = right_PAD_center_x + 150 if contact_position == UP else right_PAD_center_x + 150
            right_contact_point_y = right_PAD_center_y + 150 if contact_position == UP else right_PAD_center_y - 150
            right_contact = Waveguide(Point(right_contact_point_x, right_contact_point_y - contact_width / 2),
                                     Point(right_contact_point_x, right_contact_point_y + contact_width / 2), contact_width)
            right_contact.draw(cell, contact_layer)

            contact_link = AQuarBend(Point(right_PAD_center_x, right_PAD_center_y),
                                    Point(right_contact_point_x, right_contact_point_y), contact_bus_width)
            contact_link.draw(cell, contact_layer)


        ## heater right connector
        relative_angle_right_up = coupling_end_point.get_relative_angle(self.ring_center)
        heater_right_bend = Bend(self.ring_center, -heater_angle/2, relative_angle_right_up, heater_width,
                                self.radius)
        heater_right_bend.draw(cell, heater_layer)

        pass_point = [right_connect_start_point.to_tuple(), coupling_end_point.to_tuple(),
                      heater_right_bend.get_end_point().to_tuple()]
        heater_right_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True, layer=heater_layer
        )
        cell.add(heater_right_connector)

        ## pass connect
        left_bend_end_point = heater_left_bend.get_end_point()
        left_bend_end_point = Point(left_bend_end_point.x + 0.6*math.cos(left_bend_end_point.get_relative_angle(self.ring_center) + math.pi), left_bend_end_point.y+ 0.6*math.sin(left_bend_end_point.get_relative_angle(self.ring_center) + math.pi))
        pass_left_point = left_bend_end_point.get_percent_point(self.ring_center, 0.5)
        right_bend_end_point = heater_right_bend.get_start_point()
        right_bend_end_point = Point(right_bend_end_point.x + 0.6*math.cos(right_bend_end_point.get_relative_angle(self.ring_center)), right_bend_end_point.y+ 0.6*math.sin(right_bend_end_point.get_relative_angle(self.ring_center)))
        pass_right_point = right_bend_end_point.get_percent_point(self.ring_center, 0.5)

        pass_point = [left_bend_end_point.to_tuple(), pass_left_point.to_tuple(),pass_right_point.to_tuple(), right_bend_end_point.to_tuple()]
        pass_connector = gdspy.FlexPath(
            pass_point, width=heater_width, gdsii_path=True, layer=heater_layer
        )
        cell.add(pass_connector)

    def get_input_point(self):
        '''
        Derive the input port point of the microring
        :return: input port point
        '''
        return  self.input_point

    def get_through_point(self):
        '''
        Derive the through port point of the through port
        :return: through port point
        '''
        return  self.through_point

    def get_drop_point(self):
        '''
        Derive the drop port point of the drop point
        :return: drop port point
        '''
        return  self.drop_point

    def get_add_point(self):
        '''
        Derive the add port point of the add point
        :return: add port point
        '''
        return  self.add_point

class AEMDgrating():
    '''
    AEMDgrating Definiton in SPLayout
    start point: the input port point of the grating (grating waveguide width: 0.5μm !!!)
    relative_position: the relative position of the grating according to the device layout
    '''
    def __init__(self,start_point,relative_position):
        global grating_number
        self.start_point = start_point
        self.grating_cell = gdspy.Cell("gratings%i" % grating_number)
        if (relative_position == LEFT):
            self.grating_cell.add(gdspy.GdsLibrary(infile = "AEMD_Grating_Left.gds").top_level()[0].copy("gratings %i" % grating_number, deep_copy=False, translation=(start_point.x, start_point.y)))
            grating_number += 1
        elif (relative_position == RIGHT):
            self.grating_cell.add(gdspy.GdsLibrary(infile="AEMD_Grating_Right.gds").top_level()[0].copy("gratings %i" % grating_number, deep_copy=False, translation=(start_point.x, start_point.y)))
            grating_number += 1
        elif (relative_position == UP):
            self.grating_cell.add(gdspy.GdsLibrary(infile="AEMD_Grating_Up.gds").top_level()[0].copy("gratings %i" % grating_number, deep_copy=False, translation=(start_point.x, start_point.y)))
            grating_number += 1
        elif (relative_position == DOWN):
            self.grating_cell.add(gdspy.GdsLibrary(infile="AEMD_Grating_Down.gds").top_level()[0].copy("gratings %i" % grating_number, deep_copy=False, translation=(start_point.x, start_point.y)))
            grating_number += 1
        else:
            raise Exception("Wrong Grating Relative Direction!")

    def draw(self,cell,*args):
        '''
        Draw the Component on the layout
        :param cell:
        :param args:
        :return:
        '''
        cell.add(self.grating_cell)
        return self.start_point


class Taper():
    '''
    Taper Definiton in SPLayout
    start point: start point
    end point: end point
    start_width: the width of the start port
    end_width: the width of the end port
    '''
    def __init__(self, start_point, end_point, start_width,end_width):
        if start_point.x != end_point.x and start_point.y != end_point.y:
            raise Exception("Invalid Taper Parameter!")
        self.start_point = start_point
        self.end_point = end_point

        if (start_point == end_point):
            self.ifexist = 0
        else:
            self.ifexist = 1
        if start_point.x == end_point.x:  ## vertical taper
            if (math.fabs(start_point.y - end_point.y) < 5):
                raise Exception("Taper Too Short!")
            self.down_left_x = start_point.x - start_width / 2 if (start_point.y < end_point.y) else start_point.x - end_width / 2
            self.down_left_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.down_right_x = start_point.x + start_width / 2 if (start_point.y < end_point.y) else start_point.x + end_width / 2
            self.down_right_y = start_point.y if (start_point.y < end_point.y) else end_point.y
            self.up_right_x = end_point.x + end_width / 2 if (start_point.y < end_point.y) else start_point.x + start_width / 2
            self.up_right_y = end_point.y if (start_point.y < end_point.y) else start_point.y
            self.up_left_x = end_point.x - end_width / 2 if (start_point.y < end_point.y) else start_point.x - start_width / 2
            self.up_left_y = end_point.y if (start_point.y < end_point.y) else start_point.y
        else:  ## parallel waveguide
            if (math.fabs(start_point.x - end_point.x) < 5):
                raise Exception("Taper Too Short!")
            self.down_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.down_left_y = start_point.y - start_width / 2 if (start_point.x < end_point.x) else end_point.y - end_width / 2
            self.down_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.down_right_y = end_point.y - end_width / 2  if (start_point.x < end_point.x) else start_point.y - start_width / 2
            self.up_right_x = end_point.x if (start_point.x < end_point.x) else start_point.x
            self.up_right_y = end_point.y + end_width / 2 if (start_point.x < end_point.x) else start_point.y + start_width / 2
            self.up_left_x = start_point.x if (start_point.x < end_point.x) else end_point.x
            self.up_left_y = start_point.y + start_width / 2 if (start_point.x < end_point.x) else end_point.y + end_width / 2

    def draw(self, cell, layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        taper_pts = [(self.down_left_x,self.down_left_y),(self.down_right_x,self.down_right_y),
                     (self.up_right_x,self.up_right_y),(self.up_left_x,self.up_left_y)]
        if (self.ifexist):
            cell.add(
                gdspy.Polygon(taper_pts,
                                layer=layer))
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point


class Polygon:
    '''
    Polygon Definiton in SPLayout
    point_list:  point list of the polygon, type: tuple list or Point list
    '''
    def __init__(self,point_list):
        self.point_list = []
        self.tuple_list = []
        for item in point_list:
            if type(item) == Point:
                self.tuple_list.append(item.to_tuple())
                self.point_list.append(item)
            elif type(item) == tuple:
                self.tuple_list.append(item)
                self.point_list.append(Point(item[0],item[1]))
            else:
                raise Exception("Polygon Wrong Type Input!")

    def draw(self, cell, layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        polygon = gdspy.Polygon(self.tuple_list)
        cell.add(polygon)
        return self.point_list

    def get_the_point_at_number(self,i):
        '''
        Derive the ith point of the polygon
        :param i:
        :return: the ith Point
        '''
        if (i >= len(self.point_list)):
            raise Exception("The Request Polygon Point not Exist!")
        return self.point_list[i]


class DoubleBendConnector:
    '''
    Double Bend Connector Definiton in SPLayout with Trible Waveguide and two 90-degree Bends
    start point: start point
    end point: end point
    width: width of the waveguide, unit: μm
    radius: radius of the bend, unit: μm
    xpercent: the center point position selection in x coordinate
    ypercent: the center point position selection in y coordinate
    '''
    def __init__(self,start_point,end_point,width,radius=5, xpercent = 0.5 , ypercent = 0.5):
        self.start_point = start_point
        self.end_point = end_point
        self.radius = radius
        self.x_percent = xpercent
        self.y_percent = ypercent
        self.center_point = Point(start_point.x + (end_point.x - start_point.x)*self.x_percent, start_point.y + (end_point.y - start_point.y)*self.y_percent)
        if (math.fabs(self.start_point.x - self.center_point.x) < self.radius or math.fabs(self.start_point.y - self.center_point.y) < self.radius
        or math.fabs(self.end_point.x - self.center_point.x) < self.radius or math.fabs(self.end_point.y - self.center_point.y) < self.radius):
            raise Exception("Two Points are too Near to Use DoubleBendConnector Or the Percent Need to be Adjusted!")

        if (self.start_point.x < self.end_point.x and self.start_point.y < self.end_point.y): ## up right type
            self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
            self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
        elif (self.start_point.x < self.end_point.x and self.start_point.y > self.end_point.y): ## down right type
            self.first_bend = QuarBend(self.start_point, self.center_point, width,self.radius)
            self.second_bend = AQuarBend(self.center_point, self.end_point, width,self.radius)
        elif (self.start_point.x > self.end_point.x and self.start_point.y > self.end_point.y): ## down left type
            self.first_bend = AQuarBend(self.start_point, self.center_point, width,self.radius)
            self.second_bend = QuarBend(self.center_point, self.end_point, width,self.radius)
        elif (self.start_point.x > self.end_point.x and self.start_point.y < self.end_point.y): ## up left type
            self.first_bend = QuarBend(self.start_point, self.center_point, width,self.radius)
            self.second_bend = AQuarBend(self.center_point, self.end_point, width,self.radius)
        else:
            raise Exception("Unexpected DoubleBendConnector Error!")

    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.first_bend.draw(cell,layer)
        self.second_bend.draw(cell,layer)
        return self.start_point, self.end_point

    def get_start_point(self):
        '''
        Derive the start point of the waveguide
        :return: the start point
        '''
        return  self.start_point

    def get_end_point(self):
        '''
        Derive the end point of the waveguide
        :return: the end point
        '''
        return  self.end_point


## run for test
if __name__ == "__main__":
    TEST_LAYER = 1
    testCell = gdspy.Cell("test")

    ##  test waveguide
    # start_point = Point(0,0)
    # wg_end_point = Point(0,5)
    # first_wg = Waveguide(start_point,wg_end_point,width=0.45)
    # first_wg.draw(testCell,TEST_LAYER)

    ## test bend
    # center_point = Point(0,0)
    # start_angle = math.pi*4/5
    # end_angle = math.pi*3/2
    # width = 0.4
    # radius = 5
    # first_bend = Bend(center_point, start_angle, end_angle, width , radius)
    # first_bend.draw(testCell,TEST_LAYER)


    ## test AQuarBend
    # start_point = Point(0,0)
    # end_point = Point(-7,10)
    # width = 0.4
    # first_AQuarBend = AQuarBend(start_point,end_point,width,5)
    # first_AQuarBend.draw(testCell,TEST_LAYER)


    ## test QuarBend
    # start_point = Point(0,0)
    # end_point = Point(-7,20)
    # width = 0.4
    # first_QuarBend = AQuarBend(start_point,end_point,width,5)
    # first_QuarBend.draw(testCell,TEST_LAYER)


    ## test AddDropMicroring
    # start_point = Point(0,0)
    # radius = 5.1973
    # gap = 0.18
    # wg_width = 0.45
    # coupling_length = 5.5
    # first_ring = AddDropMicroring(start_point,radius,gap,wg_width,coupling_length)
    # first_ring.draw(testCell,TEST_LAYER)

    ## taper test
    # taper_start_point = first_ring.get_through_point()
    # taper_start_point = Point(0,0)
    # taper_length = 5
    # taper_end_point = Point(taper_start_point.x+ taper_length,taper_start_point.y )
    # first_taper = Taper(taper_start_point,taper_end_point,0.45,0.8)
    # first_taper.draw(testCell,TEST_LAYER)

    ## grating test
    # grating_port = first_taper.get_end_point()
    # grating_port = Point(0,0)
    # right_grating = AEMDgrating(grating_port,RIGHT)
    # right_grating.draw(testCell)

    ## test Double Connect
    # double_connect_start_point = Point(0,0)
    # double_connect_end_point = Point(-20,40)
    # connector = DoubleBendConnector(double_connect_start_point, double_connect_end_point, width=1, xpercent=0.5)
    # connector.draw(testCell,TEST_LAYER)


    ## test Polygon
    pointlist = [Point(0,0),Point(0,1),Point(3,5),Point(3,-2)] ## or [(0,0),(0,1),(3,5),(3,-2)]
    polygon = Polygon(pointlist)
    polygon.draw(testCell,TEST_LAYER)



    filename = "test.gds"
    writer = gdspy.GdsWriter(filename, unit=1.0e-6, precision=1.0e-9)
    writer.write_cell(testCell)
    writer.close()