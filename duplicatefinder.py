import os
import hashlib
import shutil

HASHFILE = "__hashes.txt"

class HashDb:

   def __init__(self, path):
      self.path = path
      self.map = {}
      self.name = os.path.join(self.path, HASHFILE)
      pass

   def add(self, filename, hash):
      self.map[hash] = filename
      pass

   def findHash(self, hash):
      value = self.map.get(hash)
      return value

   def save(self):
      f = open(self.name,'w')
      f.write(str(self.map))
      f.close()

   def load(self):
      try:
         f = open(self.name,'r')
         data = f.read()
         f.close()
         self.map = eval(data)
         print("Found db: ", self.name)
      except FileNotFoundError:
         print("Failed db: ", self.name)
         self.map = {}
      except:
         print("Other error")
         self.map = {}

   def findFilename(self, filename):
      for hash, name in self.map.items():
         if name == filename:
            return hash
      return None


class DirScanner:

   def __init__(self):
      self.path = None
      pass

   def scan(self, path):
      self.path = path
      self.files = []
      self.dirs = []
      filelist = os.listdir(self.path)
      for infile in sorted(filelist): 
         filepath = os.path.join(self.path, infile)
         if os.path.isfile(filepath):
            if infile != HASHFILE:
               self.files.append(infile)
         else:
            self.dirs.append(infile)      
      pass

   def getFiles(self):
      return self.files

   def getDirs(self):
      return self.dirs


class HashedFolder:

   def __init__(self, path):
      self.path = path
      self.db = None
      self.child_db_map = {}
      self.dirScanner = DirScanner()
      pass

   def addSubfolder(self, filepath):
      new_db = HashedFolder(filepath)
      self.child_db_map[filepath] = new_db
      return new_db


   def load(self):
      self.dirScanner.scan(self.path)
      self.db = HashDb(self.path)
      self.db.load()

      for infile in self.dirScanner.getDirs():
         filepath = os.path.join(self.path, infile)
         db = self.addSubfolder(filepath)
         db.load()


   def getHashFromFile(self, filename):
      try:
         sha256_hash = hashlib.sha256()
         with open(filename,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
               sha256_hash.update(byte_block)
         return sha256_hash.hexdigest()
      except:
         print("hash failed for %s" % filename)
         return None

   def scan(self):
      print ("Scan: %s" % self.path)
      for infile in self.dirScanner.getFiles():
         filepath = os.path.join(self.path, infile)
         hash = self.db.findFilename(infile)
         if None == hash:
            hash = self.getHashFromFile(filepath)
            print ("Add: %s : %s" % (str(hash), str(filepath)))
            self.db.add(infile, hash)
         else:
            #print ("Skip: %s : %s" % (str(hash), str(filepath)))
            pass
      self.db.save()
      #print("Finished scan files in %s" % self.path)

      for childFolder in self.child_db_map.values():
         childFolder.scan()

      pass

   def findHash(self, hash):
      path = self.db.findHash(hash)
      if None != path:
         path = os.path.join(self.db.path, path)
      else:
         for childFolder in self.child_db_map.values():
            path = childFolder.findHash(hash)
            if None != path:
               break
      return path


   def findDuplicateFile(self, filepath):
      path = None
      hash = self.getHashFromFile(filepath)
      if None != hash:
         path = self.findHash(hash)

      #print("Found %s => %s" % (filepath, path))
      return path
      


class DuplicateMover:

   def __init__(self, hashedFolder):
      self.hashedFolder = hashedFolder
      pass

   def moveFile(self, src, dest, filename):
      os.makedirs(dest, exist_ok=True)
      src_path = os.path.join(src, filename)
      dest_path = os.path.join(dest, filename)
      shutil.move(src_path, dest_path)

   def moveDuplicates(self, src_dir, duplicate_dir):
      scanner = DirScanner()
      scanner.scan(src_dir)
      for infile in scanner.getFiles():
         filepath = os.path.join(src_dir, infile)
         found_path = self.hashedFolder.findDuplicateFile(filepath)
         if None != found_path:
            print("Move %s from %s to %s. Found in %s" % (infile, src_dir, duplicate_dir, found_path))
            self.moveFile(src_dir, duplicate_dir, infile)
         else:
            print("Keep %s" % filepath)

      for inpath in scanner.getDirs():
         src_path_child = os.path.join(src_dir, inpath)
         dup_path_child = os.path.join(duplicate_dir, inpath)
         self.moveDuplicates(src_path_child, dup_path_child)
      pass


class DuplicateFinder:

   def __init__(self):
      self.map = {}
      pass

   def addHash(self, hash, filepath):
      value = self.map.get(hash)
      if None == value:
         self.map[hash] = [filepath]
      else:
         self.map[hash].append(filepath)
         #print("\n=%s\n=%s" % (filepath, value))
      return value

   def showDuplicates(self):
      for hash, files in self.map.items():
         if len(files) > 1:
            print("\n%s" % hash)
            for filename in files:
               print("%s" % filename)


   def find(self, hashedFolder):
      for hash, name in hashedFolder.db.map.items():
         filepath = os.path.join(hashedFolder.db.path, name)
         self.addHash(hash, filepath)

      for hf in hashedFolder.child_db_map.values():
         self.find(hf)

      self.showDuplicates()
      pass


def doit():
   checker = HashedFolder(r'C:\data\pictures')
   checker.load()
   checker.scan()
   mover = DuplicateMover(checker)
   #mover.moveDuplicates(r'C:\data\test_pic', r'C:\data\test_pic_dup')
   finder = DuplicateFinder()
   finder.find(checker)
   print("end")


doit()