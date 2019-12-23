import common
from Collector import *
from DuplicateFinder import *
from DuplicateMover import *


class Logger2:
    def __init__(self):
        pass
    def error(self, str):
        print(str)
    def info(self, str):
        print(str)
    def debug(self, str):
        print(str)




def test_get_files():
    data = common.get_file_list(path)
    for item in data:
        print("* %s" % item)

def test_get_directories(recursive):
    data = common.get_dir_list_absolute(path, recursive)
    for item in data:
        print("* %s" % item)

                
"""
print("get_file_list")
test_get_files()
print("get_dir_list_absolute")
test_get_directories(False)                
print("get_dir_list_absolute, recursive")
test_get_directories(True)                
"""

"""
collector = Collector(logger)
collector.add_dir(path, recursive = True, doScan = True, skipExisting = True)

finder = DuplicateFinder(logger)
finder.find_duplicates(collector)
finder.show_duplicates()

mover = DuplicateMover(logger)
mover.move_duplicates(collector, r'C:\data\test_pic', r'C:\data\test_pic_dup', simulate=False)
"""

src = r'E:\_aaa\a.jpg'
dest = r'E:\_aaa\b\a.jpg'

"""
f = os.path.splitdrive(file)[1]
filename = os.path.join(dup, f)
dirname = os.path.dirname(filename)
print(filename)
print(dirname)
"""

ui = Logger2()
common.move_file(src, dest, False, False, ui)