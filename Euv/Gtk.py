import Euv
import gtk
import cairo
import threading
import gobject
import Frame
import math

def get_val_default(hash,key,default):
  try:
    val = hash[key]
  except KeyError:
    val = default
  return val

class App(gtk.Window):
  """
  The application.
  """
  def __init__(self,
               size=None,
               view_port_center=(0,0),
               view_port_width=None,
               view_port_height=None):
    gtk.gdk.threads_init()

    if size is None:
      size= (800,600)
    self.view_port_center = view_port_center
    if view_port_width == None and view_port_height==None:
      raise Exception("Either view_port_width or view_port_height must be set!")
    self.view_port_width = view_port_width
    self.view_port_height = view_port_height

    super(App,self).__init__(gtk.WINDOW_TOPLEVEL)
    self.set_resizable(True)
    self.vbox = gtk.VBox(False,0)
    self.add(self.vbox)
    self.canvas = gtk.DrawingArea()
    self.set_default_size(size[0],size[1])
    self.canvas.connect("expose_event", self.on_canvas_expose)
    self.vbox.pack_start(self.canvas, True,True,0)
    self.button = gtk.Button("Quit")
    self.button.connect("clicked", self.on_button_clicked)
    self.vbox.pack_start(self.button, False,False,0)
    self.connect("delete_event", self.on_delete_event)
    self._user_break = False
    self.frames = []
    self.current_frame = None

  def app_quit(self):
    self._user_break = True
    self.hide()
    gtk.main_quit()

  def on_button_clicked(self, widget):
    self.app_quit()

  def on_delete_event(self, widget, event):
    self.app_quit()

  # The following pair are needed for any external request for
  # viewer change. The cb_* routine is needed for the actual action.
  # The idle_set receives the request from one thread and passes it
  # to the gtk thread.
  def cb_set_text(self, text):
    self.button.set_label(text)

  def idle_set_text(self, text):
    gobject.idle_add(self.cb_set_text, text)

  def user_break(self):
    return self._user_break

  def redraw(self):
    width,height = (self.canvas.allocation.width,
                    self.canvas.allocation.height)
    self.canvas.queue_draw_area(0,0,width,height)

  def set_current_frame(self, frame):
    self.current_frame = frame
    gobject.idle_add(self.redraw)
    
  def add_frame(self, frame):
    self.frames.append(frame)
    self.set_current_frame(frame)

  def on_canvas_expose(self,widget,event):
    cr = widget.window.cairo_create()
    
    # set a clip region for the expose event
    cr.rectangle(event.area.x, event.area.y,
                      event.area.width, event.area.height)
    cr.clip()

    # Scale
    width,height = (self.canvas.allocation.width,
                    self.canvas.allocation.height)
    cr.translate(width/2-self.view_port_center[0],
                      height/2-self.view_port_center[0])

    if not self.view_port_width is None:
      cr.scale(1.0*width/self.view_port_width,
                    1.0*width/self.view_port_width)
    else:
      cr.scale(1.0*height/self.view_port_height,
                    1.0*height/self.view_port_height)

    if self.current_frame is None:
      return

    # Draw the current frame
    for dc in self.current_frame.display_list:
      if 'color' in dc:
        self.rgb = dc['color'].rgb()
        cr.set_source_rgb(*self.rgb)

      if dc['type']==Frame.DrawingCommandCircle:
        radius = get_val_default(dc,'radius',10)
        cr.arc(dc['pos'][0], dc['pos'][1], radius, 0, 2.0 * math.pi)
        cr.fill()
      elif dc['type']==Frame.DrawingCommandPolygons:
        cr.new_path()
        for poly in dc['polygons']:
          cr.move_to(*poly[0])
          for p in poly[1:]:
            cr.line_to(*p)
        cr.fill()
      elif dc['type']==Frame.DrawingCommandLines:
        for line in dc['lines']:
          cr.move_to(*line[0])
          for p in line[1:]:
            cr.line_to(*p)
        cr.stroke()
      elif dc['type']==Frame.DrawingCommandText:
        if 'face' in dc:
          cr.select_font_face(dc['face'],
                              cairo.FONT_SLANT_NORMAL,
                              cairo.FONT_WEIGHT_NORMAL)
        if 'size' in dc:
          cr.set_font_size(dc['size'])
        cr.move_to(dc['pos'][0],dc['pos'][1])
        cr.show_text(dc['text'])

class Viewer:
  class MyThread(threading.Thread):
    """The thread.
    """
    def __init__(self, app):
      super(Viewer.MyThread,self).__init__()
      self.app=app
  
    def run(self):
      """Show application and run gtk.main"""
      self.app.show_all()
      gtk.main()

  def __init__(self,
               size=None,
               view_port_center=(0,0),
               view_port_width=None):
    # init gtk
    # Start the gtk application in a different thread
    self.app=App(size=size,
                 view_port_center=view_port_center,
                 view_port_width=view_port_width)
    self.t = Viewer.MyThread(self.app)
    self.t.start()
    self.frames = []

  def wait(self):
    self.t.join()

  def user_break(self):
    """Whether the user has quit the application"""
    return self.app.user_break()

  def set_text(self, text):
    """Change the text in the viewer"""
    self.app.idle_set_text(text)

  def add_frame(self,frame):
    self.app.add_frame(frame)

