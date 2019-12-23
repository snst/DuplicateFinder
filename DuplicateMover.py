import shutil
from Collector import *
from PyQt5.QtCore import QThread
import common

class DuplicateMover(QThread):

    def __init__(self, ui):
        QThread.__init__(self)
        self.ui = ui
        pass


    def move_file(self, src, dest, filename, foundPath, simulate):
        self.ui.info("Move %s from %s to %s - Master %s" %
                    (filename, src, dest, foundPath))
        if not simulate:
            os.makedirs(dest, exist_ok=True)
            src_path = os.path.join(src, filename)
            dest_path = os.path.join(dest, filename)
            shutil.move(src_path, dest_path)


    def move_duplicates(self, collector, srcDir, duplicateDir, moveFlat, recursive, simulate):
        self.argCollector = collector
        self.argSrcDir = srcDir
        self.argDuplicateDir = duplicateDir
        self.argMoveFlat = moveFlat
        self.argRecursive = recursive
        self.argSimulate = simulate
        #self.start()
        self.run()


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

        srcDirList = [srcDir]
        if recursive:
            srcDirList.extend(common.get_dir_list_absolute(srcDir, recursive))

        for curSrcDir in srcDirList:
            fileList = common.get_file_list(curSrcDir)
            curDestDir = None
            #curDestDir = os.path.relpath(curSrcDir, srcDir)
            if moveFlat:
                curDestDir = duplicateDir
            else:
                curDestDir = '.' + os.path.splitdrive(curSrcDir)[1]
                curDestDir = os.path.join(duplicateDir, curDestDir)

            for filename in fileList:
                srcFilepath = os.path.join(curSrcDir, filename)
                hash = common.get_hash_from_file(srcFilepath, self.ui)
                found_file = collector.find_hash(hash)
                if None != found_file:
                    destFilePath = os.path.normpath(os.path.join(curDestDir, filename))
                    common.move_file(srcFilepath, destFilePath, False, simulate, self.ui)


    def __del__(self):
        self.wait()


    def run(self):
        self.move_duplicates_impl(self.argCollector, self.argSrcDir, self.argDuplicateDir, self.argMoveFlat, self.argRecursive, self.argSimulate)
