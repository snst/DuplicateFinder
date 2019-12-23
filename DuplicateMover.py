import shutil
from Collector import *
from PyQt5.QtCore import QThread
import common

class DuplicateMover(QThread):

    def __init__(self, ui):
        QThread.__init__(self)
        self.ui = ui
        pass

    def move_duplicates(self, collector, srcDir, duplicateDir, moveFlat, recursive, simulate):
        self.argCollector = collector
        self.argSrcDir = srcDir
        self.argDuplicateDir = duplicateDir
        self.argMoveFlat = moveFlat
        self.argRecursive = recursive
        self.argSimulate = simulate
        self.start()
        #self.run()


    def move_duplicates_impl(self, collector, srcDir, duplicateDir, moveFlat, recursive, simulate):

        if None == collector:
            self.ui.error("No HashDB loaded")
            return

        if None == srcDir:
            self.ui.error("No src dir set")
            return

        if None == duplicateDir:
            self.ui.error("No duplicate dir set")
            return

        self.ui.info("Duplicates found in %s:" % srcDir)
        srcDirList = [srcDir]
        if recursive:
            srcDirList.extend(common.get_dir_list_absolute(srcDir, recursive))

        cntDuplicates = 0

        for curSrcDir in srcDirList:
            fileList = common.get_file_list(curSrcDir)

            for filename in fileList:
                srcFilepath = os.path.join(curSrcDir, filename)
                hash = common.get_hash_from_file(srcFilepath, self.ui)
                found_file = collector.find_hash(hash)
                if None != found_file:
                    cntDuplicates += 1
                    self.ui.info(srcFilepath)

        self.ui.info("Finished finding duplicates. %d files" % (cntDuplicates))

    def __del__(self):
        self.wait()


    def run(self):
        self.move_duplicates_impl(self.argCollector, self.argSrcDir, self.argDuplicateDir, self.argMoveFlat, self.argRecursive, self.argSimulate)
