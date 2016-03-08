#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
from operator import itemgetter
from Utils import *
import ArtworkUtils as artutils
import random


def getPluginListing(action,limit,refresh=None,optionalParam=None,randomize=False):
    #general method to get a widget/plugin listing and check cache etc.
    count = 0
    allItems = []
    cachePath = os.path.join(ADDON_DATA_PATH,"widgetcache-%s.json" %action)
    #get params for each action
    if "EPISODES" in action: 
        type = "episodes"
        refresh = WINDOW.getProperty("widgetreload-episodes")
    elif "MOVIE" in action: 
        type = "movies"
        refresh = WINDOW.getProperty("widgetreload-movies")
    elif "SHOW" in action: 
        type = "tvshows"
        refresh = WINDOW.getProperty("widgetreload-tvshows")
    elif "MEDIA" in action: 
        type = "movies"
        refresh = WINDOW.getProperty("widgetreload2")
    elif "PVR" in action: 
        type = "episodes"
        refresh = WINDOW.getProperty("widgetreload2")
    elif "ALBUM" in action: 
        type = "albums"
        refresh = WINDOW.getProperty("widgetreloadmusic")
    elif "SONG" in action: 
        type = "songs"
        refresh = WINDOW.getProperty("widgetreloadmusic")
    elif "BROWSEGENRE" in action: 
        type = "genres"
        refresh = WINDOW.getProperty("widgetreload2")
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    else: type = "files"
    if "RECENT" in action:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATEADDED)
    elif "SIMILAR" in action:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_VIDEO_RATING)
    else:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
    
    cacheStr = "skinhelper-%s-%s-%s-%s-%s" %(action,limit,optionalParam,refresh,randomize)
    
    #set widget content type
    xbmcplugin.setContent(int(sys.argv[1]), type)
    
    #try to get from cache first...
    cache = WINDOW.getProperty(cacheStr).decode("utf-8")
    if cache:
        logMsg("getPluginListing-%s-%s-%s-%s-%s -- got data from cache" %(action,limit,optionalParam,refresh,randomize))
        allItems = eval(cache)
            
    #Call the correct method to get the content from json when no cache
    if not allItems or action == "FAVOURITES":
        logMsg("getPluginListing-%s-%s-%s-%s-%s -- no cache, quering json api to get items" %(action,limit,optionalParam,refresh,randomize))
        if optionalParam:
            allItems = eval(action)(limit,optionalParam)
        else:
            allItems = eval(action)(limit)
        if randomize: allItems = sorted(allItems, key=lambda k: random.random())
        allItems = prepareListItems(allItems)
        #save the cache
        WINDOW.setProperty(cacheStr, repr(allItems).encode("utf-8"))
    
    #fill that listing...
    for item in allItems:
        liz = createListItem(item)
        isFolder = item.get("isFolder",False)
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), item['file'], liz, isFolder)
        count += 1
        if count == limit:
            break
    
    #end directory listing
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
    
def addDirectoryItem(label, path, folder=True):
    li = xbmcgui.ListItem(label, path=path)
    li.setThumbnailImage("special://home/addons/script.skin.helper.service/icon.png")
    li.setArt({"fanart":"special://home/addons/script.skin.helper.service/fanart.jpg"})
    li.setArt({"landscape":"special://home/addons/script.skin.helper.service/fanart.jpg"})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=li, isFolder=folder)

