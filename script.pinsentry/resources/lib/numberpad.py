# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui


__addon__ = xbmcaddon.Addon(id='script.pinsentry')
__cwd__ = __addon__.getAddonInfo('path').decode("utf-8")

# Import the common settings
from settings import log
from settings import Settings


# Class that uses the default Number keyboard and overwrites it's behaviour
# so that it can except hidden pin numbers
class NumberPad(xbmcgui.WindowXMLDialog):
    BUTTON_BACKSPACE = 23
    BUTTON_DONE = 21
    BUTTON_PREVIOUS = 20
    BUTTON_NEXT = 22

    def __init__(self, strXMLname, strFallbackPath, titleLangId=32103):
        self.code = ""
        self.stars = ""
        self.titleLangId = titleLangId

    @staticmethod
    def createNumberPad(titleLangId=32103):
        return NumberPad("DialogNumeric.xml", __cwd__, titleLangId=titleLangId)

    # Returns the value of the pin code
    def getPin(self):
        # Only return the pin value if it meets the required length
        if Settings.getPinLength() < len(self.code):
            return ""
        return self.code

    def onInit(self):
        # Disable the buttons we are not interested in
        try:
            prevButton = self.getControl(NumberPad.BUTTON_PREVIOUS)
            prevButton.setEnabled(False)
            nextButton = self.getControl(NumberPad.BUTTON_NEXT)
            nextButton.setEnabled(False)
        except:
            # Having the buttons enabled is not a big issue, we can just
            # continue as they will just do nothing
            log("NumberPad: Failed to disable next and previous buttons")

        # Replace Done and Backspace buttons labels
        try:
            backspaceButton = self.getControl(NumberPad.BUTTON_BACKSPACE)
            backspaceButton.setLabel(__addon__.getLocalizedString(32101).encode('utf-8'))
        except:
            log("NumberPad: Failed to update text for backspace button")

        try:
            doneButton = self.getControl(NumberPad.BUTTON_DONE)
            doneButton.setLabel(__addon__.getLocalizedString(32102).encode('utf-8'))
        except:
            log("NumberPad: Failed to update text for done button")

        # Make sure all the numbers are set correctly, some times the mapping
        # to the string class do not work
        for i in range(0, 10):
            try:
                numButton = self.getControl(i + 10)
                numButton.setLabel(str(i))
            except:
                log("NumberPad: Failed to update text on numeric button %d" % i)

        # Set the title of the dialog
        try:
            self.getControl(1).setLabel(__addon__.getLocalizedString(self.titleLangId).encode('utf-8'))
        except:
            log("NumberPad: Failed to set title")

        xbmcgui.WindowXMLDialog.onInit(self)

    # Detect things like remote control of keyboard button presses
    def onAction(self, action):
        id = action.getId()
        # actioncodes from https://github.com/xbmc/xbmc/blob/master/xbmc/input/Key.h
        ACTION_PREVIOUS_MENU = 10
        ACTION_NAV_BACK = 92
        ACTION_BACKSPACE = 110

        if (action == ACTION_PREVIOUS_MENU) or (action == ACTION_NAV_BACK):
            log("NumberPad: Close Action received: %s" % str(id))
            self.close()
        elif action == ACTION_BACKSPACE:
            # Backspace has been pressed
            self._removeLastCharacter()
        elif (id > 57) and (id < 68):
            # NumericValue found, convert it
            # Numbers as follows
            # 58 = 0, 59 = 1 ...
            # So take 58 off and you get the number
            numVal = id - 58
            self._numberEntered(numVal)
        elif (id > 139) and (id < 150):
            # Remote control can send different keys
            # NumericValue found, convert it
            # Numbers as follows
            # 140 = 0, 141 = 1 ...
            # So take 58 off and you get the number
            numVal = id - 140
            self._numberEntered(numVal)
        else:
            log("NumberPad: Unknown key pressed %s" % str(id))

    # Record that a numeric value has been entered by the user
    def _numberEntered(self, numValue):
        log("NumberPad: Entered number %d" % numValue)
        self.code += str(numValue)
        # Sets the correct number of stars on the display
        self.stars = self.stars + "*"
        self.getControl(4).setLabel(self.stars)

        # Check if we have 4 numbers, if we do, then we can close the dialog
        # automatically
        if len(self.code) == Settings.getPinLength():
            self.close()

    # Removes the last character from the code
    def _removeLastCharacter(self):
        log("NumberPad: Delete last character request")
        if len(self.code) > 0:
            self.code = self.code[:-1]
            self.stars = self.stars[:-1]
            self.getControl(4).setLabel(self.stars)

    # Detect when the user has clicked on the screen
    def onClick(self, controlID):
        # Convert all the numbers that are supported
        if (controlID > 9) and (controlID < 20):
            self._numberEntered(controlID - 10)
        elif controlID == NumberPad.BUTTON_DONE:
            # Done button has been pressed
            self.close()
        elif controlID == NumberPad.BUTTON_BACKSPACE:
            # Backspace has been pressed
            self._removeLastCharacter()
