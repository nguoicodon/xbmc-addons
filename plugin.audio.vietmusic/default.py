﻿import CommonFunctions as common
import urllib
import urllib2
import os
import xbmcplugin
import xbmcgui
import xbmcaddon
import urlfetch
import re
import random
import threading
from BeautifulSoup import BeautifulSoup

__settings__ = xbmcaddon.Addon(id='plugin.audio.vietmusic')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
thumbnails = xbmc.translatePath( os.path.join( home, 'thumbnails\\' ) )

 
__video_quality = __settings__.getSetting('video_quality') #values="240p|360p|480p|720p|1080p"
__mp3_quality = __settings__.getSetting('mp3_quality') #values="32K|128K|320K|Lossless"

__thumbnails = []

def get_thumbnail_url():
  global __thumbnails
  url = ''
  try:
    if len(__thumbnails) == 0:
      content = make_request('https://raw.github.com/onepas/xbmc-addons/master/thumbnails/thumbnails.xml')
      soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
      __thumbnails = soup.findAll('thumbnail')

    url = random.choice(__thumbnails).text
  except:
    pass
  
  return url

def _makeCookieHeader(cookie):
      cookieHeader = ""
      for value in cookie.values():
          cookieHeader += "%s=%s; " % (value.key, value.value)
      return cookieHeader

def make_request(url, headers=None):
        if headers is None:
            headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1',
                       'Referer' : 'http://www.google.com'}
        try:
            req = urllib2.Request(url,headers=headers)
            f = urllib2.urlopen(req)
            body=f.read()
            return body
        except urllib2.URLError, e:
            print 'We failed to open "%s".' % url
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            if hasattr(e, 'code'):
                print 'We failed with error code - %s.' % e.code

def get_chiasenhac(url = None):
  if url == '':
    content = make_request('http://chiasenhac.com')
    soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
    items = soup.find('div',{'id' : 'myslidemenu'}).find('ul').findAll('li')
    for item in items:
      href = item.a.get('href')
      if href is not None:
        try:
          add_dir(item.a.text, 'http://chiasenhac.com/' + href, 100, get_thumbnail_url(), query, type, 0)
        except:
          pass
    return
  
  if '/mp3/hot/' in url:  
    content = make_request(url)
    soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
    tables = soup.findAll('table',{'class' : 'tbtable'})
    threads = []
    for table in tables:
      items = table.findAll('a')
      for item in items:
        href = item.get('href')
        text = item.text.strip()
        if len(text) > 0:
          if 'playlist.chiasenhac.com' in href:  
            t = threading.Thread(target=add_link, args = ('', text, 0, href, get_thumbnail_url(), ''))
            threads.append(t)
          else:
            add_dir(text, 'http://chiasenhac.com/' + href, 100, get_thumbnail_url(), '', '', 0)
    [x.start() for x in threads]
    [x.join() for x in threads]
    return   

  if '/hd/video/' in url:
    content = make_request(url)
    soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
    tables = soup.findAll('div',{'class' : 'list-l list-1'})
    threads = []
    for table in tables:
      item = table.find('div', {'class':'info'}).find('a')
      href = item.get('href')
      text = item.get('title')
      if 'playlist.chiasenhac.com' not in href:
        href = 'http://playlist.chiasenhac.com/' + href
      img = table.find('div', {'class':'gensmall'}).find('a').find('img')
      t = threading.Thread(target=add_link, args = ('', text, 0, href, img.get('src'), ''))
      threads.append(t)
    [x.start() for x in threads]
    [x.join() for x in threads]
    return  

  if '/mp3/beat-playback/' in url or '/mp3/vietnam/' in url or '/mp3/thuy-nga/' in url or '/mp3/us-uk/' in url or '/mp3/chinese/' in url or '/mp3/korea/' in url or '/mp3/other/' in url:
    content = make_request(url)
    soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
    tables = soup.findAll('div',{'class' : 'list-r list-1'})
    threads = []
    for table in tables:
      item = table.find('div', {'class':'text2'}).find('a')
      href = item.get('href')
      text = item.get('title')
      if 'playlist.chiasenhac.com' not in href:
        href = 'http://playlist.chiasenhac.com/' + href   
      t = threading.Thread(target=add_link, args = ('', text, 0, href, get_thumbnail_url(), ''))
      threads.append(t)
    [x.start() for x in threads]
    [x.join() for x in threads]
    
    return
  return

