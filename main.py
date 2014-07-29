"""
  Viki.com
    Flash video downloader
    
  Hekar Khani 2012
"""

import sys, os, re, copy
from config import default_config
from channel import ChannelSearcher
from video import Video, VideoParts
from subtitles import Subtitle, SubtitleV4

def config_from_args(args):
  """
    Create a configuration from command line arguments.
    
    Returns created configuration
    
    Parses args like this:
      config.video['out'] will be:
        --video-out=<value>
  """
  
  config = copy.deepcopy(default_config)
  
  for i in xrange(1, len(args)):
    arg = args[i]
    
    if arg.startswith('--'):
      if arg == '--help':
        # TODO: autogenerate help
        pass
      else:
        # Split each argument
        meta_pair = arg.replace('--', '').split('-')
        attr = meta_pair[0]
        key = meta_pair[1].split('=', 2)[0]
        
        value = arg.split('=', 2)[1]
        
        if not hasattr(config, attr):
          print 'Warning: invalid argument attribute %s : %s' % (attr, arg)
        elif not key in getattr(config, attr).keys():
          print 'Warning: invalid argument key %s : %s' % (key, arg)
        else:
          # Set the configuration value
          getattr(config, attr)[key] = value
    else:
      print 'Warning: invalid argument %s' % (arg)
    
  config.purify()
  
  return config

def main(args):
  """
    Mainline of application
  """
  
  config = config_from_args(args)
  
  if config.single['id'] != '':
    id = int(config.single['id'])
    v = Video(config, id)
    s = SubtitleV4(config, id)
    filename = '%s.srt' % (os.path.basename(v.video_url()))
    s.download(filename)
    v.download()
  elif config.search['query'] == default_config.search['query']:
    print 'Please specify a query. Example: "--search-query=Queen Seon Deok"'
    sys.exit(1)
  else:
    searcher = ChannelSearcher(config)
    channels = searcher.search(config.search['query'], config.search['method'])
    
    for channel in channels:
      sys.stdout.write('Channel: %s\n' %(channel.name))
      for episode in channel.episodes():
        sys.stdout.write('Episode: %s\n' % (episode.episode_num))
        media_id = episode.media_id
        
        video = Video(config, media_id)
        if not config.video['skip']:
          video.download()
        
        video_info = video.video_info()
        
        filename = video.filename()
        
        # remove the extension
        filename = os.path.splitext(filename)[0]
        
        if config.subtitles['check_parts']:
          # videos that have multiple subtitle parts will need
          # to have them downloaded separately and merged
          parts = VideoParts(config, episode.full_url).parts()
          first = True
          start_index = 0
          for part in parts:
            start_time = int(part['part_info']['start_time'])
            subtitle = Subtitle(config, part['media_resource_id'], start_index, start_time)
            if first:
              subtitle.download(filename)
              first = False
            else:
              subtitle.merge(filename)
            start_index = subtitle.end_index
        else:
          media_resource_id = video.media_resource(video_info)
          subtitle = Subtitle(config, media_resource_id)
          subtitle.download(filename)

if __name__ == '__main__':
  main(sys.argv)
