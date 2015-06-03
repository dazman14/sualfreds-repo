# -*- coding: utf-8 -*-
import sys
import os
import xbmc
import xbmcaddon
import xbmcgui


__addon__ = xbmcaddon.Addon(id='script.pinsentry')
__icon__ = __addon__.getAddonInfo('icon')
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources').encode("utf-8")).decode("utf-8")
__lib__ = xbmc.translatePath(os.path.join(__resource__, 'lib').encode("utf-8")).decode("utf-8")

sys.path.append(__lib__)

# Import the common settings
from settings import log
from settings import Settings

from numberpad import NumberPad
from database import PinSentryDB
from background import Background


# Feature Options:
# Different Pins for different priorities (one a subset of the next)
# Restrictions based on certificate/classification (G, PG, PG-13, R, NC-17)
# Option to have different passwords without the numbers (Remote with no numbers?)


# Class to handle core Pin Sentry behaviour
class PinSentry():
    pinLevelCached = 0

    @staticmethod
    def isPinSentryEnabled():
        # Check if the Pin is set, as no point prompting if it is not
        if (not Settings.isPinSet()) or (not Settings.isPinActive()):
            return False
        return True

    @staticmethod
    def clearPinCached():
        log("PinSentry: Clearing Cached pin that was at level %d" % PinSentry.pinLevelCached)
        PinSentry.pinLevelCached = 0

    @staticmethod
    def setCachedPinLevel(level):
        # Check if the pin cache is enabled, if it is not then the cache level will
        # always remain at 0 (i.e. always need to enter the pin)
        if Settings.isPinCachingEnabled():
            if PinSentry.pinLevelCached < level:
                log("PinSentry: Updating cached pin level to %d" % level)
                PinSentry.pinLevelCached = level

    @staticmethod
    def getCachedPinLevel():
        return PinSentry.pinLevelCached

    @staticmethod
    def promptUserForPin():
        userHasAccess = True

        # Set the background
        background = Background.createBackground()
        if background is not None:
            background.show()

        # Prompt the user to enter the pin
        numberpad = NumberPad.createNumberPad()
        numberpad.doModal()

        # Remove the background if we had one
        if background is not None:
            background.close()
            del background

        # Get the code that the user entered
        enteredPin = numberpad.getPin()
        del numberpad

        # Check to see if the pin entered is correct
        if Settings.isPinCorrect(enteredPin):
            log("PinSentry: Pin entered Correctly")
            userHasAccess = True
            # Check if we are allowed to cache the pin level
            PinSentry.setCachedPinLevel(1)
        else:
            log("PinSentry: Incorrect Pin Value Entered")
            userHasAccess = False

        return userHasAccess

    @staticmethod
    def displayInvalidPinMessage():
        # Invalid Key Notification: Dialog, Popup Notification, None
        notifType = Settings.getInvalidPinNotificationType()
        if notifType == Settings.INVALID_PIN_NOTIFICATION_POPUP:
            cmd = 'XBMC.Notification("{0}", "{1}", 5, "{2}")'.format(__addon__.getLocalizedString(32001).encode('utf-8'), __addon__.getLocalizedString(32104).encode('utf-8'), __icon__)
            xbmc.executebuiltin(cmd)
        elif notifType == Settings.INVALID_PIN_NOTIFICATION_DIALOG:
            xbmcgui.Dialog().ok(__addon__.getLocalizedString(32001).encode('utf-8'), __addon__.getLocalizedString(32104).encode('utf-8'))
        # Remaining option is to not show any error


# Class to detect shen something in the system has changed
class PinSentryMonitor(xbmc.Monitor):
    def onSettingsChanged(self):
        log("PinSentryMonitor: Notification of settings change received")
        Settings.reloadSettings()

    def onScreensaverActivated(self):
        log("PinSentryMonitor: Screensaver started, clearing cached pin")
        PinSentry.clearPinCached()


# Our Monitor class so we can find out when a video file has been selected to play
class PinSentryPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)

    def onPlayBackStarted(self):
        if not Settings.isActiveVideoPlaying():
            return

        log("PinSentryPlayer: Notification that something started playing")

        # Only interested if it is not playing music
        if self.isPlayingAudio():
            return

        # Ignore screen saver videos
        if xbmcgui.Window(10000).getProperty("VideoScreensaverRunning"):
            log("PinSentryPlayer: Detected VideoScreensaver playing")
            return

        # Check if the Pin is set, as no point prompting if it is not
        if not PinSentry.isPinSentryEnabled():
            return

        # Get the information for what is currently playing
        # http://kodi.wiki/view/InfoLabels#Video_player
        tvshowtitle = xbmc.getInfoLabel("VideoPlayer.TVShowTitle")

        # If the TvShow Title is not set, then Check the ListItem as well
        if tvshowtitle in [None, ""]:
            tvshowtitle = xbmc.getInfoLabel("ListItem.TVShowTitle")

