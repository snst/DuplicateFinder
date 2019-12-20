import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from Logger import *
from DuplicateFinder import *
from DuplicateMover import *
from Collector import *


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Duplicate Finder'
        self.left = 50
        self.top = 50
        self.width = 800
        self.height = 600
        self.init_ui()

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
        self.collector = Collector(self.ui)
        self.mover = DuplicateMover(self.ui)
        self.mover_dest_dir = None

        self.show()

    def log(self, msg):
        self.logger.appendPlainText(msg)


    def handle_dummy(self, path):
        pass

    def handle_collector_add_dir(self, path, recursive, doScan):
        self.ui.info("")
        self.collector.add_dir(path, recursive = recursive, doScan = doScan)

    def handle_find_duplicates_in_hashes(self, path):
        finder = DuplicateFinder(self.ui)
        finder.find_duplicates(self.collector)
        finder.show_duplicates()

    def handle_set_mover_dest_dir(self, path):
        self.mover_dest_dir = path

    def handle_move_duplicates(self, srcDir, recursive, simulate):
        self.mover.move_duplicates(self.collector, srcDir = srcDir, duplicateDir=self.mover_dest_dir, recursive=recursive, simulate=simulate)


    def openMenu(self, position):

        i = self.tree.currentIndex()
        selectedPath = self.model.filePath(i)


        menu = QMenu()
        menu.addAction("Load hash", lambda: self.handle_collector_add_dir(selectedPath, recursive = False, doScan = False))
        menu.addAction("Load hash recursive", lambda: self.handle_collector_add_dir(selectedPath, recursive = True, doScan = False))
        menu.addAction("Calc hash", lambda: self.handle_collector_add_dir(selectedPath, recursive = False, doScan = True))
        menu.addAction("Calc hash recursive", lambda: self.handle_collector_add_dir(selectedPath, recursive = True, doScan = True))
        menu.addAction("Find duplicates in hashes", lambda: self.handle_find_duplicates_in_hashes(selectedPath))
        menu.addAction("Find duplicates in dir", lambda: self.handle_find_duplicates_in_hashes(selectedPath))

        menu.addAction("Set move duplicates dest dir", lambda: self.handle_set_mover_dest_dir(selectedPath))
        menu.addAction("Move duplicates", lambda: self.handle_move_duplicates(selectedPath, recursive = False, simulate = False))
        menu.addAction("Move duplicates recursive", lambda: self.handle_move_duplicates(selectedPath, recursive = True, simulate = False))
        menu.addAction("Move duplicates (simulate)", lambda: self.handle_move_duplicates(selectedPath, recursive = False, simulate = True))
        menu.addAction("Move duplicates recursive (simulate)", lambda: self.handle_move_duplicates(selectedPath, recursive = True, simulate = True))

        menu.exec_(self.tree.viewport().mapToGlobal(position))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
