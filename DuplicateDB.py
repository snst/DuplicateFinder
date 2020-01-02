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
        for filename in files:
            if filename.startswith(path):
                return True
        return False


    def show_duplicates(self, path = None):
        map2 = {}
        if path and not path.endswith(os.path.sep):
            path = path + os.path.sep
        duplicates_found = False
        for hash, files in self.map.items():
            if len(files) > 1:
                if self.is_in_filter_path(path, files):
                    map2[hash] = files
                    if not duplicates_found:
                        duplicates_found = True
                        self.ui.info("Duplicates found:")
                    self.ui.inc_hash_duplicates()
                    self.ui.hash("%s" % hash)
                    for filename in files:
                        self.ui.file("%s" % filename)
                        self.ui.inc_file_duplicates()
        self.map = map2


    def get_list_with_files_to_move_keep_master_path(self, master_path, with_subfolders):
        self.ui.info("Start moving duplicates...")
        all_files_to_move = []
        for hash, files in self.map.items():
            if len(files) > 1:
                files_to_move = None
                for filename in files:
                    if with_subfolders:
                        match = filename.startswith(master_path)
                    else:
                        p = os.path.dirname(filename)
                        match = (p == master_path) # found master file to keep
                    if match:
                        if not files_to_move:
                            files_to_move = list(files)
                        files_to_move.remove(filename)
                if files_to_move:
                    all_files_to_move.extend(files_to_move)
                        
        return all_files_to_move
        