
import os
import constant
import common
from HashDB import *
from PyQt5.QtCore import QThread
from enum import Enum

class CollectorCmd(Enum):
    load = 0
    scan = 1
    verify = 2

class Collector(QThread):

    def __init__(self, ui):
        QThread.__init__(self)
        self.map = {}
        self.ui = ui


    def get_db(self, path):
        db = self.map.get(path)
        if None == db:
            db = HashDB(path, self.ui)
            self.map[path] = db
        return db


    def clear(self):
        self.map = {}


    def add_dir(self, path, recursive, cmd, skipExisting = True):
        self.argPath = path
        self.argRecursive = recursive
        self.argCmd = cmd
        self.argSkipExisting = skipExisting
        self.worker = self.add_dir_wrapper
        self.start()
        #self.run()


    def find_extern_duplicates(self, srcDir, recursive, simulate):
        self.argSrcDir = srcDir
        self.argRecursive = recursive
        self.argSimulate = simulate
        self.worker = self.find_extern_duplicates_wrapper
        self.start()
        #self.run()


    def find_hash(self, hash):
        for path, db in self.map.items():
            name = db.find_hash(hash)
            if None != name:
                name = os.path.join(db.path, name)
                return name
        return None


    def __del__(self):
        self.wait()


    def run(self):
        self.worker()


    def skip_dir(self, path):
        return os.path.isfile(os.path.join(path, constant.NOHASHFILE))


    def add_dir_wrapper(self):
        self.add_dir_impl(self.argPath, self.argRecursive, self.argSkipExisting, self.argCmd)


    def add_dir_impl2(self, path, recursive, skipExisting, cmd):
        errorCnt = 0
        dir = os.path.normpath(path)
        if self.skip_dir(dir):
            self.ui.info("Skipping dir: %s" % dir)
            #skipCnt +=1
            return 0
    
        db = self.get_db(dir)
        if db.load():
            #loadedCnt += 1
            pass

        if cmd is CollectorCmd.scan:
            db.scan(skipExisting)
            db.save()
        elif cmd is CollectorCmd.verify:
            errorCnt += db.verify()

        if recursive:
            dirList = []
            dirList.extend(common.get_dir_list_absolute(path, False))
            for dir in dirList:
                errorCnt += self.add_dir_impl2(dir, recursive, skipExisting, cmd)
        return errorCnt


    def add_dir_impl(self, path, recursive, skipExisting, cmd):
        self.ui.info("Loading HashDB %sfrom: %s" % ('recursively ' if recursive else '', path))
        errorCnt = self.add_dir_impl2(path, recursive, skipExisting, cmd)
        self.ui.info("Finished loading HashDB. Errors: %d" % errorCnt)


    def remove_hash(self, path, hash):
        db = self.map.get(path)
        if None == db:
            self.ui.error("Collector.remove_hash: Error db not found: %s" % path)
        else:
            db.remove(hash)


    def save_hashes(self, forceSave):
        self.ui.info("Start saving HashDB")
        for path, db in self.map.items():
            db.save(forceSave)
        self.ui.info("Finished saving HashDB")
        pass


    def find_extern_duplicates_wrapper(self):
        self.find_extern_duplicates_impl(self.argSrcDir, self.argRecursive, self.argSimulate)

    
    def find_extern_duplicates_impl(self, srcDir, recursive, simulate):

        if None == srcDir:
            self.ui.error("No src dir set")
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
                found_file = self.find_hash(hash)
                if None != found_file:
                    cntDuplicates += 1
                    self.ui.info(srcFilepath, hash)

        self.ui.info("Finished finding duplicates. %d files" % (cntDuplicates))