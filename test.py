import common
from Collector import *
from DuplicateFinder import *
from DuplicateMover import *
from Logger import *


path = r'C:\data\pictures\stubaital 7.09-10.09.2017'

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

collector = Collector(log)
collector.add_dir(path, recursive = True, doScan = True, skipExisting = True)

finder = DuplicateFinder(log)
finder.find_duplicates(collector)
finder.show_duplicates()

mover = DuplicateMover(log)
mover.move_duplicates(collector, r'C:\data\test_pic', r'C:\data\test_pic_dup', simulate=False)