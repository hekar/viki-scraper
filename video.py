"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import httplib2
import os, sys, json, re
from urllib import urlencode
from BeautifulSoup import BeautifulSoup

class VideoParts(object):
  """
    Deals with videos that have multiple parts to the subtitles.
    
    This extracts all the media_resource_ids for a video.
  """
  def __init__(self, config, video_full_url):
    """
      video_full_url - url to the video to watch
    """
    
    # Strip the url in the show_details url format
    cells = video_full_url.replace(config.site['url'], '').split('/')
    channel_id = cells[2].split('-')[0]
    cells[2] = channel_id
    
    self.show_details_full_url = config.site['url'] + '/'.join(cells) + '/show_details'
    self.show_details_full_url = re.sub(r'\?id=\d+', '', self.show_details_full_url)
  
  def part_info(self, media_resource_id):
    
    url = 'http://www.viki.com/player/media_resources/%d/info.json?rtmp=false&source=direct&embedding_uri=www.viki.com' % (media_resource_id)
    
    resp, content = httplib2.Http(".cache").request(url, "GET")
    
    part_info = json.loads(content)
    
    return part_info
    
  
  def parts(self):
    """
      Extract the partgination information for a video :)
    """
    
    url = self.show_details_full_url
    
    resp, content = httplib2.Http(".cache").request(url, "GET")
    
    soup = BeautifulSoup(content)
    
    try:
      elements = soup.find(attrs={'class':'partgination'}).findChildren()
    except AttributeError, e:
      sys.stdout.write('content:\n%s\n' % content)
      sys.stdout.write('url: %s\n' % url)
      raise e
    
    parts = []
    part_num = 0
    for element in elements:
      # Not all elements are parts. 
      # Attempt to extract the media resource id from the data-path for the part
      try:
        part_num += 1
        media_resource_id = int(element['data-path'].replace('.json', '').split('/')[-1])
        
        part_info = self.part_info(media_resource_id)
        
        part = {
          'num' : part_num,
          'media_resource_id' : media_resource_id,
          'part_info' : part_info
        }
        
        parts.append(part)
      except KeyError:
        pass
    
    return parts

class Video(object):
  
  def __init__(self, config, media_id):
    """
      vid - Video ID
    """
    
    self.config = config
    self.media_id = media_id
  
  def video_info(self):
    """
      Download the information for the video
    """
    url = 'http://www.viki.com/api/v2/shows/%d.json' % (self.media_id)
    
    parameters = {
      'language_code' : 'en',
      'media_id' : self.media_id
    }
    
    media_id = str(self.media_id)
    rtmp = '&rtmp' if self.config.video['rtmp'] else ''
    url = 'http://www.viki.com/player/media_resources/%s/info.json?source=direct&embedding_uri=www.viki.com%s' % (media_id, rtmp)
    
    headers = {
      'Host' : 'www.viki.com',
      'Connection' : 'keep-alive',
      'X-Requested-With' : 'XMLHttpRequest',
      'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.52 Safari/536.5',
      'Accept' : '*/*',
      'Accept-Encoding' : 'gzip,deflate,sdch',
      'Accept-Language' : 'en-US,en;q=0.8',
      'Accept-Charset' : 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'If-None-Match' : '"68941462f72fa3cbe8b934e54e29b2e9"'
    }
    
    resp, content = httplib2.Http(".cache").request(url, "GET", headers=headers)
    obj = json.loads(content)
    
    return obj
    
  def media_resource(self, video_info = None):
    """
      Returns the media resource id. This id is useful for getting subtitles
      
      video_info - info to extract filename from. If not specified, then it is grabbed from the server
    """
    if video_info == None:
      video_info = self.video_info()
    
    return int(video_info['thumbnail'].split('thumbnail/')[1].split('/')[0])
  
  def stream_url(self, resolutions, video_info):
    """
      Return the stream url from the video_info
      
      resolution - List of of acceptable resolutions. Highest selected. 
        If not specified than default is ['1080', '720', '480', '380', '240']
      video_info - info to extract filename from. If not specified, then it is grabbed from the server
    """

    for res in resolutions:
      for stream in video_info['streams']:
        if str(res) + 'p' in stream['quality']:
          return stream['uri']
    print video_info
    raise KeyError('Failure to get stream url from video info')
  
  def filename(self, resolutions = None, video_info = None):
    """
      Returns the video's filename
      
      optional resolution - List of of acceptable resolutions. Highest selected. 
        If not specified than default is ['1080', '720', '480', '380', '240']
      optional video_info - info to extract filename from. If not specified, then it is grabbed from the server
    """
    
    if resolutions == None:
      resolutions = self.config.video['resolutions']
    
    if video_info == None:
      video_info = self.video_info()
      
    return self.stream_url(resolutions, video_info).split('/')[-1]
    
  def video_url(self, resolutions = None):
    """
      Get the video url for the resolution
      
      optional resolution - List of of acceptable resolutions. Highest selected. 
        If not specified than default is ['1080', '720', '480', '380', '240']
    """

    if resolutions == None:
      resolutions = self.config.video['resolutions']
    
    video_info = self.video_info()
    
    return self.stream_url(resolutions, video_info)
  
  def download(self, resolutions=None):
    """
      Download the video (does not download subtitles)
      
      optional resolution - List of of acceptable resolutions. Highest selected. 
        If not specified than default is ['1080', '720', '480', '380', '240']
    """
    
    url = self.video_url()
    
    if url == None:
      # raise an exception
      return ''
    
    
    if self.config.video['rtmp']:
      # use Rtmpdump to download video
      pass
    else:
      sys.stdout.write('Downloading file: %s\n' % (os.path.basename(url)))
      
      filename = os.path.basename(url)
      prev_dir = os.getcwd()
      out_dir = self.config.video['out']
      
      if os.path.isfile(out_dir):
        raise OSError('Video output directory is not a directory, but is a file')
      elif not os.path.isdir(out_dir):
        os.mkdir(out_dir)
        
      os.chdir(out_dir)
      os.system('wget -c %s' % (url))
      os.chdir(prev_dir)

