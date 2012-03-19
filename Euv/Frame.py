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

  def _add_command(self, cmd_type, generic_params, **kwargs):
    # Set defaults
    Cmd = { 'linewidth':1.0,
            'color':Color.Color("red") }

    # TBD - Check generic parameters against known params

    # Override
    for k in generic_params:
      if generic_params[k] is None:
        continue
      if k == 'color':
        Cmd[k] = Color.Color(generic_params[k])
      else:
        Cmd[k] = generic_params[k]

    # Set type
    Cmd['type'] = cmd_type

    # Set specific params
    for k in kwargs:
      if kwargs[k] is None:
        continue
      Cmd[k] = kwargs[k]

    self.display_list.append(Cmd)
    
  def add_circle(self,
                 pos=(0,0),
                 radius = 1,
                 **kwargs):

    self._add_command(DrawingCommandCircle,
                      kwargs,
                      pos=pos,
                      radius=radius)

  def add_text(self,
               face = None,
               size = None,
               pos = (0,0),
               text = None,
               **kwargs):
    self._add_command(DrawingCommandText,
                      kwargs,
                      face=face,
                      size=size,
                      text=text,
                      pos=pos)

  def add_polygons(self,
                   polygons=None,
                   **kwargs):
    self._add_command(DrawingCommandPolygons,
                      kwargs,
                      polygons=polygons)

  def add_lines(self,
                lines=None,
                **kwargs):
    self._add_command(DrawingCommandLines,
                      kwargs,
                      lines=lines)

