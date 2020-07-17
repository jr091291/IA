# -*- coding: utf-8 -*-

class Colors:
  def __init__(self, colors = []) :
    self.string_colors = ""
    self.colors = list(set(colors))
    self._init_string_list_colors()

  def _init_string_list_colors(self):
      self.string_colors = ",".join(self.colors)
    
  def validate_color(self, color: str)-> bool :
    if self.string_colors.find(color.strip().lower()) < 0:
      return False
    return True

  def extract_color(self, color: str, number_items = 1):
    try:
      result = []
      for item in self.colors:
        if str(color).find(str(item)) >= 0:
          result.append(item)
  
      result = list(set(result))
      return ','.join(result[:number_items]) if result else None
    except Exception as e:
      print('Error extract color {}'.format(e))
      return None

