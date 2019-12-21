
from PyQt5.QtCore import *                    

class Logger(QObject):
    speak = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        self.debugEnabled = True
        pass

    def error(self, str):
        self.speak.emit(str)
        pass

    def info(self, str):
        self.speak.emit(str)
        pass

    def debug(self, str):
        if self.debugEnabled:
            self.speak.emit(str)
        pass

    def enableDebug(self, enable):
        self.debugEnabled = enable


logger = Logger()
