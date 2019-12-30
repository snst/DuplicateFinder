import os
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
from Logger import *
from DuplicateFinder import *
from Collector import *
import subprocess

USER_ROLE_HASH = (Qt.UserRole + 1)

class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Duplicate Finder'
        self.left = 50
        self.top = 50
        self.width = 1000
        self.height = 800
        self.init_ui()

    def create_file_model(self):
        model = QFileSystemModel()
        model.setRootPath('')
        return model


    def create_file_tree(self, model):
        tree = QTreeView()
        tree.setModel(model)
        tree.setContextMenuPolicy(Qt.CustomContextMenu)
        #tree.customContextMenuRequested.connect(self.open_tree_menu)
        tree.setAnimated(False)
        tree.setIndentation(20)
        tree.setSortingEnabled(True)
        tree.sortByColumn(0, Qt.AscendingOrder)
        tree.setWindowTitle("Dir View")
        tree.resize(800, 600)
        tree.setColumnWidth(0, 400)
        return tree

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter_file = QSplitter(Qt.Horizontal)

        self.model_l = self.create_file_model()
        self.tree_l = self.create_file_tree(self.model_l)
        self.tree_l.customContextMenuRequested.connect(self.open_menu_left)

        self.model_r = self.create_file_model()
        self.tree_r = self.create_file_tree(self.model_r)
        self.tree_r.customContextMenuRequested.connect(self.open_menu_right)

        self.splitter_file.addWidget(self.tree_l)
        self.splitter_file.addWidget(self.tree_r)

        self.list_output = QListWidget()
        self.list_output.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list_output.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_output.customContextMenuRequested.connect(self.open_log_menu)

        layout_cmd = QHBoxLayout()

        self.checkbox_recursive = QCheckBox("Recursive")
        self.checkbox_recursive.setChecked(True)
        layout_cmd.addWidget(self.checkbox_recursive)

        self.checkbox_flat_move = QCheckBox("Flat move")
        self.checkbox_flat_move.setChecked(False)
        layout_cmd.addWidget(self.checkbox_flat_move)

        self.checkbox_simulate = QCheckBox("Simulate move")
        self.checkbox_simulate.setChecked(False)
        layout_cmd.addWidget(self.checkbox_simulate)

        checkbox_debug = QCheckBox("Debug")
        checkbox_debug.setChecked(False)
        checkbox_debug.stateChanged.connect(lambda:self.handle_debug_checkbox(checkbox_debug))

        layout_cmd.addWidget(checkbox_debug)

        btn = QPushButton("Abort")
        btn.clicked.connect(lambda:self.handle_abort())
        layout_cmd.addWidget(btn)

        btn = QPushButton("Save HashDB")
        btn.clicked.connect(lambda:self.handle_save_modified_hashDB(self))
        layout_cmd.addWidget(btn)

        btn = QPushButton("Clear HashDB (RAM)")
        btn.clicked.connect(lambda:self.handle_clear_hashDB())
        layout_cmd.addWidget(btn)

        btn = QPushButton("Clear Log")
        btn.clicked.connect(lambda:self.handle_clear())
        layout_cmd.addWidget(btn)


        widget_cmd = QWidget()
        widget_cmd.setLayout(layout_cmd)

        grid = QGridLayout()
        
        grid.addWidget(QLabel("Duplicate dir:"), 0, 0)
        self.duplicateDesitinationDirEdit = QLineEdit()#r'E:\_duplicates')
        grid.addWidget(self.duplicateDesitinationDirEdit, 0, 1)

        grid.addWidget(QLabel("Master dir:"), 1, 0)
        self.masterDirEdit = QLineEdit(r'')
        grid.addWidget(self.masterDirEdit, 1, 1)


        layout_bottom = QVBoxLayout()
        w = QWidget()
        w.setLayout(grid)
        layout_bottom.addWidget(w)
        layout_bottom.addWidget(widget_cmd)
        layout_bottom.addWidget(self.list_output)

        bottomWidget = QWidget()
        bottomWidget.setLayout(layout_bottom)


        self.splitter.addWidget(self.splitter_file)
        self.splitter.addWidget(bottomWidget)

        layout_window = QVBoxLayout()
        layout_window.addWidget(self.splitter)
        self.setLayout(layout_window)

        self.ui = logger
        self.collector = Collector(self.ui)
        self.finder = DuplicateFinder(self.collector, self.ui)

        logger.speak.connect(self.log)
        logger.log_hash.connect(self.log_hash)
        logger.log_info.connect(self.log_info)
        logger.log_error.connect(self.log_error)
        logger.log_file.connect(self.log_file)
        logger.enableDebug(checkbox_debug.isChecked())
        self.show()


    @pyqtSlot(str, str)
    def log(self, msg, hash):
        item = QListWidgetItem(msg)
        if hash:
            item.setData(USER_ROLE_HASH, hash)
            pass
        self.list_output.addItem(item)


    @pyqtSlot(str)
    def log_hash(self, str):
        item = QListWidgetItem(str)
        item.setBackground(QColor(150, 255, 50))
