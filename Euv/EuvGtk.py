import Euv
import gtk
import cairo
import pango
import pangocairo
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

def set_image_for_button(stock, button):
  image = gtk.Image()
  image.set_from_stock(stock,gtk.ICON_SIZE_BUTTON)
  button.set_image(image)

def image_button(stock):
  b = gtk.Button()
  set_image_for_button(stock, b)
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
               max_num_frames=None,
               flip_y=False,
               title = 'Euv',
               time_step = 0.1):
    gobject.threads_init()
    gtk.gdk.threads_init()

    if size is None:
      size= (800,600)
    self.view_port_center = view_port_center
    if view_port_width == None and view_port_height==None:
      raise Exception("Either view_port_width or view_port_height must be set!")
    self.view_port_width = view_port_width
    self.view_port_height = view_port_height

    super(App,self).__init__(gtk.WINDOW_TOPLEVEL)
    self.set_title(title)
    
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
    self.flip_y = flip_y
    self.time_step = time_step
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
    self.pause = False
    gobject.timeout_add(int(self.time_step*1000), self.play)

  def play(self):
    if not self.pause:
      if self.current_frame < len(self.frames)-1:
        self.set_current_frame(self.current_frame + 1)
    return True

  def app_quit(self):
    self._user_break = True
    self.hide()
    gtk.main_quit()

  def on_button_pause_clicked(self, widget):
    self.pause = not self.pause
    if self.pause:
      set_image_for_button(gtk.STOCK_MEDIA_PLAY, self.button_pause)
    else:
      set_image_for_button(gtk.STOCK_MEDIA_PAUSE, self.button_pause)

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
    if new_frame != self.current_frame:
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
    
  def set_max_num_frames_t(self, max_num_frames):
    self.frame_adjustment.set_property("upper",max_num_frames-1)

  def set_max_num_frames(self, max_num_frames):
    gobject.idle_add(self.set_max_num_frames_t, max_num_frames)

  def set_current_frame(self, index):
    self.current_frame = index
    if self.recording:
      gobject.idle_add(self.frame_adjustment.set_value, index)
    gobject.idle_add(self.redraw)
    
  def add_frame(self, frame):
    if self.recording:
      self.frames.append(frame)
      num_frames = len(self.frames)
      self.set_max_num_frames(num_frames)
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

    if self.flip_y:
      sy = -sy
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
        if 'closepath' in dc:
          cr.close_path()
        cr.stroke()
      elif dc['type']==Frame.DrawingCommandText:
        if 'markup' in dc:
          pango_ctx = pangocairo.CairoContext(cr)
          layout = pango_ctx.create_layout()
          face = dc['face'] if 'face' in dc else 'Sans'
          layout.set_font_description(pango.FontDescription(face))
          layout.set_markup(dc['markup'])
          cr.save()
          cr.translate(dc['pos'][0],dc['pos'][1])
          cr.move_to(0,0)
          
          if 'align' in dc:
            s = 1.0/pango.SCALE
            ink_box,log_box = layout.get_extents()
            text_width,text_height = s*log_box[2],s*log_box[3]

            if dc['align'].lower() == 'center':
              ink_box,log_box = layout.get_extents()
              cr.move_to(-text_width/2,0)
              layout.set_alignment(pango.ALIGN_CENTER)
            elif dc['align'].lower() == 'right':
              ink_box,log_box = layout.get_extents()
              cr.move_to(-text_width,0)
              layout.set_alignment(pango.ALIGN_RIGHT)

          if self.flip_y:
            cr.scale(1,-1)
          if 'scale' in dc:
            cr.scale(dc['scale'],dc['scale'])
          pango_ctx.show_layout(layout)
          cr.restore()
        else:
          if 'face' in dc:
            weight = cairo.FONT_WEIGHT_NORMAL
            if "bold" in dc['face'].lower():
              weight = cairo.FONT_WEIGHT_BOLD
            cr.select_font_face(dc['face'],
                                cairo.FONT_SLANT_NORMAL,
                                weight)
          if 'size' in dc:
            cr.set_font_size(dc['size'])
          cr.save()
          cr.translate(dc['pos'][0],dc['pos'][1])
          cr.move_to(0,0)
          if self.flip_y:
            cr.scale(1,-1)
          cr.show_text(dc['text'])
          cr.restore()

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
      gtk.threads_enter()
      gtk.main()
      gtk.threads_leave()

  def __init__(self,
               size=None,
               view_port_center=(0,0),
               view_port_width=None,
               recording=True,
               max_num_frames=None,
               flip_y=False,
               time_step = 0.1):
    # init gtk
    # Start the gtk application in a different thread
    self.app=App(size=size,
                 view_port_center=view_port_center,
                 view_port_width=view_port_width,
                 recording=recording,
                 max_num_frames=max_num_frames,
                 flip_y = flip_y,
                 time_step = time_step)
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
