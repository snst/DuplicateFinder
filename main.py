import os
import hashlib
import shutil
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import constant
from HashDb import *
from Logger import *
from DirScanner import *
from DuplicateFinder import *


class HashedFolder:

    def __init__(self, path):
        self.path = path
        self.db = None
        self.child_db_map = {}
        self.dirScanner = DirScanner()
        pass

    def add_subfolder(self, filepath):
        new_db = HashedFolder(filepath)
        self.child_db_map[filepath] = new_db
        return new_db

    def load(self):
        self.dirScanner.scan(self.path)
        self.db = HashDb(self.path, log)
        self.db.load()

        for infile in self.dirScanner.get_directories():
            filepath = os.path.join(self.path, infile)
            db = self.add_subfolder(filepath)
            db.load()

    def get_hash_from_file(self, filename):
        try:
            sha256_hash = hashlib.sha256()
            with open(filename, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except:
            log.info("hash failed for %s" % filename)
            return None

    def scan(self, recursive):
        log.info("Scan: %s" % self.path)
        for infile in self.dirScanner.get_files():
            filepath = os.path.join(self.path, infile)
            hash = self.db.find_filename(infile)
            if None == hash:
                hash = self.get_hash_from_file(filepath)
                log.info("Add: %s : %s" % (str(hash), str(filepath)))
                self.db.add(infile, hash)
            else:
                #print ("Skip: %s : %s" % (str(hash), str(filepath)))
                pass
        self.db.save()
        #print("Finished scan files in %s" % self.path)

        if recursive:
            for childFolder in self.child_db_map.values():
                childFolder.scan(recursive)

        pass

    def find_hash(self, hash):
        path = self.db.find_hash(hash)
        if None != path:
            path = os.path.join(self.db.path, path)
        else:
            for childFolder in self.child_db_map.values():
                path = childFolder.find_hash(hash)
                if None != path:
                    break
        return path

    def find_duplicate_file(self, filepath):
        path = None
        hash = self.get_hash_from_file(filepath)
        if None != hash:
            path = self.find_hash(hash)

        #print("Found %s => %s" % (filepath, path))
        return path


class DuplicateMover:

    def __init__(self, hashedFolder):
        self.hashedFolder = hashedFolder
        pass

    def move_file(self, src, dest, filename):
        os.makedirs(dest, exist_ok=True)
        src_path = os.path.join(src, filename)
        dest_path = os.path.join(dest, filename)
        shutil.move(src_path, dest_path)

    def move_duplicates(self, src_dir, duplicate_dir):
        scanner = DirScanner()
        scanner.scan(src_dir)
        for infile in scanner.get_files():
            filepath = os.path.join(src_dir, infile)
            found_path = self.hashedFolder.find_duplicate_file(filepath)
            if None != found_path:
                log.info("Move %s from %s to %s. Found in %s" %
                         (infile, src_dir, duplicate_dir, found_path))
                self.move_file(src_dir, duplicate_dir, infile)
            else:
                log.info("Keep %s" % filepath)

        for inpath in scanner.get_directories():
            src_path_child = os.path.join(src_dir, inpath)
            dup_path_child = os.path.join(duplicate_dir, inpath)
            self.move_duplicates(src_path_child, dup_path_child)
        pass



def doit():
    checker = HashedFolder(r'C:\data\pictures')
    checker.load()
    checker.scan()
    mover = DuplicateMover(checker)
    #mover.move_duplicates(r'C:\data\test_pic', r'C:\data\test_pic_dup')
    log.info("end")


# doit()

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Duplicate Finder'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.init_ui()
        self.checker = None

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.splitter = QSplitter(Qt.Vertical)

        self.model = QFileSystemModel()
        self.model.setRootPath('')
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.openMenu)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        self.tree.setWindowTitle("Dir View")
        self.tree.resize(800, 600)
        self.tree.setColumnWidth(0, 400)

        self.logger = QPlainTextEdit(self)
        self.logger.setReadOnly(True)

        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(self.logger)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.splitter)
        self.setLayout(windowLayout)

        log.logInfo = self.log
        self.ui = log

        self.show()

    def log(self, msg):
        self.logger.appendPlainText(msg)


    def handle_find_duplicates(self, path):
        finder = DuplicateFinder(log)
        finder.find(self.checker)
        finder.show_duplicates()


    def handleScan(self, path):
        log.info("handleScan: %s" % path)
        self.checker = HashedFolder(path)
        self.checker.load()
        self.checker.scan(False)

    def handleScanRecursive(self, path):
        log.info("handleScanRecursive: %s" % path)

    def openMenu(self, position):

        i = self.tree.currentIndex()
        # print(self.model.filePath(i))
        selectedPath = self.model.filePath(i)

        indexes = self.tree.selectedIndexes()
        if len(indexes) > 0:
            level = 0
            index = indexes[0]
            while index.parent().isValid():
                index = index.parent()
                level += 1

        menu = QMenu()
        menu.addAction("Scan", lambda: self.handleScan(selectedPath))
        menu.addAction("Scan recursive",
                       lambda: self.handleScanRecursive(selectedPath))
        menu.addAction("Find duplicates", lambda: self.handle_find_duplicates(selectedPath))
        menu.exec_(self.tree.viewport().mapToGlobal(position))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
