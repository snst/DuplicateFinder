
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
        self.cnt_hash_duplicates = 0
        self.cnt_file_duplicates = 0
        self.cnt_missing_file = 0
        self.cnt_file_processed = 0

    def m(self, msg, cnt):
        if cnt > 0:
            return ", %s: %d" % (msg, cnt)
        else:
            return ""

    def stats(self):
        str = "Finished"
        str += self.m("Errors", self.cnt_error)
        str += self.m("Hashed files", self.cnt_hash)
        str += self.m("Verify Ok", self.cnt_verify_ok)
        str += self.m("Verify Error", self.cnt_verify_failed)
        str += self.m("Moved files", self.cnt_moved)
        str += self.m("Moved/renamed files", self.cnt_moved_renamed)
        str += self.m("Loaded HashDB", self.cnt_hash_db_loaded)
        str += self.m("Scanned dir", self.cnt_dir_scanned)
        str += self.m("Skipped dir", self.cnt_dir_skipped)
        str += self.m("Hash duplicates", self.cnt_hash_duplicates)
        str += self.m("File duplicates", self.cnt_file_duplicates)
        str += self.m("Files missing", self.cnt_missing_file)
        str += self.m("Files processed", self.cnt_file_processed)
        self.info(str)

    def inc_file_processed(self):
        self.cnt_file_processed += 1

    def inc_missing_file(self):
        self.cnt_missing_file += 1

    def inc_hash_duplicates(self):
        self.cnt_hash_duplicates += 1

    def inc_file_duplicates(self):
        self.cnt_file_duplicates += 1

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
