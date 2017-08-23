import sys
import re
import xbmc
import xbmcgui

ADDON = sys.modules['__main__'].ADDON
ADDONID = sys.modules['__main__'].ADDONID
ADDONVERSION = sys.modules['__main__'].ADDONVERSION
LANGUAGE = sys.modules['__main__'].LANGUAGE
CWD = sys.modules['__main__'].CWD

ACTION_CANCEL_DIALOG = (9, 10, 92, 216, 247, 257, 275, 61467, 61448,)
ACTION_CONTEXT_MENU = (117,)
ACTION_SHOW_INFO = (11,)

ALL = 100
CONTENT = 101
MOVIES = 110
TVSHOWS = 120
SEASONS = 130
EPISODES = 140
MUSICVIDEOS = 150
ARTISTS = 160
ALBUMS = 170
SONGS = 180
EPG = 190
ACTORS = 200
DIRECTORS = 210
SEARCHING = 990
CATEGORY = 991
NEWSEARCH = 998
NORESULTS = 999

MOVIELABELS = ["genre", "country", "year", "top250", "setid", "rating", "userrating", "playcount", "director", "mpaa", "plot", "plotoutline", "title", "originaltitle", "sorttitle",
               "runtime", "studio", "tagline", "writer", "premiered", "set", "imdbnumber", "lastplayed", "votes", "trailer", "dateadded", "streamdetails", "art", "file", "resume"]

TVSHOWLABELS = ["genre", "year", "episode", "season", "rating", "userrating", "playcount", "mpaa", "plot", "title", "originaltitle", "sorttitle", "runtime", "studio", "premiered",
                "imdbnumber", "lastplayed", "votes", "dateadded", "art", "watchedepisodes", "file"]

SEASONLABELS = ["episode", "season", "showtitle", "tvshowid", "userrating", "watchedepisodes", "playcount", "art"]

EPISODELABELS = ["episode", "season", "rating", "userrating", "playcount", "director", "plot", "title", "originaltitle", "runtime", "writer", "showtitle", "firstaired", "lastplayed",
                 "votes", "dateadded", "streamdetails", "art", "file", "resume"]

MUSICVIDEOLABELS = ["genre", "year", "rating", "userrating", "playcount", "director", "plot", "title", "runtime", "studio", "premiered", "lastplayed", "album", "artist", "dateadded",
                    "streamdetails", "art", "file", "resume"]

ARTISTLABELS = ["genre", "description", "formed", "disbanded", "born", "yearsactive", "died", "mood", "style", "instrument", "thumbnail", "fanart"]

ALBUMLABELS = ["title", "description", "albumlabel", "artist", "genre", "year", "thumbnail", "fanart", "theme", "type", "mood", "style", "rating", "userrating", "artistid"]

SONGLABELS = ["title", "artist", "album", "genre", "duration", "year", "file", "thumbnail", "fanart", "comment", "rating", "userrating", "track", "playcount", "artistid", "albumid"]

