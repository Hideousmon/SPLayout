from ..utils.utils import *
from ..components.waveguide import Waveguide
from ..components.polygon import Polygon

## global parameters
AEMDGratingCount = -1
AEMDGratingComponent_cell_list = []

def MAKE_AEMD_GRATING(port_width=0.45,waveguide_layer=Layer(1,0),etch_layer=Layer(2,0),grating_number=40,grating_period=0.63,grating_duty=0.3/0.63):
    """
    Make an AEMD Grating Class.

    Parameters
    ----------
    port_width : float (unit: μm)
        The port width of the grating.
    waveguide_layer : Layer
        The layer for waveguide.
    etch_layer : Layer
        The layer for etching.
    grating_number : int
        Number of the etching slices.
    grating_period : float
        Period of the grating.
    grating_duty : float
        Duty of the grating.

    Returns
    -------
    out : ‘Class’
        Can be used to define an AEMD grating.

    Notes
    --------
    The port width should not be too small or too large (better between 0.4 and 0.5).
    The returned Class has two parameters: start_point,relative_position.
    It can be drawn on the cell with:  object.draw(cell).

    Examples
    --------
    >>> # get a AEMD grating definition
    >>> AEMDgrating = MAKE_AEMD_GRATING(port_width=0.5)
    >>> # start point for the AEMD grating
    >>> grating_point = Point(90,-30)
    >>> # make the AEMD grating
    >>> right_grating = AEMDgrating(grating_point,RIGHT)
    >>> # draw the AEMD grating on the layout
    >>> right_grating.draw(cell)
    """
    global AEMDGratingComponent_cell_list
    global AEMDGratingCount
    port_waveguide_width = port_width
    grating_number = grating_number
    grating_period = grating_period
    grating_duty = grating_duty
    grating_width = 18

    grating_polygon = Polygon(
        [ (226.71000, -7.44000),  (186.71500, -6.36500),
          (146.72500, -4.91400),  (106.71500, -3.46200),
          (18.22500, -0.26900),   (8.22700, -0.26900),
          (4.16200, -0.25000),    (0.00000, -port_waveguide_width / 2),
          (0.00000, port_waveguide_width / 2),  (4.16200, 0.25000),
          (8.22700, 0.27000), (18.22500, 0.27000),
          (106.73400, 3.46200),  (186.71500, 6.36400),
          (226.71000, 7.43900),  (276.35500, 7.43900),
          (276.35500, -7.44000)])

    grating_etch_list = []
    for i in range(0, grating_number):
        grating_etch_list.append(Waveguide( Point(246.061, 0.207) - (grating_period *grating_duty/2, 0) + (
                grating_period * i, 0),
            Point(246.061, 0.207) + (grating_period * grating_duty/2, 0) + (
                grating_period * i, 0),
            width=grating_width))
    AEMD_grating_cell = Cell("AEMD_GRATING_" + str(AEMDGratingCount+1))
    grating_polygon.draw(AEMD_grating_cell, waveguide_layer)
    for item in grating_etch_list:
        item.draw(AEMD_grating_cell, etch_layer)

    AEMDGratingComponent_cell_list.append(AEMD_grating_cell)
    AEMDGratingCount += 1
    AEMDGratingCount_local = AEMDGratingCount

    class AEMDgrating():
        def __init__(self,start_point,relative_position = RIGHT):
            self.start_point = tuple_to_point(start_point)
            self.rotate_radian = relative_position
            self.count = AEMDGratingCount_local

        def draw(self, cell, *args):
            global AEMDGratingComponent_cell_list

            cell.cell.add(gdspy.CellReference(AEMDGratingComponent_cell_list[self.count].cell, (self.start_point.x, self.start_point.y),rotation=self.rotate_radian))

            return self.start_point

        def get_start_point(self):

            return self.start_point

    return AEMDgrating


