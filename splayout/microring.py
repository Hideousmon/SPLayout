from splayout.utils import *
from splayout.waveguide import Waveguide
from splayout.bend import Bend
from splayout.quarbend import AQuarBend,QuarBend

## global parameters
add_drop_microring_number = 0
add_drop_microring_heater_number = 0
add_drop_microring_flat_number = 0
add_drop_microring_flat_heater_number = 0

class AddDropMicroringFlat:
    '''
    AddDropMicroring Definiton in SPLayout with Dual Coupling Waveguide and a Microring
    start point: the input port point of the microring
    radius: radius of the bend, unit: μm
    gap: the gap between microring and coupling waveguide, unit: μm
    wg_width: width of the waveguide, unit: μm
    coupling_length: the coupling length between coupling waveguide and the microring, unit: μm
    dirction: the component direction
    '''
    def __init__(self,start_point,radius,gap,wg_width,coupling_length,relative_position = RIGHT):
        self.start_point = start_point
        self.radius = radius
        self.gap = gap
        self.width = wg_width
        self.coupling_length = coupling_length
        ## force limit
        if (self.coupling_length == 0):
            self.coupling_length = 0.001
        self.rotate_angle = relative_position
        self.default_bend_radius = 5

        global add_drop_microring_flat_number
        self.temp_cell = Cell("AddDropMicroringFlat" + str(add_drop_microring_flat_number))
        add_drop_microring_flat_number += 1


        self.coupling_angle = self.coupling_length / self.radius
        # print("coupling angle degree:",self.coupling_angle * 180 / math.pi) ## for test
        if (self.coupling_angle >= math.pi*2/3):
            raise Exception("Coupling Length Too Long!")

        ## up waveguide
        # self.input_point = self.start_point
        # self.through_point = Point(self.start_point.x + coupling_length,self.start_point.y)

        ## initialize the start point to Zero
        self.relative_input_point = Point(0,0)
        self.relative_through_point = Point(coupling_length, 0)


        self.up_waveguide = Waveguide(self.relative_input_point,self.relative_through_point,width=self.width)

        ## ring up waveguide
        ring_up_waveguide_start_point = Point(self.relative_input_point.x,self.relative_input_point.y - self.width - self.gap)
        ring_up_waveguide_end_point = Point(self.relative_input_point.x + self.coupling_length,self.relative_input_point.y - self.width - self.gap)
        self.ring_up_waveguide = Waveguide(ring_up_waveguide_start_point,ring_up_waveguide_end_point,width=self.width)

        ## calculate efficient radius
        self.eff_radius = (self.radius * math.pi * 2 - self.coupling_length*2) / (math.pi * 2)

        ## left half ring
        self.left_half_ring_center = Point(ring_up_waveguide_start_point.x, ring_up_waveguide_start_point.y -  self.eff_radius)
        self.left_half_ring = Bend(self.left_half_ring_center,math.pi/2,math.pi*3/2,width=self.width,radius=self.eff_radius)

        ## right half ring
        self.right_half_ring_center = Point(ring_up_waveguide_end_point.x,
                                      ring_up_waveguide_end_point.y - self.eff_radius)
        self.right_half_ring = Bend(self.right_half_ring_center, -math.pi / 2, math.pi / 2, width=self.width,
                                   radius=self.eff_radius)

        self.ring_center = Point((self.left_half_ring_center.x + self.right_half_ring_center.x)/2,self.left_half_ring_center.y)

        ## ring down waveguide
        ring_down_waveguide_start_point = Point(self.left_half_ring_center.x, self.left_half_ring_center.y - self.eff_radius)
        ring_down_waveguide_end_point = Point(self.right_half_ring_center.x,
                                            self.right_half_ring_center.y - self.eff_radius)
        self.ring_down_waveguide = Waveguide(ring_down_waveguide_start_point, ring_down_waveguide_end_point,
                                           width=self.width)

        ## down waveguide
        self.relative_drop_point = Point(ring_down_waveguide_start_point.x,
                                    ring_down_waveguide_start_point.y - self.width - self.gap)
        self.relative_add_point = Point(ring_down_waveguide_end_point.x,
                                   ring_down_waveguide_end_point.y - self.width - self.gap)
        self.down_waveguide = Waveguide(self.relative_drop_point, self.relative_add_point, width=self.width)

        ## calculate port with rotation

        if (self.rotate_angle == RIGHT):
            self.input_point = self.start_point
            self.through_point = self.start_point + self.relative_through_point
            self.drop_point = self.start_point + self.relative_drop_point
            self.add_point = self.start_point + self.relative_add_point
        elif (self.rotate_angle == UP):
            self.input_point = self.start_point
            self.through_point = self.start_point + Point(-self.relative_through_point.y,
                                                          self.relative_through_point.x)
            self.drop_point = self.start_point + Point(-self.relative_drop_point.y,
                                                       self.relative_drop_point.x)
            self.add_point = self.start_point + Point(-self.relative_add_point.y, self.relative_add_point.x)
        elif (self.rotate_angle == LEFT):
            self.input_point = self.start_point
            self.through_point = self.start_point + Point(-self.relative_through_point.x,
                                                          -self.relative_through_point.y)
            self.drop_point = self.start_point + Point(-self.relative_drop_point.x,
                                                       -self.relative_drop_point.y)
            self.add_point = self.start_point + Point(-self.relative_add_point.x,
                                                      -self.relative_add_point.y)
        elif (self.rotate_angle == DOWN):
            self.input_point = self.start_point
            self.through_point = self.start_point + Point(self.relative_through_point.y,
                                                          -self.relative_through_point.x)
            self.drop_point = self.start_point + Point(self.relative_drop_point.y,
                                                       -self.relative_drop_point.x)
            self.add_point = self.start_point + Point(self.relative_add_point.y,
                                                      -self.relative_add_point.x)
        else:
            raise  Exception("Wrong relative position!")

        ## prepare for the contact and pad position return
        self.left_contact_point = None
        self.right_contact_point = None
        self.left_pad_point = None
        self.right_pad_point = None




    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        self.up_waveguide.draw(self.temp_cell,layer)
        self.ring_up_waveguide.draw(self.temp_cell,layer)
        self.left_half_ring.draw(self.temp_cell,layer)
        self.right_half_ring.draw(self.temp_cell, layer)
        self.ring_down_waveguide.draw(self.temp_cell, layer)
        self.down_waveguide.draw(self.temp_cell, layer)

        ## rotate
        cell.cell.add(gdspy.CellReference(self.temp_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_angle))

        return self.input_point, self.through_point,self.drop_point,self.add_point

    def add_heater(self,cell,heater_layer,heater_angle = math.pi/2, heater_width = 2, connect_pad_width = 14, bus_width = 4 , contact = 0 , contact_layer =None,contact_width = 150,contact_bus_width = 10,contact_position = UP,open = 0, open_layer =None,open_width = 140,touch = 0,touch_layer = None):
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

        global add_drop_microring_flat_heater_number
        temp_heater_cell = Cell("AddDropMicroringFlatHeater" + str(add_drop_microring_flat_heater_number))
        add_drop_microring_flat_heater_number += 1

        left_connect_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y + 10)
        coupling_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y)
        right_connect_start_point = Point(self.relative_through_point.x + 10,self.relative_through_point.y + 10)
        coupling_end_point = Point(self.relative_through_point.x + 10, self.relative_through_point.y)

        ## heater left connector
        relative_angle_left_up = coupling_start_point.get_relative_angle(self.left_half_ring_center) + math.pi
        heater_left_bend = Bend(self.left_half_ring_center, relative_angle_left_up, math.pi + heater_angle / 2, heater_width,
                                self.eff_radius)
        heater_left_bend.draw(temp_heater_cell, heater_layer)

        pass_point = [left_connect_start_point.to_tuple(), coupling_start_point.to_tuple(),heater_left_bend.get_start_point().to_tuple()]
        heater_left_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True , layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(heater_left_connector)

        ## left PAD
        left_PAD_center_x = left_connect_start_point.x
        left_PAD_center_y = left_connect_start_point.y
        self.left_pad_point = Point(left_PAD_center_x,left_PAD_center_y)
        left_pad = Waveguide(Point(left_PAD_center_x ,left_PAD_center_y- connect_pad_width/2),Point(left_PAD_center_x ,left_PAD_center_y + connect_pad_width/2),connect_pad_width)
        left_pad.draw(temp_heater_cell, heater_layer)
        if (touch):
            if (touch_layer == None):
                raise  Exception("The touch layer should be ")
            left_pad.draw(temp_heater_cell, contact_layer)
            for i in range(0,16):
                for j in range(0,16):
                    touch_unit_x = left_PAD_center_x - 0.3*15 + 0.6*i
                    touch_unit_y = left_PAD_center_y - 0.3*15 + 0.6*j
                    touch_unit_width = 0.25
                    touch_unit = Waveguide(Point(touch_unit_x ,touch_unit_y- touch_unit_width/2),Point(touch_unit_x ,touch_unit_y + touch_unit_width/2),touch_unit_width)
                    touch_unit.draw(temp_heater_cell,touch_layer)
        ## link to contact
        if (contact):
            left_contact_point_x = left_PAD_center_x - 150 if contact_position == UP else left_PAD_center_x - 150
            left_contact_point_y = left_PAD_center_y + 150 if contact_position == UP else left_PAD_center_y - 150
            self.left_contact_point = Point(left_contact_point_x, left_contact_point_y)
            left_contact = Waveguide(Point(left_contact_point_x, left_contact_point_y - contact_width / 2),
                                 Point(left_contact_point_x, left_contact_point_y + contact_width / 2), contact_width)
            left_contact.draw(temp_heater_cell, contact_layer)
            if (open):
                left_open = Waveguide(Point(left_contact_point_x, left_contact_point_y - open_width / 2),
                                 Point(left_contact_point_x, left_contact_point_y + open_width / 2), open_width)
                left_open.draw(temp_heater_cell, open_layer)

            contact_link = QuarBend(Point(left_PAD_center_x ,left_PAD_center_y),Point(left_contact_point_x,left_contact_point_y),contact_bus_width)
            contact_link.draw(temp_heater_cell, contact_layer)


        ## right PAD
        right_PAD_center_x = right_connect_start_point.x
        right_PAD_center_y = right_connect_start_point.y
        self.right_pad_point = Point(right_PAD_center_x,right_PAD_center_y)
        right_pad = Waveguide(Point(right_PAD_center_x, right_PAD_center_y - connect_pad_width / 2),
                             Point(right_PAD_center_x, right_PAD_center_y + connect_pad_width / 2), connect_pad_width)
        right_pad.draw(temp_heater_cell, heater_layer)
        if (touch):
            right_pad.draw(temp_heater_cell, contact_layer)
            for i in range(0,16):
                for j in range(0,16):
                    touch_unit_x = right_PAD_center_x - 0.3*15 + 0.6*i
                    touch_unit_y = right_PAD_center_y - 0.3*15 + 0.6*j
                    touch_unit_width = 0.25
                    touch_unit = Waveguide(Point(touch_unit_x ,touch_unit_y- touch_unit_width/2),Point(touch_unit_x ,touch_unit_y + touch_unit_width/2),touch_unit_width)
                    touch_unit.draw(temp_heater_cell, touch_layer)

        ## link to contact
        if (contact):
            right_contact_point_x = right_PAD_center_x + 150 if contact_position == UP else right_PAD_center_x + 150
            right_contact_point_y = right_PAD_center_y + 150 if contact_position == UP else right_PAD_center_y - 150
            self.right_contact_point = Point(right_contact_point_x,right_contact_point_y)
            right_contact = Waveguide(Point(right_contact_point_x, right_contact_point_y - contact_width / 2),
                                     Point(right_contact_point_x, right_contact_point_y + contact_width / 2), contact_width)
            right_contact.draw(temp_heater_cell, contact_layer)

            if (open):
                left_open = Waveguide(Point(right_contact_point_x, right_contact_point_y - open_width / 2),
                                 Point(right_contact_point_x, right_contact_point_y + open_width / 2), open_width)
                left_open.draw(temp_heater_cell, open_layer)

            contact_link = AQuarBend(Point(right_PAD_center_x, right_PAD_center_y),
                                    Point(right_contact_point_x, right_contact_point_y), contact_bus_width)
            contact_link.draw(temp_heater_cell, contact_layer)


        ## heater right connector
        relative_angle_right_up = coupling_end_point.get_relative_angle(self.right_half_ring_center)
        heater_right_bend = Bend(self.right_half_ring_center, -heater_angle/2, relative_angle_right_up, heater_width,
                                self.eff_radius)
        heater_right_bend.draw(temp_heater_cell, heater_layer)

        pass_point = [right_connect_start_point.to_tuple(), coupling_end_point.to_tuple(),
                      heater_right_bend.get_end_point().to_tuple()]
        heater_right_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(heater_right_connector)

        ## pass connect
        left_bend_end_point = heater_left_bend.get_end_point()
        left_bend_end_point = Point(left_bend_end_point.x + 0.6*math.cos(left_bend_end_point.get_relative_angle(self.left_half_ring_center) + math.pi), left_bend_end_point.y+ 0.6*math.sin(left_bend_end_point.get_relative_angle(self.ring_center) + math.pi))
        pass_left_point = left_bend_end_point.get_percent_point(self.left_half_ring_center, 0.5)
        right_bend_end_point = heater_right_bend.get_start_point()
        right_bend_end_point = Point(right_bend_end_point.x + 0.6*math.cos(right_bend_end_point.get_relative_angle(self.right_half_ring_center)), right_bend_end_point.y+ 0.6*math.sin(right_bend_end_point.get_relative_angle(self.ring_center)))
        pass_right_point = right_bend_end_point.get_percent_point(self.right_half_ring_center, 0.5)

        pass_point = [left_bend_end_point.to_tuple(), pass_left_point.to_tuple(),pass_right_point.to_tuple(), right_bend_end_point.to_tuple()]
        pass_connector = gdspy.FlexPath(
            pass_point, width=heater_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(pass_connector)

        ## rotate
        cell.cell.add(gdspy.CellReference(temp_heater_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_angle))

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

    def get_left_contact_point(self):
        if (self.left_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            return self.left_contact_point

    def get_right_contact_point(self):
        if (self.right_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            return self.right_contact_point

    def get_left_pad_point(self):
        if (self.left_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            return self.left_pad_point

    def get_right_pad_point(self):
        if (self.right_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            return self.right_pad_point



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
    def __init__(self,start_point,radius,gap,wg_width,coupling_length,relative_position = RIGHT):
        self.start_point = start_point
        self.radius = radius
        self.gap = gap
        self.width = wg_width
        self.coupling_length = coupling_length
        ## force limit
        if (self.coupling_length == 0):
            self.coupling_length = 0.001
        self.rotate_angle = relative_position
        self.default_bend_radius = 5

        global add_drop_microring_number
        self.temp_cell = Cell("AddDropMicroring"+str(add_drop_microring_number))
        add_drop_microring_number += 1

        ## initialize the input point to Zero
        self.relative_input_point = Point(0,0)

        self.coupling_angle = self.coupling_length / self.radius
        # print("coupling angle degree:",self.coupling_angle * 180 / math.pi) ## for test
        if (self.coupling_angle >= math.pi*2/3):
            raise Exception("Coupling Length Too Long!")

        ## input bend
        self.input_bend = Bend(Point(self.relative_input_point.x,self.relative_input_point.y + self.default_bend_radius), - math.pi / 2 , - math.pi / 2 + self.coupling_angle/2,
                                self.width, self.default_bend_radius)


        # print("input bend end:", self.input_bend.get_end_point().x) ## for test


        ## up coupling bend
        ring_center_x = self.relative_input_point.x + self.default_bend_radius*math.sin(self.coupling_angle/2) + (self.radius + self.width + self.gap)*math.sin(self.coupling_angle/2)
        ring_center_y = self.relative_input_point.y + self.default_bend_radius*( 1- math.cos(self.coupling_angle/2) ) - (self.radius + self.width + self.gap)*math.cos(self.coupling_angle/2)
        self.ring_center = Point(ring_center_x,ring_center_y)
        self.up_coupling_bend = Bend(self.ring_center,  math.pi / 2 - self.coupling_angle/2,  math.pi / 2 + self.coupling_angle/2,
                                self.width, (self.radius + self.width + self.gap))

        # print("up coupling bend end:", self.up_coupling_bend.get_end_point().y)  ## for test
        # print("up coupling bend start:", self.up_coupling_bend.get_end_point().x)  ## for test

        ## through bend
        up_coupling_bend_right_point = self.up_coupling_bend.get_start_point()
        self.through_bend = Bend(Point(up_coupling_bend_right_point.x + self.default_bend_radius*math.sin(self.coupling_angle/2), self.relative_input_point.y + self.default_bend_radius), - math.pi / 2- self.coupling_angle / 2,
                               - math.pi / 2 ,
                               self.width, self.default_bend_radius)



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



        ## add bend
        down_coupling_bend_right_point = self.down_coupling_bend.get_end_point()
        self.add_bend = Bend(
            Point(down_coupling_bend_right_point.x + self.default_bend_radius * math.sin(self.coupling_angle / 2),
                  down_coupling_bend_right_point.y - self.default_bend_radius * math.cos(self.coupling_angle / 2)),
            math.pi / 2,
            math.pi / 2 + self.coupling_angle / 2,
            self.width, self.default_bend_radius)

        ## get relative points
        self.relative_through_point = self.through_bend.get_end_point()
        self.relatvie_drop_point = self.drop_bend.get_end_point()
        self.relatvie_add_point = self.add_bend.get_start_point()



        ## calculate port with rotation
        if (self.rotate_angle == RIGHT):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + self.relative_through_point
            self.drop_point = self.start_point + self.relatvie_drop_point
            self.add_point = self.start_point + self.relatvie_add_point
        elif (self.rotate_angle == UP):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + Point(-self.relative_through_point.y,self.relative_through_point.x)
            self.drop_point = self.start_point + Point(-self.relatvie_drop_point.y,self.relatvie_drop_point.x)
            self.add_point = self.start_point + Point(-self.relatvie_add_point.y,self.relatvie_add_point.x)
        elif (self.rotate_angle == LEFT):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + Point(-self.relative_through_point.x,
                                                          -self.relative_through_point.y)
            self.drop_point = self.start_point + Point(-self.relatvie_drop_point.x,
                                                       -self.relatvie_drop_point.y)
            self.add_point = self.start_point + Point(-self.relatvie_add_point.x, -self.relatvie_add_point.y)
        elif (self.rotate_angle == DOWN):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + Point(self.relative_through_point.y,
                                                          -self.relative_through_point.x)
            self.drop_point = self.start_point + Point(self.relatvie_drop_point.y,
                                                       -self.relatvie_drop_point.x)
            self.add_point = self.start_point + Point(self.relatvie_add_point.y,
                                                      -self.relatvie_add_point.x)
        else:
            raise  Exception("Wrong relative position!")

        ## prepare for the contact and pad position return
        self.left_contact_point = None
        self.right_contact_point = None
        self.left_pad_point = None
        self.right_pad_point = None




    def draw(self,cell,layer):
        '''
        Draw the Component on the layout
        :param cell:
        :param layer:
        :return:
        '''
        ## add all the component on the temp cell
        self.input_bend.draw(self.temp_cell,layer)
        self.up_coupling_bend.draw(self.temp_cell,layer)
        self.through_bend.draw(self.temp_cell,layer)
        self.ring.draw(self.temp_cell, layer)
        self.down_coupling_bend.draw(self.temp_cell, layer)
        self.drop_bend.draw(self.temp_cell, layer)
        self.add_bend.draw(self.temp_cell, layer)

        ## rotate
        cell.cell.add(gdspy.CellReference(self.temp_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_angle))
        return self.input_point, self.through_point,self.drop_point,self.add_point

    def add_heater(self,cell,heater_layer,heater_angle = math.pi/2, heater_width = 2, connect_pad_width = 14, bus_width = 4 , contact = 0 , contact_layer =None,contact_width = 150,contact_bus_width = 10,contact_position = UP,open = 0, open_layer =None,open_width = 140,touch = 0,touch_layer = None):
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

        global add_drop_microring_heater_number
        temp_heater_cell = Cell("AddDropMicroringHeater" + str(add_drop_microring_heater_number))
        add_drop_microring_heater_number += 1


        left_connect_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y + 10)
        coupling_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y)
        right_connect_start_point = Point(self.relative_through_point.x + 10,self.relative_through_point.y + 10)
        coupling_end_point = Point(self.relative_through_point.x + 10, self.relative_through_point.y)

        ## heater left connector
        relative_angle_left_up = coupling_start_point.get_relative_angle(self.ring_center) + math.pi
        heater_left_bend = Bend(self.ring_center, relative_angle_left_up, math.pi + heater_angle / 2, heater_width,
                                self.radius)
        heater_left_bend.draw(temp_heater_cell, heater_layer)

        pass_point = [left_connect_start_point.to_tuple(), coupling_start_point.to_tuple(),heater_left_bend.get_start_point().to_tuple()]
        heater_left_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True , layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(heater_left_connector)

        ## left PAD
        left_PAD_center_x = left_connect_start_point.x
        left_PAD_center_y = left_connect_start_point.y
        self.left_pad_point = Point(left_PAD_center_x,left_PAD_center_y)
        left_pad = Waveguide(Point(left_PAD_center_x ,left_PAD_center_y- connect_pad_width/2),Point(left_PAD_center_x ,left_PAD_center_y + connect_pad_width/2),connect_pad_width)
        left_pad.draw(temp_heater_cell, heater_layer)
        if (touch):
            if (touch_layer == None):
                raise Exception("The touch layer should be ")
            left_pad.draw(temp_heater_cell, contact_layer)
            for i in range(0, 16):
                for j in range(0, 16):
                    touch_unit_x = left_PAD_center_x - 0.3 * 15 + 0.6 * i
                    touch_unit_y = left_PAD_center_y - 0.3 * 15 + 0.6 * j
                    touch_unit_width = 0.25
                    touch_unit = Waveguide(Point(touch_unit_x, touch_unit_y - touch_unit_width / 2),
                                           Point(touch_unit_x, touch_unit_y + touch_unit_width / 2), touch_unit_width)
                    touch_unit.draw(temp_heater_cell, touch_layer)

        ## link to contact
        if (contact):
            left_contact_point_x = left_PAD_center_x - 150 if contact_position == UP else left_PAD_center_x - 150
            left_contact_point_y = left_PAD_center_y + 150 if contact_position == UP else left_PAD_center_y - 150
            self.left_contact_point = Point(left_contact_point_x,left_contact_point_y)
            left_contact = Waveguide(Point(left_contact_point_x, left_contact_point_y - contact_width / 2),
                                 Point(left_contact_point_x, left_contact_point_y + contact_width / 2), contact_width)
            left_contact.draw(temp_heater_cell, contact_layer)

            if (open):
                left_open = Waveguide(Point(left_contact_point_x, left_contact_point_y - open_width / 2),
                                 Point(left_contact_point_x, left_contact_point_y + open_width / 2), open_width)
                left_open.draw(temp_heater_cell, open_layer)

            contact_link = QuarBend(Point(left_PAD_center_x ,left_PAD_center_y),Point(left_contact_point_x,left_contact_point_y),contact_bus_width)
            contact_link.draw(temp_heater_cell, contact_layer)


        ## right PAD
        right_PAD_center_x = right_connect_start_point.x
        right_PAD_center_y = right_connect_start_point.y
        self.right_pad_point = Point(right_PAD_center_x,right_PAD_center_y)
        right_pad = Waveguide(Point(right_PAD_center_x, right_PAD_center_y - connect_pad_width / 2),
                             Point(right_PAD_center_x, right_PAD_center_y + connect_pad_width / 2), connect_pad_width)
        right_pad.draw(temp_heater_cell, heater_layer)
        if (touch):
            right_pad.draw(temp_heater_cell, contact_layer)
            for i in range(0, 16):
                for j in range(0, 16):
                    touch_unit_x = right_PAD_center_x - 0.3 * 15 + 0.6 * i
                    touch_unit_y = right_PAD_center_y - 0.3 * 15 + 0.6 * j
                    touch_unit_width = 0.25
                    touch_unit = Waveguide(Point(touch_unit_x, touch_unit_y - touch_unit_width / 2),
                                           Point(touch_unit_x, touch_unit_y + touch_unit_width / 2), touch_unit_width)
                    touch_unit.draw(temp_heater_cell, touch_layer)

        ## link to contact
        if (contact):
            right_contact_point_x = right_PAD_center_x + 150 if contact_position == UP else right_PAD_center_x + 150
            right_contact_point_y = right_PAD_center_y + 150 if contact_position == UP else right_PAD_center_y - 150
            self.right_contact_point = Point(right_contact_point_x,right_contact_point_y)
            right_contact = Waveguide(Point(right_contact_point_x, right_contact_point_y - contact_width / 2),
                                     Point(right_contact_point_x, right_contact_point_y + contact_width / 2), contact_width)
            right_contact.draw(temp_heater_cell, contact_layer)

            if (open):
                left_open = Waveguide(Point(right_contact_point_x, right_contact_point_y - open_width / 2),
                                      Point(right_contact_point_x, right_contact_point_y + open_width / 2), open_width)
                left_open.draw(temp_heater_cell, open_layer)

            contact_link = AQuarBend(Point(right_PAD_center_x, right_PAD_center_y),
                                    Point(right_contact_point_x, right_contact_point_y), contact_bus_width)
            contact_link.draw(temp_heater_cell, contact_layer)


        ## heater right connector
        relative_angle_right_up = coupling_end_point.get_relative_angle(self.ring_center)
        heater_right_bend = Bend(self.ring_center, -heater_angle/2, relative_angle_right_up, heater_width,
                                self.radius)
        heater_right_bend.draw(temp_heater_cell, heater_layer)

        pass_point = [right_connect_start_point.to_tuple(), coupling_end_point.to_tuple(),
                      heater_right_bend.get_end_point().to_tuple()]
        heater_right_connector = gdspy.FlexPath(
            pass_point, width=bus_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(heater_right_connector)

        ## pass connect
        left_bend_end_point = heater_left_bend.get_end_point()
        left_bend_end_point = Point(left_bend_end_point.x + 0.6*math.cos(left_bend_end_point.get_relative_angle(self.ring_center) + math.pi), left_bend_end_point.y+ 0.6*math.sin(left_bend_end_point.get_relative_angle(self.ring_center) + math.pi))
        pass_left_point = left_bend_end_point.get_percent_point(self.ring_center, 0.5)
        right_bend_end_point = heater_right_bend.get_start_point()
        right_bend_end_point = Point(right_bend_end_point.x + 0.6*math.cos(right_bend_end_point.get_relative_angle(self.ring_center)), right_bend_end_point.y+ 0.6*math.sin(right_bend_end_point.get_relative_angle(self.ring_center)))
        pass_right_point = right_bend_end_point.get_percent_point(self.ring_center, 0.5)

        pass_point = [left_bend_end_point.to_tuple(), pass_left_point.to_tuple(),pass_right_point.to_tuple(), right_bend_end_point.to_tuple()]
        pass_connector = gdspy.FlexPath(
            pass_point, width=heater_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(pass_connector)

        ## rotate
        cell.cell.add(gdspy.CellReference(temp_heater_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_angle))

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

    def get_left_contact_point(self):
        if (self.left_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            return self.left_contact_point

    def get_right_contact_point(self):
        if (self.right_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            return self.right_contact_point

    def get_left_pad_point(self):
        if (self.left_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            return self.left_pad_point

    def get_right_pad_point(self):
        if (self.right_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            return self.right_pad_point