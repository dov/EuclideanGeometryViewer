import Color

class DrawingCommandCircle:
  def __repr__(self):
    return "DrawingCommandCircle"

class DrawingCommandText:
  def __repr__(self):
    return "DrawingCommandText"

class DrawingCommandPolygons:
  def __repr__(self):
    return "DrawingCommandPolygons"

class DrawingCommandLines:
  def __repr__(self):
    return "DrawingCommandLines"

class Frame:
  def __init__(self):
    self.display_list = []
    self.current_color = Color.Color("red")

  def add_circle(self,
                 color=None,
                 pos=(0,0),
                 radius = None):
    Cmd = { "type":DrawingCommandCircle,
            "pos":pos}
    if not radius is None:
      Cmd['radius']=radius
    if not color is None:
      Cmd['color'] = color
    self.display_list += [Cmd]

  def add_text(self,
               face = None,
               size = None,
               pos = (0,0),
               text = None,
               color=None):
    
    Cmd = { "type":DrawingCommandText,
            "pos":pos,
            "text":text}
    if not face is None:
      Cmd['face']=face
    if not size is None:
      Cmd['size']=size
    if not color is None:
      Cmd['color']=color
    self.display_list += [Cmd]

  def add_polygons(self,
                   polygons=None,
                   color=None,
                   alpha=None):
    
    if polygons is None:
      return
    Cmd = { "type":DrawingCommandPolygons,
            "polygons":polygons  };
    if not color is None:
      Cmd['color']=color
    if not alpha is None:
      Cmd['alpha']=alpha
    self.display_list += [Cmd]

  def add_lines(self,
                lines=None,
                color=None):
    
    if lines is None:
      return
    Cmd = { "type":DrawingCommandLines,
            "lines":lines  };
    if not color is None:
      Cmd['color']=color
    self.display_list += [Cmd]

  def set_color(self,
                color = Color.Color("red")):
    self.display_list += [{'color':color}]
  
    
    
