
class Logger:
    def __init__(self):
        self.logInfo = print
        self.logError = print
        pass

    def error(self, str):
        self.logInfo(str)
        pass

    def info(self, str):
        self.logInfo(str)
        pass


log = Logger()
