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

def isDir(path):
    if os.path.isdir(path):
        return True
    return False

def getExtantion(file):
    lenth = len(file) - 1
    while file[lenth] != '.' and lenth >= 0:
        lenth -= 1
    extantion = file[lenth+1::]
    return extantion

def getFileName(file):
    lenth = len(file) - 1
    while file[lenth] != '.' and lenth >= 0:
        lenth -= 1
    filename = file[0:lenth]
    return filename

def isFile(path, extantion=SupportedExtantion):
    if os.path.isfile(path):
        if extantion != None:
            ext = getExtantion(path)
            if ext in extantion:
                return True
            else:
                return False
        else:
            return True
    return False

def getVSpaceItem():
    return QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

def getHSpacerItem():
    return QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

def getQIcon(path):
    return QtGui.QIcon(path)

def get_Qpixmap(img):
    return QtGui.QPixmap(img)

def get_QCursor(cursor):
    if cursor == 'pointer':
        return QtCore.Qt.PointingHandCursor

def clickable(widget, function, argument=None):
    class Filter(QObject):
        def setFunctionAndValues(self, Widget, Function, Argument=None):
            self.ObjData = [Widget, Function, Argument]

        def eventFilter(self, obj, event):
            if obj == self.ObjData[0]:
                if event.type() == QEvent.MouseButtonRelease:
                    if obj.rect().contains(event.pos()):
                        self.ObjData[1](self.ObjData[2]) if self.ObjData[2] is not None else self.ObjData[1]()
                        # The developer can opt for .emit(obj) to get the object within the slot.
                        return True
            return False

    filter = Filter(widget)
    filter.setFunctionAndValues(widget, function, argument)
    widget.installEventFilter(filter)


def getScrollArea(ElementContainnerPosition = 'up'):
    ScrollArea = QtWidgets.QScrollArea()
    ScrollArea.setWidgetResizable(True)

    GroupBox = QtWidgets.QGroupBox(ScrollArea)
    ScrollArea.setWidget(GroupBox)

    GroupBoxLayout = QtWidgets.QVBoxLayout(GroupBox)
    GroupBox.setLayout(GroupBoxLayout)

    ElementContainnerLayout = QtWidgets.QVBoxLayout(GroupBox)
    if ElementContainnerPosition == 'up':
        GroupBoxLayout.addLayout(ElementContainnerLayout)
        GroupBoxLayout.addItem(getVSpaceItem())
    else:
        GroupBoxLayout.addItem(getVSpaceItem())
        GroupBoxLayout.addLayout(ElementContainnerLayout)

    return [ScrollArea, GroupBox, GroupBoxLayout, ElementContainnerLayout]



class Files(QtWidgets.QFrame):
    def __init__(self, filename, path, RemoveFile):
        super(Files, self).__init__()
        self.file = filename
        self.path = path
        self.removeFile = RemoveFile
        self.convertedStatus = False
        self.warning = "Media/warning.png"
        self.deleteicon = "Media/delete.png"
        self.tickicon = "Media/check.png"
        self.setup_Ui()