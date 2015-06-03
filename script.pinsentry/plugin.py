# -*- coding: utf-8 -*-
import sys
import os
import urllib
import urlparse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson


__addon__ = xbmcaddon.Addon(id='script.pinsentry')
__icon__ = __addon__.getAddonInfo('icon')
__fanart__ = __addon__.getAddonInfo('fanart')
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")
__profile__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources').encode("utf-8")).decode("utf-8")
__lib__ = xbmc.translatePath(os.path.join(__resource__, 'lib').encode("utf-8")).decode("utf-8")


sys.path.append(__resource__)
sys.path.append(__lib__)

# Import the common settings
from settings import Settings
from settings import log
from database import PinSentryDB


###################################################################
# Class to handle the navigation information for the plugin
###################################################################
class MenuNavigator():
    MOVIES = 'movies'
    TVSHOWS = 'tvshows'
    MOVIESETS = 'sets'
    PLUGINS = 'plugins'

    def __init__(self, base_url, addon_handle):
        self.base_url = base_url
        self.addon_handle = addon_handle

    # Creates a URL for a directory
    def _build_url(self, query):
        return self.base_url + '?' + urllib.urlencode(query)

    # Display the default list of items in the root menu
    def showRootMenu(self):
        # Movies
        url = self._build_url({'mode': 'folder', 'foldername': MenuNavigator.MOVIES})
        li = xbmcgui.ListItem(__addon__.getLocalizedString(32201), iconImage=__icon__)
        li.setProperty("Fanart_Image", __fanart__)
        li.addContextMenuItems([], replaceItems=True)
        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

        # TV Shows
        url = self._build_url({'mode': 'folder', 'foldername': MenuNavigator.TVSHOWS})
        li = xbmcgui.ListItem(__addon__.getLocalizedString(32202), iconImage=__icon__)
        li.setProperty("Fanart_Image", __fanart__)
        li.addContextMenuItems([], replaceItems=True)
        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

        # Movie Sets
        url = self._build_url({'mode': 'folder', 'foldername': MenuNavigator.MOVIESETS})
        li = xbmcgui.ListItem(__addon__.getLocalizedString(32203), iconImage=__icon__)
        li.setProperty("Fanart_Image", __fanart__)
        li.addContextMenuItems([], replaceItems=True)
        xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

        # Plugins
        if Settings.isActivePlugins():
            url = self._build_url({'mode': 'folder', 'foldername': MenuNavigator.PLUGINS})
            li = xbmcgui.ListItem(__addon__.getLocalizedString(32204), iconImage=__icon__)
            li.setProperty("Fanart_Image", __fanart__)
            li.addContextMenuItems([], replaceItems=True)
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(self.addon_handle)

    # Show the list of videos in a given set
    def showFolder(self, foldername):
        # Check for the special case of manually defined folders
        if foldername == MenuNavigator.TVSHOWS:
            self._setList(MenuNavigator.TVSHOWS, 'GetTVShows', 'tvshowid')
        elif foldername == MenuNavigator.MOVIES:
            self._setList(MenuNavigator.MOVIES, 'GetMovies', 'movieid')
        elif foldername == MenuNavigator.MOVIESETS:
            self._setList(MenuNavigator.MOVIESETS, 'GetMovieSets', 'setid')
        elif foldername == MenuNavigator.PLUGINS:
            self._setList(MenuNavigator.PLUGINS)

    # Produce the list of videos and flag which ones with security details
    def _setList(self, target, jsonGet='', dbid=''):
        items = []
        if target == MenuNavigator.PLUGINS:
            items = self._setPluginList()
        else:
            # Everything other plugins are forms of video
            items = self._getVideos(jsonGet, target, dbid)

        # Now add the security details to the list
        items = self._addSecurityFlags(target, items)

        for item in items:
            # Create the list-item for this video
            li = xbmcgui.ListItem(item['title'], iconImage=item['thumbnail'])

            # Remove the default context menu
            li.addContextMenuItems([], replaceItems=True)
            # Get the title of the video owning the extras
            title = item['title']
            try:
                title = item['title'].encode("utf-8")
            except:
                log("setVideoList: Failed to encode title %s" % title)

            # Record what the new security level will be is selected
            newSecurityLevel = 1
            # Add a tick if security is set
            if item['securityLevel'] > 0:
                li.setInfo('video', {'PlayCount': 1})
                # Next time the item is selected, it will be disabled
                newSecurityLevel = 0

            url = self._build_url({'mode': 'setsecurity', 'level': newSecurityLevel, 'type': target, 'title': title, 'id': item['dbid']})
            xbmcplugin.addDirectoryItem(handle=self.addon_handle, url=url, listitem=li, isFolder=True)

        xbmcplugin.endOfDirectory(self.addon_handle)

    # Do a lookup in the database for the given type of videos
    def _getVideos(self, jsonGet, target, dbid):
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.%s", "params": {"properties": ["title", "thumbnail", "fanart"], "sort": { "method": "title" } }, "id": 1}' % jsonGet)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        log(json_response)
        videolist = []
        if ("result" in json_response) and (target in json_response['result']):
            for item in json_response['result'][target]:
                videoItem = {}
                videoItem['title'] = item['title']

                if item['thumbnail'] is None:
                    videoItem['thumbnail'] = 'DefaultFolder.png'
                else:
                    videoItem['thumbnail'] = item['thumbnail']
                videoItem['fanart'] = item['fanart']

                videoItem['dbid'] = item[dbid]

                videolist.append(videoItem)
        return videolist

    # Adds the current security details to the items
    def _addSecurityFlags(self, type, items):
        # Make sure we have some items to append the details to
        if len(items) < 1:
            return items

        # Make the call to the DB to get all the specific security settings
        pinDB = PinSentryDB()

        securityDetails = {}
        if type == MenuNavigator.TVSHOWS:
            securityDetails = pinDB.getAllTvShowsSecurity()
        elif type == MenuNavigator.MOVIES:
            securityDetails = pinDB.getAllMoviesSecurity()
        elif type == MenuNavigator.MOVIESETS:
            securityDetails = pinDB.getAllMovieSetsSecurity()
        elif type == MenuNavigator.PLUGINS:
            securityDetails = pinDB.getAllPluginsSecurity()

        for item in items:
            # Default security to 0 (Not Set)
            securityLevel = 0
            if item['title'] in securityDetails:
                title = item['title']
                securityLevel = securityDetails[title]
                log("%s has security level %d" % (title, securityLevel))

            item['securityLevel'] = securityLevel

        del pinDB
        return items

    # get the list of plugins installed on the system
    def _setPluginList(self):
        # Make the call to find out all the addons that are installed
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddons", "params": { "type": "xbmc.python.pluginsource", "enabled": true, "properties": ["name", "thumbnail", "fanart"] }, "id": 1}')
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        log(json_response)
        plugins = []
        if ("result" in json_response) and ('addons' in json_response['result']):
            # Check each of the plugins that are installed on the system
            for addonItem in json_response['result']['addons']:
                addonId = addonItem['addonid']
                # Need to skip ourselves
                if addonId in ['script.pinsentry']:
                    log("setPluginList: Skipping PinSentry Plugin")
                    continue

                pluginDetails = {}
                pluginDetails['title'] = addonItem['name']
                pluginDetails['dbid'] = addonId

                if addonItem['thumbnail'] is None:
                    pluginDetails['thumbnail'] = 'DefaultAddon.png'
                else:
                    pluginDetails['thumbnail'] = addonItem['thumbnail']
                pluginDetails['fanart'] = addonItem['fanart']

                plugins.append(pluginDetails)
        return plugins

    # Set the security value for a given video
    def setSecurity(self, type, title, id, level):
        log("Setting security for (id:%s) %s" % (id, title))
        if title not in [None, ""]:
            pinDB = PinSentryDB()
            if type == MenuNavigator.TVSHOWS:
                # Set the security level for this title, setting it to zero
                # will result in the entry being removed from the database
                # as the default for an item is unset
                pinDB.setTvShowSecurityLevel(title, int(id), level)
            elif type == MenuNavigator.MOVIES:
                pinDB.setMovieSecurityLevel(title, int(id), level)
            elif type == MenuNavigator.MOVIESETS:
                pinDB.setMovieSetSecurityLevel(title, int(id), level)
                # As well as setting the security on the Movie set, we need
                # to also set it on each movie in the Movie Set
                self._setSecurityOnMoviesInMovieSets(int(id), level)
            elif type == MenuNavigator.PLUGINS:
                pinDB.setPluginSecurityLevel(title, id, level)
            del pinDB

        # Now reload the screen to reflect the change
        xbmc.executebuiltin("Container.Refresh")

    # Sets the security details on all the Movies in a given Movie Set
    def _setSecurityOnMoviesInMovieSets(self, setid, level):
        log("Setting security for movies in movie set %d" % setid)
        # Get all the movies in the movie set
        json_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovieSetDetails", "params": { "setid": %d, "properties": ["title"] }, "id": 1}' % setid)
        json_query = unicode(json_query, 'utf-8', errors='ignore')
        json_response = simplejson.loads(json_query)
        log(json_response)
        if ("result" in json_response) and ('setdetails' in json_response['result']):
            if 'movies' in json_response['result']['setdetails']:
                for item in json_response['result']['setdetails']['movies']:
                    # Now set the security on the movies in the set
                    self.setSecurity(MenuNavigator.MOVIES, item['label'], item['movieid'], level)
        return


