"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import os
from config import default_config
from video import Video
from subtitles import SubtitleV4

if __name__ == '__main__':
  media_id = 1042610
  c = default_config
  v = Video(c, media_id)
  s = SubtitleV4(c, media_id)

  filename = '%s.srt' % (os.path.basename(v.video_url()))
  s.download(filename)
  v.download()