#         cert = xbmc.getInfoLabel("VideoPlayer.mpaa")
#         listmpaa = xbmc.getInfoLabel("ListItem.Mpaa")

#         log("*** ROB ***: VideoPlayer.mpaa: %s" % str(cert))
#         log("*** ROB ***: ListItem.Mpaa: %s" % str(listmpaa))

        securityLevel = 0
        # If it is a TvShow, then check to see if it is enabled for this one
        if tvshowtitle not in [None, ""]:
            log("PinSentryPlayer: TVShowTitle: %s" % tvshowtitle)
            pinDB = PinSentryDB()
            securityLevel = pinDB.getTvShowSecurityLevel(tvshowtitle)
            del pinDB
            if securityLevel < 1:
                log("PinSentryPlayer: No security enabled for %s" % tvshowtitle)
                return
        else:
            # Not a TvShow, so check for the Movie Title
            title = xbmc.getInfoLabel("VideoPlayer.Title")

            # If no title is found, check the ListItem rather then the Player
            if title in [None, ""]:
                title = xbmc.getInfoLabel("ListItem.Title")

            if title not in [None, ""]:
                log("PinSentryPlayer: Title: %s" % title)
                pinDB = PinSentryDB()
                securityLevel = pinDB.getMovieSecurityLevel(title)
                del pinDB
                if securityLevel < 1:
                    log("PinSentryPlayer: No security enabled for %s" % title)
                    return
            else:
                # Not a TvShow or Movie - so allow the user to continue
                # without entering a pin code
                log("PinSentryPlayer: No security enabled, no title available")
                return

        # Check if we have already cached the pin number and at which level
        if PinSentry.getCachedPinLevel() >= securityLevel:
            log("PinSentryPlayer: Already cached pin at level %d, allowing access" % PinSentry.getCachedPinLevel())
            return

        # Before we start prompting the user for the pin, check to see if we
        # have already been called and are prompting in another thread
        if xbmcgui.Window(10000).getProperty("PinSentryPrompting"):
            log("PinSentryPlayer: Already prompting for security code")
            return

        # Set the flag so other threads know we are processing this play request
        xbmcgui.Window(10000).setProperty("PinSentryPrompting", "true")

        # Pause the video so that we can prompt for the Pin to be entered
        # On some systems we could get notified that we have started playing a video
        # before it has actually been started, so keep trying to pause until we get
        # one that works
        while not xbmc.getCondVisibility("Player.Paused"):
            self.pause()

        log("PinSentryPlayer: Pausing video to check if OK to play")

        # Prompt the user for the pin, returns True if they knew it
        if PinSentry.promptUserForPin():
            log("PinSentryPlayer: Resuming video")
            # Pausing again will start the video playing again
            self.pause()
        else:
            log("PinSentryPlayer: Stopping video")
            self.stop()
            PinSentry.displayInvalidPinMessage()

        xbmcgui.Window(10000).clearProperty("PinSentryPrompting")


