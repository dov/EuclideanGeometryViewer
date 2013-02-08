import Euv.Frame as Frame
import Euv.EuvGtk as Euv
import Euv.Color as Color
import Euv.Shapes as Shapes
import time
import math

N=200
v = Euv.Viewer(size=(800,600),
               view_port_center = (0,0),
               view_port_width = 800,
               max_num_frames=N,
               recording=True,
               flip_y = True)
for i in range(N):
    f = Frame.Frame()
    x = 400 * 1.0*(i-N/2)/N
    n = 40
    for j in range(n):
      f.add_circle(pos=(x+j*5,20*math.sin(2*math.pi*(i+j)/n)),
                   color=Color.Color("red"),
                   radius=3)
    f.add_lines(color=Color.Color("midnightblue"),
                lines=[[(x+5,105),(x+35,105)]])
    f.add_polygons(color=Color.Color("magenta3"),
                   polygons = [[(x,100),
                                (x+10,100),
                                (x+5,110)],
                               [(x+30,100),
                                (x+40,100),
                                (x+35,110)],
                               ])
    arw = Shapes.arrow_head_polygon((x,-25),
                                    scale=10)
    rect = Shapes.rotated_rectangle((x,-150),
                                    width=50,
                                    height=10,
                                    angle=-1.0*i/N * math.pi*2,
                                    )
    wheels = Shapes.rectangle_pair((x,-25),
                                   5.,2.,7.,
                                   left_angle = 1.0*i/N * math.pi*2,
                                   scale=10)
    f.add_polygons(polygons = [arw,
                               rect],
                   color="cyan",
                   alpha=0.5)
    f.add_polygons(polygons = wheels,
                   color="black",
                   alpha=0.7)

    f.add_text(pos=(250,200),
               face="Serif 18",
               markup=("<big>Frame %d</big>\n"%i
                       + "A <b>bold</b> line\n"
                         "Greek: &#945;\n"
                         "<span fgcolor=\"red\">R</span>"
                         "<span fgcolor=\"green\">G</span>"
                         "<span fgcolor=\"blue\">B</span>"),
               align='center',
               color=Color.Color("darkgreen"))
    if v.user_break():
      break
    v.add_frame(f)
    time.sleep(1.0/40)

v.wait()


