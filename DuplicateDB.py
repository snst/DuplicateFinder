import os
import common

class DuplicateDB:

    def __init__(self, ui):
        self.ui = ui
        self.reset()


    def reset(self):
        self.map = {}


    def count(self):
        return len(self.map)


    def find_hash(self, hash):
        return None != self.map.get(hash)


    def add_hash(self, hash, filepath):
        value = self.map.get(hash)
        if None == value:
            self.map[hash] = [filepath]
        else:
            self.map[hash].append(filepath)
        return value
        

    def is_in_filter_path(self, path, files):
        if not path:
            return True
        path = path + os.path.sep
        for filename in files:
            if filename.startswith(path):
                return True
        return False


    def show_duplicates(self, path = None):
        duplicates_found = False
        for hash, files in self.map.items():
            if len(files) > 1:
                if self.is_in_filter_path(path, files):
                    if not duplicates_found:
                        duplicates_found = True
                        self.ui.info("Duplicates found:")
                    self.ui.inc_hash_duplicates()
                    self.ui.hash("%s" % hash)
                    for filename in files:
                        self.ui.file("%s" % filename)
                        self.ui.inc_file_duplicates()
                    #cnt_duplicates -= 1 # decrement for original
        #self.ui.info("Finished finding duplicates. Found hashes: %d, files: %d" % (cnt_hashes, cnt_duplicates))
        #if not duplicates_found:
        #    self.ui.info("No duplicates found.")


    def move_duplicates_with_master_dir_impl(self, master_path, duplicate_path, simulate, collector):
        self.ui.info("Start moving duplicates...")
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
                        if not simulate:
                            dir_name = os.path.dirname(src_path)
                            collector.remove_hash(dir_name, hash)
                    except Exception as e:
                        self.ui.error("Error moving: %s, %s" % (str(e), src_path))
                        pass

        collector.save_hashes()                            
        #self.ui.info("Finished moving %d duplicates. Errors: %d" % (cnt_moved, cnt_error))