def get_chiasenhac_album(url = None):
  
  #content = make_request(url)
  #soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES) 
  #album_url = 'http://chiasenhac.com/' + soup.find('th',{'class' : 'catLeft'}).find('a').get('href')
  album_url = url + 'album.html'

  content = make_request(album_url)
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)

  albums_thumbs = {}
  albums = soup.findAll('span',{'class' : 'genmed'})
  for album in albums:
    a = album.find('a').get('href')
    b = album.find('img').get('src')
    albums_thumbs[a] = b

  albums = soup.findAll('span',{'class' : 'gen'})
  for album in albums:
    href = album.find('a', {'class' : 'musictitle'})
    title = href.get('title')
    link = href.get('href')
    thumb = albums_thumbs[link]

    add_dir(title, link, 102, thumb, query, type, 0)
    
  return   

def get_chiasenhac_album_songs(url = None):
  content = make_request(url)
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)

  albums = soup.find('div',{'id':'playlist'}).findAll('span',{'class' : 'gen'})
  threads = []
  for album in albums:
    a = album.findAll('a')
    if (len(a) == 3):
      href = 'http://chiasenhac.com/' + a[1].get('href')
      text = album.text;
      t = threading.Thread(target=add_link, args = ('', text, 0, href, get_thumbnail_url(), ''))
      threads.append(t)
      
  [x.start() for x in threads]
  [x.join() for x in threads]

  return 

def get_categories():
    add_dir('Xếp hạng', 'mp3/hot/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Video Clip','hd/video/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Playback','mp3/beat-playback/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Việt Nam','mp3/vietnam/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Thuý Nga','mp3/thuy-nga/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Âu, Mỹ','mp3/us-uk/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Nhạc Hoa','mp3/chinese/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Nhạc Hàn','mp3/korea/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Nước Khác','mp3/other/', 1,  get_thumbnail_url(), query, type, 0)
    add_dir('Tìm kiếm Video/Nhạc','', 10, get_thumbnail_url(), query, type, 0)
    add_dir('Add-on settings', '', 99, get_thumbnail_url(), query, type, 0)
    

def get_sub_categories(url, mode):
  content = make_request('http://chiasenhac.com')
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
  items = soup.find('div',{'id' : 'myslidemenu'}).find('ul').findAll('li')
  for item in items:
    href = item.a.get('href')
    if href is not None:
      try:
        if href.startswith(url) and len(href) > len(url):
          prefix = ''
          if url != 'mp3/hot/' and url !='hd/video/':
            prefix = 'Songs: '
          add_dir(prefix + item.a.text, 'http://chiasenhac.com/' + href, 100, get_thumbnail_url(), query, type, 0)
      except:
        pass
  for item in items:
    href = item.a.get('href')
    if href is not None:
      try:
        if url != 'mp3/hot/' and url !='hd/video/' and href.startswith(url) and len(href) > len(url):
          add_dir('Albums: ' + item.a.text, 'http://chiasenhac.com/' + href, 101, get_thumbnail_url(), query, type, 0)
      except:
        pass
  add_dir('Tìm kiếm Video/Nhạc','', 10, get_thumbnail_url(), query, type, 0)
  return
 
def search(url):
  query = common.getUserInput('Search', '')
  if query is None:
    return
  url = 'http://search.chiasenhac.com/search.php?s=' + urllib.quote_plus(query)
  content = make_request(url)
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
  items = soup.findAll('div',{'class' : 'tenbh'})
  threads = []
  for item in items:
    a = item.find('a')
    p = item.findAll('p')[1]
    if a is not None:
      href = a.get('href')
      if 'chiasenhac.com' not in href:
        href = 'http://chiasenhac.com/' + href   
      t = threading.Thread(target=add_link, args = ('', a.text + '-' + p.text, 0, href, get_thumbnail_url(), ''))
      threads.append(t)
  [x.start() for x in threads]
  [x.join() for x in threads]
  return

def resolve_url(url):

  content = make_request(url)
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
  items = soup.find('noscript').find('object').findAll('param')
  for item in items:
      name = item.get('name')
      if name is not None and name == 'FlashVars':
          value = urllib.unquote(item.get('value'))
          pairsofparams=value.split('&')
          for i in range(len(pairsofparams)):
              splitparams=pairsofparams[i].split('=')
              if splitparams[0] == 'audioUrl' or splitparams[0] == 'file':
                  mediaUrl = splitparams[1]
                  xbmc.Player().play(mediaUrl)
                  return
                  break
    

  return

