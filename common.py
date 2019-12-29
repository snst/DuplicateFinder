import os
import hashlib
import constant
import shutil
import subprocess


def get_hash_from_file(filename, ui):
    try:
        #ui.info("hashing: %s" % filename)
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
                if ui.is_abort():
                    return None
        digest = sha256_hash.hexdigest()
        ui.inc_hash()
        return digest
    except:
        ui.info("hash failed for %s" % filename)
        ui.inc_error()
        return None


def get_file_list(path):
    data = []
    filelist = os.listdir(path)
    for item in sorted(filelist): 
        filepath = os.path.join(path, item)
        if os.path.isfile(filepath):
            if item != constant.HASHFILE:
                data.append(item)
    return data


def get_dir_list_absolute(path, recursive):
    data = []
    filelist = os.listdir(path)
    for item in sorted(filelist): 
        filepath = os.path.join(path, item)
        if os.path.isdir(filepath):
            data.append(filepath)
            if recursive:
                childList = get_dir_list_absolute(filepath, True)
                data.extend(childList)

    return data        


def create_new_filename(filepath):
    split_name = os.path.splitext(os.path.basename(filepath))
    filename = split_name[0]
    ext = split_name[1]
    dirname = os.path.dirname(filepath)
    cnt = 0
    newfilepath = filepath
    while os.path.isfile(newfilepath):
        newname = filename + ("_%d" % cnt) + ext
        newfilepath = os.path.join(dirname, newname)
        cnt += 1
    return newfilepath


def create_duplicate_dest_path(srcPath, duplicateDir, flat):
    if flat:
        destPath = os.path.join(duplicateDir, os.path.basename(srcPath))
    else:
        destPath = '.' + os.path.splitdrive(srcPath)[1]
        destPath = os.path.join(duplicateDir, destPath)
    return os.path.normpath(destPath)


def move_file(srcPath, destPath, overwrite, simulate, ui):
    ui.info("Move %s   ==>   %s" % (srcPath, destPath))
    if not simulate:
        try:
            destDir = os.path.dirname(destPath)
            if not os.path.exists(destDir):
                os.makedirs(destDir, exist_ok=True)

            if not overwrite and os.path.isfile(destPath):
                destPath = create_new_filename(destPath)
                ui.info("Renamed moved file to %s" % destPath)
                shutil.move(srcPath, destPath)
                ui.inc_moved_renamed()
            else:
                shutil.move(srcPath, destPath)
                ui.inc_moved()
        except:
            ui.error("Failed to move %s to %s" %
                (srcPath, destPath))
            ui.inc_error()
            pass


def open_file(filename):
    subprocess.Popen(r'explorer ' + filename)


def open_folder(filename):
    subprocess.Popen(r'explorer /select, ' + filename)
