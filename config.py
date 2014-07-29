"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import os


"""
  Useful piece for debugging
  
  import code; code.interact(local=locals())
"""

class Config(object):
  """
    Configuration for application
  """
  
  def __init__(self):
    self.debug = 'off'
    self.rtmp = {}
    self.video = {}
    self.search = {}
    
  def load_defaults(self):
    """
      Load a default configuration
    """
    
    # Print debugging information. Values can be 'info', 'warning', 'off'
    # self.debug = 'info'

    self.single = {
      'id': ''
    }
    
    self.site = {
      'url' : 'http://viki.com',
    }
    
    self.rtmp = {
      'swf' : 'http://a0.vikiassets.com/1338547542/swfs/vikiplayer.swf?1338547542',
      'page_url' : 'http://www.viki.com',
      'start' : 0,
      'timeout' : 60
    }
    
    self.video = {
      # Do not download any videos
      'skip' : False,
      'out' : '.',
      'episode_start' : 0,
      'episode_end' : 99,
      # Use RTMP instead of HTTP for video transfer
      'rtmp' : False,
      # Allowed resolutions, split by comma.
      # This will be cleaned into a list (ie. ['1080', '720', '480', '360', '240'])
      'resolutions' : '1080,720,480,360,240'
    }
    
    self.subtitles = {
      # Do not download any subtitles
      'skip' : False,
      'out' : '.',
      'url' : 'http://www.viki.com/subtitles/media_resource/%d/en.json',
      'check_parts' : False
    } 
    
    self.search = {
      'query' : '',
      'url' : 'http://www.viki.com/search?utf8=%E2%9C%93&q=',
      
      # 'exact', 'exact-ignore-case', 'fuzzy' or 'regex'
      'method' : 'exact-ignore-case'
    }
  
  def purify(self):
    """
      Clean up any values, so the rest of the application
      can expect a consistent contract
      
      Configuration must be setup, before this configuration can run.
      Use load_default, if you're unsure of this
      
      ie. a path must end with os.path.sep
    """
    
    def fix_path_separators(path):
      """
        Replace path separators with operating system specific versions
        
        Append a path separator to the end
      """
      path = path.replace('/', os.path.sep).replace('\\', os.path.sep)
      if not path.endswith(os.path.sep):
        path += os.path.sep
        
      return path
      
    def string_to_bool(s):
      """
        Convert a string to a boolean.
        
        If the value is not a string, then its original value
        as a boolean is returned
      """
      if s == 'true':
        return True
      elif s == 'false':
        return False
      else:
        return bool(s)
    
    self.video['out'] = fix_path_separators(self.video['out'])
    
    self.video['episode_start'] = max(int(self.video['episode_start']) - 1, 0)
    self.video['episode_end'] = int(self.video['episode_end'])
    self.video['rtmp'] = string_to_bool(self.video['rtmp'])
    self.video['skip'] = string_to_bool(self.video['skip'])
    
    self.rtmp['start'] = int(self.rtmp['start'])
    self.rtmp['timeout'] = int(self.rtmp['timeout'])
    
    if self.video['out'] != '.' and self.subtitles['out'] == '.':
      self.subtitles['out'] = self.video['out']
    else:
      self.subtitles['out'] = fix_path_separators(self.subtitles['out'])
      
    self.subtitles['check_parts'] = string_to_bool(self.subtitles['check_parts'])
    
    self.video['resolutions'] = [res.strip() for res in self.video['resolutions'].split(',')]
    

default_config = Config()
default_config.load_defaults()

