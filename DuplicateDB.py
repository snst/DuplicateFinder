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


    def get_list_with_files_to_move_keep_master_path(self, master_path):
        self.ui.info("Start moving duplicates...")
        all_files_to_move = []
        for hash, files in self.map.items():
            if len(files) > 1:
                for filename in files:
                    p = os.path.dirname(filename)
                    if p == master_path: # found master file to keep
                        files_to_move = list(files)
                        files_to_move.remove(filename)
                        all_files_to_move.extend(files_to_move)
                        break
        return all_files_to_move
        