import shutil
from Collector import *
from PyQt5.QtCore import QThread

class DuplicateMover(QThread):

    def __init__(self, ui):
        QThread.__init__(self)
        self.ui = ui
        pass


    def move_file(self, src, dest, filename, foundPath, simulate):
        self.ui.info("Move %s from %s to %s. Found in %s" %
                    (filename, src, dest, foundPath))
        if not simulate:
            os.makedirs(dest, exist_ok=True)
            src_path = os.path.join(src, filename)
            dest_path = os.path.join(dest, filename)
            shutil.move(src_path, dest_path)


    def move_duplicates(self, collector, srcDir, duplicateDir, recursive = True, simulate = True):
        self.argCollector = collector
        self.argSrcDir = srcDir
        self.argDuplicateDir = duplicateDir
        self.argRecursive = recursive
        self.argSimulate = simulate
        self.start()


    def move_duplicates_impl(self, collector, srcDir, duplicateDir, recursive = True, simulate = True):

        if None == collector:
            self.ui.error("No hashes loaded")
            return

        if None == srcDir:
            self.ui.error("No src dir set")
            return

        if None == duplicateDir:
            self.ui.error("No duplicate dir set")
            return

        srcDirList = [srcDir]
        if recursive:
            srcDirList.extend(common.get_dir_list_absolute(srcDir, recursive))

        for curSrcDir in srcDirList:
            fileList = common.get_file_list(curSrcDir)
            curDestDir = os.path.relpath(curSrcDir, srcDir)
            #curDestDir = os.path.basename(curDestDir)
            curDestDir = os.path.join(duplicateDir, curDestDir)
            for infile in fileList:
                filepath = os.path.join(curSrcDir, infile)
                hash = common.get_hash_from_file(filepath, self.ui)
                found_file = collector.find_hash(hash)
                if None != found_file:
                    self.move_file(curSrcDir, curDestDir, infile, found_file, simulate)
                else:
                    #self.ui.info("Keep %s" % filepath)
                    pass


    def __del__(self):
        self.wait()


    def run(self):
        self.ui.info("Thread started")
        self.move_duplicates_impl(self.argCollector, self.argSrcDir, self.argDuplicateDir, self.argRecursive, self.argSimulate)
        self.ui.info("Thread finished")   