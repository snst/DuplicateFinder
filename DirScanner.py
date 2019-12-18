
import os
import constant

class DirScanner:

    def __init__(self):
        pass

    def scan(self, path):
        self.files = []
        self.dirs = []
        filelist = os.listdir(path)
        for infile in sorted(filelist): 
            filepath = os.path.join(path, infile)
            if os.path.isfile(filepath):
                if infile != constant.HASHFILE:
                    self.files.append(infile)
            else:
                self.dirs.append(infile)      
        pass

    def get_files(self):
        return self.files

    def get_directories(self):
        return self.dirs
