'''
Created on 04-04-2012

please use this as sudo python main_app

@author: pita
'''

import pyinotify
from os import path, listdir
from time import sleep
from recipie import backup_files
import sys
from PyQt4 import QtGui, QtCore


def parseConfig(conf_path):
    with open(conf_path) as f:
        for line in f:
            yield line.strip()

class MyEventHandler(pyinotify.ProcessEvent):
    def __init__(self,icon):
        pyinotify.ProcessEvent.__init__(self)
        self.icon = icon
    def process_IN_CREATE(self, event):
        if path.isdir(event.pathname):
            print "Mounted new drive:", path.basename(event.pathname)
            self.icon.show_message("Mounted new drive:", str(path.basename(event.pathname)))
            
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
                self.icon.show_message("Great!", "Mounted drive is LightSync backup drive")
                #try:
                #    mode = int(raw_input('Choose:\n1. Backup files\n2. Restore file\n'))
                #except ValueError:
                #    print "Not a number"
                #e = Example()
                #mode = e.result
                msgBox = QtGui.QMessageBox()
                msgBox.setWindowTitle('Choose action')
                msgBox.setText('Do you want to backup or restore?')
                btnB   = QtGui.QPushButton('Backup')
                msgBox.addButton(btnB, QtGui.QMessageBox.YesRole)
                btnR   = QtGui.QPushButton('Restore')
                msgBox.addButton(btnR, QtGui.QMessageBox.NoRole)
                btnC   = QtGui.QPushButton('Cancel')
                msgBox.addButton(btnC, QtGui.QMessageBox.RejectRole)
                msgBox.exec_()                

            if msgBox.clickedButton() == btnB:
                # get list of catalogs to backup
                for bkup_f in parseConfig(path.join(event.pathname, l[0])):
                    backup_files(bkup_f, path.join(event.pathname, 'LighSyncBackup'))
                print 'backup complete...'
                self.icon.show_message('Completed','Backup complete!')

            elif msgBox.clickedButton() == btnR:
                msgBox2 = QtGui.QMessageBox()
                msgBox2.setWindowTitle('Choose backup path')
                msgBox2.setText('Do you want to choose the backup path or use the default one?')
                btnC   = QtGui.QPushButton('Choose')
                msgBox2.addButton(btnC, QtGui.QMessageBox.YesRole)
                btnD   = QtGui.QPushButton('Default')
                msgBox2.addButton(btnD, QtGui.QMessageBox.NoRole)
                msgBox2.exec_()
                
                if msgBox2.clickedButton() == btnC:
                    restore_path = str(QtGui.QFileDialog.getExistingDirectory(None,"Select Directory"))
                dialog = QtGui.QDialog()
                dialog.setWindowTitle("Things to restore")

                grid = QtGui.QGridLayout()
                grid.setSpacing(10)
                    
                listW = QtGui.QListWidget()
                if msgBox2.clickedButton() == btnC:
                    files = listdir(path.join(event.pathname, 'LighSyncBackup'))
                elif msgBox2.clickedButton() == btnD:
                    files = parseConfig(path.join(event.pathname, l[0]))
                print files
                for restr_f in files:
                    item = QtGui.QListWidgetItem(restr_f)
                    item.setCheckState(QtCore.Qt.Checked)
                    listW.addItem(item)

                ok = QtGui.QPushButton("Restore selected")

                if msgBox2.clickedButton() == btnC:
                    ok.clicked.connect(lambda: do_restore1(getCheckedItems(listW), dialog, event.pathname, restore_path))
                elif msgBox2.clickedButton() == btnD:
                    ok.clicked.connect(lambda: do_restore2(getCheckedItems(listW), dialog, event.pathname))

                grid.addWidget(listW,0,0,4,7)
                grid.addWidget(ok,5,3)

                dialog.setLayout(grid)

                dialog.resize(300,180)
                dialog.exec_()
                    
                    #for restr_f in listdir(path.join(event.pathname, 'LighSyncBackup')):
                        #backup_files(path.join(event.pathname, 'LighSyncBackup', restr_f), restore_path)
                    
                    #for restr_f in parseConfig(path.join(event.pathname, l[0])):
                        #backup_files(path.join(event.pathname, 'LighSyncBackup', path.split(restr_f)[-1]), path.dirname(restr_f))

#restore_path = raw_input('Enter path to restore backup or type \"default\" to choose previous locations:\n')
#                    if restore_path == "default" : 
                #for restr_f in parseConfig(path.join(event.pathname, l[0])):
               #     backup_files(path.join(event.pathname, 'LighSyncBackup', path.split(restr_f)[-1]), path.dirname(restr_f))
                #else: 
        #            for restr_f in listdir(path.join(event.pathname, 'LighSyncBackup')):
        #                backup_files(path.join(event.pathname, 'LighSyncBackup', restr_f), restore_path)

                print "Restoring files complete"
                self.icon.show_message('Completed','Restore complete!')

def do_restore1(files,dialog,lPath,rPath):
    for f in files:
        print f
        backup_files(path.join(lPath,'LighSyncBackup',f), rPath)
    dialog.accept()

def do_restore2(files,dialog,lPath):
    for f in files:
        print f
        backup_files(path.join(lPath,'LighSyncBackup',path.split(f)[-1]), path.dirname(f))
    dialog.accept()
    

def getCheckedItems(l):
    for i in range(l.count()):
        if l.item(i).checkState() == QtCore.Qt.Checked:
            yield str(l.item(i).text())


class SystemTrayIcon(QtGui.QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        QtGui.QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QtGui.QMenu(parent)
        exitAction = self.menu.addAction("Exit")
        exitAction.triggered.connect(QtGui.qApp.quit)
        self.setContextMenu(self.menu)
        
    def show_message(self,title,content):
        QtCore.QTimer.singleShot(10, (lambda: self.showMessage(title,content)))
    def show(self):
        QtGui.QSystemTrayIcon.show(self)
        self.show_message('Hello','This is LightSync')
            
def main():
    app = QtGui.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    style = app.style()
    icon = QtGui.QIcon(style.standardPixmap(QtGui.QStyle.SP_DriveHDIcon))
    trayIcon = SystemTrayIcon(icon)

    if len(sys.argv) == 2:
        with open(sys.argv[1]) as conf_file:
            for line in conf_file:
                MOUNT_DRIVE = line.strip()
    else:
        MOUNT_DRIVE = '/media/' 
    wm = pyinotify.WatchManager()
    wm.add_watch(MOUNT_DRIVE, pyinotify.ALL_EVENTS, rec=False)

    # event handler
    eh = MyEventHandler(trayIcon)

    # notifier
    notifier = pyinotify.Notifier(wm, eh,timeout=10)

    # notifier.loop()
    # notifier.run()

    timer = QtCore.QTimer()
    QtCore.QObject.connect(timer, QtCore.SIGNAL("timeout()"), (lambda: quick_check(notifier)))
    timer.start(100)

    trayIcon.show()
    
    app.exec_()
    #sys.exit(app.exec_())

def quick_check(notifier):
    assert notifier._timeout is not None, 'Notifier must be constructed with a short timeout'
    notifier.process_events()
    while notifier.check_events():  #loop in case more events appear while we are processing
        notifier.read_events()
        notifier.process_events()

if __name__ == '__main__':
    main()
