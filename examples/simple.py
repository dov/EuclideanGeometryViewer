#!/usr/bin/python

import Euv.Frame as Frame
import Euv.EuvGtk as Euv
import Euv.Color as Color
import time

v = Euv.Viewer(size=(800,600),
               view_port_center = (0,0),
               view_port_width = 800)

N = 1000
for i in range(N):
    f = Frame.Frame()
    x = 600. * (i-N/2)/N
    f.add_circle(pos=(x,x),
                 color="red",
                 alpha=0.5,
                 radius=15)
    f.add_circle(pos=(-x,x),
                 color="blue",
                 alpha=0.5,
                 radius=15)
    f.add_text(pos=(250,200),
               face="Sans",
               size=20,
               text="Frame %d"%i,
               color=Color.Color("darkgreen"))
    if v.user_break():
      break
    v.add_frame(f)
v.wait()