def doMainListing():
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    addDirectoryItem(ADDON.getLocalizedString(32000), "plugin://script.skin.helper.service/?action=favourites&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32001), "plugin://script.skin.helper.service/?action=favouritemedia&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32002), "plugin://script.skin.helper.service/?action=nextepisodes&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32003), "plugin://script.skin.helper.service/?action=recommendedmovies&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32004), "plugin://script.skin.helper.service/?action=RecommendedMedia&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32005), "plugin://script.skin.helper.service/?action=recentmedia&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32006), "plugin://script.skin.helper.service/?action=similarmovies&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32130), "plugin://script.skin.helper.service/?action=similarshows&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32162), "plugin://script.skin.helper.service/?action=similarmedia&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32086), "plugin://script.skin.helper.service/?action=inprogressmedia&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32007), "plugin://script.skin.helper.service/?action=inprogressandrecommendedmedia&limit=100")
    addDirectoryItem(xbmc.getLocalizedString(359), "plugin://script.skin.helper.service/?action=recentalbums&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32087), "plugin://script.skin.helper.service/?action=recentsongs&limit=100")
    addDirectoryItem(xbmc.getLocalizedString(517), "plugin://script.skin.helper.service/?action=recentplayedalbums&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32088), "plugin://script.skin.helper.service/?action=recentplayedsongs&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32131), "plugin://script.skin.helper.service/?action=recommendedalbums&limit=100")
    addDirectoryItem(ADDON.getLocalizedString(32132), "plugin://script.skin.helper.service/?action=recommendedsongs&limit=100")
    if xbmc.getCondVisibility("System.HasAddon(script.tv.show.next.aired)"):
        addDirectoryItem(ADDON.getLocalizedString(32055), "plugin://script.skin.helper.service/?action=nextairedtvshows&limit=100")
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    
def FAVOURITES(limit):
    return FAVOURITEMEDIA(limit,True)

def PVRRECORDINGS(limit):
    allItems = []
    allUnSortedItems = []
    if xbmc.getCondVisibility("PVR.HasTVChannels"):
        # Get a list of all the unwatched tv recordings   
        json_result = getJSON('PVR.GetRecordings', '{"properties": [ %s ]}' %fields_pvrrecordings)
        pvr_backend = xbmc.getInfoLabel("Pvr.BackendName").decode("utf-8")
        for item in json_result:
            #exclude live tv items from recordings list (mythtv hack)
            if item["playcount"] == 0 and not ("mythtv" in pvr_backend.lower() and "/livetv/" in item.get("file","").lower()):
                channelname = item["channel"]
                item["channel"] = channelname
                item["art"] = artutils.getPVRThumbs(item["title"], channelname, "recordings")
                item["channellogo"] = item["art"].get("channellogo","")
                item["cast"] = None
                item["file"] = sys.argv[0] + "?action=playrecording&path=" + str(item["recordingid"])
                allUnSortedItems.append((item["endtime"],item))
                
        #sort the list so we return a recently added list or recordings
        allUnSortedItems = sorted(allUnSortedItems,key=itemgetter(0),reverse=True)
        for item in allUnSortedItems:
            allItems.append(item[1])
    return allItems

def NEXTPVRRECORDINGS(limit,reversed="false"):
    #returns the first unwatched episode of all recordings, starting at the oldest
    allItems = []
    allTitles = []
    allUnSortedItems = []
    if xbmc.getCondVisibility("PVR.HasTVChannels"):
        # Get a list of all the unwatched tv recordings   
        json_result = getJSON('PVR.GetRecordings', '{"properties": [ %s ]}' %fields_pvrrecordings)
        pvr_backend = xbmc.getInfoLabel("Pvr.BackendName").decode("utf-8")
        for item in json_result:
            #exclude live tv items from recordings list (mythtv hack)
            if not (item.get("directory") and item["directory"] in allTitles) and item["playcount"] == 0 and not ("mythtv" in pvr_backend.lower() and "/livetv/" in item.get("file","").lower()):
                channelname = item["channel"]
                item["art"] = artutils.getPVRThumbs(item["title"], channelname, "recordings")
                item["channellogo"] = item["art"].get("channellogo","")
                item["cast"] = None
                allUnSortedItems.append((item["endtime"],item))
                if item.get("directory"): allTitles.append(item["directory"])
                
        #sort the list so we return the list with the oldest unwatched first
        if reversed == "true":
            allUnSortedItems = sorted(allUnSortedItems,key=itemgetter(0),reverse=True)
        else:
            allUnSortedItems = sorted(allUnSortedItems,key=itemgetter(0),reverse=False)
        for item in allUnSortedItems:
            allItems.append(item[1])
    return allItems    

def PVRTIMERS(limit):
    # Get a list of all the upcoming timers
    allItems = []
    allUnSortedItems = []
    if xbmc.getCondVisibility("PVR.HasTVChannels"):
        json_result = getJSON('PVR.GetTimers', '{"properties": [ "title","endtime","starttime","channelid","summary","file" ]}' )
        for item in json_result:
            item["file"] = "plugin://script.skin.helper.service/?action=launch&path=ActivateWindow(tvtimers,return)"
            channel_details = getJSON('PVR.GetChannelDetails', '{ "channelid": %d}' %item["channelid"])
            channelname = channel_details.get("label","")
            item["channel"] = channelname
            item["art"] = artutils.getPVRThumbs(item["title"], channelname, "recordings")
            item["channellogo"] = item["art"].get("channellogo","")
            if not item.get("plot"): item["plot"] = item.get("summary","")
            allUnSortedItems.append((item["starttime"],item))
                
        #sort the list so we return the list with the oldest unwatched first
        allUnSortedItems = sorted(allUnSortedItems,key=itemgetter(0),reverse=False)
        for item in allUnSortedItems:
            allItems.append(item[1])
    return allItems  
    
def PVRCHANNELS(limit):
    count = 0
    allItems = []
    # Perform a JSON query to get all channels
    json_query = getJSON('PVR.GetChannels', '{"channelgroupid": "alltv", "properties": [ "thumbnail", "channeltype", "hidden", "locked", "channel", "lastplayed", "broadcastnow" ], "limits": {"end": %d}}' %( limit ) )
    for channel in json_query:
        channelname = channel["label"]
        channelid = channel["channelid"]
        channelicon = channel['thumbnail']
        if channel.has_key('broadcastnow'):
            #channel with epg data
            item = channel['broadcastnow']
            item["art"] = artutils.getPVRThumbs(item["title"], channelname, "channels")
            if not channelicon: channelicon = item["art"].get("channelicon")
        else:
            #channel without epg
            item = channel
            item["title"] = item["label"]
            channelname = channel["label"]
            channelid = channel["channelid"]
            channelicon = channel['thumbnail']
            if not channelicon: channelicon = searchChannelLogo(channelname)
        item["file"] = sys.argv[0] + "?action=launchpvr&path=" + str(channelid)
        item["channelicon"] = channelicon
        item["icon"] = channelicon
        item["channel"] = channelname
        item["cast"] = None
        allItems.append(item)
    return allItems

def PVRCHANNELGROUPS(limit):
    count = 0
    #Code is not yet working... not possible to navigate to a specific channel group in pvr windows
    xbmcplugin.setContent(int(sys.argv[1]), 'files')
    # Perform a JSON query to get all channels
    json_query = getJSON('PVR.GetChannelGroups', '{"channeltype": "tv"}' )
    for item in json_query:
        item["file"] = "pvr://channels/tv/%s/" %(item["label"])
        item["title"] = item["label"]
        liz = createListItem(item)
        liz.setProperty('IsPlayable', 'false')
        xbmcplugin.addDirectoryItem(int(sys.argv[1]), item['file'], liz, True)
        count += 1
        if count == limit:
            break
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1])) 
       
def getThumb(searchphrase):
    WINDOW.clearProperty("SkinHelper.ListItemThumb")
    
    while xbmc.getCondVisibility("Container.Scrolling") or WINDOW.getProperty("getthumbbusy")=="busy":
        xbmc.sleep(150)
    image = artutils.searchThumb(searchphrase)
    if image:
        WINDOW.setProperty("SkinHelper.ListItemThumb",image)
    else:
        WINDOW.clearProperty("SkinHelper.ListItemThumb")
    li = xbmcgui.ListItem(searchphrase, path=image)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=image, listitem=li)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def RECENTALBUMS(limit,browse=""):
    allItems = []
    json_result = getJSON('AudioLibrary.GetRecentlyAddedAlbums', '{ "properties": [ %s ], "limits":{"end":%d} }' %(fields_albums,limit))
    for item in json_result:
        item["art"] = artutils.getMusicArtwork(item["displayartist"], item["label"])
        item["type"] = "album"
        item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
        item['album_description'] = item["art"].get("info","")
        if browse == "true":
            item["extraproperties"]["IsPlayable"] = "false"
            item["file"] = "musicdb://albums/%s/" %str(item["albumid"])
        else:
            item['file'] = "plugin://script.skin.helper.service/?action=playalbum&path=%s" %item['albumid']
        allItems.append(item)

    return allItems

def RECENTPLAYEDALBUMS(limit,browse=""):
    allItems = []
    json_result = getJSON('AudioLibrary.GetRecentlyPlayedAlbums', '{ "sort": { "order": "descending", "method": "lastplayed" }, "properties": [ %s ], "limits":{"end":%d} }' %(fields_albums,limit))
    for item in json_result:
        item["art"] = artutils.getMusicArtwork(item["displayartist"], item["label"])
        item["type"] = "album"
        item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
        item['album_description'] = item["art"].get("info","")
        if browse == "true":
            item["extraproperties"]["IsPlayable"] = "false"
            item["file"] = "musicdb://albums/%s/" %str(item["albumid"])
        else:
            item['file'] = "plugin://script.skin.helper.service/?action=playalbum&path=%s" %item['albumid']
        allItems.append(item)

    return allItems

def RECENTPLAYEDSONGS(limit):
    allItems = []
    json_result = getJSON('AudioLibrary.GetRecentlyPlayedSongs', '{ "properties": [ %s ], "limits":{"end":%d} }' %(fields_songs,limit))
    for item in json_result:
        item["art"] = artutils.getMusicArtwork(item["displayartist"], item["album"])
        item["type"] = "song"
        item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
        item['album_description'] = item["art"].get("info","")
        allItems.append(item)
    return allItems    

def RECENTSONGS(limit):
    allItems = []
    json_result = getJSON('AudioLibrary.GetRecentlyAddedSongs', '{ "properties": [ %s ], "limits":{"end":%d} }' %(fields_songs,limit))
    for item in json_result:
        item["art"] = artutils.getMusicArtwork(item["displayartist"], item["album"])
        item["type"] = "song"
        item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
        item['album_description'] = item["art"].get("info","")
        allItems.append(item)
    return allItems    
    