CATEGORIES = {
              'movies':{
                        'order':1,
                        'enabled':False,
                        'type':'movies',
                        'method':'VideoLibrary.GetMovies',
                        'properties':MOVIELABELS,
                        'sort':'title',
                        'rule':'"filter":{"field":"title", "operator":"contains", "value":"%s"}',
                        'streamdetails':True,
                        'label':342,
                        'icon':'DefaultVideo.png',
                        'media':'video',
                        'control':MOVIES
                       },
              'tvshows':{
                         'order':2,
                         'enabled':False,
                         'type':'tvshows',
                         'method':'VideoLibrary.GetTVShows',
                         'properties':TVSHOWLABELS,
                         'sort':'label',
                         'rule':'"filter":{"field":"title", "operator":"contains", "value":"%s"}',
                         'streamdetails':False,
                         'label':20343,
                         'icon':'DefaultVideo.png',
                         'media':'video',
                         'control':TVSHOWS
                        },
              'episodes':{
                          'order':3,
                          'enabled':False,
                          'type':'episodes',
                          'method':'VideoLibrary.GetEpisodes',
                          'properties':EPISODELABELS,
                          'sort':'title',
                          'rule':'"filter":{"field":"title", "operator":"contains", "value":"%s"}',
                          'streamdetails':True,
                          'label':20360,
                          'icon':'DefaultVideo.png',
                          'media':'video',
                          'control':EPISODES
                         },
              'musicvideos':{
                             'order':4,
                             'enabled':False,
                             'type':'musicvideos',
                             'method':'VideoLibrary.GetMusicVideos',
                             'properties':MUSICVIDEOLABELS,
                             'sort':'label',
                             'rule':'"filter":{"field":"title", "operator":"contains", "value":"%s"}',
                             'streamdetails':True,
                             'label':20389,
                             'icon':'DefaultVideo.png',
                             'media':'video',
                             'control':MUSICVIDEOS
                            },
              'artists':{
                         'order':5,
                         'enabled':False,
                         'type':'artists',
                         'method':'AudioLibrary.GetArtists',
                         'properties':ARTISTLABELS,
                         'sort':'label',
                         'rule':'"filter":{"field": "artist", "operator": "contains", "value": "%s"}',
                         'streamdetails':False,
                         'label':133,
                         'icon':'DefaultArtist.png',
                         'media':'music',
                         'control':ARTISTS
                        },
              'albums':{
                        'order':6,
                        'enabled':False,
                        'type':'albums',
                        'method':'AudioLibrary.GetAlbums',
                        'properties':ALBUMLABELS,
                        'sort':'label',
                        'rule':'"filter":{"field": "album", "operator": "contains", "value": "%s"}',
                        'streamdetails':False,
                        'label':132,
                        'icon':'DefaultAlbumCover.png',
                        'media':'music',
                        'control':ALBUMS
                       },
              'songs':{
                       'order':7,
                       'enabled':False,
                       'type':'songs',
                       'method':'AudioLibrary.GetSongs',
                       'properties':SONGLABELS,
                       'sort':'title',
                       'rule':'"filter":{"field": "title", "operator": "contains", "value": "%s"}',
                       'streamdetails':False,
                       'label':134,
                       'icon':'DefaultAudio.png',
                       'media':'music',
                       'control':SONGS
                      },
              'epg':{
                     'order':9,
                     'enabled':False,
                     'type':'epg'
                    },  
              'actors':{
                        'order':10,
                        'enabled':False,
                        'type':'movies',
                        'method':'VideoLibrary.GetMovies',
                        'properties':MOVIELABELS,
                        'sort':'title',
                        'rule':'"filter":{"field":"actor", "operator":"contains", "value":"%s"}',
                        'streamdetails':True,
                        'label':344,
                        'icon':'DefaultVideo.png',
                        'media':'video',
                        'control':ACTORS
                       },
              'directors':{
                           'order':11,
                           'enabled':False,
                           'type':'movies',
                           'method':'VideoLibrary.GetMovies',
                           'properties':MOVIELABELS,
                           'sort':'title',
                           'rule':'"filter":{"field":"director", "operator":"contains", "value":"%s"}',
                           'streamdetails':True,
                           'label':20348,
                           'icon':'DefaultVideo.png',
                           'media':'video',
                           'control':DIRECTORS
                          },
              'tvshowseasons':{
                               'order':11,
                               'enabled':False,
                               'type':'seasons',
                               'method':'VideoLibrary.GetSeasons',
                               'properties':SEASONLABELS,
                               'sort':'label',
                               'rule':'"tvshowid":%s',
                               'streamdetails':False,
                               'label':20373,
                               'icon':'DefaultVideo.png',
                               'media':'video',
                               'control':SEASONS
                              },
              'tvshowepisodes':{
                                'order':12,
                                'enabled':False,
                                'type':'episodes',
                                'method':'VideoLibrary.GetEpisodes',
                                'properties':EPISODELABELS,
                                'sort':'title',
                                'rule':'"tvshowid":%s',
                                'streamdetails':True,
                                'label':20360,
                                'icon':'DefaultVideo.png',
                                'media':'video',
                                'control':EPISODES
                               },
              'artistalbums':{
                              'order':13,
                              'enabled':False,
                              'type':'albums',
                              'method':'AudioLibrary.GetAlbums',
                              'properties':ALBUMLABELS,
                              'sort':'label',
                              'rule':'"filter":{"artistid":%s}',
                              'streamdetails':False,
                              'label':132,
                              'icon':'DefaultAlbumCover.png',
                              'media':'music',
                              'control':ALBUMS
                             },
              'artistsongs':{
                             'order':14,
                             'enabled':False,
                             'type':'songs',
                             'method':'AudioLibrary.GetSongs',
                             'properties':SONGLABELS,
                             'sort':'title',
                             'rule':'"filter":{"artistid":%s}',
                             'streamdetails':False,
                             'label':134,
                             'icon':'DefaultAudio.png',
                             'media':'music',
                             'control':SONGS
                            },
              'songalbum':{
                           'order':15,
                           'enabled':False,
                           'type':'albums',
                           'method':'AudioLibrary.GetAlbums',
                           'properties':ALBUMLABELS,
                           'sort':'label',
                           'rule':'"filter":{"artistid":%s}',
                           'streamdetails':False,
                           'label':132,
                           'icon':'DefaultAlbumCover.png',
                           'media':'music',
                           'control':ALBUMS
                          }
             }