def get_resolve_url(url):
  content = make_request(url)
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
  items = soup.find('noscript').find('object').findAll('param')
  for item in items:
      name = item.get('name')
      if name is not None and name == 'FlashVars':
          value = urllib.unquote(item.get('value'))
          pairsofparams=value.split('&')
          for i in range(len(pairsofparams)):
              splitparams=pairsofparams[i].split('=')
              if splitparams[0] == 'audioUrl' or splitparams[0] == 'file':
                  mediaUrl = splitparams[1]
                  return mediaUrl
                  break
    

  return

def extract_link_with_quality(video_quality, mp3_quality, url):
  #video="240p|360p|480p|720p|1080p"
  #mp3="32k|128k|320k|Lossless"
  if mp3_quality == 'Lossless':
      mp3_quality = 'm4a'

  mp3_q = '128'
  if mp3_quality == 'm4a':
      mp3_q = 'm4a'
  if mp3_quality == '320k':
      mp3_q = '320'   

  video_q = '128'
  if video_quality == '1080p':
      video_q = 'flac'
  if video_quality == '720p':
      video_q = 'm4a'
  if video_quality == '480p':
      video_q = '320'

  media_link = ''
  content = make_request(url)
  
  soup = BeautifulSoup(str(content), convertEntities=BeautifulSoup.HTML_ENTITIES)
  items = soup.find('noscript').find('object').findAll('param')
  for item in items:
      name = item.get('name')
      if name is not None and name == 'FlashVars':
          value = urllib.unquote(item.get('value'))
          pairsofparams=value.split('&')
          for i in range(len(pairsofparams)):
              splitparams=pairsofparams[i].split('=')
              if splitparams[0] == 'audioUrl' or splitparams[0] == 'file':
                  media_link = splitparams[1]
  
  #images/32k.png -> 128
  #images/128k_l.png -> 128
  #images/320k.png -> 320
  #images/m4a.png -> m4a

  #images/240p.png -> 32
  #images/360p_l.png -> 128
  #images/480p.png -> 320
  #images/720p.png -> m4a
  #images/1080p.png -> flac

  items = soup.find('div',{'class' : 'gen'}).findAll('img')
  quality_availables  = ''
  for item in items:
      quality_availables += item.get('src') + ','

  if video_quality not in quality_availables:
      video_q = '128'
  if mp3_quality not in quality_availables:
      mp3_q = '128'

  parts = media_link.split('/')

  if media_link.endswith('mp4.csn'):
      parts[len(parts) - 2] = video_q
  if media_link.endswith('mp3.csn'):
      parts[len(parts) - 2] = mp3_q
      if mp3_q == 'm4a':
          parts[len(parts) - 1] = parts[len(parts) - 1].replace('.mp3.csn','.m4a.csn')

  
  return '/'.join(parts)

def add_link(date, name, duration, href, thumb, desc):

    description = date+'\n\n'+desc
    u=extract_link_with_quality(__video_quality, __mp3_quality, href)

    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={ "Title": name, "Plot": description, "Duration": duration})
    if 'chiasenhac' in href:
      liz.setProperty('IsPlayable', 'false')
    else:
      liz.setProperty('IsPlayable', 'true')

    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)


def add_dir(name,url,mode,iconimage,query='',type='f',page=0):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&query="+str(query)+"&type="+str(type)+"&page="+str(page)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]

        return param

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

params=get_params()

url=''
name=None
mode=None
query=None
type='f'
page=0

try:
    type=urllib.unquote_plus(params["type"])
except:
    pass
try:
    page=int(urllib.unquote_plus(params["page"]))
except:
    pass
try:
    query=urllib.unquote_plus(params["query"])
except:
    pass
try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "type: "+str(type)
print "page: "+str(page)
print "query: "+str(query)

if mode==None:
  get_categories()
elif mode==1:
  get_sub_categories(url,mode)
elif mode==4:
  resolve_url(url)
elif mode==10:
  search(url)
elif mode==100:
  get_chiasenhac(url)
elif mode==101:
  get_chiasenhac_album(url)
elif mode==102:
  get_chiasenhac_album_songs(url)
elif mode==99:
   __settings__.openSettings()
   
xbmcplugin.endOfDirectory(int(sys.argv[1]))