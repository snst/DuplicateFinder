
import os
import constant
import common
from HashDB import *
from PyQt5.QtCore import QThread

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

    def add_dir(self, path, recursive, doScan, skipExisting = True):
        self.argPath = path
        self.argRecursive = recursive
        self.argDoScan = doScan
        self.argSkipExisting = skipExisting
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
        self.add_dir_impl()


    def add_dir_impl(self):
        self.ui.info("Loading hash DB %sfrom: %s" % ('recursively ' if self.argRecursive else '', self.argPath))
        dirList = [self.argPath]
        loadedCnt = 0
        if self.argRecursive:
            dirList.extend(common.get_dir_list_absolute(self.argPath, self.argRecursive))

        for dir in dirList:
            dir = os.path.normpath(dir)
            db = self.get_db(dir)
            if db.load():
                loadedCnt += 1
            if self.argDoScan:
                db.scan(self.argSkipExisting)
            db.save()
        self.ui.info("Finished loading %d hash DB." % loadedCnt)


    def remove_hash(self, path, hash):
        db = self.map.get(path)
        if None == db:
            self.ui.error("Collector.remove_hash: Error db not found: %s" % path)
        else:
            db.remove(hash)


    def save_hashes(self, forceSave):
        self.ui.info("Start save HashDB")
        for path, db in self.map.items():
            db.save(forceSave)
        self.ui.info("Finished save HashDB")
        pass