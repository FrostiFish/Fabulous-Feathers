from fullcontrol import Point, Extruder, ExtrusionGeometry, Vector, move, move_polar, Union, PrinterCommand, travel_to
from math import cos, sin, pi, tau, sqrt, floor
from z_lift import z_lift

def vaneXY(start_geometry: Union[Point, list], end_geometry: Union[Point, list], vector: Vector=Vector()) -> list:
    '''generate barbs
    '''
    steps = []

    if len(start_geometry) != len(end_geometry):
        raise Exception("start_geometry and end_geometry don't have the same length")

    for point_index in range(len(start_geometry)):
        steps.append(Extruder(on=False))
        steps.append(start_geometry[point_index])
        steps.append(Extruder(on=True))
        steps.append(end_geometry[point_index])
    
    return move(steps, vector)

def cartesian_ellipse_arcXY(centre: Point, a: float, b: float, start_percentage: float=0.0, end_percentage: float=1.0, segments: int=100, mirror: bool=False) -> list:
    '''generate a partial ellipse, based on cartesian definition of an ellipse y = b/a * sqrt(a^2 - x^2). By default it will generate half an ellipse above the X-axis. 
    '''
    steps = []
    
    for point_index in range(segments+1):
        x = (end_percentage-start_percentage)*2*a*point_index/segments - a + (start_percentage*2*a)
        #print(x)
        steps.append(Point(x=x + centre.x, 
                           y=b/a * sqrt(a**2 - x**2) + centre.y, 
                           z=centre.z
                           )
                    )
    
    if mirror:
        for point_index in range(1, segments+1):
            x = (start_percentage-end_percentage)*2*a*point_index/segments - a + (end_percentage*2*a)
            #print(x)
            steps.append(Point(x=x + centre.x, 
                            y=-b/a * sqrt(a**2 - x**2) + centre.y, 
                            z=centre.z
                            )
                        )

    return steps

def cartesian_ellipse_arcXYpolar(centre: Point, direction_polar: float, a: float, b: float, start_percentage: float=0.0, end_percentage: float=1.0, segments: int=100) -> list:
    steps = []
    steps.extend(cartesian_ellipse_arcXY(centre, a, b, start_percentage, end_percentage, segments))
    return move_polar(steps, centre, 0, direction_polar)

def cartesian_ellipseXY(centre: Point, a: float, b: float, segments: int=100, cw: bool=True) -> list:
    '''generate an ellipse, based on cartesian definition of an ellipse using y = b/a * sqrt(a^2 - x^2)
    '''
    steps = []

    if cw:
        half_ellipse_steps = cartesian_ellipse_arcXY(centre, a, b, 0.0, 1.0, segments)
        half_ellipse_steps.pop(-1)
        steps.extend(half_ellipse_steps)
        steps.extend(cartesian_ellipse_arcXY(centre, a, -b, 1.0, 0.0, segments))
    
    else:
        half_ellipse_steps = cartesian_ellipse_arcXY(centre, a, -b, 0.0, 1.0, segments)
        half_ellipse_steps.pop(-1)
        steps.extend(half_ellipse_steps)
        steps.extend(cartesian_ellipse_arcXY(centre, a, b, 1.0, 0.0, segments))

    return steps

def ellipse_arcXY(centre: Point, a: float, b: float, start_angle: float, arc_angle: float, segments: int=100) -> list:
    '''generate a partial ellipse based on trigonometric definition of an ellipse x = a*cos(t), y = b*sin(t), by default it will have 100 segments
    '''
    steps = []
    angle_increment = arc_angle/(segments)

    for point_index in range(segments+1):
        t = start_angle + point_index*angle_increment
        steps.append(Point(x=a*cos(t) + centre.x, y=b*sin(t) + centre.y, z=centre.z))

    return steps

def ellipseXY(centre: Point, a: float, b: float, start_angle: float, segments: int=100, cw: bool=False) -> list:
    '''generate an ellipse based on trigonometric definition of an ellipse x = a*cos(t), y = b*sin(t), by default it will have 100 segments and be drawn counter-clockwise
    '''
    steps = []

    if not(cw):
        steps = ellipse_arcXY(centre, a, b, start_angle, start_angle + tau, segments)
    
    else:
        steps = ellipse_arcXY(centre, a, b, start_angle, start_angle - tau, segments)

    return steps

def _quill_rachis_perimeterXY(
    start_point: Point, 
    quill_length: float, 
    quill_width: float, 
    rachis_length: float, 
    segments: int=100, 
    start_offset: float=0.0, 
    end_offset: float=0.0
    ) -> list:
    '''generate perimeter for the quill and rachis geometry
    '''
    steps = []
    steps.append(Point(x=start_point.x+start_offset, y=start_point.y+quill_width/2, z=start_point.z))
    steps.extend(ellipse_arcXY(Point(x=start_point.x+quill_length, y=start_point.y, z=start_point.z), 
                               a = rachis_length, 
                               b=quill_width/2, 
                               start_angle=pi/2,
                               arc_angle=-pi,
                               segments=segments
                               )
                )
    steps.append(Point(x=start_point.x+end_offset, y=start_point.y-quill_width/2, z=start_point.z))

    return steps

