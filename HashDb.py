import os
import constant


class HashDb:

    def __init__(self, path, ui):
        self.path = path
        self.map = {}
        self.ui = ui
        self.name = os.path.join(self.path, constant.HASHFILE)

    def add(self, filename, hash):
        self.map[hash] = filename

    def save(self):
        try:
            f = open(self.name, 'w')
            f.write(str(self.map))
            f.close()
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
