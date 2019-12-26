import os
import constant
import common
import copy


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
        infoHash = False
        for item in files:
            hash = self.find_filename(item)
            if skipExisting and None != hash:
                self.ui.debug("Skip hashing: %s" % item)
            else:
                filepath = os.path.join(self.path, item)
                if not infoHash:
                    infoHash = True
                    self.ui.info("Hashing:")
                self.ui.info(filepath)
                hash = common.get_hash_from_file(filepath, self.ui)
                self.add(item, hash)
            self.map.pop(hash, None)
            newMap[hash] = item

        for hash, name in self.map.items():
            self.ui.info("Removing hash for not found file %s - %s" % (name, hash))
            self.modified = True
        self.map = newMap
        pass


    def verify(self):
        errorCnt = 0
        files = common.get_file_list(self.path)
        self.ui.info("Verifing %d files in %s" % (len(files), self.path))
        map2 = copy.deepcopy(self.map)
        for item in files:
            found_hash = self.find_filename(item)
            filepath = os.path.join(self.path, item)
            if found_hash:
                map2.pop(found_hash, None)
                calc_hash = common.get_hash_from_file(filepath, self.ui)
                if found_hash != calc_hash:
                    self.ui.info("!! Wrong hash for %s" % filepath)
                    self.ui.info("!! HashDB/Calc: %s <=> %s" % (found_hash, calc_hash))
                    errorCnt += 1
            else:
                self.ui.info("!! New file: %s" % filepath)
                errorCnt += 1

        for hash, name in map2.items():
            self.ui.info("!! Missing file: %s" % (name))
            errorCnt += 1
        return errorCnt

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
