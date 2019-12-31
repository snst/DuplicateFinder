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
            self.ui.error("Failed to remove hash from HashDB: %s -- %s" % (hash, self.path))
            return
        self.ui.debug("Remove hash %s from %s" % (hash, self.path))
        self.map.pop(hash, None)
        self.modified = True


    def check_for_duplicate(self, duplicate_db, hash, filename):
        existing_file = self.find_hash(hash)
        if existing_file:
            if not duplicate_db.find_hash(hash):
                duplicate_db.add_hash(hash, os.path.join(self.path, existing_file))
            duplicate_db.add_hash(hash, filename)
            self.ui.debug("Already existing: %s" % existing_file)
            return True
        return False


    def remove_missing_files_from_hashDB(self, files):
        missing_files = {}
        for hash, name in self.map.items():
            if not name in files:
                missing_files[hash] = name
        
        if len(missing_files):
            self.ui.info("Removing missing files from HashDB:")

        for hash, name in missing_files.items():
            self.ui.info("%s - %s" % (name, hash))
            self.map.pop(hash, None)
            self.ui.inc_missing_file()
            self.modified = True


    def scan(self, duplicate_db, skipExisting):
        files = common.get_file_list(self.path)
        self.ui.info("Scannning %d files in %s" % (len(files), self.path))
        self.remove_missing_files_from_hashDB(files)

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
                if not self.check_for_duplicate(duplicate_db, hash, filepath):
                    self.add(item, hash)
      

    def verify(self):
        files = common.get_file_list(self.path)
        self.ui.info("Verifing %d files in %s" % (len(files), self.path))
        map2 = copy.deepcopy(self.map)
        for item in files:
            if self.ui.is_abort():
                return
            found_hash = self.find_filename(item)
            filepath = os.path.join(self.path, item)
            if found_hash:
                map2.pop(found_hash, None)
                calc_hash = common.get_hash_from_file(filepath, self.ui)
                if found_hash != calc_hash:
                    self.ui.error("!! Wrong hash for %s" % filepath)
                    self.ui.error("!! HashDB/Calc: %s <=> %s" % (found_hash, calc_hash))
                    self.ui.inc_verify_failed()
                    self.ui.inc_error()
                else:
                    self.ui.inc_verify_ok()
            else:
                self.ui.error("!! New file: %s" % filepath)
                self.ui.inc_error()

        for hash, name in map2.items():
            self.ui.error("!! Missing file: %s" % (name))
            self.ui.inc_error()


    def save(self, force = False):
        if self.modified or force:
            try:
                self.ui.info("Save hashes: %s" % self.name)
                f = open(self.name, 'w', encoding="utf-8")
                txt = str(self.map)
                f.write(txt)
                f.close()
                self.modified = False
            except Exception as e:
                self.ui.error("Failed to save: %s\n%s" % (self.name, str(e)))


    def load(self):
        self.map = {}
        if not os.path.isfile(self.name):
            return False
        try:
            f = open(self.name, 'r', encoding="utf-8")
            data = f.read()
            f.close()
            self.map = eval(data)
            self.ui.debug("Loaded: %s" % self.name)
            return True
        except Exception as e:
            self.ui.error("Failed to load: %s\n%s" % (self.name, str(e)))
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


    def remove_filename(self, filename):
        hash = self.find_filename(filename)
        if hash:
            self.remove(hash)