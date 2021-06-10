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