# Description

The EuclideanGeometryViewer (or Euv for short) is a python module for displaying 2D graphics animation. It is based on the concept of frames, which is composed of a number of geometrical objects.

It was developed in 2012 as a graphics framework (scratching my own itch) for the udacity course "How to Build a Self Driving Car".

The graphics is shown using Gtk.

# Installation

This module is installed as a standard python module.

# Usage

    import Euv.Frame as Frame
    import Euv.EuvGtk as Euv
    import Euv.Color as Color
    import time
    
    v = Euv.Viewer(size=(800,600),
                   view_port_center = (0,0),
                   view_port_width = 800)
    
    for i in range(10):
        f = Frame.Frame()
        x = 800 * (i-5)/10.0
        f.add_circle(pos=(x,x),
                     color="red",
                     radius=3)
        f.add_text(pos=(250,200),
                   face="Sans",
                   size=20,
                   text="Frame %d"%i,
                   color=Color.Color("darkgreen"))
        if v.user_break():
          break
        v.add_frame(f)
        time.sleep(1.0/25)
    v.wait()

# License

This script is released under the LGPL licence version 3.0

# Author

Dov Grobgeld <dov.grobgeld@gmail.com>
Sun Jan 19 2025
