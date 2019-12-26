
from PyQt5.QtCore import *                    

class Logger(QObject):
    speak = pyqtSignal(str, str)

    def __init__(self):
        QObject.__init__(self)
        self.debugEnabled = True
        pass

    def error(self, str, hash = None):
        self.speak.emit(str, hash)
        pass

    def info(self, str, hash = None):
        self.speak.emit(str, hash)
        pass

    def debug(self, str, hash = None):
        if self.debugEnabled:
            self.speak.emit(str, hash)
        pass

    def enableDebug(self, enable):
        self.debugEnabled = enable


logger = Logger()
