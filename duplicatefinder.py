import os
from Logger import *


class DuplicateFinder:

    def __init__(self, ui):
        self.map = {}
        self.ui = ui
        pass

    def add_hash(self, hash, filepath):
        value = self.map.get(hash)
        if None == value:
            self.map[hash] = [filepath]
        else:
            self.map[hash].append(filepath)
            #print("\n=%s\n=%s" % (filepath, value))
        return value

    def find(self, hashedFolder):
        if None == hashedFolder:
            self.ui.error("First scan folder")
        else:
            for hash, name in hashedFolder.db.map.items():
                filepath = os.path.join(hashedFolder.db.path, name)
                self.add_hash(hash, filepath)

            for hf in hashedFolder.child_db_map.values():
                self.find(hf)

    def show_duplicates(self):
        self.ui.info("Found duplicates:")
        for hash, files in self.map.items():
            if len(files) > 1:
                self.ui.info("\n%s" % hash)
                for filename in files:
                    self.ui.info("%s" % filename)
