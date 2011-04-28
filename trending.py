# -*- coding: utf-8 -*-
# 

import os
import xbmc,xbmcaddon,xbmcgui
import time, socket
import simplejson as json
from utilities import *

try:
    # Python 3.0 +
    import http.client as httplib
except ImportError:
    # Python 2.7 and earlier
    import httplib

try:
  # Python 2.6 +
  from hashlib import sha as sha
except ImportError:
  # Python 2.5 and earlier
  import sha

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

# read settings
__settings__ = xbmcaddon.Addon( "script.TraktUtilities" )
__language__ = __settings__.getLocalizedString

apikey = '48dfcb4813134da82152984e8c4f329bc8b8b46a'
username = __settings__.getSetting("username")
pwd = sha.new(__settings__.getSetting("password")).hexdigest()
debug = __settings__.getSetting( "debug" )

conn = httplib.HTTPConnection('api.trakt.tv')
headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

def showTrendingMovies():
    
    movies = getTrendingMoviesFromTrakt()
    watchlist = traktMovieListByImdbID(getWatchlistMoviesFromTrakt())
    
    if movies == None: # movies = None => there was an error
        return # error already displayed in utilities.py
    
    if len(movies) == 0:
        xbmcgui.Dialog().ok("Trakt Utilities", "there are no trending movies")
        return
    
    for movie in movies:
        if movie['imdb_id'] in watchlist:
            movie['watchlist'] = True
    
    # display trending movie list
    import windows
    ui = windows.MoviesWindow("movies.xml", __settings__.getAddonInfo('path'), "Default")
    ui.passReference(movies)
    ui.doModal()
    del ui

def showTrendingTVShows():

    tvshows = getTrendingTVShowsFromTrakt()
    
    if tvshows == None: # tvshows = None => there was an error
        return # error already displayed in utilities.py
    
    if len(tvshows) == 0:
        xbmcgui.Dialog().ok("Trakt Utilities", "there are no trending tv shows")
        return
    
    # display trending tv shows
    import windows
    ui = windows.TVShowsWindow("tvshows.xml", __settings__.getAddonInfo('path'), "Default")
    ui.initWindow(tvshows)
    ui.doModal()
    del ui
