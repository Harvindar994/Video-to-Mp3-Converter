from PyQt5 import QtCore, QtGui, QtWidgets
import os
from PyQt5.QtCore import QObject, QEvent
import clipboard
import time
from moviepy.editor import *
import sys
import pickle

class settings:
    def __init__(self):
        self.filename = 'record.txt'
        self.lastOuputPath = 'c:/'
        self.lastFileLoadingPath = 'c:/'

    def openfile(self, mode='wb'):
        try:
            file = open(self.filename, mode)
        except FileNotFoundError:
            return False
        except FileExistsError:
            return False
        return file

    def closeFile(self, file):
        try:
            file.close()
        except:
            return False
        return True

    def saveSettings(self):
        file = self.openfile()
        if file != False:
            try:
                pickle.dump(self, file)
                self.closeFile(file)
            except:
                return False
            return True
        return False

    def readSettings(self):
        file = self.openfile('rb')
        if file != False:
            try:
                data = pickle.load(file)
                self.lastFileLoadingPath = data.lastFileLoadingPath
                self.lastOuputPath = data.lastOuputPath
                self.closeFile(file)
            except:
                self.lastOuputPath = ''
                self.lastFileLoadingPath = 'c:/'
                return False
            return True
        else:
            self.lastOuputPath = ''
            self.lastFileLoadingPath = 'c:/'
            return False

# Global Data exchanger.
SupportedExtantion = ['mp4',]
FilesList = []
Status = ""
SavePath = ""
TotalLoadedFiles = 0
settingData = settings()
Loadingdilay = 0.04

def getListOfDirWithBasePath(basepath, extantion=SupportedExtantion):
    list = []
    with os.scandir(basepath) as entries:
        for entry in entries:
            filedict = {'file': entry.name,
                        'path': os.path.join(basepath, entry.name)}
            if isFile(filedict['path'], SupportedExtantion):
                list.append(filedict)
    return list