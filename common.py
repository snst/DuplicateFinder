import os
import hashlib
import constant

def get_hash_from_file(filename, ui):
    try:
        #ui.info("hashing: %s" % filename)
        sha256_hash = hashlib.sha256()
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        ui.info("hash failed for %s" % filename)
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