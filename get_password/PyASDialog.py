# PyASDialog
# A simple Python wrapper for an AppleScript dialog.
# Franz Heidl 2013
# http://github.com/franzheidl/py-asalert-asdialog
# MIT license.


import os
import subprocess


class ASDialog:

    def __init__(self, **kwargs):

        iconCodes = {"0", "1", "2"}
        iconTypes = {"stop", "note", "caution"}

        self.dialog = {}

        if "text" in kwargs.keys():
            self.text = kwargs["text"]
        else:
            self.text = ' '
        self.dialog["text"] = self.text
        self.dialogString = 'set theResult to display dialog ' + '\"' + self.text + '\"'

        if "application" in kwargs.keys():
            self.application = kwargs["application"]
        else:
            self.application = "System Events"
        self.dialog["application"] = self.application
        self.applicationString = 'tell application \"' + self.application + '\"'


        if "defaultAnswer" in kwargs.keys():
            self.defaultAnswer = kwargs["defaultAnswer"]
            self.dialog["defaultAnswer"] = self.defaultAnswer
            self.dialogString = self.dialogString + ' default answer ' + '\"' + self.defaultAnswer + '\"'


        if "hiddenAnswer" in kwargs.keys():
            hA = kwargs["hiddenAnswer"]
            if hA == True or hA == "True":
                self.hiddenAnswer = kwargs["hiddenAnswer"]
                self.dialog["hiddenAnswer"] = self.hiddenAnswer
                self.dialogString = self.dialogString + ' with hidden answer'


        if "buttons" in kwargs.keys():
            self.buttons = (kwargs["buttons"]).split(", ")
            self.dialog["buttons"] = self.buttons
            self.buttonString = ', '.join([('\"' + button + '\"') for button in self.buttons if button])
            self.dialogString = self.dialogString + ' buttons {' + self.buttonString + '}'


        if "defaultButton" in kwargs.keys():
            dB = kwargs["defaultButton"]
            if isinstance(dB, str) or isinstance(dB, int):
                try:
                    if int(dB) <= len(self.buttons):
                        self.defaultButton = dB
                        self.dialog["defaultButton"] = self.defaultButton
                        self.dialogString = self.dialogString + ' default button ' + str(self.defaultButton)
                except:
                    if str(dB) in self.buttons:
                        self.defaultButton = dB
                        self.dialog["defaultButton"] = self.defaultButton
                        self.dialogString = self.dialogString + ' default button ' + '\"' + str(self.defaultButton) + '\"'


        if "cancelButton" in kwargs.keys():
            cB = kwargs["cancelButton"]
            if isinstance(cB, str) or isinstance(cB, int):
                try:
                    if int(cB) <= len(self.buttons):
                        self.cancelButton = cB
                        self.dialog["cancelButton"] = self.cancelButton
                        self.dialogString = self.dialogString + ' cancel button ' + str(self.cancelButton)
                except:
                    if str(cB) in self.buttons:
                        self.cancelButton = cB
                        self.dialog["cancelButton"] = self.cancelButton
                        self.dialogString = self.dialogString + ' cancel button ' + '\"' + str(self.cancelButton) + '\"'


        if "title" in kwargs.keys():
            self.title = kwargs["title"]
            self.dialog["title"] = self.title
            self.dialogString = self.dialogString + ' with title ' + '\"' + self.title + '\"'


        if "icon" in kwargs.keys():
            i = kwargs["icon"]
            if str(i) in iconCodes or str(i) in iconTypes:
                self.icon = i
                self.dialog["icon"] = self.icon
                self.dialogString = self.dialogString + ' with icon ' + self.icon
            else:
                try:
                    i= str(os.path.abspath(i))
                    if os.path.exists(i):
                        hI = self._hfsPath(i)
                        if hI != "false":
                            self.icon = hI
                            self.dialog["icon"] = self.icon
                            self.dialogString = self.dialogString + ' with icon file \"' + self.icon + '\"'
                except:
                    pass


        if "givingUpAfter" in kwargs.keys():
            try:
                self.givingUpAfter = int(kwargs["givingUpAfter"])
                self.dialog["givingUpAfter"] = self.givingUpAfter
                self.dialogString = self.dialogString + ' giving up after ' + str(self.givingUpAfter)
            except:
                pass

        self._result = self.displayDialog(self.applicationString, self.dialogString)
        self.dialog["result"] = self._result

    def displayDialog(self, theApplication, theDialog):
        self.output = subprocess.check_output(['osascript',
            '-e', theApplication,
            '-e', 'activate',
            '-e', 'try',
            '-e', theDialog,
            '-e', 'on error number -128',
            '-e', 'set theResult to \"canceled: True\"',
            '-e', 'end try',
            '-e', 'return theResult',
            '-e', 'end tell'])
        return self._dictify(self.output)


    def result(self):
        if self._result:
            return self._result
        else:
            return False


    def buttonReturned(self):
        if self.result():
            try:
                return (self.result())["button returned"]
            except KeyError:
                return False
        else:
            return False


    def canceled(self):
        if self.result():
            try:
                return (self.result())["canceled"]
            except KeyError:
                return False
        else:
            return False


    def textReturned(self):
        if self.result():
            try:
                return (self.result())["text returned"]
            except KeyError:
                return False
        else:
            return False


    def _dictify(self, result):
        _rString = str(result).strip()
        _rPairs = _rString.split(', ')
        _rDict = {}
        for _rPair in _rPairs:
            _rPair = _rPair.split(':')
            _rDict[(_rPair[0])] = _rPair[1]
        return _rDict


    def _hfsPath(self, path):
        self.hfsIcon = subprocess.check_output(['osascript',
            '-e', 'set iPath to \"' + path + '\"',
            '-e', 'try',
            '-e', 'set hIcon to (POSIX file iPath as text)',
            '-e', 'set test to (hIcon as alias)',
            '-e', 'on error',
            '-e', 'set hIcon to false',
            '-e', 'end try',
            '-e', 'return hIcon'])
        return (self.hfsIcon).strip()