def NEXTEPISODES(limit):
    allItems = []
    count = 0
    # First we get a list of all the in-progress TV shows
    json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "studio", "mpaa", "file", "art" ] }')
    # If we found any, find the oldest unwatched show for each one.
    for show in json_result:
        json_episodes = getJSON('VideoLibrary.GetEpisodes', '{ "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ %s ], "limits":{"end":1}}' %(show['tvshowid'],fields_episodes))
        for item in json_episodes:
            allItems.append(item)
            count +=1
            if count == limit:
                break       
    if count < limit:
        # Fill the list with first episodes of unwatched tv shows
        json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "ascending", "method": "dateadded" }, "filter": {"and": [{"operator":"false", "field":"inprogress", "value":""}]}, "properties": [ "title", "studio", "mpaa", "file", "art" ] }')
        for show in json_result:
            json_episodes = getJSON('VideoLibrary.GetEpisodes', '{ "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ %s ], "limits":{"end":1}}' %(show['tvshowid'],fields_episodes))
            for item in json_episodes:
                allItems.append(item)
                count +=1
                if count == limit:
                    break
                    
    return allItems

def NEXTAIREDTVSHOWS(limit):
    count = 0
    allItems = []
    #get data from next aired script
    nextairedTotal = WINDOW.getProperty("NextAired.Total")
    if nextairedTotal:
        nextairedTotal = int(nextairedTotal)
        for count in range(nextairedTotal):
            tvshow = WINDOW.getProperty("NextAired.%s.Label"%str(count)).decode("utf-8")
            if tvshow:
                json_result = getJSON('VideoLibrary.GetTvShows','{ "filter": {"operator":"is", "field":"title", "value":"%s"}, "properties": [ %s ] }' %(tvshow,fields_tvshows))
                if len(json_result) > 0:
                    item = json_result[0]
                    extraprops = {}
                    extraprops["airtime"] = WINDOW.getProperty("NextAired.%s.AirTime"%str(count)).decode("utf-8")
                    extraprops["Path"] = WINDOW.getProperty("NextAired.%s.Path"%str(count)).decode("utf-8")
                    extraprops["Library"] = WINDOW.getProperty("NextAired.%s.Library"%str(count)).decode("utf-8")
                    extraprops["Status"] = WINDOW.getProperty("NextAired.%s.Status"%str(count)).decode("utf-8")
                    extraprops["StatusID"] = WINDOW.getProperty("NextAired.%s.StatusID"%str(count)).decode("utf-8")
                    extraprops["Network"] = WINDOW.getProperty("NextAired.%s.Network"%str(count)).decode("utf-8")
                    extraprops["Started"] = WINDOW.getProperty("NextAired.%s.Started"%str(count)).decode("utf-8")
                    extraprops["Genre"] = WINDOW.getProperty("NextAired.%s.Genre"%str(count)).decode("utf-8")
                    extraprops["Premiered"] = WINDOW.getProperty("NextAired.%s.Premiered"%str(count)).decode("utf-8")
                    extraprops["Country"] = WINDOW.getProperty("NextAired.%s.Country"%str(count)).decode("utf-8")
                    extraprops["Runtime"] = WINDOW.getProperty("NextAired.%s.Runtime"%str(count)).decode("utf-8")
                    extraprops["Fanart"] = WINDOW.getProperty("NextAired.%s.Fanart"%str(count)).decode("utf-8")
                    extraprops["Today"] = WINDOW.getProperty("NextAired.%s.Today"%str(count)).decode("utf-8")
                    extraprops["NextDate"] = WINDOW.getProperty("NextAired.%s.NextDate"%str(count)).decode("utf-8")
                    extraprops["NextDay"] = WINDOW.getProperty("NextAired.%s.NextDay"%str(count)).decode("utf-8")
                    extraprops["NextTitle"] = WINDOW.getProperty("NextAired.%s.NextTitle"%str(count)).decode("utf-8")
                    extraprops["NextNumber"] = WINDOW.getProperty("NextAired.%s.NextNumber"%str(count)).decode("utf-8")
                    extraprops["NextEpisodeNumber"] = WINDOW.getProperty("NextAired.%s.NextEpisodeNumber"%str(count)).decode("utf-8")
                    extraprops["NextSeasonNumber"] = WINDOW.getProperty("NextAired.%s.NextSeasonNumber"%str(count)).decode("utf-8")
                    extraprops["LatestDate"] = WINDOW.getProperty("NextAired.%s.LatestDate"%str(count)).decode("utf-8")
                    extraprops["LatestDay"] = WINDOW.getProperty("NextAired.%s.LatestDay"%str(count)).decode("utf-8")
                    extraprops["LatestTitle"] = WINDOW.getProperty("NextAired.%s.LatestTitle"%str(count)).decode("utf-8")
                    extraprops["LatestNumber"] = WINDOW.getProperty("NextAired.%s.LatestNumber"%str(count)).decode("utf-8")
                    extraprops["LatestEpisodeNumber"] = WINDOW.getProperty("NextAired.%s.LatestEpisodeNumber"%str(count)).decode("utf-8")
                    extraprops["LatestSeasonNumber"] = WINDOW.getProperty("NextAired.%s.LatestSeasonNumber"%str(count)).decode("utf-8")
                    extraprops["AirDay"] = WINDOW.getProperty("NextAired.%s.AirDay"%str(count)).decode("utf-8")
                    extraprops["ShortTime"] = WINDOW.getProperty("NextAired.%s.ShortTime"%str(count)).decode("utf-8")
                    extraprops["SecondWeek"] = WINDOW.getProperty("NextAired.%s.SecondWeek"%str(count)).decode("utf-8")
                    extraprops["Art(poster)"] = WINDOW.getProperty("NextAired.%s.Art(poster)"%str(count)).decode("utf-8")
                    extraprops["Art(fanart)"] = WINDOW.getProperty("NextAired.%s.Art(fanart)"%str(count)).decode("utf-8")
                    extraprops["Art(landscape)"] = WINDOW.getProperty("NextAired.%s.Art(landscape)"%str(count)).decode("utf-8")
                    extraprops["Art(clearlogo)"] = WINDOW.getProperty("NextAired.%s.Art(clearlogo)"%str(count)).decode("utf-8")
                    extraprops["Art(clearart)"] = WINDOW.getProperty("NextAired.%s.Art(clearart)"%str(count)).decode("utf-8")
                    extraprops["Art(characterart)"] = WINDOW.getProperty("NextAired.%s.Art(characterart)"%str(count)).decode("utf-8")
                    item["extraproperties"] = extraprops
                    tvshowpath = "ActivateWindow(Videos,videodb://tvshows/titles/%s/,return)" %str(item["tvshowid"])
                    item["file"]="plugin://script.skin.helper.service?action=LAUNCH&path=" + tvshowpath
                    item["tvshowtitle"] = WINDOW.getProperty("NextAired.%s.Label"%str(count)).decode("utf-8")
                    item["title"] = WINDOW.getProperty("NextAired.%s.NextTitle"%str(count)).decode("utf-8")
                    item["season"] = WINDOW.getProperty("NextAired.%s.NextSeasonNumber"%str(count)).decode("utf-8")
                    item["episode"] = WINDOW.getProperty("NextAired.%s.NextEpisodeNumber"%str(count)).decode("utf-8")
                    allItems.append(item)
                    count += 1
                    if count == limit:
                        break
    return allItems

