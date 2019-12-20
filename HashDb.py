import os
import constant
import common


class HashDB:

    def __init__(self, path, ui):
        self.path = path
        self.map = {}
        self.ui = ui
        self.name = os.path.join(self.path, constant.HASHFILE)
        self.modified = False

    def add(self, filename, hash):
        self.map[hash] = filename
        self.modified = True

    def scan(self, skipExisting):
        files = common.get_file_list(self.path)
        for item in files:
            if skipExisting and None != self.find_filename(item):
                self.ui.info("Skip hashing: %s" % item)
            else:
                filepath = os.path.join(self.path, item)
                hash = common.get_hash_from_file(filepath, self.ui)
                self.add(item, hash)

    def save(self):
        if self.modified:
            try:
                self.ui.info("Save hashes: %s" % self.name)
                f = open(self.name, 'w')
                f.write(str(self.map))
                f.close()
                self.modified = False
            except:
                self.ui.error("Failed to save: %s" % self.name)

    def load(self):
        try:
            f = open(self.name, 'r')
            data = f.read()
            f.close()
            self.map = eval(data)
            self.ui.info("Loaded: %s" % self.name)
        except:
            self.ui.info("Failed to load: %s " % self.name)
            self.map = {}

    def find_filename(self, filename):
        for hash, name in self.map.items():
            if name == filename:
                return hash
        return None

    def find_hash(self, hash):
        value = self.map.get(hash)
        return value