def quill_rachisXY(start_point: Point, quill_length: float, quill_width: float, rachis_length: float, extrusion_width: float, segments: int=100) -> list:
    '''generate multi-line quill + rachis
    '''
    steps = []
    final_quill_length = quill_length-extrusion_width/2
    final_quill_width = quill_width-extrusion_width
    final_rachis_length = rachis_length-extrusion_width/2
    perimeters = floor(final_quill_width/extrusion_width)

    for perimeter in range(perimeters):
        steps.extend(_quill_rachis_perimeterXY(start_point,
                                               quill_length=final_quill_length,
                                               quill_width=final_quill_width-extrusion_width*perimeter,
                                               rachis_length=final_rachis_length-2*extrusion_width*perimeter,
                                               segments=segments,
                                               start_offset=extrusion_width*perimeter-extrusion_width,
                                               end_offset=extrusion_width*perimeter
                                  )
                    )
    
    return steps

def single_line_quill_rachisXY(
    start_point: Point, 
    quill_length: float, 
    quill_width: float, 
    rachis_length: float, 
    max_extrusion_width: float=1.0, 
    segments: int=100,
    reverse: bool=True
    ) -> list:
    '''generate steps for printing a single line layer quill + rachis, width varying extrusion width
    '''
    steps = []

    if quill_width > max_extrusion_width:
        raise Exception("quill_width exceeds max_extrusion_width, decrease quill_width. If 3d printer is capable of extruding wider lines, increase max_extrusion_width accordingly")
    
    perimeter_geometry = cartesian_ellipse_arcXY(Point(x=0, y=0, z=0),
                                                 a=rachis_length,
                                                 b=quill_width/2,
                                                 start_percentage=1.0,
                                                 end_percentage=0.5,
                                                 segments=segments
                                                 )

    if reverse:
        steps.append(Point(x=start_point.x, y=start_point.y, z=start_point.z))
        steps.append(Point(x=start_point.x+1, y=start_point.y, z=start_point.z))
        for point in reversed(perimeter_geometry):
            #print("extrusion width=", str(2*point.y))
            steps.append(ExtrusionGeometry(width=2*point.y))
            steps.append(Point(x=point.x+start_point.x+quill_length,
                            y=start_point.y,
                            z=start_point.z
                            )
                        )
    
    else:
        for point in perimeter_geometry:
            #print("extrusion width=", str(2*point.y))
            steps.append(ExtrusionGeometry(width=2*point.y))
            steps.append(Point(x=point.x+start_point.x+quill_length,
                            y=start_point.y,
                            z=start_point.z
                            )
                        )
        steps.append(Point(x=start_point.x, y=start_point.y, z=start_point.z))

    return steps

def single_line_quill_rachis3D(
    start_point: Point, 
    quill_length: float, 
    quill_width: float, 
    quill_height: float,
    EH: float,
    rachis_length: float, 
    afterfeather_length: float = 0,
    max_extrusion_width: float=1.0, 
    segments: int=100,
    z_lift: float = 0
    ) -> list:
    '''[WORK IN PROGRESS] 3D single line quill + rachis 
    '''
    
    # generate rachis and quill
    rachis_steps = []
    rachis_steps.append(ExtrusionGeometry(height=EH))
    
        # travel to begin of rachis
    rachis_steps.extend(travel_to(Point(x=quill_length+afterfeather_length+rachis_length, 
                                        y=0, 
                                        z=start_point.z+z_lift
                                        )
                                    )
                        )
    rachis_steps.extend(travel_to(Point(x=quill_length+afterfeather_length+rachis_length, 
                                        y=0, 
                                        z=start_point.z
                                        )
                                    )
                        )
    
    for  layer in range(segments):
        # find x in an ellipse: x = a/b * sqrt(b^2 - y^2)
        # use to get x for rachis_length (to get a rounded tip) and quill_width (to get rounded quill)
        z=quill_height*layer/(segments)
        x = rachis_length/(quill_height) * sqrt((quill_height)**2 - z**2)
        
        #print('height: '+ str(z))
    
        if quill_width > max_extrusion_width:
            raise Exception("quill_width exceeds max_extrusion_width, decrease quill_width. If 3d printer is capable of extruding wider lines, increase max_extrusion_width accordingly")

        perimeter_geometry = cartesian_ellipse_arcXY(Point(x=0, y=0, z=0),
                                                a=rachis_length,
                                                b=quill_width/2,
                                                start_percentage=1.0,
                                                end_percentage=0.5,
                                                segments=segments
                                                )

        for point in perimeter_geometry:
            rachis_steps.append(ExtrusionGeometry(width=2*point.y, height=z))
            rachis_steps.append(Point(x=start_point.x+quill_length+x,
                                y=start_point.y,
                                z=start_point.z+EH+z
                                )
                        )

            rachis_steps.append(Point(x=start_point.x, y=start_point.y, z=start_point.z))
    return rachis_steps
    