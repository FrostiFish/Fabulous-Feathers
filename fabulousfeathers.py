from fullcontrol import Point, travel_to, ExtrusionGeometry, Printer, Vector, move, PrinterCommand
from math import floor
from fabuloushelpers import vaneXY, cartesian_ellipse_arcXY, single_line_quill_rachisXY
from z_lift import z_lift

class FabulousFeather:
    def __init__(self, 
                 start_point: Point, 
                 EW: float, 
                 EH: float, 
                 barb_spacing: float, 
                 barb_quill_connection: float, 
                 vane_width: float, 
                 vane_rachis_extent: float,
                 rachis_length: float,
                 quill_length: float,
                 quill_width: float,
                 quill_EH: float,
                 quill_height: float,
                 afterfeather_angle: float,
                 afterfeather_length: float,
                 afterfeather_extent: float,
                 z_lift: float,
                 wipe_distance: float = 0,
                 vane_speed: float = 1000,
                 quill_speed: float = 100,
                 retraction: bool = False
                 ) -> None:
        self.start_point = start_point
        self.EW = EW
        self.EH = EH
        self.barb_spacing = barb_spacing
        self.barb_quill_connection = barb_quill_connection
        self.vane_width = vane_width
        self.vane_rachis_extent = vane_rachis_extent
        self.rachis_length = rachis_length
        self.quill_length = quill_length
        self.quill_width = quill_width
        self.quill_EH = quill_EH
        self.quill_height = quill_height
        self.afterfeather_angle = afterfeather_angle
        self.afterfeather_length = afterfeather_length
        self.afterfeather_extent = afterfeather_extent
        self.z_lift = z_lift
        self.wipe_distance = wipe_distance
        self.vane_speed = vane_speed
        self.quill_speed = quill_speed
        self.retraction = retraction
    
    def steps(self) -> list:
        '''return steps for the feather
        '''
        
        steps = []
        steps.append(ExtrusionGeometry(area_model='rectangle', width=self.EW, height=self.EH))
        steps.append(Printer(print_speed=self.vane_speed))

        # generate first half of afterfeather
        afterfeather_count = floor(self.afterfeather_length/(self.EW+self.barb_spacing))
        afterfeather_inner_geometry = []
        for afterfeather_index in range(afterfeather_count):
            afterfeather_inner_geometry.append(Point(x=self.quill_length+self.afterfeather_length%(self.EW+self.barb_spacing)+afterfeather_index*(self.EW+self.barb_spacing), 
                                                    y=self.quill_width/2 - self.barb_quill_connection, 
                                                    z=self.EH
                                                    )
                                            )
            
        afterfeather_outer_geometry = cartesian_ellipse_arcXY(centre=Point(x=self.quill_length+self.afterfeather_length, y=0, z=self.EH), 
                                                    a=self.afterfeather_length + self.afterfeather_extent,
                                                    b=self.vane_width/2,
                                                    start_percentage=0.35,
                                                    end_percentage=0.5,
                                                    segments=afterfeather_count
                                                    )
        afterfeather_outer_geometry.pop(-1)

        prevane_afterfeather_steps = vaneXY(afterfeather_inner_geometry, afterfeather_outer_geometry)
        steps.extend(prevane_afterfeather_steps)

        # generate main vane
        barb_count_per_side = floor(self.rachis_length/(self.EW+self.barb_spacing))

        vane_outer_geometry = cartesian_ellipse_arcXY(centre=Point(x=self.quill_length+self.afterfeather_length, y=0, z=self.EH), 
                                                        a=self.rachis_length + self.vane_rachis_extent,
                                                        b=self.vane_width/2,
                                                        start_percentage=0.5,
                                                        end_percentage=0.98,
                                                        segments=barb_count_per_side,
                                                        mirror=True
                                            )

        vane_inner_geometry = cartesian_ellipse_arcXY(centre=Point(x=self.quill_length+self.afterfeather_length, y=0, z=self.EH),
                                                        a=self.rachis_length,
                                                        b=self.quill_width/2-self.barb_quill_connection,
                                                        start_percentage=0.5,
                                                        end_percentage=1.0,
                                                        segments=barb_count_per_side,
                                                        mirror=True
                                            )

        steps.extend(vaneXY(start_geometry=vane_inner_geometry, end_geometry=vane_outer_geometry))

        # generate reflected part of afterfeather
        reflected_afterfeather_inner_geometry = []
        for afterfeather_index in range(afterfeather_count):
            reflected_afterfeather_inner_geometry.append(Point(x=self.quill_length+self.afterfeather_length%(self.EW+self.barb_spacing)+afterfeather_index*(self.EW+self.barb_spacing), 
                                                    y=-self.quill_width/2+self.barb_quill_connection, 
                                                    z=self.EH
                                                    )
                                            )
        reflected_afterfeather_inner_geometry.reverse()

        reflected_afterfeather_outer_geometry = cartesian_ellipse_arcXY(centre=Point(x=self.quill_length+self.afterfeather_length, y=0, z=self.EH), 
                                                    a=self.afterfeather_length + self.afterfeather_extent,
                                                    b=-self.vane_width/2,
                                                    start_percentage=0.35,
                                                    end_percentage=0.5,
                                                    segments=afterfeather_count
                                                    )
        reflected_afterfeather_outer_geometry.pop(-1)
        reflected_afterfeather_outer_geometry.reverse()


        postvane_afterfeather_steps = vaneXY(reflected_afterfeather_inner_geometry, reflected_afterfeather_outer_geometry)

        steps.extend(postvane_afterfeather_steps)
        
        if self.retraction:
                steps.append(PrinterCommand(id='retract'))

        # lift z
        steps.extend(z_lift(steps, self.z_lift))

        # generate rachis and quill
        rachis_steps = []
        rachis_steps.append(ExtrusionGeometry(height=self.quill_EH))
        rachis_layers = round(self.quill_height/self.quill_EH)
        for  layer in range(rachis_layers):
            rachis_layer_steps = []
            # travel to begin of rachis
            rachis_steps.extend(travel_to(Point(x=self.quill_length+self.afterfeather_length+(self.rachis_length+0.25-self.rachis_length/4*layer), 
                                                y=0, 
                                                z=(self.quill_EH+layer*self.quill_EH)+self.z_lift
                                                )
                                          )
                                )
            if self.retraction:
                rachis_layer_steps.append(PrinterCommand(id='unretract'))
            # draw rachis layer
            rachis_layer_steps.extend(single_line_quill_rachisXY(Point(x=0, y=0, z=self.EH+layer*self.quill_EH), 
                                                                 quill_length=self.quill_length+self.afterfeather_length, 
                                                                 quill_width=self.quill_width-self.quill_width/10*layer, 
                                                                 rachis_length=self.rachis_length+0.25-self.rachis_length/4*layer ,
                                                                 max_extrusion_width=self.quill_width,
                                                                 segments=int(self.rachis_length*4)
                                                                 )
                            )
            # wipe nozzle
            rachis_layer_steps.extend(travel_to(Point(x=rachis_layer_steps[-1].x+self.wipe_distance, 
                                                      y=rachis_layer_steps[-1].y, 
                                                      z=rachis_layer_steps[-1].z
                                                      )
                                                )
                                      )
            
            if self.retraction:
                rachis_layer_steps.append(PrinterCommand(id='retract'))

            # lift z
            rachis_layer_steps.extend(z_lift(rachis_layer_steps, self.z_lift))
            rachis_steps.extend(rachis_layer_steps)
            

        steps.append(Printer(print_speed=self.quill_speed))
        steps.extend(rachis_steps)

        steps = move(steps, Vector(x=self.start_point.x, y=self.start_point.y))
        
        return steps