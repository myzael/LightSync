#!/usr/bin/env python

# Backup files - As published in Python Cookbook
# by O'Reilly with some bug-fixes.

# Credit: Anand Pillai, Tiago Henriques, Mario Ruggier
import sys,os, shutil, filecmp

MAXVERSIONS=100
BAKFOLDER = '.bak'

def restore_files(tree_top, bakdir_name=BAKFOLDER):
    top_dir = os.path.basename(tree_top)
    tree_top += os.sep
    
    for dir, subdirs, files in os.walk(tree_top):

        if os.path.isabs(bakdir_name):
            relpath = dir.replace(tree_top,'')
            backup_dir = os.path.join(bakdir_name, top_dir, relpath)
        else:
            backup_dir = os.path.join(dir, bakdir_name)

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        print 'Restoring files in: ' + backup_dir 
        # To avoid recursing into sub-directories
        subdirs[:] = [d for d in subdirs if d != bakdir_name]
        for f in files:
            filepath = os.path.join(dir, f)
            destpath = os.path.join(backup_dir, f)
            try:
                if not os.path.exists(destpath):
                    print 'Copying %s to %s...' % (filepath, destpath)
                    shutil.copy(filepath, destpath)
            except (OSError, IOError), e:
                pass        
        backups_dirs = os.listdir(backup_dir)
        filesys_dirs = os.listdir(dir)
        if(len(filesys_dirs) < len(backups_dirs)):
            to_remove = set(backups_dirs).difference(set(filesys_dirs))
            for rm_file in [os.path.join(backup_dir, x) for x in to_remove]:
                if os.path.isdir(rm_file):
                    try:
                        print "Removing folder: " + str(rm_file)
                        shutil.rmtree(rm_file)
                    except (OSError, IOError), e:
                        print e
                        pass
                elif os.path.isfile(rm_file):
                    print "Removing file: " + str(rm_file)
                    os.unlink(rm_file)

def backup_files(tree_top, bakdir_name=BAKFOLDER):
    
    top_dir = os.path.basename(tree_top)
    tree_top += os.sep
    
    for dir, subdirs, files in os.walk(tree_top):
        
        if os.path.isabs(bakdir_name):
            relpath = dir.replace(tree_top,'')
            backup_dir = os.path.join(bakdir_name, top_dir, relpath)
        else:
            backup_dir = os.path.join(dir, bakdir_name)

        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # To avoid recursing into sub-directories
        subdirs[:] = [d for d in subdirs if d != bakdir_name]
        for f in files:
            filepath = os.path.join(dir, f)
            destpath = os.path.join(backup_dir, f)
            
            if os.path.exists(destpath):
                if os.path.isfile(destpath) and filecmp.cmp(destpath, filepath, shallow=False):
                    continue
            try:
                print 'Copying %s to %s...' % (filepath, destpath)
                shutil.copy(filepath, destpath)
            except (OSError, IOError), e:
                print e
                pass
        backups_dirs = os.listdir(backup_dir)
        filesys_dirs = os.listdir(dir)
        if(len(filesys_dirs) < len(backups_dirs)):
            to_remove = set(backups_dirs).difference(set(filesys_dirs))
            for rm_file in [os.path.join(backup_dir, x) for x in to_remove]:
                if os.path.isdir(rm_file):
                    try:
                        print "Removing folder: " + str(rm_file)
                        shutil.rmtree(rm_file)
                    except (OSError, IOError), e:
                        print e
                        pass
                elif os.path.isfile(rm_file):
                    print "Removing file: " + str(rm_file)
                    os.unlink(rm_file)

if __name__=="__main__":
    if len(sys.argv)<2:
        sys.exit("Usage: %s [directory] [backup directory]" % sys.argv[0])
        
    tree_top = os.path.abspath(os.path.expanduser(os.path.expandvars(sys.argv[1])))
    
    if len(sys.argv)>=3:
        bakfolder = os.path.abspath(os.path.expanduser(os.path.expandvars(sys.argv[2])))
    else:
        bakfolder = BAKFOLDER
        
    if os.path.isdir(tree_top):
        backup_files(tree_top, bakfolder)