def RECOMMENDEDMOVIES(limit):
    count = 0
    allItems = []
    # First we get a list of all the in-progress Movies
    numitems = 0
    json_result = getJSON('VideoLibrary.GetMovies','{ "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ %s ] }' %fields_movies)
    for item in json_result:
        if numitems >= limit:
            break
        allItems.append(item)
        numitems +=1
    
    #plex in progress
    if WINDOW.getProperty("plexbmc.0.title"):
        nodes = []
        for i in range(50):
            key = "plexbmc.%s.ondeck"%(str(i))
            path = WINDOW.getProperty(key + ".content")
            label = WINDOW.getProperty(key + ".title")
            type = WINDOW.getProperty("plexbmc.%s.type"%(str(i)))
            if not label: break
            else:
                if "movie" in type:
                    json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(path,fields_files))
                    for item in json_result:
                        if numitems >= limit:
                            break
                        allItems.append(item)
                        numitems +=1
    
    # Fill the list with random items with a score higher then 7
    json_result = getJSON('VideoLibrary.GetMovies','{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"greaterthan", "field":"rating", "value":"7"}]}, "properties": [ %s ] }' %fields_movies)
    # If we found any, find the oldest unwatched show for each one.
    for item in json_result:
        if numitems >= limit:
            break
        allItems.append(item)
        numitems +=1
        
    #plex recommended
    if WINDOW.getProperty("plexbmc.0.title"):
        for i in range(50):
            key = "plexbmc.%s.ondeck"%(str(i))
            path = WINDOW.getProperty(key + ".unwatched")
            label = WINDOW.getProperty(key + ".title")
            type = WINDOW.getProperty("plexbmc.%s.type"%(str(i)))
            if not label: break
            if "movie" in type:
                json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(path,fields_files))
                for item in json_result:
                    rating = item["rating"]
                    if rating > 7:
                        if numitems >= limit:
                            break
                        allItems.append(item)
                        numitems +=1    
        
    return allItems

def RECOMMENDEDALBUMS(limit,browse=False):
    count = 0
    allItems = []
    allTitles = list()
    #query last played albums and find albums of same genre and sort by rating
    json_result = getJSON('AudioLibrary.GetRecentlyPlayedAlbums', '{ "sort": { "order": "descending", "method": "lastplayed" }, "properties": [ %s ], "limits":{"end":%d} }' %(fields_albums,limit))
    if not json_result:
        #if no recent played albums just grab a list of random albums...
        json_result = getJSON('AudioLibrary.GetAlbums', '{ "sort": { "order": "descending", "method": "random" }, "properties": [ %s ], "limits":{"end":%d} }' %(fields_albums,limit))

    for item in json_result:
        genres = item["genre"]
        similartitle = item["title"]
        if count == limit: break
        #get all movies from the same genre
        for genre in genres:
            if count == limit: break
            json_result = getJSON('AudioLibrary.GetAlbums', '{ "sort": { "order": "descending", "method": "rating" }, "filter": {"operator":"is", "field":"genre", "value":"%s"}, "properties": [ %s ] }' %(genre,fields_albums))
            for item in json_result:
                if count == limit: break
                if not item["title"] in allTitles and not item["title"] == similartitle and genre in item["genre"]:
                    item["art"] = artutils.getMusicArtwork(item["displayartist"], item["label"])
                    item["type"] = "album"
                    item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
                    item['album_description'] = item["art"].get("info","")
                    if browse == "true":
                        item["file"] = "musicdb://albums/%s/" %str(item["albumid"])
                    else:
                        item['file'] = "plugin://script.skin.helper.service/?action=playalbum&path=%s" %item['albumid']
                    allItems.append((item["rating"],item))
                    allTitles.append(item["title"])
                    count += 1

        #sort the list by rating 
        allItems = sorted(allItems,key=itemgetter(0),reverse=True)
        if allItems: WINDOW.setProperty("skinhelper-recommendedalbums", repr(allItems))

    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef

def RECOMMENDEDSONGS(limit):
    count = 0
    allItems = []
    allTitles = list()
    #query last played songs and find songs of same genre and sort by rating
    json_result = getJSON('AudioLibrary.GetRecentlyPlayedSongs', '{ "sort": { "order": "descending", "method": "lastplayed" }, "properties": [ %s ], "limits":{"end":%d} }' %(fields_songs,limit))
    if not json_result:
        json_result = getJSON('AudioLibrary.GetSongs', '{ "sort": { "order": "descending", "method": "random" }, "properties": [ %s ], "limits":{"end":%d} }' %(fields_songs,limit))
    for item in json_result:
        genres = item["genre"]
        similartitle = item["title"]
        if count == limit: break
        #get all movies from the same genre
        for genre in genres:
            if count == limit: break
            json_result = getJSON('AudioLibrary.GetSongs', '{ "sort": { "order": "descending", "method": "rating" }, "filter": {"operator":"is", "field":"genre", "value":"%s"}, "properties": [ %s ],"limits":{"end":%d} }' %(genre,fields_songs,limit))
            for item in json_result:
                if count == limit: break
                if not item["title"] in allTitles and not item["title"] == similartitle:
                    item["art"] = artutils.getMusicArtwork(item["displayartist"], item["album"])
                    item["type"] = "song"
                    item["extraproperties"] = {"extrafanart": item["art"].get("extrafanart",""), "tracklist":item["art"].get("tracklist","")}
                    item['album_description'] = item["art"].get("info","")
                    allItems.append((item["rating"],item))
                    allTitles.append(item["title"])
                    count += 1
                    

        #sort the list by rating 
        allItems = sorted(allItems,key=itemgetter(0),reverse=True)

    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef
    
def SIMILARMOVIES(limit,imdbid="",unSorted=False):
    count = 0
    allItems = []
    allTitles = list()
    json_result = []
    #lookup movie by imdbid or just pick a random watched movie

    if imdbid:
        json_result = getJSON('VideoLibrary.GetMovies', '{ "properties": [ "title", "rating", "genre", "imdbnumber"]}')
        for item in json_result:
            if item.get("imdbnumber") == imdbid:
                json_result = [item]
                break
    if not json_result: json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"operator":"isnot", "field":"playcount", "value":"0"}, "properties": [ "title", "rating", "genre"],"limits":{"end":1}}')
    for item in json_result:
        if count == limit: break
        genres = item["genre"]
        similartitle = item["title"]
        #get all movies from the same genre
        for genre in genres:
            if count == limit: break
            json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"genre", "value":"%s"}, {"operator":"is", "field":"playcount", "value":"0"}]}, "properties": [ %s ],"limits":{"end":%d} }' %(genre,fields_movies,limit))
            for item in json_result:
                if count == limit: break
                if not item["title"] in allTitles and not item["title"] == similartitle:
                    item["extraproperties"] = {"similartitle": similartitle, "originalpath": item["file"]}
                    allItems.append((item["rating"],item))
                    allTitles.append(item["title"])
                    count +=1
    
    #sort the list by rating
    if unSorted: return allItems
    allItems = sorted(allItems,key=itemgetter(0),reverse=True)
        
    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef

