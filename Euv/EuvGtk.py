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

def image_button(stock,size=gtk.ICON_SIZE_BUTTON):
  image = gtk.Image()
  image.set_from_stock(stock,size)
  b = gtk.Button()
  b.set_image(image)
  b.set_label("")
  return b

class App(gtk.Window):
  """
  The application.
  """
  def __init__(self,
               size=None,
               view_port_center=(0,0),
               view_port_width=None,
               view_port_height=None,
               recording=True,
               max_num_frames=None):
    gtk.gdk.threads_init()

    if size is None:
      size= (800,600)
    self.view_port_center = view_port_center
    if view_port_width == None and view_port_height==None:
      raise Exception("Either view_port_width or view_port_height must be set!")
    self.view_port_width = view_port_width
    self.view_port_height = view_port_height

    super(App,self).__init__(gtk.WINDOW_TOPLEVEL)
    
    settings = gtk.settings_get_default()
    settings.set_long_property("gtk-button-images", 1, '*')

    self.set_resizable(True)
    self.vbox = gtk.VBox(False,0)
    self.add(self.vbox)
    self.canvas = gtk.DrawingArea()
    self.set_default_size(size[0],size[1])
    self.canvas.connect("expose_event", self.on_canvas_expose)
    self.vbox.pack_start(self.canvas, True,True,0)
    hbox = gtk.HBox(False,0)
    self.vbox.pack_start(hbox, False,True,0)
    self.recording = recording
    if recording:
      self.buttonbox = gtk.HBox(False,0)
      hbox.pack_start(self.buttonbox, True,False,0)
      self.button_previous = image_button(stock=gtk.STOCK_MEDIA_REWIND)
      self.button_previous.connect("clicked", self.on_button_previous_clicked)
      self.buttonbox.pack_start(self.button_previous, False,False,0)
  
      self.button_pause = image_button(stock=gtk.STOCK_MEDIA_PAUSE)
      self.button_pause.connect("clicked", self.on_button_pause_clicked)
      self.buttonbox.pack_start(self.button_pause, False,False,0)
  
      self.button_next = image_button(stock=gtk.STOCK_MEDIA_FORWARD)
      self.button_next.connect("clicked", self.on_button_next_clicked)
      self.buttonbox.pack_start(self.button_next, False,False,0)
  
      self.frame_scale = gtk.HScale()
      self.frame_adjustment = self.frame_scale.get_adjustment()
      self.frame_scale.set_digits(0)
      self.frame_adjustment.connect("value-changed",self.on_frame_adjustment_value_changed)
      self.frame_scale.set_size_request(400,-1)
      self.buttonbox.pack_start(self.frame_scale, True,True,0)
      if not max_num_frames is None:
        self.set_max_num_frames(max_num_frames)

    self.connect("delete_event", self.on_delete_event)
    self._user_break = False
    self.frames = []
    self.current_frame = -1
    self.pause=False

  def app_quit(self):
    self._user_break = True
    self.hide()
    gtk.main_quit()

  def on_button_pause_clicked(self, widget):
    self.pause = not self.pause

  def on_button_next_clicked(self, widget):
    if self.current_frame < len(self.frames)-1:
      self.set_current_frame(self.current_frame+1)

  def on_button_previous_clicked(self, widget):
    if self.current_frame > 0:
      self.set_current_frame(self.current_frame-1)

  def on_button_clicked(self, widget):
    self.app_quit()

  def on_delete_event(self, widget, event):
    self.app_quit()

  def on_frame_adjustment_value_changed(self,adjustment):
    new_frame = int(adjustment.value)
    if new_frame < len(self.frames):
      self.set_current_frame(new_frame)

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

  def get_max_num_frames(self):
    return self.frame_adjustment.get_property("upper")

  def set_max_num_frames(self, max_num_frames):
    self.frame_adjustment.set_property("upper",max_num_frames)

  def set_current_frame(self, index):
    self.current_frame = index
    if self.recording:
      self.frame_adjustment.set_value(index)
    gobject.idle_add(self.redraw)
    
  def add_frame(self, frame):
    if self.recording:
      self.frames.append(frame)
      num_frames = len(self.frames)-1
      max_frames = self.get_max_num_frames()
      if len(self.frames)-1 > self.get_max_num_frames():
        self.set_max_num_frames(num_frames)

    if self.recording:
      if not self.pause:
        self.set_current_frame(len(self.frames)-1)
    else:
      self.frames=[frame]
      self.set_current_frame(0)

  def on_canvas_expose(self,widget,event):
    cr = widget.window.cairo_create()
    
    # set a clip region for the expose event
    cr.rectangle(event.area.x, event.area.y,
                      event.area.width, event.area.height)
    cr.clip()

    width,height = (self.canvas.allocation.width,
                    self.canvas.allocation.height)
    # Scale
    if not self.view_port_width is None:
      sx = sy = 1.0*width/self.view_port_width
    else:
      sx = sy = 1.0*height/self.view_port_height

    cr.translate(width/2-self.view_port_center[0]*sx,
                 height/2-self.view_port_center[1]*sy)

    cr.scale(sx,sy)

    if self.current_frame < 0:
      return

    # Draw the current frame
    for dc in self.frames[self.current_frame].display_list:
      if 'color' in dc:
        self.rgb = dc['color'].rgb()
        if 'alpha' in dc:
          cr.set_source_rgba(self.rgb[0],self.rgb[1],self.rgb[2],dc['alpha'])
        else:
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
        cr.set_line_width(dc['linewidth'])
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
               view_port_width=None,
               recording=True,
               max_num_frames=None):
    # init gtk
    # Start the gtk application in a different thread
    self.app=App(size=size,
                 view_port_center=view_port_center,
                 view_port_width=view_port_width,
                 recording=recording,
                 max_num_frames=max_num_frames)
    self.t = Viewer.MyThread(self.app)
    self.t.start()
    self.frames = []

  def wait(self):
    self.app.set_current_frame(0)
    self.t.join()

  def user_break(self):
    """Whether the user has quit the application"""
    return self.app.user_break()

  def set_text(self, text):
    """Change the text in the viewer"""
    self.app.idle_set_text(text)

  def add_frame(self,frame):
    self.app.add_frame(frame)

  def set_max_num_frames(self,max_num_frames):
    self.app.set_max_num_frames(max_num_frames)
