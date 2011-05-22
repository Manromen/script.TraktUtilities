# -*- coding: utf-8 -*-
# 

import xbmc,xbmcaddon,xbmcgui
import telnetlib, time
import simplejson as json
import thread
from utilities import *
from rating import *
from sync_update import *

__author__ = "Ralph-Gordon Paul, Adrian Cowan"
__credits__ = ["Ralph-Gordon Paul", "Adrian Cowan", "Justin Nemeth",  "Sean Rudford"]
__license__ = "GPL"
__maintainer__ = "Ralph-Gordon Paul"
__email__ = "ralph-gordon.paul@uni-duesseldorf.de"
__status__ = "Production"

__settings__ = xbmcaddon.Addon( "script.TraktUtilities" )
__language__ = __settings__.getLocalizedString

Debug("service: " + __settings__.getAddonInfo("id") + " - version: " + __settings__.getAddonInfo("version"))

# starts update/sync
def autostart():
    thread.start_new_thread(ratingLoop, ())

    if checkSettings(True):
        
        autosync_moviecollection = __settings__.getSetting("autosync_moviecollection")
        autosync_tvshowcollection = __settings__.getSetting("autosync_tvshowcollection")
        autosync_seenmovies = __settings__.getSetting("autosync_seenmovies")
        autosync_seentvshows = __settings__.getSetting("autosync_seentvshows")
        
        if autosync_moviecollection == "true":
            notification("Trakt Utilities", __language__(1180).encode( "utf-8", "ignore" )) # start movie collection update
            updateMovieCollection(True)
        if autosync_tvshowcollection == "true":
            notification("Trakt Utilities", __language__(1181).encode( "utf-8", "ignore" )) # start tvshow collection update
            updateTVShowCollection(True)
        if autosync_seenmovies == "true":
            Debug("autostart sync seen movies")
            notification("Trakt Utilities", __language__(1182).encode( "utf-8", "ignore" )) # start sync seen movies
            syncSeenMovies(True)
        if autosync_seentvshows == "true":
            Debug("autostart sync seen tvshows")
            notification("Trakt Utilities", __language__(1183).encode( "utf-8", "ignore" )) # start sync seen tv shows
            syncSeenTVShows(True)
            
        if autosync_moviecollection == "true" or autosync_tvshowcollection == "true" or autosync_seenmovies == "true" or autosync_seentvshows == "true":
            notification("Trakt Utilities", __language__(1184).encode( "utf-8", "ignore" )) # update / sync done

def ratingLoop():
    #initial state
    totalTime = 0
    watchedTime = 0
    startTime = 0
    curVideo = None
    
    #while xbmc is running
    while (not xbmc.abortRequested):
        try:
            tn = telnetlib.Telnet('localhost', 9090, 10)
        except IOError as (errno, strerror):
            #connection failed, try again soon
            print "[~] Telnet too soon? ("+str(errno)+") "+strerror
            time.sleep(1)
            continue
        while (not xbmc.abortRequested):
            try:
                raw = tn.read_until("\n")
                data = json.loads(raw)
                if 'method' in data and 'params' in data and 'sender' in data['params'] and data['params']['sender'] == 'xbmc':
                    if data['method'] in ('Player.PlaybackStopped', 'Player.PlaybackEnded'):
                        if startTime <> 0:
                            watchedTime += time.time() - startTime
                            if watchedTime <> 0:
                                Debug("[Rating] Time watched: "+str(watchedTime)+", Item length: "+str(totalTime))     
                                if 'type' in curVideo and 'id' in curVideo:                                   
                                    if totalTime/2 < watchedTime:
                                        # you can disable rating in options
                                        rateMovieOption = __settings__.getSetting("rate_movie")
                                        rateEpisodeOption = __settings__.getSetting("rate_episode")
                                        
                                        if curVideo['type'] == 'movie' and rateMovieOption == 'true':
                                            doRateMovie(curVideo['id'])
                                        if curVideo['type'] == 'episode' and rateEpisodeOption == 'true':
                                            doRateEpisode(curVideo['id'])
                                watchedTime = 0
                            startTime = 0
                    elif data['method'] in ('Player.PlaybackStarted', 'Player.PlaybackResumed'):
                        if xbmc.Player().isPlayingVideo():
                            curVideo = getCurrentPlayingVideoFromXBMC()
                            if curVideo <> None:
                                if 'type' in curVideo and 'id' in curVideo: Debug("[Rating] Watching: "+curVideo['type']+" - "+str(curVideo['id']))
                                totalTime = xbmc.Player().getTotalTime()
                                startTime = time.time()
                    elif data['method'] == 'Player.PlaybackPaused':
                        if startTime <> 0:
                            watchedTime += time.time() - startTime
                            Debug("[Rating] Paused after: "+str(watchedTime))
                            startTime = 0
            except EOFError:
                break #go out to the other loop to restart the connection
        time.sleep(1)

autostart()
