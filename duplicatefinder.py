from Collector import *


class DuplicateFinder:

    def __init__(self, ui):
        self.map = {}
        self.ui = ui
        pass

    def add_hash(self, hash, filepath):
        value = self.map.get(hash)
        if None == value:
            self.map[hash] = [filepath]
        else:
            self.map[hash].append(filepath)
            #print("\n=%s\n=%s" % (filepath, value))
        return value

    def find_duplicates(self, collector):
        if None == collector:
            self.ui.error("First scan folder")
        else:
            for path, db in collector.map.items():
                for hash, name in db.map.items():
                    filepath = os.path.join(db.path, name)
                    self.add_hash(hash, filepath)

    def show_duplicates(self):
        self.ui.info("\nFound duplicates:")
        for hash, files in self.map.items():
            if len(files) > 1:
                self.ui.info("\n%s" % hash)
                for filename in files:
                    self.ui.info("%s" % filename)