#        item.setData(USER_ROLE_HASH, str)
        self.list_output.addItem(item)

    @pyqtSlot(str)
    def log_file(self, str):
        item = QListWidgetItem(str)
        item.setBackground(QColor(200, 230, 255))
        self.list_output.addItem(item)

    @pyqtSlot(str)
    def log_error(self, str):
        item = QListWidgetItem(str)
        item.setBackground(QColor(255, 0, 0))
        self.list_output.addItem(item)


    @pyqtSlot(str)
    def log_info(self, str):
        item = QListWidgetItem(str)
#        item.setBackground(QColor(150, 255, 50))
#        item.setData(USER_ROLE_HASH, str)
        self.list_output.addItem(item)



    def handle_clear(self):
        self.list_output.clear()


    def handle_debug_checkbox(self, checkbox):
        logger.enableDebug(checkbox.isChecked())


    def get_selected_filename_from_finder(self):
        filenames = []
        items = self.list_output.selectedItems()
        if items:
            for item in items:
                txt = item.text()
                if os.path.isfile(txt):
                    filenames.append(txt)
        return filenames


    def handle_set_master_dir(self, filename):
        str = os.path.dirname(filename) + os.sep
        self.masterDirEdit.setText(str)


    def handle_keep_files_in_this_folder_move_duplicates(self, filename):
        self.ui.reset()
        master_dir = os.path.dirname(filename)
        dest_dir = self.get_mover_dest_dir()
        if None != master_dir and None != dest_dir:
            self.finder.move_duplicates_with_master_dir(master_dir, dest_dir, self.is_simulation())


    def handle_open_files(self, filenames):
        for filename in filenames:
            common.open_file(filename)


    def handle_open_folders(self, filenames):
        for filename in filenames:
            common.open_folder(filename)


    def handle_move_files(self, filenames, moveFlat):
        self.ui.reset()
        for filename in filenames:
            destFilepath = common.create_duplicate_dest_path(filename, self.get_mover_dest_dir(), moveFlat)
            common.move_file(filename, destFilepath, False, self.is_simulation(), self.ui)


    def handle_save_modified_hashDB(self, a):
        self.ui.reset()
        self.collector.save_hashes()
        pass


    def is_simulation(self):
        return self.checkbox_simulate.isChecked()


    def is_recursive(self):
        return self.checkbox_recursive.isChecked()


    def is_flat_move(self):
        return self.checkbox_flat_move.isChecked()


    def handle_find_duplicates_in_folder(self, path):
        self.ui.reset()
        self.finder.find_and_show_duplicates_in_folder(path)


    def set_default_dest_dir(self, path):
        dest = self.duplicateDesitinationDirEdit.text()
        if not dest:
            dest = os.path.normpath(os.path.join(os.path.splitdrive(path)[0], os.sep + "_duplicates"))
            self.duplicateDesitinationDirEdit.setText(dest)


    def handle_collector_process_dir(self, path, recursive, cmd):
        self.set_default_dest_dir(path)
        self.ui.reset()
        self.collector.add_dir(path, recursive = recursive, cmd = cmd, duplicate_db = self.finder.db, skipExisting = True)


    def handle_find_duplicates_in_hashDB(self, path):
        self.ui.reset()
        self.finder.find_and_show_duplicates_in_hashDB(path)


    def handle_clear_hashDB(self):
        self.ui.reset()
        self.collector.clear()


    def handle_abort(self):
        self.ui.info("Aborting operation")
        self.ui.abort()


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
        self.ui.reset()
        self.collector.find_extern_duplicates(srcDir = srcDir, recursive=recursive, simulate=self.is_simulation())


    def handle_find_duplicate_file_in_hashDB_and_show_infobox(self, filename):
        if os.path.isfile(filename):
            hash = common.get_hash_from_file(filename, self.ui)
            found_files = self.collector.find_hash_all(hash)
            if len(found_files):
                str = ""
                for found_file in found_files:
                    str = str + found_file + "\n"

                btn = QMessageBox.question(self, 'Open folder?', "Found hash\n\n%s\n\nin\n\n%s" % (hash, str), QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if btn == QMessageBox.No:
                    return
                else:
                    common.open_folder(found_files[0])
            else:
                QMessageBox.information(self, 'Info', 'Hash not found in HashDB:\n\n%s' % hash)
                pass


    def open_log_menu(self, position):
        menu = QMenu()
        menu.addAction("Clear", lambda: self.handle_clear())
        filenames = self.get_selected_filename_from_finder()
        if len(filenames):
            menu.addAction("Set master dir", lambda: self.handle_set_master_dir(filenames[0]))
            menu.addAction("Find file in HashDB", lambda: self.handle_find_duplicate_file_in_hashDB_and_show_infobox(filenames[0]))
            menu.addAction("Open", lambda: self.handle_open_files(filenames))
            menu.addAction("Open folder", lambda: self.handle_open_folders(filenames))
            menu.addAction("Move selected files", lambda: self.handle_move_files(filenames, self.is_flat_move()))
            menu.addAction("Keep files in this folder, move other duplicates", lambda: self.handle_keep_files_in_this_folder_move_duplicates(filenames[0]))

        menu.exec_(self.list_output.viewport().mapToGlobal(position))


    def handle_enable_dir_hashing(self, filename, enable):
        if enable:
            os.remove(filename)
        else:
            open(filename, 'a')


    def add_hashes_option_to_menu(self, menu, path):
        if os.path.isdir(path):
            filename = os.path.join(path, constant.NOHASHFILE)
            if os.path.exists(filename):
                menu.addAction("Include dir in HashDB", lambda: self.handle_enable_dir_hashing(filename, True))
            else:
                menu.addAction("Exclude dir from HashDB", lambda: self.handle_enable_dir_hashing(filename, False))

    def open_tree_menu(self, tree, position):
        i = tree.currentIndex()
        selectedPath = os.path.normpath(self.model_l.filePath(i))
        menu = QMenu()
        menu.addAction("Load HashDB", lambda: self.handle_collector_process_dir(selectedPath, recursive = self.is_recursive(), cmd = CollectorCmd.load))
        menu.addAction("Scan dir", lambda: self.handle_collector_process_dir(selectedPath, recursive = self.is_recursive(), cmd = CollectorCmd.scan))
        menu.addAction("Verify hashes", lambda: self.handle_collector_process_dir(selectedPath, recursive = self.is_recursive(), cmd = CollectorCmd.verify))
        menu.addAction("Scan extern dir for duplicates in HashDB", lambda: self.handle_find_extern_duplicates(selectedPath, recursive = self.is_recursive()))
        menu.addAction("Find duplicates in HashDB", lambda: self.handle_find_duplicates_in_hashDB(selectedPath))
        menu.addSeparator()
        self.add_hashes_option_to_menu(menu, selectedPath)
        menu.addAction("Set duplicates dest dir", lambda: self.handle_set_mover_dest_dir(selectedPath))
        menu.addAction("Scan extern dir for duplicates (no HashDB)", lambda: self.handle_find_duplicates_in_folder(selectedPath))
        menu.addAction("Open", lambda: self.handle_open_files([selectedPath]))
        menu.exec_(tree.viewport().mapToGlobal(position))


    def open_menu_left(self, position):
        self.open_tree_menu(self.tree_l, position)


    def open_menu_right(self, position):
        self.open_tree_menu(self.tree_r, position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