def MOVIESFORGENRE(limit,genretitle=""):
    count = 0
    allItems = []

    if not genretitle:
        #get a random genre
        json_result = getJSON('VideoLibrary.GetGenres', '{ "sort": { "order": "descending", "method": "random" }, "type": "movie","limits":{"end":1}}')
        if json_result: genretitle = json_result[0].get("label")

    if genretitle:
        #get all movies from the same genre
        allTitles = list()
        json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"genre", "value":"%s"}, {"operator":"is", "field":"playcount", "value":"0"}]}, "properties": [ %s ],"limits":{"end":%d} }' %(genretitle,fields_movies,limit))
        for item in json_result:
            if not item["title"] in allTitles:
                item["extraproperties"] = {"genretitle": genretitle, "originalpath": item["file"]}
                allItems.append((item["rating"],item))
                allTitles.append(item["title"])

        #sort the list by rating
        allItems = sorted(allItems,key=itemgetter(0),reverse=True)

    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef
   
def BROWSEGENRES(limit, type="movie"):
    count = 0
    allItems = []

    #get all genres
    json_result = getJSON('VideoLibrary.GetGenres', '{"type": "%s", "sort": { "order": "ascending", "method": "title" }}' %type)
    for genre in json_result:
        #for each genre we get 5 random items from the library
        genre["art"] = {}
        if type== "tvshow":
            genre["file"] = "videodb://tvshows/genres/%s/"%genre["genreid"]
            json_result = getJSON('VideoLibrary.GetTvshows', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"operator":"is", "field":"genre", "value":"%s"}, "properties": [ %s ],"limits":{"end":%d} }' %(genre["label"],fields_tvshows,5))
        else:
            genre["file"] = "videodb://movies/genres/%s/"%genre["genreid"]
            json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"operator":"is", "field":"genre", "value":"%s"}, "properties": [ %s ],"limits":{"end":%d} }' %(genre["label"],fields_movies,5))
        for count, item in enumerate(json_result):
            genre["art"]["poster.%s" %count] = item["art"].get("poster","")
            genre["art"]["fanart.%s" %count] = item["art"].get("fanart","")
        genre["isFolder"] = True
        genre["IsPlayable"] = "false"
        genre["thumbnail"] = "DefaultGenre.png"
        allItems.append(genre)

    return allItems
    
def SIMILARSHOWS(limit,imdbid="",unSorted=False):
    count = 0
    allItems = []
    allTitles = list()
    json_result = []
    #lookup show by imdbid or just pick a random in progress show
    if imdbid: 
        json_result = getJSON('VideoLibrary.GetTVShows', '{ "properties": [ "title", "rating", "genre", "imdbnumber"]}')
        for item in json_result:
            if item.get("imdbnumber") == imdbid:
                json_result = [item]
                break
    if not json_result: json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "rating", "genre"],"limits":{"end":1}}')
    for item in json_result:
        genres = item["genre"]
        similartitle = item["title"]
        #get all movies from the same genre
        for genre in genres:
            json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"genre", "value":"%s"}, {"operator":"is", "field":"playcount", "value":"0"}]}, "properties": [ %s ],"limits":{"end":%d} }' %(genre,fields_tvshows,limit))
            for item in json_result:
                if not item["title"] in allTitles and not item["title"] == similartitle:
                    item["extraproperties"] = {"similartitle": similartitle, "IsPlayable": "false", "originalpath": item["file"]}
                    tvshowpath = "ActivateWindow(Videos,videodb://tvshows/titles/%s/,return)" %str(item["tvshowid"])
                    item["file"]="plugin://script.skin.helper.service?action=LAUNCH&path=" + tvshowpath
                    allItems.append((item["rating"],item))
                    allTitles.append(item["title"])
        
        #sort the list by rating
        if unSorted: return allItems
        allItems = sorted(allItems,key=itemgetter(0),reverse=True)
        
    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef

def SIMILARMEDIA(limit,imdb=""):
    #get similar results for both movies and shows
    allItems = SIMILARMOVIES(limit,imdb,True)
    allItems += SIMILARSHOWS(limit,imdb,True)
    #sort the list by rating
    allItems = sorted(allItems,key=itemgetter(0),reverse=True)
        
    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef
       
def SHOWSFORGENRE(limit,genretitle=""):
    count = 0
    allItems = []
    
    if not genretitle:
        #get a random genre
        json_result = getJSON('VideoLibrary.GetGenres', '{ "sort": { "order": "descending", "method": "random" }, "type": "tvshow","limits":{"end":1}}')
        if json_result: genretitle = json_result[0].get("label")

    #get all shows from the same genre
    if genretitle:
        allTitles = list()
        json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"genre", "value":"%s"}, {"operator":"is", "field":"playcount", "value":"0"}]}, "properties": [ %s ],"limits":{"end":%d} }' %(genretitle,fields_tvshows,limit))
        for item in json_result:
            if not item["title"] in allTitles:
                item["extraproperties"] = {"genretitle": genretitle, "IsPlayable": "false", "originalpath": item["file"]}
                tvshowpath = "ActivateWindow(Videos,videodb://tvshows/titles/%s/,return)" %str(item["tvshowid"])
                item["file"]="plugin://script.skin.helper.service?action=LAUNCH&path=" + tvshowpath
                allItems.append((item["rating"],item))
                allTitles.append(item["title"])

        #sort the list by rating
        allItems = sorted(allItems,key=itemgetter(0),reverse=True)

    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef
  
