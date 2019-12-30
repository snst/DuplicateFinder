from Collector import *
from DuplicateDB import *
from PyQt5.QtCore import QThread


class DuplicateFinder(QThread):

    def __init__(self, collector, ui):
        QThread.__init__(self)
        self.collector = collector
        self.ui = ui
        self.db = DuplicateDB(ui)
        self.worker = None
        pass


    def find_duplicates_in_hashDB(self, collector):
        self.ui.info("Start finding duplicates in HashDB...")
        self.db.reset()
        cnt_files = 0
        if None == collector:
            self.ui.error("No HashDB loaded")
        else:
            for path, db in collector.map.items():
                for hash, name in db.map.items():
                    filepath = os.path.normpath(os.path.join(db.path, name))
                    self.db.add_hash(hash, filepath)
                    cnt_files += 1
        self.ui.info("Finished finding duplicates. Processed hashes: %d, files: %d" % (self.db.count(), cnt_files))


    def find_duplicates_in_folder(self, path):
        self.db.reset()
        files = common.get_file_list(path)
        self.ui.info("Scannning %d files for duplicates in %s" % (len(files), path))
        for item in files:
            if self.ui.is_abort():
                return
            self.ui.info("Hashing: %s" % item)
            filepath = os.path.normpath(os.path.join(path, item))
            hash = common.get_hash_from_file(filepath, self.ui)
            self.db.add_hash(hash, filepath)
        self.ui.info("Finished finding duplicates.")


    def find_and_show_duplicates_in_folder_worker(self):
        self.find_and_show_duplicates_in_folder_impl(self.argPath)
        self.ui.stats()


    def find_and_show_duplicates_in_folder_impl(self, path):
        self.find_duplicates_in_folder(path)
        self.db.show_duplicates(None)


    def find_and_show_duplicates_in_folder(self, path):
        self.argPath = path
        self.worker = self.find_and_show_duplicates_in_folder_worker
        if constant.USE_THREADS:
            self.start()
        else:
            self.worker()


    def find_and_show_duplicates_in_hashDB_worker(self):
        self.find_duplicates_in_hashDB(self.collector)
        self.db.show_duplicates(self.argPath)
        self.ui.stats()


    def find_and_show_duplicates_in_hashDB(self, path):
        self.argPath = path
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
        self.db.move_duplicates_with_master_dir_impl(self.arg_master_path, self.arg_duplicate_path, self.arg_simulate, self.collector)
        self.ui.stats()

