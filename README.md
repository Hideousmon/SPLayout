# SPLayout
 Silicon Photonics Design Tools for GDSII Files. It is based on gdspy([heitzmann/gdspy: Python module for creating GDSII stream files, usually CAD layouts. (github.com)](https://github.com/heitzmann/gdspy)) and can interact with it.

### Pre-Installation

* gdspy 

### Usage

#### Parallel / Vertical Waveguide

```
    start_point = Point(0,0)
    wg_end_point = Point(5,0)
    first_wg = Waveguide(start_point,wg_end_point,width=0.45)
    first_wg.draw(ringCell,RING_LAYER)
```

![waveguide](./pictures/waveguide.png)

#### Bend

```
    center_point = Point(0,0)
    start_angle = math.pi*4/5
    end_angle = math.pi*3/2
    width = 0.4
    radius = 5
    first_bend = Bend(center_point, start_angle, end_angle, width , radius)
    first_bend.draw(ringCell,RING_LAYER)
```

![bend](./pictures/bend.png)

#### Anticlockwise Quarter Bend Connector

```
    start_point = Point(0,0)
    end_point = Point(-7,10)
    width = 0.4
    first_AQuarBend = AQuarBend(start_point,end_point,width,5)
    first_AQuarBend.draw(ringCell,RING_LAYER)
```

![AQuarBend](./pictures/AQuarBend.png)

#### Clockwise Quarter Bend Connector

```
    start_point = Point(0,0)
    end_point = Point(-7,20)
    width = 0.4
    first_QuarBend = AQuarBend(start_point,end_point,width,5)
    first_QuarBend.draw(ringCell,RING_LAYER)
```

![QuarBend](./pictures/QuarBend.png)

#### Add-Drop Microring

```
    start_point = Point(0,0)
    radius = 5.1973
    gap = 0.18
    wg_width = 0.45
    coupling_length = 5.5
    first_ring = AddDropMicroring(start_point,radius,gap,wg_width,coupling_length)
    first_ring.draw(ringCell,RING_LAYER)
```
![Taper](./pictures/Add-Drop Microring.png)


#### Taper

```
    taper_start_point = Point(0,0)
    taper_length = 5
    taper_end_point = Point(taper_start_point.x+ taper_length,taper_start_point.y )
    first_taper = Taper(taper_start_point,taper_end_point,0.45,0.8)
    first_taper.draw(ringCell,RING_LAYER)
```
![Taper](./pictures/Taper.png)


#### AEMD Grating

```
    grating_port = Point(0,0)
    right_grating = AEMDgrating(grating_port,RIGHT)
    right_grating.draw(ringCell)
```

![AEMDGrating](./pictures/AEMDGrating.png)

#### Double Bend Connector :star:

```
    double_connect_start_point = Point(0,0)
    double_connect_end_point = Point(-20,40)
    connector = DoubleBendConnector(double_connect_start_point, double_connect_end_point, width=1, xpercent=0.5)
    connector.draw(ringCell,RING_LAYER)
```

![DoubleConnector](./pictures/DoubleConnector.png)

### Example

[example_single_microring.py](https://github.com/Hideousmon/SPLayout/example_single_microring.py) 

![example](./pictures/example.png)
