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
    unload = 3

class Collector(QThread):

    def __init__(self, ui):
        QThread.__init__(self)
        self.map = {}
        self.duplicate_db = DuplicateDB(ui)
        self.ui = ui


    def get_db(self, path):
        db = self.map.get(path)
        if None == db:
            db = HashDB(path, self.ui)
            self.map[path] = db
        return db


    def clear(self):
        self.map = {}
        self.ui.hash_cnt(0)


    def add_dir(self, path, recursive, cmd, skipExisting):
        self.argPath = path
        self.argRecursive = recursive
        self.argCmd = cmd
        self.argSkipExisting = skipExisting
        self.worker = self.add_dir_worker
        self.exec()


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


    def is_skip_dir(self, path):
        return os.path.isfile(os.path.join(path, constant.NOHASHFILE))


    def add_dir_worker(self):
        self.ui.reset()
        self.add_dir_impl(self.argPath, self.argRecursive, self.argSkipExisting, self.argCmd)
        self.ui.hash_cnt(len(self.map))
        self.ui.stats()


    def add_dir_impl2(self, path, recursive, skipExisting, cmd):
        dir = os.path.normpath(path)
        self.ui.status(dir)
        if self.is_skip_dir(dir):
            self.ui.info("Skipping dir: %s" % dir)
            self.ui.inc_dir_skipped()
            return
    
        db = self.get_db(dir)
        if db.load():
            self.ui.inc_hash_db_loaded()
            pass

        if cmd is CollectorCmd.scan:
            db.scan(self.duplicate_db, skipExisting)
            self.ui.inc_dir_scanned()
            db.save()
        elif cmd is CollectorCmd.verify:
            db.verify()

        if recursive:
            dirList = []
            dirList.extend(common.get_dir_list_absolute(path, False))
            for dir in dirList:
                self.add_dir_impl2(dir, recursive, skipExisting, cmd)
                if self.ui.is_abort():
                    return
        self.ui.hash_cnt(len(self.map))


    def remove_dir_from_hash_db(self, path, recursive):
        to_remove = []
        if recursive:
            for db_path, db in self.map.items():
                if db_path.startswith(path):
                    to_remove.append(db_path)
        else:
            for db_path, db in self.map.items():
                if db_path == path:
                    to_remove.append(db_path)
                    break
        for p in to_remove:
            self.ui.info("Remove hashDB: %s" % p)
            self.map.pop(p, None)
           

    def add_dir_impl(self, path, recursive, skipExisting, cmd):

        if cmd is CollectorCmd.unload:
            self.ui.info("Unloading HashDB %sfrom: %s" % ('recursively ' if recursive else '', path))
            self.remove_dir_from_hash_db(path, recursive)
            self.ui.debug("Finished unloading %d HashDB." % (len(self.map)))
        else:
            self.duplicate_db.reset()
            self.ui.info("Loading HashDB %sfrom: %s" % ('recursively ' if recursive else '', path))
            self.add_dir_impl2(path, recursive, skipExisting, cmd)
            self.ui.debug("Finished loading %d HashDB." % (len(self.map)))
            self.duplicate_db.show_duplicates(None, False)


    def remove_hash(self, path, hash):
        db = self.map.get(path)
        if None == db:
            self.ui.error("Collector.remove_hash: Error db not found: %s" % path)
        else:
            db.remove(hash)


    def remove_file(self, filepath):
        path = os.path.dirname(filepath)
        filename = os.path.basename(filepath)
        db = self.map.get(path)
        if db:
            db.remove_filename(filename)
        else:
            self.ui.debug("remove_file: HashDB not found: %s" % path)

    def save_hashes(self, forceSave = False):
        self.ui.info("Start saving HashDB")
        for path, db in self.map.items():
            db.save(forceSave)
        self.ui.info("Finished saving HashDB")
        pass


    def find_duplicates_in_hashDB_impl(self):
        self.ui.info("Start finding duplicates in HashDB...")
        self.duplicate_db.reset()
        for path, db in self.map.items():
            for hash, name in db.map.items():
                filepath = os.path.normpath(os.path.join(db.path, name))
                self.duplicate_db.add_hash(hash, filepath)
                self.ui.inc_file_processed()
        self.ui.debug("Finished finding duplicates")


    def find_and_show_duplicates_in_hashDB_worker(self):
        self.find_duplicates_in_hashDB_impl()
        self.duplicate_db.show_duplicates(self.arg_path, self.arg_recursive)
        self.ui.stats()


    def find_and_show_duplicates_in_hashDB(self, path, recursive):
        self.arg_path = path
        self.arg_recursive = recursive
        self.worker = self.find_and_show_duplicates_in_hashDB_worker
        self.exec()


    def exec(self):
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def move_duplicates_with_master_dir(self, master_path, dest_dir, move_flat, with_subfolders, simulate):
        self.arg_master_path = master_path
        self.arg_dest_dir = dest_dir
        self.arg_move_flat = move_flat
        self.arg_simulate = simulate
        self.arg_with_subfolders = with_subfolders
        self.worker = self.move_duplicates_with_master_dir_worker
        self.exec()


    def move_duplicates_with_master_dir_worker(self):
        filenames = self.duplicate_db.get_list_with_files_to_move_keep_master_path(self.arg_master_path, self.arg_with_subfolders)
        self.move_files(filenames, self.arg_move_flat, self.arg_dest_dir, self.arg_simulate)


    def move_files(self, filenames, move_flat, dest_dir, is_simulation):
        self.ui.reset()
        for filename in filenames:
            if self.ui.is_abort():
                break
            path = common.create_duplicate_dest_path(filename, dest_dir, move_flat)
            common.move_file(filename, path, False, is_simulation, self.ui)
            if not is_simulation:
                self.remove_file(filename)
        if not is_simulation:
            self.save_hashes()
        self.ui.stats()

