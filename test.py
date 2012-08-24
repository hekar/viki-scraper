"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

from config import default_config
from video import Video
from subtitles import Subtitle

if __name__ == '__main__':
  c = default_config
  v = Video(c, 3375)
  media = v.media_resource()
  
  s = Subtitle(c, media)
  print s.download()
  

