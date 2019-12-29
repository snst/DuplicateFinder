
from PyQt5.QtCore import *                    

class Logger(QObject):
    speak = pyqtSignal(str, str)
    log_hash = pyqtSignal(str)
    log_file = pyqtSignal(str)
    log_info = pyqtSignal(str)
    log_error = pyqtSignal(str)

    def __init__(self):
        QObject.__init__(self)
        self.debugEnabled = True
        pass

    def error(self, str):
        self.log_error.emit(str)
        pass

    def info(self, str):
        self.log_info.emit(str)
        pass

    def debug(self, str, hash = None):
        if self.debugEnabled:
            self.speak.emit(str, hash)
        pass

    def hash(self, str):
        self.log_hash.emit(str)
        pass

    def file(self, str):
        self.log_file.emit(str)
        pass

    def enableDebug(self, enable):
        self.debugEnabled = enable

    def is_abort(self):
        return self.abort_flag

    def abort(self):
        self.abort_flag = True

    def reset(self):
        self.abort_flag = False
        self.cnt_hash = 0
        self.cnt_error = 0
        self.cnt_verify_ok = 0
        self.cnt_verify_failed = 0
        self.cnt_moved = 0
        self.cnt_moved_renamed = 0
        self.cnt_hash_db_loaded = 0
        self.cnt_dir_skipped = 0
        self.cnt_dir_scanned = 0

    def stats(self):
        self.info("error: %s, hashed: %d, verify_ok: %d, verify_error: %d, moved: %s, moved+renamed: %d, loaded HashDB: %d, scanned dir: %d, skipped dir: %d" % 
        (self.cnt_error, self.cnt_hash, self.cnt_verify_ok, self.cnt_verify_failed, self.cnt_moved, 
        self.cnt_moved_renamed, self.cnt_hash_db_loaded, self.cnt_dir_scanned, self.cnt_dir_skipped))

    def inc_hash(self):
        self.cnt_hash += 1

    def inc_error(self):
        self.cnt_error += 1

    def inc_verify_ok(self):
        self.cnt_verify_ok += 1

    def inc_verify_failed(self):
        self.cnt_verify_failed += 1

    def inc_moved(self):
        self.cnt_moved += 1

    def inc_moved_renamed(self):
        self.cnt_moved_renamed += 1

    def inc_hash_db_loaded(self):
        self.cnt_hash_db_loaded += 1

    def inc_dir_scanned(self):
        self.cnt_dir_scanned += 1

    def inc_dir_skipped(self):
        self.cnt_dir_skipped += 1

logger = Logger()
