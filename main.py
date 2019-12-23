import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from Logger import *
from DuplicateFinder import *
from Collector import *
import subprocess


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Duplicate Finder'
        self.left = 50
        self.top = 50
        self.width = 1000
        self.height = 800
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
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
        self.tree.sortByColumn(0, Qt.AscendingOrder)


        self.tree.setWindowTitle("Dir View")
        self.tree.resize(800, 600)
        self.tree.setColumnWidth(0, 400)

        self.logEdit = QListWidget()
        self.logEdit.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.logEdit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.logEdit.customContextMenuRequested.connect(self.openFinderMenu)

        cmdLayout = QHBoxLayout()

        self.simulateOnlyCheckbox = QCheckBox("Simulate only")
        self.simulateOnlyCheckbox.setChecked(True)
        cmdLayout.addWidget(self.simulateOnlyCheckbox)

        debugCheckBox = QCheckBox("Debug")
        debugCheckBox.setChecked(False)
        debugCheckBox.stateChanged.connect(lambda:self.handle_debug_checkbox(debugCheckBox))

        cmdLayout.addWidget(debugCheckBox)

        btn = QPushButton("Find duplicates in HashDB")
        btn.clicked.connect(lambda:self.handle_find_duplicates_in_hashes())
        cmdLayout.addWidget(btn)

        btn = QPushButton("Move duplicates in HashDB")
        btn.clicked.connect(lambda:self.handle_move_duplicates_in_hashes())
        cmdLayout.addWidget(btn)

        btn = QPushButton("Save HashDB")
        btn.clicked.connect(lambda:self.handle_save_modified_hashDB(self))
        cmdLayout.addWidget(btn)

        btn = QPushButton("Clear HashDB (RAM)")
        btn.clicked.connect(lambda:self.handle_clear_db())
        cmdLayout.addWidget(btn)

        btn = QPushButton("Clear Log")
        btn.clicked.connect(lambda:self.handle_clear())
        cmdLayout.addWidget(btn)


        cmdWidget = QWidget()
        cmdWidget.setLayout(cmdLayout)

        grid = QGridLayout()
        
        grid.addWidget(QLabel("Duplicate dir:"), 0, 0)
        self.duplicateDesitinationDirEdit = QLineEdit(r'E:\_duplicates')
        grid.addWidget(self.duplicateDesitinationDirEdit, 0, 1)

        grid.addWidget(QLabel("Master dir:"), 1, 0)
        self.masterDirEdit = QLineEdit(r'')
        grid.addWidget(self.masterDirEdit, 1, 1)


        bottomLayout = QVBoxLayout()
        w = QWidget()
        w.setLayout(grid)
        bottomLayout.addWidget(w)
        bottomLayout.addWidget(cmdWidget)
        bottomLayout.addWidget(self.logEdit)

        bottomWidget = QWidget()
        bottomWidget.setLayout(bottomLayout)


        self.splitter.addWidget(self.tree)
        self.splitter.addWidget(bottomWidget)

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.splitter)
        self.setLayout(windowLayout)

        self.ui = logger
        self.collector = Collector(self.ui)
        self.finder = DuplicateFinder(self.collector, self.ui)

        logger.speak.connect(self.log)
        logger.enableDebug(debugCheckBox.isChecked())
        self.show()


    @pyqtSlot(str)
    def log(self, msg):
        #self.logEdit.appendPlainText(msg)
        item = QListWidgetItem(msg)
        self.logEdit.addItem(item)


    def handle_clear(self):
        self.logEdit.clear()


    def handle_debug_checkbox(self, checkbox):
        logger.enableDebug(checkbox.isChecked())


    def get_selected_filename_from_finder(self):
        filenames = []
        items = self.logEdit.selectedItems()
        if items:
            for item in items:
                txt = item.text()
                if os.path.isfile(txt):
                    filenames.append(txt)
        return filenames


    def handle_set_master_dir(self, filename):
        str = os.path.dirname(filename) + os.sep
        self.masterDirEdit.setText(str)


    def handle_open_files(self, filenames):
        for filename in filenames:
            common.open_file(filename)


    def handle_open_folders(self, filenames):
        for filename in filenames:
            common.open_folder(filename)


    def handle_move_files(self, filenames, moveFlat):
        for filename in filenames:
            destFilepath = common.create_duplicate_dest_path(filename, self.get_mover_dest_dir(), moveFlat)
            common.move_file(filename, destFilepath, False, self.is_simulation(), self.ui)


    def handle_save_modified_hashDB(self, a):
        self.collector.save_hashes(False)
        pass


    def is_simulation(self):
        return self.simulateOnlyCheckbox.isChecked()


    def handle_dummy(self, path):
        pass


    def handle_find_duplicates_in_folder(self, path):
        self.finder.find_and_show_duplicates_in_folder(path)


    def handle_collector_add_dir(self, path, recursive, doScan):
        self.ui.info("")
        self.collector.add_dir(path, recursive = recursive, doScan = doScan)


    def handle_find_duplicates_in_hashes(self):
        self.finder.find_and_show_duplicates()


    def handle_clear_db(self):
        self.collector.clear()


    def handle_move_duplicates_in_hashes(self):
        masterDir = self.get_master_dir()
        destDir = self.get_mover_dest_dir()
        if None != masterDir and None != destDir:
            self.finder.find_and_move_duplicates(masterDir, destDir, self.is_simulation())
        pass


    def get_master_dir(self):
        path = self.masterDirEdit.text()
        if not path:
            QMessageBox.information(self, 'Info', 'Master directory is empty.')
            return None
        if not os.path.isdir(path):
            QMessageBox.information(self, 'Error', 'Master directory is invalid.')
            return None
        return os.path.normpath(path)


    def get_mover_dest_dir(self):
        path = self.duplicateDesitinationDirEdit.text()
        if not path:
            QMessageBox.information(self, 'Info', 'Destination directory is empty.')
            return None

        if not os.path.isdir(path):
            buttonReply = QMessageBox.question(self, 'Info', "Directory does not exist. Create it?\n%s" % path, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.No:
                return None
            else:
                os.makedirs(path, exist_ok=True)
                if not os.path.isdir(path):
                    QMessageBox.information(self, 'Error', 'Failed to create destination directory.')
                    return None
        return os.path.normpath(path)


    def handle_set_mover_dest_dir(self, path):
        self.duplicateDesitinationDirEdit.setText(path)
        

    def handle_find_extern_duplicates(self, srcDir, recursive):
        self.collector.find_extern_duplicates(srcDir = srcDir, recursive=recursive, simulate=self.is_simulation())


    def openFinderMenu(self, position):
        menu = QMenu()
        menu.addAction("Clear", lambda: self.handle_clear())
        filenames = self.get_selected_filename_from_finder()
        if len(filenames):
            menu.addAction("Set master dir", lambda: self.handle_set_master_dir(filenames[0]))
            menu.addAction("Open", lambda: self.handle_open_files(filenames))
            menu.addAction("Open folder", lambda: self.handle_open_folders(filenames))
            menu.addAction("Move flat", lambda: self.handle_move_files(filenames, True))
            menu.addAction("Move with path", lambda: self.handle_move_files(filenames, False))
        menu.exec_(self.logEdit.viewport().mapToGlobal(position))


    def openMenu(self, position):

        i = self.tree.currentIndex()
        selectedPath = os.path.normpath(self.model.filePath(i))
        menu = QMenu()
        menu.addAction("Load HashDB (recursively)", lambda: self.handle_collector_add_dir(selectedPath, recursive = True, doScan = False))
        menu.addAction("Scan dir (recursively)", lambda: self.handle_collector_add_dir(selectedPath, recursive = True, doScan = True))
        menu.addAction("Load HashDB", lambda: self.handle_collector_add_dir(selectedPath, recursive = False, doScan = False))
        menu.addAction("Scan dir", lambda: self.handle_collector_add_dir(selectedPath, recursive = False, doScan = True))
        menu.addSeparator()
        menu.addAction("Set duplicates dest dir", lambda: self.handle_set_mover_dest_dir(selectedPath))
        menu.addSeparator()
        menu.addAction("Scan extern dir for duplicates in HashDB", lambda: self.handle_find_extern_duplicates(selectedPath, recursive = False))
        menu.addAction("Scan extern dir for duplicates in HashDB (recursively)", lambda: self.handle_find_extern_duplicates(selectedPath, recursive = True))
        menu.addSeparator()
        menu.addAction("Scan extern dir for duplicates (no HashDB)", lambda: self.handle_find_duplicates_in_folder(selectedPath))
        menu.addSeparator()
        menu.addAction("Open", lambda: self.handle_open_files([selectedPath]))

        menu.exec_(self.tree.viewport().mapToGlobal(position))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
