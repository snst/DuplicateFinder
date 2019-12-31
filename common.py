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


def create_duplicate_dest_path(src_path, dest_dir, flat):
    if flat:
        dest_path = os.path.join(dest_dir, os.path.basename(src_path))
    else:
        dest_path = '.' + os.path.splitdrive(src_path)[1]
        dest_path = os.path.join(dest_dir, dest_path)
    return os.path.normpath(dest_path)


def move_file(src_path, dest_path, overwrite, simulate, ui):
    ui.info("Move %s   ==>   %s" % (src_path, dest_path))
    if not simulate:
        try:
            dest_path = os.path.dirname(dest_path)
            if not os.path.exists(dest_path):
                os.makedirs(dest_path, exist_ok=True)

            if not overwrite and os.path.isfile(dest_path):
                dest_path = create_new_filename(dest_path)
                ui.info("Renamed moved file to %s" % dest_path)
                shutil.move(src_path, dest_path)
                ui.inc_moved_renamed()
            else:
                shutil.move(src_path, dest_path)
                ui.inc_moved()
        except:
            ui.error("Failed to move %s to %s" %
                (src_path, dest_path))
            ui.inc_error()
            pass


def open_file(filename):
    subprocess.Popen(r'explorer ' + filename)


def open_folder(filename):
    subprocess.Popen(r'explorer /select, ' + filename)