def buildRecommendedMediaListing(limit,ondeckContent=False,recommendedContent=True):
    count = 0
    allTitles = list()
    allItems = []
    
    if ondeckContent:
        allOndeckItems = []

        #netflix in progress
        if WINDOW.getProperty("netflix.generic.inprogress.content"):
            json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(WINDOW.getProperty("netflix.generic.inprogress.content").decode("utf-8"),fields_files))
            for item in json_result:
                lastplayed = item["lastplayed"]
                if not item["title"] in allTitles:
                    allOndeckItems.append((lastplayed,item))
                    allTitles.append(item["title"])
        
        #plex in progress
        if WINDOW.getProperty("plexbmc.0.title"):
            for i in range(50):
                key = "plexbmc.%s.ondeck"%(str(i))
                path = WINDOW.getProperty(key + ".content")
                label = WINDOW.getProperty(key + ".title")
                if not path: break
                json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(path,fields_files))
                for item in json_result:
                    lastplayed = item["lastplayed"]
                    if not item["title"] in allTitles:
                        allOndeckItems.append((lastplayed,item))
                        allTitles.append(item["title"])

        # Get a list of all the in-progress Movies
        json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ %s ] }' %fields_movies)
        for item in json_result:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles:
                allOndeckItems.append((lastplayed,item))
                allTitles.append(item["title"])
        
        # Get a list of all the in-progress MusicVideos
        json_result = getJSON('VideoLibrary.GetMusicVideos', '{ "sort": { "order": "descending", "method": "lastplayed" }, "limits": { "start" : 0, "end": 25 }, "properties": [ %s ] }' %fields_musicvideos)
        for item in json_result:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles and item["resume"]["position"] != 0:
                allOndeckItems.append((lastplayed,item))
                allTitles.append(item["title"])
        
        # Get a list of all the in-progress music songs
        json_result = getJSON('AudioLibrary.GetRecentlyPlayedSongs', '{ "sort": { "order": "descending", "method": "lastplayed" }, "limits": { "start" : 0, "end": 5 }, "properties": [ %s ] }' %fields_songs)
        for item in json_result:
            lastplayed = item["lastplayed"]
            if not item["title"] in allTitles and lastplayed and item["thumbnail"]:
                allOndeckItems.append((lastplayed,item))
                allTitles.append(item["title"])
        
        # Get a list of all the in-progress tv recordings   
        json_result = PVRRECORDINGS(limit)
        for item in json_result:
            lastplayed = None
            if not item["title"] in allTitles:
                allOndeckItems.append((lastplayed,item))
                allTitles.append(item["title"])

        # NextUp episodes
        json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "lastplayed" }, "filter": {"and": [{"operator":"true", "field":"inprogress", "value":""}]}, "properties": [ "title", "lastplayed" ] }')
        for show in json_result:
            json_query2 = getJSON('VideoLibrary.GetEpisodes', '{ "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ %s ], "limits":{"end":1}}' %(show['tvshowid'], fields_episodes))
            for item in json_query2:
                lastplayed = sorted([show["lastplayed"], item["dateadded"]], reverse=True)[0]
                if not item["title"] in allTitles:
                    allOndeckItems.append((lastplayed,item))
                    allTitles.append(item["title"])
        
        #sort the list with in progress items by lastplayed date   
        allItems = sorted(allOndeckItems,key=itemgetter(0),reverse=True)
        
    
    if recommendedContent:
        allRecommendedItems = []
                        
        # Random movies with a score higher then 7
        json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"greaterthan", "field":"rating", "value":"7"}]}, "properties": [ %s ], "limits":{"end":25} }' %fields_movies)
        for item in json_result:
            rating = item["rating"]
            if not item["title"] in set(allTitles):
                allRecommendedItems.append((rating,item))
                allTitles.append(item["title"])
                    
        # Random tvshows with a score higher then 7
        json_result = getJSON('VideoLibrary.GetTVShows', '{ "sort": { "order": "descending", "method": "random" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"greaterthan", "field":"rating", "value":"7"}]}, "properties": [ %s ],"limits":{"end":25} }' %fields_tvshows)
        for item in json_result:
            rating = item["rating"]
            if not item["title"] in set(allTitles):
                #get the first unwatched episode for this show
                json_query2 = getJSON('VideoLibrary.GetEpisodes', '{ "tvshowid": %d, "sort": {"method":"episode"}, "filter": {"and": [ {"field": "playcount", "operator": "lessthan", "value":"1"}, {"field": "season", "operator": "greaterthan", "value": "0"} ]}, "properties": [ "title", "file" ], "limits":{"end":1}}' %item['tvshowid'])
                if json_query2:
                    item["file"] = json_query2[0]["file"]
                    item["tvshowtitle"] = item["title"]
                    allRecommendedItems.append((rating,item))
                    allTitles.append(item["title"])
                    
        #plex recommended
        if WINDOW.getProperty("plexbmc.0.title"):
            for i in range(50):
                key = "plexbmc.%s.unwatched"%(str(i))
                path = WINDOW.getProperty(key + ".content")
                label = WINDOW.getProperty(key + ".title")
                type = WINDOW.getProperty("plexbmc.%s.type"%(str(i)))
                if not label: break
                if "movie" in type or "show" in type:
                    json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(path,fields_files))
                    for item in json_result:
                        rating = item["rating"]
                        if not item["title"] in allTitles and rating > 7:
                            allOndeckItems.append((rating,item))
                            allTitles.append(item["title"])
                    
        #sort the list with recommended items by rating 
        allItems += sorted(allRecommendedItems,key=itemgetter(0),reverse=True)
        
    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef

def INPROGRESSANDRECOMMENDEDMEDIA(limit):
    return buildRecommendedMediaListing(limit,ondeckContent=True,recommendedContent=True)

def INPROGRESSMEDIA(limit):
    return buildRecommendedMediaListing(limit,ondeckContent=True,recommendedContent=False)

def RECOMMENDEDMEDIA(limit):
    return buildRecommendedMediaListing(limit,ondeckContent=False,recommendedContent=True)

def RECENTMEDIA(limit):
    count = 0
    allItems = []
    allTitles = []
    # Get a list of all the recent Movies (unwatched and not in progress)
    json_result = getJSON('VideoLibrary.GetMovies', '{ "sort": { "order": "descending", "method": "dateadded" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"false", "field":"inprogress", "value":""}]}, "properties": [ %s ], "limits":{"end":15} }' %fields_movies)
    for item in json_result:
        dateadded = item["dateadded"]
        if not item["title"] in allTitles:
            allItems.append((dateadded,item))
            allTitles.append(item["title"])
    
    # Get a list of all the recent MusicVideos (unwatched and not in progress)
    json_result = getJSON('VideoLibrary.GetMusicVideos', '{ "limits": { "start" : 0, "end": 15 },"sort": { "order": "descending", "method": "dateadded" }, "filter": {"operator":"is", "field":"playcount", "value":"0"}, "properties": [ %s ] }' %fields_musicvideos)
    for item in json_result:
        dateadded = item["dateadded"]
        if not item["title"] in allTitles and item["resume"]["position"] == 0:
            allItems.append((dateadded,item))
            allTitles.append(item["title"])
    
    # Get a list of all the recent music songs
    json_result = getJSON('AudioLibrary.GetSongs', '{ "limits": { "start" : 0, "end": 15 }, "sort": {"order": "descending", "method": "dateadded" }, "filter": {"operator":"is", "field":"playcount", "value":"0"}, "properties": [ %s ] }' %fields_songs)
    for item in json_result:
        dateadded = ""
        if not item["title"] in allTitles and item["thumbnail"]:
            allItems.append((dateadded,item))
            allTitles.append(item["title"])
    
    # Get a list of all the recent episodes (unwatched and not in progress)
    json_result = getJSON('VideoLibrary.GetEpisodes', '{ "sort": { "order": "descending", "method": "dateadded" }, "filter": {"and": [{"operator":"is", "field":"playcount", "value":"0"},{"operator":"false", "field":"inprogress", "value":""}]}, "properties": [ %s ], "limits":{"end":15} }' %fields_episodes)
    for item in json_result:
        dateadded = item["dateadded"]
        if not item["title"] in allTitles:
            allItems.append((dateadded,item))
            allTitles.append(item["title"])
            
    # Get a list of all the unwatched recent tv recordings   
    json_result = PVRRECORDINGS(limit)
    for item in json_result:
        lastplayed = item["endtime"]
        if not item["title"] in allTitles:
            allItems.append((lastplayed,item))
            allTitles.append(item["title"])
    
    #recent plex items
    if WINDOW.getProperty("plexbmc.0.title"):
        nodes = []
        for i in range(50):
            key = "plexbmc.%s.recent"%(str(i))
            path = WINDOW.getProperty(key + ".content")
            label = WINDOW.getProperty(key + ".title")
            type = WINDOW.getProperty("plexbmc.%s.type"%(str(i)))
            if not label: break
            json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(path,fields_files))
            for item in json_result:
                dateadded = item["dateadded"]
                if not item["title"] in allTitles:
                    allItems.append((dateadded,item))
                    allTitles.append(item["title"])
    
    #sort the list with in recent items by lastplayed date   
    allItems = sorted(allItems,key=itemgetter(0),reverse=True)
    if allItems: WINDOW.setProperty("skinhelper-recentmedia", repr(allItems))
    
    #only return the listitems, we dont care about the sortkey
    allItemsDef = []
    for item in allItems:
        allItemsDef.append(item[1])
    return allItemsDef

