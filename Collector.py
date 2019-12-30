
import os
import constant
import common
from HashDB import *
from PyQt5.QtCore import QThread
from enum import Enum
from DuplicateDB import *

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


    def add_dir(self, path, recursive, cmd, duplicate_db, skipExisting):
        self.argPath = path
        self.argRecursive = recursive
        self.argCmd = cmd
        self.argSkipExisting = skipExisting
        self.arg_duplicate_db = duplicate_db
        self.worker = self.add_dir_wrapper
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def find_extern_duplicates(self, srcDir, recursive, simulate):
        self.argSrcDir = srcDir
        self.argRecursive = recursive
        self.arg_simulate = simulate
        self.worker = self.find_extern_duplicates_wrapper
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def find_hash(self, hash):
        for path, db in self.map.items():
            name = db.find_hash(hash)
            if None != name:
                name = os.path.join(db.path, name)
                return name
        return None


    def find_hash_all(self, hash):
        found = []
        for path, db in self.map.items():
            name = db.find_hash(hash)
            if None != name:
                name = os.path.join(db.path, name)
                found.append(name)
        return found


    def __del__(self):
        self.wait()


    def run(self):
        self.worker()


    def skip_dir(self, path):
        return os.path.isfile(os.path.join(path, constant.NOHASHFILE))


    def add_dir_wrapper(self):
        self.add_dir_impl(self.argPath, self.argRecursive, self.argSkipExisting, self.argCmd, self.arg_duplicate_db)
        self.ui.stats()



    def add_dir_impl2(self, path, recursive, skipExisting, cmd, duplicate_db):
        dir = os.path.normpath(path)
        if self.skip_dir(dir):
            self.ui.info("Skipping dir: %s" % dir)
            self.ui.inc_dir_skipped()
            return
    
        db = self.get_db(dir)
        if db.load():
            self.ui.inc_hash_db_loaded()
            pass

        if cmd is CollectorCmd.scan:
            db.scan(duplicate_db, skipExisting)
            self.ui.inc_dir_scanned()
            db.save()
        elif cmd is CollectorCmd.verify:
            db.verify()

        if recursive:
            dirList = []
            dirList.extend(common.get_dir_list_absolute(path, False))
            for dir in dirList:
                self.add_dir_impl2(dir, recursive, skipExisting, cmd, duplicate_db)
                if self.ui.is_abort():
                    return


    def add_dir_impl(self, path, recursive, skipExisting, cmd, duplicate_db):
        duplicate_db.reset()
        self.ui.info("Loading HashDB %sfrom: %s" % ('recursively ' if recursive else '', path))
        self.add_dir_impl2(path, recursive, skipExisting, cmd, duplicate_db)
        self.ui.debug("Finished loading %d HashDB." % (len(self.map)))
        duplicate_db.show_duplicates()


    def remove_hash(self, path, hash):
        db = self.map.get(path)
        if None == db:
            self.ui.error("Collector.remove_hash: Error db not found: %s" % path)
        else:
            db.remove(hash)


    def save_hashes(self, forceSave = False):
        self.ui.info("Start saving HashDB")
        for path, db in self.map.items():
            db.save(forceSave)
        self.ui.info("Finished saving HashDB")
        pass


    def find_extern_duplicates_wrapper(self):
        self.find_extern_duplicates_impl(self.argSrcDir, self.argRecursive, self.arg_simulate)

    
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
                    self.ui.info(srcFilepath)

        self.ui.info("Finished finding duplicates. %d files" % (cntDuplicates))