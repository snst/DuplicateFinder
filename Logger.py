
from PyQt5.QtCore import *                    

class Logger(QObject):
    speak = pyqtSignal(str)
    def __init__(self):
        QObject.__init__(self)
        #self.logInfo = print
        #self.logError = print
        
        pass

    def error(self, str):
        #self.logInfo(str)
        self.speak.emit(str)
        pass

    def info(self, str):
        #self.logInfo(str)
        self.speak.emit(str)
        pass


logger = Logger()
