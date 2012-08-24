"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import httplib2
import json, os, sys

class Subtitle(object):
  def __init__(self, config, media_resource_id, start_index = 0, start_time = 0):
    """
      config - configuration
      media_resource_id - This is special id that denotes resources such as thumbnails for a video. It's different from a media id
      optional start_index - Index to begin the subtitle counter at. Look at end_index to carry over
      optional start_time - Time to begin the subtitle counter at. This is in milliseconds.
    """
    self.config = config
    self.media_resource_id = media_resource_id
    self.start_index = start_index
    self.start_time = start_time
    self.end_index = self.start_index
  
  def _ms_to_time(self, milliseconds):
    """
      Datetime does not support lengthy digits of milliseconds on all operating systems.
      
      Therefore this function will convert milliseconds to %H:%M:%S,%f
    """
    
    ms = milliseconds
    
    # Get the last 3 digits of the milliseconds
    trunc_ms = ms % 1000
    seconds = (ms / 1000)
    minutes = (seconds / 60)
    hours = minutes / 60
    
    # hours can go above 24, so don't modulus
    return '%02d:%02d:%02d,%03d' % (hours, minutes % 60, seconds % 60, trunc_ms)
  
  def to_srt(self, subtitles):
    """
      Json version of the subtitles that Viki.com uses as standard
      
      Returns newly formed ".srt" data
    """
    
    srt_data = ''
    subtitle_num = self.start_index
    for subtitle in subtitles:
      subtitle_num += 1
      
      offset = self.start_time
      
      start_time = self._ms_to_time(subtitle['start_time'] + offset)
      end_time = self._ms_to_time(subtitle['end_time'] + offset)
      
      content = subtitle['content'].replace('<br>', ' ')
      
      srt_data += str(subtitle_num) + '\r\n'
      srt_data += '%s --> %s' % (start_time, end_time) + '\r\n'
      srt_data += content  + '\r\n'
      srt_data += '\r\n'
    
    self.end_index = subtitle_num
    
    return srt_data
  
  def download_data(self, format = 'srt'):
    """
      Download the subtitles
      
      format - subtitle format 'srt' or None
      
      Returns data as string
    """
    
    def to_ascii(data):
      """
      Remove non-ascii characters
      """
      return ''.join([x for x in data if ord(x) < 128])
    
    url = self.config.subtitles['url'] % (self.media_resource_id)
    
    print url
    resp, content = httplib2.Http(".cache").request(url, "GET")
    
    subtitles = json.loads(content)['subtitles']
    
    final_data = ''
    if format == 'srt':
      final_data += self.to_srt(subtitles)
    else:
      final_data += subtitles
  
    return to_ascii(final_data)
  
  def merge(self, filename = None, format = 'srt'):
    """
      Download the subtitles and write them to a file. Appends instead of overwrites
      
      filename - Name of file. Output path comes from configuration. ".srt" Extension automatically added
      format - Subtitle format 'srt' or None
      
      Returns data as string
    """
    
    return self.download(filename, format, True)
  
  def download(self, filename = None, format = 'srt', append = False):
    """
      Download the subtitles and write them to a file
      
      filename - Name of file. Output path comes from configuration. ".srt" Extension automatically added
      format - Subtitle format 'srt' or None
      append - Append to the output file, rather than overwrite
      
      Returns data as string
    """
    
    data = self.download_data(format)
    
    if filename != None:
      extension = '' if filename.lower().endswith('.srt') else '.srt'
      
      sys.stdout.write('Saving subtitle...\n')
      
      out_dir = self.config.subtitles['out']
      if os.path.isfile(out_dir):
        raise OSError('Video output directory is not a directory, but is a file')
      elif not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        
      mod = 'a' if append else 'w'
      f = open(out_dir + os.path.sep + filename + extension, mod)
      f.write(data)
      f.close()
      
    return data 
    
