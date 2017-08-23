from defs import *


class GUI(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.listitem = kwargs["listitem"]

    def onInit(self):
        self._show_info()

    def _show_info(self):
        self.getControl(100).addItem(self.listitem)

    def _close_dialog(self):
        self.close()
		# workaround to trigger the onfocus animation of the listitem in the main window
        self.setFocus(self.getControl(100))

    def onFocus(self, controlId):
        pass

    def onAction(self, action):
        if (action.getId() in ACTION_CANCEL_DIALOG) or (action.getId() in ACTION_SHOW_INFO):
            self._close_dialog()
