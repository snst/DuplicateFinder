from Collector import *
from PyQt5.QtCore import QThread


class DuplicateFinder(QThread):

    def __init__(self, collector, ui):
        QThread.__init__(self)
        self.collector = collector
        self.map = {}
        self.ui = ui
        self.worker = None
        pass


    def add_hash(self, hash, filepath):
        value = self.map.get(hash)
        if None == value:
            self.map[hash] = [filepath]
        else:
            self.map[hash].append(filepath)
            #print("\n=%s\n=%s" % (filepath, value))
        return value
        

    def find_duplicates_in_hashDB(self, collector):
        self.ui.info("Start finding duplicates in HashDB...")
        self.map = {}
        cnt_files = 0
        if None == collector:
            self.ui.error("No HashDB loaded")
        else:
            for path, db in collector.map.items():
                for hash, name in db.map.items():
                    filepath = os.path.normpath(os.path.join(db.path, name))
                    self.add_hash(hash, filepath)
                    cnt_files += 1
        self.ui.info("Finished finding duplicates. Processed hashes: %d, files: %d" % (len(self.map), cnt_files))


    def find_duplicates_in_folder(self, path):
        self.map = {}
        files = common.get_file_list(path)
        self.ui.info("Scannning %d files for duplicates in %s" % (len(files), path))
        for item in files:
            if self.ui.is_abort():
                return
            self.ui.info("Hashing: %s" % item)
            filepath = os.path.normpath(os.path.join(path, item))
            hash = common.get_hash_from_file(filepath, self.ui)
            self.add_hash(hash, filepath)
        self.ui.info("Finished finding duplicates.")


    def show_duplicates(self):
        self.ui.info("Duplicates found:")
        cnt_hashes = 0
        cnt_duplicates = 0
        for hash, files in self.map.items():
            if len(files) > 1:
                cnt_hashes += 1
                self.ui.hash("%s" % hash)
                for filename in files:
                    self.ui.file("%s" % filename)
                    cnt_duplicates += 1
                cnt_duplicates -= 1 # decrement for original
        self.ui.info("Finished finding duplicates. Found hashes: %d, files: %d" % (cnt_hashes, cnt_duplicates))


    def find_and_show_duplicates_in_folder_worker(self):
        self.find_and_show_duplicates_in_folder_impl(self.argPath)
        self.ui.stats()


    def find_and_show_duplicates_in_folder_impl(self, path):
        self.find_duplicates_in_folder(path)
        self.show_duplicates()


    def find_and_show_duplicates_in_folder(self, path):
        self.argPath = path
        self.worker = self.find_and_show_duplicates_in_folder_worker
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def find_and_show_duplicates_in_hashDB_worker(self):
        self.find_duplicates_in_hashDB(self.collector)
        self.show_duplicates()


    def find_and_show_duplicates_in_hashDB(self):
        self.worker = self.find_and_show_duplicates_in_hashDB_worker
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def move_duplicates_with_master_dir(self, master_path, duplicate_path, simulate):
        self.arg_master_path = master_path
        self.arg_duplicate_path = duplicate_path
        self.arg_simulate = simulate
        self.worker = self.move_duplicates_with_master_dir_worker
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def __del__(self):
        self.wait()


    def run(self):
        if None != self.worker:
            self.worker()


    def move_duplicates_with_master_dir_worker(self):
        self.move_duplicates_with_master_dir_impl(self.arg_master_path, self.arg_duplicate_path, self.arg_simulate)


    def move_duplicates_with_master_dir_impl(self, master_path, duplicate_path, simulate):
        self.ui.info("Start moving duplicates...")
        cnt_moved = 0
        cnt_error = 0
        for hash, files in self.map.items():
            if len(files) > 1:
                files_to_move = []
                master_file = None
                for filename in files:
                    p = os.path.dirname(filename)
                    if p == master_path:
                        #self.ui.info("Found master: %s" % filename)
                        master_file = filename
                        files_to_move = list(files)
                        files_to_move.remove(filename)
                        break

                for src_path in files_to_move:
                    try:
                        path = "." + os.path.splitdrive(src_path)[1]
                        path = os.path.normpath(path)
                        dest_path = os.path.join(duplicate_path, path)
                        self.ui.debug("Move %s to %s - Master: %s" % (src_path, dest_path, master_file))
                        common.move_file(src_path, dest_path, False, simulate, self.ui)
                        cnt_moved += 1
                        if not simulate:
                            dir_name = os.path.dirname(src_path)
                            self.collector.remove_hash(dir_name, hash)
                    except:
                        self.ui.error("Error moving: %s" % src_path)
                        cnt_error += 1
                        pass

        self.collector.save_hashes()                            
        self.ui.info("Finished moving %d duplicates. Errors: %d" % (cnt_moved, cnt_error))