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


    def add_dir(self, path, recursive, cmd, skipExisting):
        self.argPath = path
        self.argRecursive = recursive
        self.argCmd = cmd
        self.argSkipExisting = skipExisting
        self.worker = self.add_dir_worker
        self.exec()


    def find_extern_duplicates(self, srcDir, recursive, simulate):
        self.argSrcDir = srcDir
        self.argRecursive = recursive
        self.arg_simulate = simulate
        self.worker = self.find_extern_duplicates_worker
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
        self.ui.stats()


    def add_dir_impl2(self, path, recursive, skipExisting, cmd):
        dir = os.path.normpath(path)
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


    def add_dir_impl(self, path, recursive, skipExisting, cmd):
        self.duplicate_db.reset()
        self.ui.info("Loading HashDB %sfrom: %s" % ('recursively ' if recursive else '', path))
        self.add_dir_impl2(path, recursive, skipExisting, cmd)
        self.ui.debug("Finished loading %d HashDB." % (len(self.map)))
        self.duplicate_db.show_duplicates()


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


    def find_extern_duplicates_worker(self):
        self.ui.reset()
        self.find_extern_duplicates_impl(self.argSrcDir, self.argRecursive, self.arg_simulate)
        self.ui.stats()

    
    def find_extern_duplicates_impl(self, srcDir, recursive, simulate):
        self.ui.info("Duplicates found in %s:" % srcDir)
        srcDirList = [srcDir]
        if recursive:
            srcDirList.extend(common.get_dir_list_absolute(srcDir, recursive))

        for curSrcDir in srcDirList:
            fileList = common.get_file_list(curSrcDir)

            for filename in fileList:
                srcFilepath = os.path.join(curSrcDir, filename)
                hash = common.get_hash_from_file(srcFilepath, self.ui)
                found_file = self.find_hash(hash)
                if None != found_file:
                    self.ui.inc_file_duplicates()
                    self.ui.file(srcFilepath)

        #self.ui.info("Finished finding duplicates. %d files" % (cntDuplicates))



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
        self.duplicate_db.show_duplicates(self.arg_path)
        self.ui.stats()


    def find_and_show_duplicates_in_hashDB(self, path):
        self.arg_path = path
        self.worker = self.find_and_show_duplicates_in_hashDB_worker
        self.exec()


    def exec(self):
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def move_duplicates_with_master_dir(self, master_path, dest_dir, move_flat, simulate):
        self.arg_master_path = master_path
        self.arg_dest_dir = dest_dir
        self.arg_move_flat = move_flat
        self.arg_simulate = simulate
        self.worker = self.move_duplicates_with_master_dir_worker
        self.exec()


    def move_duplicates_with_master_dir_worker(self):
        filenames = self.duplicate_db.get_list_with_files_to_move_keep_master_path(self.arg_master_path)
        self.move_files(filenames, self.arg_move_flat, self.arg_dest_dir, self.arg_simulate)


    def move_files(self, filenames, move_flat, dest_dir, is_simulation):
        self.ui.reset()
        for filename in filenames:
            path = common.create_duplicate_dest_path(filename, dest_dir, move_flat)
            common.move_file(filename, path, False, is_simulation, self.ui)
            if not is_simulation:
                self.remove_file(filename)
        if not is_simulation:
            self.save_hashes()
        self.ui.stats()


    def find_and_show_duplicates_in_folder(self, path):
        self.arg_path = path
        self.worker = self.find_and_show_duplicates_in_folder_worker
        self.exec()


    def find_and_show_duplicates_in_folder_worker(self):
        self.ui.reset()
        self.find_and_show_duplicates_in_folder_impl(self.arg_path)
        self.duplicate_db.show_duplicates(None)
        self.ui.stats()


    def find_and_show_duplicates_in_folder_impl(self, path):
        self.duplicate_db.reset()
        files = common.get_file_list(path)
        self.ui.info("Scannning %d files for duplicates in %s" % (len(files), path))
        for item in files:
            if self.ui.is_abort():
                return
            self.ui.info("Hashing: %s" % item)
            filepath = os.path.normpath(os.path.join(path, item))
            hash = common.get_hash_from_file(filepath, self.ui)
            self.duplicate_db.add_hash(hash, filepath)
        self.ui.info("Finished finding duplicates.")

