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


    def is_modified(self):
        return self.modified


    def add(self, filename, hash):
        self.map[hash] = filename
        self.modified = True


    def remove(self, hash):
        if None == self.find_hash(hash):
            self.ui.info("HashDB.remove: Error: not found: %s %s" % (self.path, hash))
            return
        self.ui.info("Remove hash %s from %s" % (hash, self.path))
        self.map.pop(hash, None)
        self.modified = True


    def scan(self, skipExisting):
        files = common.get_file_list(self.path)
        self.ui.info("Scannning %d files in %s" % (len(files), self.path))
        newMap = {}
        for item in files:
            hash = self.find_filename(item)
            if skipExisting and None != hash:
                self.ui.debug("Skip hashing: %s" % item)
            else:
                self.ui.info("Hashing: %s" % item)
                filepath = os.path.join(self.path, item)
                hash = common.get_hash_from_file(filepath, self.ui)
                self.add(item, hash)
            self.map.pop(hash, None)
            newMap[hash] = item

        for hash, name in self.map.items():
            self.ui.info("Removing hash %s for not found file %s" % (hash, name))
            self.modified = True
        self.map = newMap
        pass


    def save(self, force = False):
        if self.modified or force:
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
            self.ui.debug("Loaded: %s" % self.name)
            return True
        except:
            self.ui.debug("Failed to load: %s " % self.name)
            self.map = {}
            return False


    def find_filename(self, filename):
        for hash, name in self.map.items():
            if name == filename:
                return hash
        return None


    def find_hash(self, hash):
        value = self.map.get(hash)
        return value
