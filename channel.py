"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import json, re, math, sys
from httplib2 import Http
from urllib import urlencode
from BeautifulSoup import BeautifulSoup

class Episode(object):
  def __init__(self, name, media_id, episode_num, full_url):
    """
      name - name of the episode
      media_id - media id
      episode_num - number of the episode starting from 1
      full_url - url to the video page
    """
    self.name = name
    self.media_id = media_id
    self.episode_num = episode_num
    self.full_url = full_url

class Channel(object):
  def __init__(self, config, name, full_url, channel_id):
    """
      name - name of the channel
      full_url - full url to the channel page
      media_id - id of the channel
    """
    self.config = config
    self.name = name
    self.full_url = full_url
    self.channel_id = channel_id
    
  def download(self, start_episode=1, end_episode=None):
    """
      Download a video from viki.com
      

      start_episode - Episode number to start at
      optional end_episode - Episode number to end at (None means up to last)
    """
    
    if end_episode == None:
      # Download all episodes
      end_episode = 99
    
    resp, content = httplib2.Http(".cache").request('', "GET")

    pass
    
  def episodes(self):
    """
      Generator that produces a list of episodes
    """
    
    episodes_per_page = 10
    
    start_page = max(int(math.ceil(self.config.video['episode_start'] / episodes_per_page)), 1)
    end_page = int(math.ceil(self.config.video['episode_end'] / episodes_per_page)) + 1
    
    print 'end_page=' + str(end_page)
    for page in xrange(start_page, end_page):
      
      video_list_url = self.full_url + '/videos?page=%d' % (page)
      
      resp, content = Http(".cache").request(video_list_url, 'GET')
      
      soup = BeautifulSoup(content)
      episodes = soup.findAll(attrs={'class':'show-info'})
      
      episode_num = max(self.config.video['episode_start'], 1)
      episodes = episodes[self.config.video['episode_start'] % episodes_per_page:]
      
      for episode in episodes:
        name = episode.h3.a.string.strip()
        url = episode.h3.a.attrs[0][1]
        
        media_id = int(url.split('/')[-1].split('-')[0].split('?id=')[0])
        
        full_url = self.config.site['url'] + url
        
        found_episode = Episode(name, media_id, episode_num, full_url)
        
        episode_num += 1
        
        yield found_episode
        
    
class ChannelSearcher(object):
  def __init__(self, config):
    self.config = config
    
  def search(self, match, method):
    """
      Search for channels that match the match string
      
      match - String to match against
      method - String to select match method. Methods are: 'exact', 'exact-ignore-case', 'fuzzy' or 'regex'
    """
    
    url = self.config.search['url'] + match.replace(' ', '%20')
    resp, html_data = Http(".cache").request(url, 'GET')
    
    soup = BeautifulSoup(html_data)
    channels = soup.findAll(attrs={'class':'show-info'})
    
    found_channels = []
    if len(channels) == 0:
      sys.stdout.write('Failure to load channel search page: %s\n' % (match))
      return []
    
    for channel in channels:
      name = channel.h3.a.string.strip()
      url = channel.h3.a.attrs[0][1]
      
      channel_id = int(url.split('/')[-1].split('-')[0])
      
      full_url = self.config.site['url'] + url
      
      # Perform the actual match
      add = False
      if method == 'exact':
        if match.strip() == name.strip():
          add = True
      elif method == 'exact-ignore-case':
        if match.lower().strip() == name.lower().strip():
          add = True
      elif method == 'fuzzy':
        if match.lower() in name.lower():
          add = True
      elif method == 'regex':
        if re.match(match, name):
          add = True
      else:
        raise KeyError('Search method --search-method=%s is not valid\n' % method)
      
      if add:
        found_channel = Channel(self.config, name, full_url, channel_id)
        found_channels.append(found_channel)
    
    if len(found_channels) == 0:
      sys.stdout.write('No channels with the name: %s\n' % (match))
    
    return found_channels
    
