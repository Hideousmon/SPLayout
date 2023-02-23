from ..utils.utils import *
from ..components.waveguide import Waveguide
from ..components.bend import Bend
from ..components.quarbend import AQuarBend,QuarBend

## global parameters
add_drop_microring_number = 0
add_drop_microring_heater_number = 0
add_drop_microring_flat_number = 0
add_drop_microring_flat_heater_number = 0

class AddDropMicroringFlat:
    """
    Add-drop micro-ring Definition in SPLayout with two flat coupling region.

    Parameters
    ----------
    start_point : Point
        Input port point of the Add-drop micro-ring.
    radius : float
        Radius of the ring (μm).
    gap : float
        Gap between the two waveguides in coupling region (μm).
    wg_width : float
        Width of the waveguides.
    coupling_length : float
        The coupling length in coupling region (μm).
    relative_position : RIGHT or UP or LEFT or DOWN
        The relative position of the microring according to the other components.
    """
    def __init__(self,start_point,radius,gap,wg_width,coupling_length,relative_position = RIGHT):
        self.start_point = tuple_to_point(start_point)
        self.radius = radius
        self.gap = gap
        self.width = wg_width
        self.coupling_length = coupling_length
        ## force limit
        if (self.coupling_length == 0):
            self.coupling_length = 0.001
        self.rotate_radian = relative_position
        self.default_bend_radius = 5

        global add_drop_microring_flat_number
        self.temp_cell = Cell("AddDropMicroringFlat" + str(add_drop_microring_flat_number))
        add_drop_microring_flat_number += 1


        self.coupling_radian = self.coupling_length / self.radius
        # print("coupling radian degree:",self.coupling_radian * 180 / math.pi) ## for test
        if (self.coupling_radian >= math.pi*2/3):
            raise Exception("Coupling Length Too Long!")

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

        if (self.rotate_radian == RIGHT):
            self.input_point = self.start_point
            self.through_point = self.start_point + self.relative_through_point
            self.drop_point = self.start_point + self.relative_drop_point
            self.add_point = self.start_point + self.relative_add_point
        elif (self.rotate_radian == UP):
            self.input_point = self.start_point
            self.through_point = self.start_point + Point(-self.relative_through_point.y,
                                                          self.relative_through_point.x)
            self.drop_point = self.start_point + Point(-self.relative_drop_point.y,
                                                       self.relative_drop_point.x)
            self.add_point = self.start_point + Point(-self.relative_add_point.y, self.relative_add_point.x)
        elif (self.rotate_radian == LEFT):
            self.input_point = self.start_point
            self.through_point = self.start_point + Point(-self.relative_through_point.x,
                                                          -self.relative_through_point.y)
            self.drop_point = self.start_point + Point(-self.relative_drop_point.x,
                                                       -self.relative_drop_point.y)
            self.add_point = self.start_point + Point(-self.relative_add_point.x,
                                                      -self.relative_add_point.y)
        elif (self.rotate_radian == DOWN):
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
        """
        Draw the Component on the layout.

        Parameters
        ----------
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.

        Returns
        -------
        out : Point,Point,Point,Point
            Input point, through point, drop point, add point.
        """
        self.up_waveguide.draw(self.temp_cell,layer)
        self.ring_up_waveguide.draw(self.temp_cell,layer)
        self.left_half_ring.draw(self.temp_cell,layer)
        self.right_half_ring.draw(self.temp_cell, layer)
        self.ring_down_waveguide.draw(self.temp_cell, layer)
        self.down_waveguide.draw(self.temp_cell, layer)

        ## rotate
        cell.cell.add(gdspy.CellReference(self.temp_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_radian))

        return self.input_point, self.through_point,self.drop_point,self.add_point

    def add_heater(self,cell,heater_layer,heater_radian = math.pi/2, heater_width = 2, connect_pad_width = 14, bus_width = 4 , contact = 0 , contact_layer =None,contact_width = 150,contact_bus_width = 10,contact_position = UP,open = 0, open_layer =None,open_width = 140,touch = 0,touch_layer = None):
        """
        Add heater and corresponding pads for the micro-ring.

        Parameters
        ----------
        cell : Cell
            Cell to draw the heater and pads.
        heater_layer : Layer
            Layer to draw heater.
        heater_radian : float
            Radian for adjusting the cover region of the heater (radian) [can be easily defined by math.pi].
        heater_width : float
            Width of the heater (μm).
        connect_pad_width : float
            The width of pads that connect the heater material to the conductor material.
        bus_width : float
            The width of the heater material bus waveguide (μm).
        contact : bool or int
            If add contact (conductor material) for the microring.
        contact_layer : Layer
            The Layer to draw the contact (conductor material).
        contact_bus_width : float
            The width of the conductor bus waveguide (μm).
        contact_position : UP or DOWN
            The relative position of the contact pads according to the microring.
        open : bool or int
            If add an open region for the contact pad.
        open_layer : Layer
            The Layer to draw the open region.
        open_width : float
            The width of the open region (rectradian) (μm).
        touch : bool or int
            If add an touch region for the connect pad.
        touch_layer : Layer
            The Layer to draw the touch region.

        """

        global add_drop_microring_flat_heater_number
        temp_heater_cell = Cell("AddDropMicroringFlatHeater" + str(add_drop_microring_flat_heater_number))
        add_drop_microring_flat_heater_number += 1

        left_connect_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y + 10)
        coupling_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y)
        right_connect_start_point = Point(self.relative_through_point.x + 10,self.relative_through_point.y + 10)
        coupling_end_point = Point(self.relative_through_point.x + 10, self.relative_through_point.y)

        ## heater left connector
        relative_radian_left_up = coupling_start_point.get_relative_radian(self.left_half_ring_center) + math.pi
        heater_left_bend = Bend(self.left_half_ring_center, relative_radian_left_up, math.pi + heater_radian / 2, heater_width,
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
        left_pad.draw(temp_heater_cell, contact_layer)
        if (touch):
            if (touch_layer == None):
                raise  Exception("The touch layer should be ")
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
        right_pad.draw(temp_heater_cell, contact_layer)
        if (touch):
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
        relative_radian_right_up = coupling_end_point.get_relative_radian(self.right_half_ring_center)
        heater_right_bend = Bend(self.right_half_ring_center, -heater_radian/2, relative_radian_right_up, heater_width,
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
        left_bend_end_point = Point(left_bend_end_point.x + 0.6*math.cos(left_bend_end_point.get_relative_radian(self.left_half_ring_center) + math.pi), left_bend_end_point.y+ 0.6*math.sin(left_bend_end_point.get_relative_radian(self.ring_center) + math.pi))
        pass_left_point = left_bend_end_point.get_percent_point(self.left_half_ring_center, 0.5)
        right_bend_end_point = heater_right_bend.get_start_point()
        right_bend_end_point = Point(right_bend_end_point.x + 0.6*math.cos(right_bend_end_point.get_relative_radian(self.right_half_ring_center)), right_bend_end_point.y+ 0.6*math.sin(right_bend_end_point.get_relative_radian(self.ring_center)))
        pass_right_point = right_bend_end_point.get_percent_point(self.right_half_ring_center, 0.5)

        pass_point = [left_bend_end_point.to_tuple(), pass_left_point.to_tuple(),pass_right_point.to_tuple(), right_bend_end_point.to_tuple()]
        pass_connector = gdspy.FlexPath(
            pass_point, width=heater_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(pass_connector)

        ## rotate
        cell.cell.add(gdspy.CellReference(temp_heater_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_radian))

    def get_input_point(self):
        """
        Derive the input port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Input point.
        """
        return  self.input_point

    def get_through_point(self):
        """
        Derive the through port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Through point.
        """
        return  self.through_point

    def get_drop_point(self):
        """
        Derive the drop port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Drop point.
        """
        return  self.drop_point

    def get_add_point(self):
        """
        Derive the add port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Add point.
        """
        return  self.add_point

    def get_left_contact_point(self):
        """
        Derive the left contact center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Left contact center point.
        """
        if (self.left_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                left_contact_point = self.start_point + self.left_contact_point
                return left_contact_point
            elif (self.rotate_radian == UP):
                left_contact_point = self.start_point + Point(-self.left_contact_point.y,
                                                              self.left_contact_point.x)
                return left_contact_point
            elif (self.rotate_radian == LEFT):
                left_contact_point = self.start_point + Point(-self.left_contact_point.x,
                                                              -self.left_contact_point.y)
                return left_contact_point
            elif (self.rotate_radian == DOWN):
                left_contact_point = self.start_point + Point(self.left_contact_point.y,
                                                              -self.left_contact_point.x)
                return left_contact_point

    def get_right_contact_point(self):
        """
        Derive the right contact center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Right contact center point.
        """
        if (self.right_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                right_contact_point = self.start_point + self.right_contact_point
                return right_contact_point
            elif (self.rotate_radian == UP):
                right_contact_point = self.start_point + Point(-self.right_contact_point.y,
                                                               self.right_contact_point.x)
                return right_contact_point
            elif (self.rotate_radian == LEFT):
                right_contact_point = self.start_point + Point(-self.right_contact_point.x,
                                                               -self.right_contact_point.y)
                return right_contact_point
            elif (self.rotate_radian == DOWN):
                right_contact_point = self.start_point + Point(self.right_contact_point.y,
                                                               -self.right_contact_point.x)
                return right_contact_point

    def get_left_pad_point(self):
        """
        Derive the left conductor pad center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Left conductor pad center point.
        """
        if (self.left_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                left_pad_point = self.start_point + self.left_pad_point
                return left_pad_point
            elif (self.rotate_radian == UP):
                left_pad_point = self.start_point + Point(-self.left_pad_point.y,
                                                          self.left_pad_point.x)
                return left_pad_point
            elif (self.rotate_radian == LEFT):
                left_pad_point = self.start_point + Point(-self.left_pad_point.x,
                                                          -self.left_pad_point.y)
                return left_pad_point
            elif (self.rotate_radian == DOWN):
                left_pad_point = self.start_point + Point(self.left_pad_point.y,
                                                          -self.left_pad_point.x)
                return left_pad_point

    def get_right_pad_point(self):
        """
        Derive the right conductor pad center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Right conductor pad center point.
        """
        if (self.right_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                right_pad_point = self.start_point + self.right_pad_point
                return right_pad_point
            elif (self.rotate_radian == UP):
                right_pad_point = self.start_point + Point(-self.right_pad_point.y,
                                                           self.right_pad_point.x)
                return right_pad_point
            elif (self.rotate_radian == LEFT):
                right_pad_point = self.start_point + Point(-self.right_pad_point.x,
                                                           -self.right_pad_point.y)
                return right_pad_point
            elif (self.rotate_radian == DOWN):
                right_pad_point = self.start_point + Point(self.right_pad_point.y,
                                                           -self.right_pad_point.x)
                return right_pad_point



class AddDropMicroring:
    """
    Add-drop micro-ring Definition in SPLayout with two bend coupling region.

    Parameters
    ----------
    start_point : Point
        Input port point of the Add-drop micro-ring.
    radius : float
        Radius of the ring (μm).
    gap : float
        Gap between the two waveguides in coupling region (μm).
    wg_width : float
        Width of the waveguides.
    coupling_length : float
        The coupling length in coupling region (μm).
    relative_position : RIGHT or UP or LEFT or DOWN
        The relative position of the microring according to the other components.
    """
    def __init__(self,start_point,radius,gap,wg_width,coupling_length,relative_position = RIGHT):
        self.start_point = tuple_to_point(start_point)
        self.radius = radius
        self.gap = gap
        self.width = wg_width
        self.coupling_length = coupling_length
        ## force limit
        if (self.coupling_length == 0):
            self.coupling_length = 0.001
        self.rotate_radian = relative_position
        self.default_bend_radius = 5

        global add_drop_microring_number
        self.temp_cell = Cell("AddDropMicroring"+str(add_drop_microring_number))
        add_drop_microring_number += 1

        ## initialize the input point to Zero
        self.relative_input_point = Point(0,0)

        self.coupling_radian = self.coupling_length / self.radius
        # print("coupling radian degree:",self.coupling_radian * 180 / math.pi) ## for test
        if (self.coupling_radian >= math.pi*2/3):
            raise Exception("Coupling Length Too Long!")

        ## input bend
        self.input_bend = Bend(Point(self.relative_input_point.x,self.relative_input_point.y + self.default_bend_radius), - math.pi / 2 , - math.pi / 2 + self.coupling_radian/2,
                                self.width, self.default_bend_radius)


        # print("input bend end:", self.input_bend.get_end_point().x) ## for test


        ## up coupling bend
        ring_center_x = self.relative_input_point.x + self.default_bend_radius*math.sin(self.coupling_radian/2) + (self.radius + self.width + self.gap)*math.sin(self.coupling_radian/2)
        ring_center_y = self.relative_input_point.y + self.default_bend_radius*( 1- math.cos(self.coupling_radian/2) ) - (self.radius + self.width + self.gap)*math.cos(self.coupling_radian/2)
        self.ring_center = Point(ring_center_x,ring_center_y)
        self.up_coupling_bend = Bend(self.ring_center,  math.pi / 2 - self.coupling_radian/2,  math.pi / 2 + self.coupling_radian/2,
                                self.width, (self.radius + self.width + self.gap))

        # print("up coupling bend end:", self.up_coupling_bend.get_end_point().y)  ## for test
        # print("up coupling bend start:", self.up_coupling_bend.get_end_point().x)  ## for test

        ## through bend
        up_coupling_bend_right_point = self.up_coupling_bend.get_start_point()
        self.through_bend = Bend(Point(up_coupling_bend_right_point.x + self.default_bend_radius*math.sin(self.coupling_radian/2), self.relative_input_point.y + self.default_bend_radius), - math.pi / 2- self.coupling_radian / 2,
                               - math.pi / 2 ,
                               self.width, self.default_bend_radius)



        ## Ring
        self.ring = Bend(self.ring_center, 0 ,
                                math.pi * 2,
                               self.width, self.radius)

        ## down coupling bend
        self.down_coupling_bend = Bend(self.ring_center, -math.pi / 2 - self.coupling_radian / 2,
                                     -math.pi / 2 + self.coupling_radian / 2,
                                     self.width, (self.radius + self.width + self.gap))

        ## drop bend
        down_coupling_bend_left_point = self.down_coupling_bend.get_start_point()
        self.drop_bend = Bend(Point(down_coupling_bend_left_point.x - self.default_bend_radius*math.sin(self.coupling_radian/2), down_coupling_bend_left_point.y - self.default_bend_radius*math.cos(self.coupling_radian/2)), math.pi / 2 -  self.coupling_radian / 2,
                                math.pi / 2 ,
                               self.width, self.default_bend_radius)



        ## add bend
        down_coupling_bend_right_point = self.down_coupling_bend.get_end_point()
        self.add_bend = Bend(
            Point(down_coupling_bend_right_point.x + self.default_bend_radius * math.sin(self.coupling_radian / 2),
                  down_coupling_bend_right_point.y - self.default_bend_radius * math.cos(self.coupling_radian / 2)),
            math.pi / 2,
            math.pi / 2 + self.coupling_radian / 2,
            self.width, self.default_bend_radius)

        ## get relative points
        self.relative_through_point = self.through_bend.get_end_point()
        self.relatvie_drop_point = self.drop_bend.get_end_point()
        self.relatvie_add_point = self.add_bend.get_start_point()



        ## calculate port with rotation
        if (self.rotate_radian == RIGHT):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + self.relative_through_point
            self.drop_point = self.start_point + self.relatvie_drop_point
            self.add_point = self.start_point + self.relatvie_add_point
        elif (self.rotate_radian == UP):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + Point(-self.relative_through_point.y,self.relative_through_point.x)
            self.drop_point = self.start_point + Point(-self.relatvie_drop_point.y,self.relatvie_drop_point.x)
            self.add_point = self.start_point + Point(-self.relatvie_add_point.y,self.relatvie_add_point.x)
        elif (self.rotate_radian == LEFT):
            self.input_point = self.start_point + self.relative_input_point
            self.through_point = self.start_point + Point(-self.relative_through_point.x,
                                                          -self.relative_through_point.y)
            self.drop_point = self.start_point + Point(-self.relatvie_drop_point.x,
                                                       -self.relatvie_drop_point.y)
            self.add_point = self.start_point + Point(-self.relatvie_add_point.x, -self.relatvie_add_point.y)
        elif (self.rotate_radian == DOWN):
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
        """
        Draw the Component on the layout.

        Parameters
        ----------
        cell : Cell
            Cell to draw the component.
        layer : Layer
            Layer to draw.

        Returns
        -------
        out : Point,Point,Point,Point
            Input point, through point, drop point, add point.
        """
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
                                          rotation=self.rotate_radian))
        return self.input_point, self.through_point,self.drop_point,self.add_point

    def add_heater(self,cell,heater_layer,heater_radian = math.pi/2, heater_width = 2, connect_pad_width = 14, bus_width = 4 , contact = 0 , contact_layer =None,contact_width = 150,contact_bus_width = 10,contact_position = UP,open = 0, open_layer =None,open_width = 140,touch = 0,touch_layer = None):
        """
        Add heater and corresponding pads for the micro-ring.

        Parameters
        ----------
        cell : Cell
            Cell to draw the heater and pads.
        heater_layer : Layer
            Layer to draw heater.
        heater_radian : float
            Radian for adjusting the cover region of the heater (radian) [can be easily defined by math.pi].
        heater_width : float
            Width of the heater (μm).
        connect_pad_width : float
            The width of pads that connect the heater material to the conductor material.
        bus_width : float
            The width of the heater material bus waveguide (μm).
        contact : bool or int
            If add contact (conductor material) for the microring.
        contact_layer : Layer
            The Layer to draw the contact (conductor material).
        contact_bus_width : float
            The width of the conductor bus waveguide (μm).
        contact_position : UP or DOWN
            The relative position of the contact pads according to the microring.
        open : bool or int
            If add an open region for the contact pad.
        open_layer : Layer
            The Layer to draw the open region.
        open_width : float
            The width of the open region (rectradian) (μm).
        touch : bool or int
            If add an touch region for the connect pad.
        touch_layer : Layer
            The Layer to draw the touch region.

        """

        global add_drop_microring_heater_number
        temp_heater_cell = Cell("AddDropMicroringHeater" + str(add_drop_microring_heater_number))
        add_drop_microring_heater_number += 1


        left_connect_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y + 10)
        coupling_start_point = Point(self.relative_input_point.x - 10,self.relative_input_point.y)
        right_connect_start_point = Point(self.relative_through_point.x + 10,self.relative_through_point.y + 10)
        coupling_end_point = Point(self.relative_through_point.x + 10, self.relative_through_point.y)

        ## heater left connector
        relative_radian_left_up = coupling_start_point.get_relative_radian(self.ring_center) + math.pi
        heater_left_bend = Bend(self.ring_center, relative_radian_left_up, math.pi + heater_radian / 2, heater_width,
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
        left_pad.draw(temp_heater_cell, contact_layer)
        if (touch):
            if (touch_layer == None):
                raise Exception("The touch layer should be ")
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
        right_pad.draw(temp_heater_cell, contact_layer)
        if (touch):
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
        relative_radian_right_up = coupling_end_point.get_relative_radian(self.ring_center)
        heater_right_bend = Bend(self.ring_center, -heater_radian/2, relative_radian_right_up, heater_width,
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
        left_bend_end_point = Point(left_bend_end_point.x + 0.6*math.cos(left_bend_end_point.get_relative_radian(self.ring_center) + math.pi), left_bend_end_point.y+ 0.6*math.sin(left_bend_end_point.get_relative_radian(self.ring_center) + math.pi))
        pass_left_point = left_bend_end_point.get_percent_point(self.ring_center, 0.5)
        right_bend_end_point = heater_right_bend.get_start_point()
        right_bend_end_point = Point(right_bend_end_point.x + 0.6*math.cos(right_bend_end_point.get_relative_radian(self.ring_center)), right_bend_end_point.y+ 0.6*math.sin(right_bend_end_point.get_relative_radian(self.ring_center)))
        pass_right_point = right_bend_end_point.get_percent_point(self.ring_center, 0.5)

        pass_point = [left_bend_end_point.to_tuple(), pass_left_point.to_tuple(),pass_right_point.to_tuple(), right_bend_end_point.to_tuple()]
        pass_connector = gdspy.FlexPath(
            pass_point, width=heater_width, gdsii_path=True, layer=heater_layer.layer,datatype=heater_layer.datatype
        )
        temp_heater_cell.cell.add(pass_connector)

        ## rotate
        cell.cell.add(gdspy.CellReference(temp_heater_cell.cell, (self.start_point.x, self.start_point.y),
                                          rotation=self.rotate_radian))

    def get_input_point(self):
        """
        Derive the input port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Input point.
        """
        return self.input_point

    def get_through_point(self):
        """
        Derive the through port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Through point.
        """
        return self.through_point

    def get_drop_point(self):
        """
        Derive the drop port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Drop point.
        """
        return self.drop_point

    def get_add_point(self):
        """
        Derive the add port point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Add point.
        """
        return self.add_point

    def get_left_contact_point(self):
        """
        Derive the left contact center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Left contact center point.
        """
        if (self.left_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                left_contact_point = self.start_point + self.left_contact_point
                return left_contact_point
            elif (self.rotate_radian == UP):
                left_contact_point = self.start_point + Point(-self.left_contact_point.y,
                                                              self.left_contact_point.x)
                return left_contact_point
            elif (self.rotate_radian == LEFT):
                left_contact_point = self.start_point + Point(-self.left_contact_point.x,
                                                              -self.left_contact_point.y)
                return left_contact_point
            elif (self.rotate_radian == DOWN):
                left_contact_point = self.start_point + Point(self.left_contact_point.y,
                                                              -self.left_contact_point.x)
                return left_contact_point

    def get_right_contact_point(self):
        """
        Derive the right contact center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Right contact center point.
        """
        if (self.right_contact_point == None):
            raise Exception("You Don't have a contact for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                right_contact_point = self.start_point + self.right_contact_point
                return right_contact_point
            elif (self.rotate_radian == UP):
                right_contact_point = self.start_point + Point(-self.right_contact_point.y,
                                                               self.right_contact_point.x)
                return right_contact_point
            elif (self.rotate_radian == LEFT):
                right_contact_point = self.start_point + Point(-self.right_contact_point.x,
                                                               -self.right_contact_point.y)
                return right_contact_point
            elif (self.rotate_radian == DOWN):
                right_contact_point = self.start_point + Point(self.right_contact_point.y,
                                                               -self.right_contact_point.x)
                return right_contact_point

    def get_left_pad_point(self):
        """
        Derive the left conductor pad center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Left conductor pad center point.
        """
        if (self.left_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                left_pad_point = self.start_point + self.left_pad_point
                return left_pad_point
            elif (self.rotate_radian == UP):
                left_pad_point = self.start_point + Point(-self.left_pad_point.y,
                                                          self.left_pad_point.x)
                return left_pad_point
            elif (self.rotate_radian == LEFT):
                left_pad_point = self.start_point + Point(-self.left_pad_point.x,
                                                          -self.left_pad_point.y)
                return left_pad_point
            elif (self.rotate_radian == DOWN):
                left_pad_point = self.start_point + Point(self.left_pad_point.y,
                                                          -self.left_pad_point.x)
                return left_pad_point

    def get_right_pad_point(self):
        """
        Derive the right conductor pad center point of the AddDropMicroringFlat.

        Returns
        -------
        out : Point
            Right conductor pad center point.
        """
        if (self.right_pad_point == None):
            raise Exception("You Don't have a pad for the ring!")
        else:
            if (self.rotate_radian == RIGHT):
                right_pad_point = self.start_point + self.right_pad_point
                return right_pad_point
            elif (self.rotate_radian == UP):
                right_pad_point = self.start_point + Point(-self.right_pad_point.y,
                                                           self.right_pad_point.x)
                return right_pad_point
            elif (self.rotate_radian == LEFT):
                right_pad_point = self.start_point + Point(-self.right_pad_point.x,
                                                           -self.right_pad_point.y)
                return right_pad_point
            elif (self.rotate_radian == DOWN):
                right_pad_point = self.start_point + Point(self.right_pad_point.y,
                                                           -self.right_pad_point.x)
                return right_pad_point