################################
# Main of the PinSentry Plugin
################################
if __name__ == '__main__':
    # Get all the arguments
    base_url = sys.argv[0]
    addon_handle = int(sys.argv[1])
    args = urlparse.parse_qs(sys.argv[2][1:])

    # Record what the plugin deals with, files in our case
    xbmcplugin.setContent(addon_handle, 'files')

    # Get the current mode from the arguments, if none set, then use None
    mode = args.get('mode', None)

    log("PinSentryPlugin: Called with addon_handle = %d" % addon_handle)

    # If None, then at the root
    if mode is None:
        log("PinSentryPlugin: Mode is NONE - showing root menu")
        menuNav = MenuNavigator(base_url, addon_handle)
        menuNav.showRootMenu()
        del menuNav

    elif mode[0] == 'folder':
        log("PinSentryPlugin: Mode is FOLDER")

        # Get the actual folder that was navigated to
        foldername = args.get('foldername', None)

        if (foldername is not None) and (len(foldername) > 0):
            menuNav = MenuNavigator(base_url, addon_handle)
            menuNav.showFolder(foldername[0])
            del menuNav

    elif mode[0] == 'setsecurity':
        log("PinSentryPlugin: Mode is SET SECURITY")

        # Get the actual details of the selection
        type = args.get('type', None)
        title = args.get('title', None)
        level = args.get('level', None)
        id = args.get('id', None)

        if (type is not None) and (len(type) > 0):
            log("PinSentryPlugin: Type to set security for %s" % type[0])
            secTitle = ""
            if (title is not None) and (len(title) > 0):
                secTitle = title[0]
            secLevel = 0
            if (level is not None) and (len(level) > 0):
                secLevel = int(level[0])
            dbid = 0
            if (id is not None) and (len(id) > 0):
                dbid = id[0]

            menuNav = MenuNavigator(base_url, addon_handle)
            menuNav.setSecurity(type[0], secTitle, dbid, secLevel)
            del menuNav
