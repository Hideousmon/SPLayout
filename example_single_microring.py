from utils import *


def single_microring(start_point,radius,gap,ring_wg_width,coupling_length,grating_wg_width = 0.5):
    first_ring = AddDropMicroring(start_point,radius,gap,ring_wg_width,coupling_length)
    first_ring.draw(ringCell,RING_LAYER)
    first_ring.add_heater(ringCell,HEATER_LAYER)

    ## through port
    taper_start_point = first_ring.get_through_point()
    taper_length = 5
    taper_end_point = Point(taper_start_point.x + taper_length, taper_start_point.y)
    taper = Taper(taper_start_point, taper_end_point, ring_wg_width, grating_wg_width)
    taper.draw(ringCell, RING_LAYER)

    connector_start_point = taper.get_end_point()
    connector_end_point = Point(start_point.x + 30, start_point.y +50)
    connector = DoubleBendConnector(connector_start_point, connector_end_point, grating_wg_width)
    connector.draw(ringCell, RING_LAYER)

    through_port = connector.get_end_point()
    right_grating = AEMDgrating(through_port, RIGHT)
    right_grating.draw(ringCell)

    ## input port
    taper_start_point = first_ring.get_input_point()
    taper_length = 5
    taper_end_point = Point(taper_start_point.x - taper_length, taper_start_point.y)
    taper = Taper(taper_start_point, taper_end_point, ring_wg_width,grating_wg_width)
    taper.draw(ringCell, RING_LAYER)

    connector_start_point = taper.get_end_point()
    connector_end_point = Point(start_point.x -30, start_point.y + 50)
    connector = DoubleBendConnector(connector_start_point,connector_end_point,grating_wg_width)
    connector.draw(ringCell, RING_LAYER)

    input_port = connector.get_end_point()
    right_grating = AEMDgrating(input_port, LEFT)
    right_grating.draw(ringCell)

    ## drop port
    taper_start_point = first_ring.get_drop_point()
    taper_length = 5
    taper_end_point = Point(taper_start_point.x - taper_length, taper_start_point.y)
    taper = Taper(taper_start_point, taper_end_point, ring_wg_width, grating_wg_width)
    taper.draw(ringCell, RING_LAYER)
    drop_port = taper.get_end_point()

    bend_start_point= drop_port
    bend_end_point = Point(bend_start_point.x - 10, bend_start_point.y -50)
    bend = AQuarBend(bend_start_point,bend_end_point,grating_wg_width)
    bend.draw(ringCell, RING_LAYER)

    bend_start_point = bend.get_end_point()
    bend_end_point = Point(start_point.x + 30,  start_point.y-110)
    bend = AQuarBend(bend_start_point, bend_end_point, grating_wg_width)
    bend.draw(ringCell, RING_LAYER)

    grating_start_point = bend.get_end_point()
    right_grating = AEMDgrating(grating_start_point, RIGHT)
    right_grating.draw(ringCell)

    ## add port
    taper_start_point = first_ring.get_add_point()
    taper_length = 5
    taper_end_point = Point(taper_start_point.x + taper_length, taper_start_point.y)
    taper = Taper(taper_start_point, taper_end_point, ring_wg_width, grating_wg_width)
    taper.draw(ringCell, RING_LAYER)

    connector_start_point = taper.get_end_point()
    connector_end_point = Point(start_point.x + 30, start_point.y -30)
    connector = DoubleBendConnector(connector_start_point, connector_end_point, grating_wg_width)
    connector.draw(ringCell, RING_LAYER)

    add_port = connector.get_end_point()
    right_grating = AEMDgrating(add_port, RIGHT)
    right_grating.draw(ringCell)


if __name__ == "__main__":
    RING_LAYER = 1
    HEATER_LAYER = 3
    ringCell = gdspy.Cell("ring")


    start_point = Point(0, 0)
    radius = 5.1973
    gap = 0.18
    ring_wg_width = 0.45
    coupling_length = 5.5
    single_microring(start_point,radius,gap,ring_wg_width,coupling_length)

    filename = "example_single_ring.gds"
    writer = gdspy.GdsWriter(filename, unit=1.0e-6, precision=1.0e-9)
    writer.write_cell(ringCell)
    writer.close()