def FAVOURITEMEDIA(limit,AllKodiFavsOnly=False):
    count = 0
    allItems = []
    
    if not AllKodiFavsOnly:
        #netflix favorites
        if WINDOW.getProperty("netflix.generic.mylist.content"):
            json_result = getJSON('Files.GetDirectory', '{ "directory": "%s", "media": "files", "properties": [ %s ] }' %(WINDOW.getProperty("netflix.generic.mylist.content").decode("utf-8"),fields_files))
            for item in json_result:
                allItems.append(item)
        
        #emby favorites
        if xbmc.getCondVisibility("System.HasAddon(plugin.video.emby) + Skin.HasSetting(SmartShortcuts.emby)"):
            json_result = getJSON('VideoLibrary.GetMovies', '{ "filter": {"operator":"contains", "field":"tag", "value":"Favorite movies"}, "properties": [ %s ] }' %fields_movies)
            for item in json_result:
                allItems.append(item)
            
            json_result = getJSON('VideoLibrary.GetTvShows', '{ "filter": {"operator":"contains", "field":"tag", "value":"Favorite tvshows"}, "properties": [ %s ] }' %fields_tvshows)
            for item in json_result:
                tvshowpath = "ActivateWindow(Videos,videodb://tvshows/titles/%s/,return)" %str(item["tvshowid"])
                tvshowpath="plugin://script.skin.helper.service?action=launch&path=" + tvshowpath
                item["file"] == tvshowpath
                allItems.append(item)
    
    #Kodi favourites
    json_result = getJSON('Favourites.GetFavourites', '{"type": null, "properties": ["path", "thumbnail", "window", "windowparameter"]}')
    for fav in json_result:
        matchFound = False
        if "windowparameter" in fav:
            if fav["windowparameter"].startswith("videodb://tvshows/titles"):
                #it's a tv show
                try:
                    tvshowid = int(fav["windowparameter"].split("/")[-2])
                except: continue
                json_result = getJSON('VideoLibrary.GetTVShowDetails', '{ "tvshowid": %d, "properties": [ %s ]}' %(tvshowid, fields_tvshows))
                if json_result:
                    matchFound = True
                    tvshowpath = "ActivateWindow(Videos,%s,return)" %fav["windowparameter"]
                    tvshowpath="plugin://script.skin.helper.service?action=launch&path=" + tvshowpath
                    json_result["file"] == tvshowpath
                    allItems.append(json_result)            
        if fav["type"] == "media":
            path = fav["path"]
            if "/" in path:
                sep = "/"
            else:
                sep = "\\"
            pathpart = path.split(sep)[-1] #apparently only the filename can be used for the search
            #is this a movie?
            json_result = getJSON('VideoLibrary.GetMovies', '{ "filter": {"operator":"contains", "field":"filename", "value":"%s"}, "properties": [ %s ] }' %(pathpart,fields_movies))
            for item in json_result:
                if item['file'] == path:
                    matchFound = True
                    allItems.append(item)
            
            if matchFound == False:
                #is this an episode ?
                json_result = getJSON('VideoLibrary.GetEpisodes', '{ "filter": {"operator":"contains", "field":"filename", "value":"%s"}, "properties": [ %s ] }' %(pathpart,fields_episodes))
                for item in json_result:
                    if item['file'] == path:
                        matchFound = True
                        allItems.append(item)
            if matchFound == False:
                #is this a song?
                json_result = getJSON('AudioLibrary.GetSongs', '{ "filter": {"operator":"contains", "field":"filename", "value":"%s"}, "properties": [ %s ] }' %(pathpart, fields_songs))
                for item in json_result:
                    if item['file'] == path:
                        matchFound = True
                        allItems.append(item)
                            
            if matchFound == False:
                #is this a musicvideo?
                json_result = getJSON('VideoLibrary.GetMusicVideos', '{ "filter": {"operator":"contains", "field":"filename", "value":"%s"}, "properties": [ %s ] }' %(pathpart, fields_musicvideos))
                for item in json_result:
                    if item['file'] == path:
                        matchFound = True
                        allItems.append(item)
        if not matchFound and AllKodiFavsOnly:
            #add unknown item in the result...
            if fav.get("type") == "window":
                path = 'ActivateWindow(%s,"%s",return)' %(fav.get("window",""),fav.get("windowparameter",""))
                path="plugin://script.skin.helper.service/?action=launch&path=" + path
            elif fav.get("type") == "script":
                path='plugin://script.skin.helper.service/?action=launch&path=RunScript("%s")' %fav.get("path")
            else:
                path = fav.get("path")
            if not fav.get("label"): fav["label"] = fav.get("title")
            if not fav.get("title"): fav["label"] = fav.get("label")
            item = {"label": fav.get("label"), "title": fav.get("title"), "thumbnail":fav.get("thumbnail"), "file":path}
            if fav.get("thumbnail").endswith("icon.png") and fav.get("thumbnail").endswith("icon.png") and  xbmcvfs.exists(fav.get("thumbnail").replace("icon.png","fanart.jpg")):
                item["art"] = {"landscape": fav.get("thumbnail"), "poster": fav.get("thumbnail"), "fanart": fav.get("thumbnail").replace("icon.png","fanart.jpg")}
            item["extraproperties"] = {"IsPlayable": "false"}
            allItems.append(item)
            
    return allItems
    
def getExtraFanArt(path):
    extrafanarts = []
    #get extrafanarts from window property
    if path.startswith("EFA_FROMWINDOWPROP_"):
        extrafanarts = eval(WINDOW.getProperty(path).decode("utf-8"))
    #get extrafanarts by passing an artwork cache xml file
    else:
        if not xbmcvfs.exists(path):
            filepart = path.split("/")[-1]
            path = path.replace(filepart,"") + normalize_string(filepart)
            if not xbmcvfs.exists(path):
                logMsg("getExtraFanArt FAILED for path: %s" %path,0)
        artwork = artutils.getArtworkFromCacheFile(path)
        if artwork.get("extrafanarts"):
            extrafanarts = eval( artwork.get("extrafanarts") )
            
    #process extrafanarts
    for item in extrafanarts:
        li = xbmcgui.ListItem(item, path=item)
        li.setProperty('mimetype', 'image/jpeg')
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item, listitem=li)
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))

