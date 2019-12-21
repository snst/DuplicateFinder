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
        self.ui.info("Finding duplicates...")
        self.map = {}
        if None == collector:
            self.ui.error("First scan folder")
        else:
            for path, db in collector.map.items():
                for hash, name in db.map.items():
                    filepath = os.path.normpath(os.path.join(db.path, name))
                    self.add_hash(hash, filepath)
        self.ui.info("Finished finding duplicates.")


    def find_duplicates_in_folder(self, path):
        self.map = {}
        files = common.get_file_list(path)
        self.ui.info("Scannning %d files for duplicates in %s" % (len(files), path))
        for item in files:
            self.ui.info("Hashing: %s" % item)
            filepath = os.path.normpath(os.path.join(path, item))
            hash = common.get_hash_from_file(filepath, self.ui)
            self.add_hash(hash, filepath)
        self.ui.info("Finished finding duplicates.")


    def show_duplicates(self):
        self.ui.info("Found duplicates:")
        cntHashes = 0
        cntDuplicates = 0
        for hash, files in self.map.items():
            if len(files) > 1:
                cntHashes += 1
                self.ui.info("\n%s" % hash)
                for filename in files:
                    self.ui.info("%s" % filename)
                    cntDuplicates += 1

        self.ui.info("Finished finding duplicates. %d hashes, %d files" % (cntHashes, cntDuplicates))


    def find_and_show_duplicates_in_folder_impl(self):
        self.find_duplicates_in_folder(self.argPath)
        self.show_duplicates()

    def find_and_show_duplicates_in_folder(self, path):
        self.argPath = path
        self.worker = self.find_and_show_duplicates_in_folder_impl
        self.start()
        #self.worker()

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
        if None != self.worker:
            self.worker()


    def find_and_move_duplicates_impl(self):
        self.ui.info("Start moving duplicates...")
        cntMoved = 0
        cntMovedError = 0
        for hash, files in self.map.items():
            if len(files) > 1:
                filesToMove = []
                masterFile = None
                for filename in files:
                    if filename.startswith(self.argMasterPath):
                        #self.ui.info("Found master: %s" % filename)
                        masterFile = filename
                        filesToMove = list(files)
                        filesToMove.remove(filename)
                        break

                for srcPath in filesToMove:
                    try:
                        path = "." + os.path.splitdrive(srcPath)[1]
                        path = os.path.normpath(path)
                        destPath = os.path.join(self.argDuplicatePath, path)
                        self.ui.info("Move %s to %s - Master: %s" % (srcPath, destPath, masterFile))
                        common.move_file2(srcPath, destPath, self.argSimulate, self.ui)
                        cntMoved += 1
                        if not self.argSimulate:
                            dirName = os.path.dirname(srcPath)
                            self.collector.remove_hash(dirName, hash)
                    except:
                        self.ui.info("Error moving: %s" % srcPath)
                        cntMovedError += 1
                        pass

                            
        self.ui.info("Finished moving %d duplicates. Errors: %d" % (cntMoved, cntMovedError))