from Collector import *
from PyQt5.QtCore import QThread


class DuplicateFinder(QThread):

    def __init__(self, collector, ui):
        QThread.__init__(self)
        self.collector = collector
        self.map = {}
        self.ui = ui
        self.worker = None
        pass

    def add_hash(self, hash, filepath):
        value = self.map.get(hash)
        if None == value:
            self.map[hash] = [filepath]
        else:
            self.map[hash].append(filepath)
            #print("\n=%s\n=%s" % (filepath, value))
        return value
        

    def find_duplicates(self, collector):
        self.map = {}
        if None == collector:
            self.ui.error("First scan folder")
        else:
            for path, db in collector.map.items():
                for hash, name in db.map.items():
                    filepath = os.path.normpath(os.path.join(db.path, name))
                    self.add_hash(hash, filepath)


    def show_duplicates(self):
        self.ui.info("\nFound duplicates:")
        for hash, files in self.map.items():
            if len(files) > 1:
                self.ui.info("\n%s" % hash)
                for filename in files:
                    self.ui.info("%s" % filename)


    def find_and_show_duplicates_impl(self):
        self.find_duplicates(self.collector)
        self.show_duplicates()


    def find_and_show_duplicates(self):
        self.worker = self.find_and_show_duplicates_impl
        self.start()
        #self.worker()

    def find_and_move_duplicates(self, masterPath, duplicatePath, simulate):
        self.argMasterPath = masterPath
        self.argDuplicatePath = duplicatePath
        self.argSimulate = simulate
        self.worker = self.find_and_move_duplicates_impl
        self.start()
        #self.worker()

    def __del__(self):
        self.wait()

    def run(self):
        self.ui.info("Thread started")
        if None != self.worker:
            self.worker()
        self.ui.info("Thread finished")   


    def find_and_move_duplicates_impl(self):
        self.ui.info("Start move duplicates:\nMaster dir: %s\nDuplicate dir: %s" % (self.argMasterPath, self.argDuplicatePath))
        for hash, files in self.map.items():
            if len(files) > 1:
                filesToMove = []
                for filename in files:
                    if filename.startswith(self.argMasterPath):
                        self.ui.info("Found master: %s" % filename)
                        filesToMove = list(files)
                        filesToMove.remove(filename)
                        break

                for srcPath in filesToMove:
                    try:
                        path = "." + os.path.splitdrive(srcPath)[1]
                        path = os.path.normpath(path)
                        destPath = os.path.join(self.argDuplicatePath, path)
                        common.move_file2(srcPath, destPath, self.argSimulate, self.ui)
                        if not self.argSimulate:
                            dirName = os.path.dirname(srcPath)
                            self.collector.remove_hash(dirName, hash)
                    except:
                        self.ui.info("Error moving: %s" % srcPath)
                        pass

                            
        self.ui.info("Finished move duplicates")