def GETCASTMEDIA(limit,name=""):
    allItems = []
    if name:
        json_result = getJSON('VideoLibrary.GetMovies', '{ "properties": [ %s ] }' %fields_movies)
        for item in json_result:
            for castmember in item["cast"]:
                if castmember["name"].lower() == name.lower():
                    url = "RunScript(script.skin.helper.service,action=showinfo,movieid=%s)" %item["movieid"]
                    item["file"] = "plugin://script.skin.helper.service/?action=launch&path=" + url
                    allItems.append(item)
        json_result = getJSON('VideoLibrary.GetTvShows', '{ "properties": [ %s ] }' %fields_tvshows)
        for item in json_result:
            for castmember in item["cast"]:
                if castmember["name"].lower() == name.lower():
                    url = "RunScript(script.skin.helper.service,action=showinfo,tvshowid=%s)" %item["tvshowid"]
                    item["file"] = "plugin://script.skin.helper.service/?action=launch&path=" + url
                    allItems.append(item)
    return allItems
    
def getCast(movie=None,tvshow=None,movieset=None,episode=None,downloadThumbs=False,listOnly=False):
    itemId = None
    item = {}
    allCast = []
    castNames = list()
    cachedataStr = ""
    try:
        if movieset:
            cachedataStr = "movieset.castcache-" + str(movieset)+str(downloadThumbs)
            itemId = int(movieset)
        elif tvshow:
            cachedataStr = "tvshow.castcache-" + str(tvshow)+str(downloadThumbs)
            itemId = int(tvshow)
        elif movie:
            cachedataStr = "movie.castcache-" + str(movie)+str(downloadThumbs)
            itemId = int(movie)
        elif episode:
            cachedataStr = "episode.castcache-" + str(episode)+str(downloadThumbs)
            itemId = int(episode)
        elif not (movie or tvshow or episode or movieset) and xbmc.getCondVisibility("Window.IsActive(DialogVideoInfo.xml)"):
            cachedataStr = xbmc.getInfoLabel("ListItem.Title")+xbmc.getInfoLabel("ListItem.FileNameAndPath")+str(downloadThumbs)
    except: pass
    
    cachedata = WINDOW.getProperty(cachedataStr).decode("utf-8")
    if cachedata:
        #get data from cache
        allCast = eval(cachedata)
    else:
        
        #retrieve data from json api...
        if movie and itemId:
            json_result = getJSON('VideoLibrary.GetMovieDetails', '{ "movieid": %d, "properties": [ "title", "cast" ] }' %itemId)
            if json_result and json_result.get("cast"): allCast = json_result.get("cast")
        elif movie and not itemId:
            json_result = getJSON('VideoLibrary.GetMovies', '{ "filter": {"operator":"is", "field":"title", "value":"%s"}, "properties": [ "title", "cast" ] }' %movie.encode("utf-8"))
            if json_result and json_result[0].get("cast"): allCast = json_result[0].get("cast")
        elif tvshow and itemId:
            json_result = getJSON('VideoLibrary.GetTVShowDetails', '{ "tvshowid": %d, "properties": [ "title", "cast" ] }' %itemId)
            if json_result and json_result.get("cast"): allCast = json_result.get("cast")
        elif tvshow and not itemId:
            json_result = getJSON('VideoLibrary.GetTvShows', '{ "filter": {"operator":"is", "field":"title", "value":"%s"}, "properties": [ "title", "cast" ] }' %tvshow.encode("utf-8"))
            if json_result and json_result[0].get("cast"): allCast = json_result[0].get("cast")
        elif episode and itemId:
            json_result = getJSON('VideoLibrary.GetEpisodeDetails', '{ "episodeid": %d, "properties": [ "title", "cast" ] }' %itemId)
            if json_result and json_result.get("cast"): allCast = json_result.get("cast")
        elif episode and not itemId:
            json_result = getJSON('VideoLibrary.GetEpisodes', '{ "filter": {"operator":"is", "field":"title", "value":"%s"}, "properties": [ "title", "cast" ] }' %episode.encode("utf-8"))
            if json_result and json_result[0].get("cast"): allCast = json_result[0].get("cast")
        elif movieset:
            moviesetmovies = []
            if itemId:
                json_result = getJSON('VideoLibrary.GetMovieSetDetails', '{ "setid": %d, "properties": [ "title" ] }' %itemId)
                if json_result.has_key("movies"): moviesetmovies = json_result['movies']
            elif not itemId:
                json_result = getJSON('VideoLibrary.GetMovieSets', '{ "properties": [ "title" ] }')
                for result in json_result:
                    if result.get("title") == movieset:
                        moviesetmovies = result['movies']
                        break
            if moviesetmovies:
                for setmovie in moviesetmovies:
                    json_result = getJSON('VideoLibrary.GetMovieDetails', '{ "movieid": %d, "properties": [ "title", "cast" ] }' %setmovie["movieid"])
                    if json_result and json_result.get("cast"): allCast += json_result.get("cast")
        
        #no item provided, try to grab the cast list from container 50 (dialogvideoinfo)
        elif not (movie or tvshow or episode or movieset) and xbmc.getCondVisibility("Window.IsActive(DialogVideoInfo.xml)"):
            for i in range(250):
                label = xbmc.getInfoLabel("Container(50).ListItemNoWrap(%s).Label" %i).decode("utf-8")
                if not label: break
                label2 = xbmc.getInfoLabel("Container(50).ListItemNoWrap(%s).Label2" %i).decode("utf-8")
                thumb = getCleanImage( xbmc.getInfoLabel("Container(50).ListItemNoWrap(%s).Thumb" %i).decode("utf-8") )
                allCast.append( { "name": label, "role": label2, "thumbnail": thumb } )
        else:
            #no id or title provided, skip...
            allCast = []
                
        #lookup tmdb if item is requested that is not in local db
        tmdbdetails = {}
        if movie and not allCast and not itemId:
            tmdbdetails = artutils.getTmdbDetails(movie,None,"movie",True)
        elif tvshow and not allCast and not itemId:
            tmdbdetails = artutils.getTmdbDetails(tvshow,None,"tv",True)
        if tmdbdetails:
            allCast = tmdbdetails.get("cast")
        
        
        #optional: download missing actor thumbs
        if allCast and downloadThumbs:
            for cast in allCast:
                if cast.get("thumbnail"): cast["thumbnail"] = getCleanImage(cast.get("thumbnail"))
                if not cast.get("thumbnail"): 
                    artwork = artutils.getTmdbDetails(cast["name"],None,"person")
                    cast["thumbnail"] = artwork.get("thumb","")

        #save to cache    
        WINDOW.setProperty(cachedataStr,repr(allCast))
    
    #process listing with the results...
    if listOnly: return allCast
    for cast in allCast:
        if cast.get("name") not in castNames:
            liz = xbmcgui.ListItem(label=cast.get("name"),label2=cast.get("role"),iconImage=cast.get("thumbnail"))
            liz.setProperty('IsPlayable', 'false')
            url = "RunScript(script.extendedinfo,info=extendedactorinfo,name=%s)"%cast.get("name")
            path="plugin://script.skin.helper.service/?action=launch&path=" + url
            castNames.append(cast.get("name"))
            liz.setThumbnailImage(cast.get("thumbnail"))
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=path, listitem=liz, isFolder=False)
    
    WINDOW.setProperty('SkinHelper.ListItemCast', "[CR]".join(castNames))
    
    xbmcplugin.endOfDirectory(int(sys.argv[1]))    