# Class to handle prompting for a pin when navigating the menu's
class NavigationRestrictions():
    def __init__(self):
        self.lastTvShowChecked = ""
        self.lastMovieSetChecked = ""
        self.lastPluginChecked = ""
        self.canChangeSettings = False

    # Checks if the user has navigated to a TvShow that needs a pin
    def checkTvShows(self):
        # For TV Shows Users could either be in Seasons or Episodes
        if (not xbmc.getCondVisibility("Container.Content(seasons)")) and (not xbmc.getCondVisibility("Container.Content(episodes)")):
            # Not in a TV Show view, so nothing to do, Clear any previously
            # recorded TvShow
            if 'videodb://' in xbmc.getInfoLabel("Container.FolderPath"):
                self.lastTvShowChecked = ""
            return

        # Get the name of the TvShow
        tvshow = xbmc.getInfoLabel("ListItem.TVShowTitle")

        if tvshow in [None, "", self.lastTvShowChecked]:
            # No TvShow currently set - this can take a little time
            # So do nothing this time and wait until the next time
            # or this is a TvShow that has already been checked
            return

        # If we reach here we have a TvShow that we need to check
        log("NavigationRestrictions: Checking access to view TvShow: %s" % tvshow)
        self.lastTvShowChecked = tvshow

        # Check to see if the user should have access to this show
        pinDB = PinSentryDB()
        securityLevel = pinDB.getTvShowSecurityLevel(tvshow)
        if securityLevel < 1:
            log("NavigationRestrictions: No security enabled for %s" % tvshow)
            return
        del pinDB

        # Check if we have already cached the pin number and at which level
        if PinSentry.getCachedPinLevel() >= securityLevel:
            log("NavigationRestrictions: Already cached pin at level %d, allowing access" % PinSentry.getCachedPinLevel())
            return

        # Prompt the user for the pin, returns True if they knew it
        if PinSentry.promptUserForPin():
            log("NavigationRestrictions: Allowed access to %s" % tvshow)
        else:
            log("NavigationRestrictions: Not allowed access to %s which has security level %d" % (tvshow, securityLevel))
            # Move back to the TvShow Section as they are not allowed where they are at the moment
            # The following does seem strange, but you can't just call the TV Show list on it's own
            # In order to get there I had to first go via the home screen
            xbmc.executebuiltin("ActivateWindow(home)", True)
            xbmc.executebuiltin("ActivateWindow(Videos,videodb://tvshows/titles/)", True)
            # Clear the previous TV Show as we will want to prompt for the pin again if the
            # user navigates there again
            self.lastTvShowChecked = ""
            PinSentry.displayInvalidPinMessage()

    # Checks if the user has navigated to a Movie Set that needs a pin
    def checkMovieSets(self):
        # Check if the user has navigated into a movie set
        navPath = xbmc.getInfoLabel("Container.FolderPath")

        if 'videodb://movies/sets/' not in navPath:
            # Not in a Movie Set view, so nothing to do
            if 'videodb://' in navPath:
                self.lastMovieSetChecked = ""
            return

        # Get the name of the movie set
        moveSetName = xbmc.getInfoLabel("Container.FolderName")

        if moveSetName in [None, "", self.lastMovieSetChecked]:
            # No Movie Set currently set - this can take a little time
            # So do nothing this time and wait until the next time
            # or this is a Movie set that has already been checked
            return

        # If we reach here we have a Movie Set that we need to check
        log("NavigationRestrictions: Checking access to view Movie Set: %s" % moveSetName)
        self.lastMovieSetChecked = moveSetName

        # Check to see if the user should have access to this set
        pinDB = PinSentryDB()
        securityLevel = pinDB.getMovieSetSecurityLevel(moveSetName)
        if securityLevel < 1:
            log("NavigationRestrictions: No security enabled for movie set %s" % moveSetName)
            return
        del pinDB

        # Check if we have already cached the pin number and at which level
        if PinSentry.getCachedPinLevel() >= securityLevel:
            log("NavigationRestrictions: Already cached pin at level %d, allowing access" % PinSentry.getCachedPinLevel())
            return

        # Prompt the user for the pin, returns True if they knew it
        if PinSentry.promptUserForPin():
            log("NavigationRestrictions: Allowed access to movie set %s" % moveSetName)
        else:
            log("NavigationRestrictions: Not allowed access to movie set %s which has security level %d" % (moveSetName, securityLevel))
            # Move back to the Movie Section as they are not allowed where they are at the moment
            xbmc.executebuiltin("ActivateWindow(Videos,videodb://movies/titles/)", True)
            # Clear the previous Movie Set as we will want to prompt for the pin again if the
            # user navigates there again
            self.lastMovieSetChecked = ""
            PinSentry.displayInvalidPinMessage()

    # Check if a user has navigated to a Plugin that requires a Pin
    def checkPlugins(self):
        navPath = xbmc.getInfoLabel("Container.FolderPath")
        if 'plugin://' not in navPath:
            # No Plugin currently set or this is a Movie set that has already been checked
            return

        # Check if we are in a plugin location
        pluginName = xbmc.getInfoLabel("Container.FolderName")

        if pluginName in [None, "", self.lastPluginChecked]:
            # No Plugin currently set or this is a Movie set that has already been checked
            return

        # If we reach here we have aPlugin that we need to check
        log("NavigationRestrictions: Checking access to view Plugin: %s" % pluginName)
        self.lastPluginChecked = pluginName

        # Check for the case where the user does not want to check plugins
        # but the Pin Sentry plugin is selected, we always need to check this
        # as it is how permissions are set
        if (not Settings.isActivePlugins()) and ('PinSentry' not in pluginName):
            return

        securityLevel = 0
        # Check to see if the user should have access to this plugin
        pinDB = PinSentryDB()
        securityLevel = pinDB.getPluginSecurityLevel(pluginName)
        if securityLevel < 1:
            # Check for the special case that we are accessing ourself
            # in which case we have a minimum security level
            if 'PinSentry' in pluginName:
                securityLevel = 1
            else:
                log("NavigationRestrictions: No security enabled for plugin %s" % pluginName)
                return
        del pinDB

        # Check if we have already cached the pin number and at which level
        if PinSentry.getCachedPinLevel() >= securityLevel:
            log("NavigationRestrictions: Already cached pin at level %d, allowing access" % PinSentry.getCachedPinLevel())
            return

        # Prompt the user for the pin, returns True if they knew it
        if PinSentry.promptUserForPin():
            log("NavigationRestrictions: Allowed access to plugin %s" % pluginName)
        else:
            log("NavigationRestrictions: Not allowed access to plugin %s which has security level %d" % (pluginName, securityLevel))
            # Move back to the Video plugin Screen as they are not allowed where they are at the moment
            xbmc.executebuiltin("ActivateWindow(Video,addons://sources/video/)", True)
            # Clear the previous plugin as we will want to prompt for the pin again if the
            # user navigates there again
            self.lastPluginChecked = ""
            PinSentry.displayInvalidPinMessage()

    # Checks to see if the PinSentry addons screen has been opened
    def checkSettings(self):
        # Check if we are in the Addon Information page (which can be used to disable the addon)
        # or the actual setting page
        addonSettings = xbmc.getCondVisibility("Window.IsActive(10140)")
        addonInformation = xbmc.getCondVisibility("Window.IsActive(10146)")

        if not addonSettings and not addonInformation:
            self.canChangeSettings = False
            return

        # If we have already allowed the user to change settings, no need to check again
        if self.canChangeSettings:
            return

        # Check if the addon is the PinSentry addon
        addonId = xbmc.getInfoLabel("ListItem.Property(Addon.ID)")
        if 'script.pinsentry' not in addonId:
            return

        # Need to make sure this user has access to change the settings
        pinDB = PinSentryDB()
        securityLevel = pinDB.getPluginSecurityLevel('PinSentry')
        del pinDB

        if securityLevel < 1:
            securityLevel = 1

        # Check if we have already cached the pin number and at which level
        if PinSentry.getCachedPinLevel() >= securityLevel:
            log("NavigationRestrictions: Already cached pin at level %d, allowing access" % PinSentry.getCachedPinLevel())
            return

        # Before we prompt the user we need to close the dialog, otherwise the pin
        # dialog will appear behind it
        xbmc.executebuiltin("Dialog.Close(all, true)", True)

        # Prompt the user for the pin, returns True if they knew it
        if PinSentry.promptUserForPin():
            log("NavigationRestrictions: Allowed access to settings")
            self.canChangeSettings = True
            # Open the dialogs that should be shown
            if addonInformation:
                # Open the addon Information dialog
                xbmc.executebuiltin("ActivateWindow(10146)", True)
            elif addonSettings:
                # Open the addon settings dialog
                xbmc.executebuiltin("Addon.OpenSettings(script.pinsentry)", True)
        else:
            log("NavigationRestrictions: Not allowed access to settings which has security level %d" % securityLevel)
            self.canChangeSettings = False
            PinSentry.displayInvalidPinMessage()


##################################
# Main of the PinSentry Service
##################################
if __name__ == '__main__':
    log("Starting Pin Sentry Service")

    playerMonitor = PinSentryPlayer()
    systemMonitor = PinSentryMonitor()
    navRestrictions = NavigationRestrictions()

    while (not xbmc.abortRequested):
        xbmc.sleep(100)
        # Check if the Pin is set, as no point prompting if it is not
        if PinSentry.isPinSentryEnabled():
            # Check to see if we need to restrict navigation access
            if Settings.isActiveNavigation():
                navRestrictions.checkTvShows()
                navRestrictions.checkMovieSets()
            # Always call the plugin check as we have to check if the user is setting
            # permissions using the PinSentry plugin
            navRestrictions.checkPlugins()
            navRestrictions.checkSettings()

    log("Stopping Pin Sentry Service")
    del navRestrictions
    del playerMonitor
    del systemMonitor
