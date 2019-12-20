
import os
import constant
import common
from HashDB import *


class Collector:

    def __init__(self, ui):
        self.map = {}
        self.ui = ui
        pass

    def get_db(self, path):
        db = self.map.get(path)
        if None == db:
            db = HashDB(path, self.ui)
            self.map[path] = db
        return db

    def add_dir(self, path, recursive, doScan, skipExisting = True):
        dirList = [path]
        if recursive:
            dirList.extend(common.get_dir_list_absolute(path, recursive))

        for dir in dirList:
            db = self.get_db(dir)
            db.load()
            if doScan:
                db.scan(skipExisting)
            db.save()

    def find_hash(self, hash):
        for path, db in self.map.items():
            name = db.find_hash(hash)
            if None != name:
                name = os.path.join(db.path, name)
                return name
        return None
