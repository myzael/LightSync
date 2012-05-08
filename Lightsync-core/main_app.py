'''
Created on 04-04-2012

please use this as sudo python main_app

@author: pita
'''

import pyinotify
from os import path, listdir
from time import sleep
from recipie import backup_files, restore_files
import sys


def parseConfig(conf_path):
    with open(conf_path) as f:
        for line in f:
            yield line.strip()


class MyEventHandler(pyinotify.ProcessEvent):

    def process_IN_CREATE(self, event):
        if path.isdir(event.pathname):
            print "Mounted new dirve:", path.basename(event.pathname)
            
            # give mounted device time to mount
            sleep(0.5)
            l = [name for name in listdir(event.pathname) if name == '.lightsync']
            i = 0
            
            # if device is empty or big as it didn't mount in moment, wait for some time
            while len(l) == 0 and i < 5:
                sleep(0.3)
                l = [name for name in listdir(event.pathname)]
                i += 1
            
            if len(l) == 1 :
                print "Mounted drive is LightSync backup drive\n"
                try:
                    mode = int(raw_input('Choose:\n1. Backup files\n2. Restore file\n'))
                except ValueError:
                    print "Not a number"
                if mode == 1:
                    # get list of catalogs to backup
                    for bkup_f in parseConfig(path.join(event.pathname, l[0])):
                        backup_files(bkup_f, path.join(event.pathname, 'LighSyncBackup'))
                    print 'backup complete...'
                elif mode == 2:
                    restore_path = raw_input('Enter path to restore backup:\n')
                    for restr_f in listdir(path.join(event.pathname, 'LighSyncBackup')):
                        backup_files(path.join(event.pathname, 'LighSyncBackup', restr_f), restore_path)
                    print "Restoring files complete"
                else:
                    print "wrong number"
  
             
            
def main():
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as conf_file:
            for line in conf_file:
                MOUNT_DRIVE = line.strip()
    else:
        MOUNT_DRIVE = '/media/' 
    wm = pyinotify.WatchManager()
    wm.add_watch(MOUNT_DRIVE, pyinotify.ALL_EVENTS, rec=False)

    # event handler
    eh = MyEventHandler()

    # notifier
    notifier = pyinotify.Notifier(wm, eh)
    notifier.loop()

if __name__ == '__main__':
    main()
