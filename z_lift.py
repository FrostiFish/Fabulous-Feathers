from fullcontrol import Point, travel_to, Union

def z_lift(geometry: Union[Point, list], lift_height: float) -> list:
    '''lift z from Point or last position in provided geometry, extend to geometry
    '''
    if type(geometry) == list:
        final_point_index = max(index for index, item in enumerate(geometry) if type(item) == Point)
        return travel_to(Point(x=geometry[final_point_index].x, y=geometry[final_point_index].y, z=geometry[final_point_index].z+lift_height))
    else:
        return travel_to(Point(x=geometry.x, y=geometry.y, z=geometry.z+lift_height))

def z_unlift(geometry: Union[Point, list], lift_height: float) -> list:
    '''unlift z from Point or last position in provided geometry, extend to geometry
    '''
    if type(geometry) == list:
        final_point_index = max(index for index, item in enumerate(geometry) if type(item) == Point)
        return travel_to(Point(x=geometry[final_point_index].x, y=geometry[final_point_index].y, z=geometry[final_point_index].z-lift_height))
    else:
        return travel_to(Point(x=geometry.x, y=geometry.y, z=geometry.z-lift_height))