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

    def setup_Ui(self):
        self.setToolTip(self.file)
        self.setStyleSheet("QFrame{\n"
                           "background-color: #86C2EB;\n"
                           "color: black;\n"
                           "border: 0px solid black;\n"
                           "border-bottom: 2px solid #3C3F41;\n"
                           "border-radius: 3px;\n"
                           "}\n"
                           "QLabel{\n"
                           "border: 0px solid black;\n"
                           "}\n"
                           "QPushButton{\n"
                           "background-color: transparent;\n"
                           "margin-left: 5px;\n"
                           "}")
        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)
        self.filename = QtWidgets.QLabel(self.file)
        self.mainLayout.addWidget(self.filename)
        self.mainLayout.addItem(getHSpacerItem())
        self.indigator = QtWidgets.QPushButton()
        self.mainLayout.addWidget(self.indigator)
        self.delete = QtWidgets.QPushButton()
        self.delete.setCursor(get_QCursor('pointer'))
        clickable(self.delete, self.removeFile, self)
        self.delete.setIcon(getQIcon(self.deleteicon))
        self.mainLayout.addWidget(self.delete)

    def setIndigator(self, indigate = 'tick'):
        if indigate == 'tick':
            self.indigator.setIcon(getQIcon(self.tickicon))
            self.convertedStatus = True
        else:
            self.indigator.setIcon(getQIcon(self.warning))
            self.convertedStatus = None


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    insert_File = QtCore.pyqtSignal(object)
    remove_File = QtCore.pyqtSignal(object)
    progress = QtCore.pyqtSignal(int)
    message = QtCore.pyqtSignal(object)
    hidewidgets = QtCore.pyqtSignal(object)


class BackendThread(QtCore.QRunnable):
    def __init__(self, user_interface):
        super(BackendThread, self).__init__()
        self.ui = user_interface
        self.signals = WorkerSignals()
        self.BackThreadLife = True
        self.SignalsList = []
        self.processingStatus = ""
        self.Sig_LoadFile = 'loadfile'
        self.Sig_Convert = 'convert'
        self.Sig_RemoveAllFile = 'removeAllFile'
        self.Sig_ConvertingProcess = False
        self.Sig_LoadingProcess = False


    @QtCore.pyqtSlot()
    def run(self):
        self.loadApplication()
        self.loadFiles(sys.argv)
        while self.BackThreadLife:
            while True:
                try:
                    signal = self.SignalsList.pop()
                except IndexError:
                    break
                if self.Sig_LoadFile in signal:
                    data = signal[self.Sig_LoadFile]
                    if type(data) == list:
                        self.loadFiles(data)
                if self.Sig_RemoveAllFile in signal:
                    self.removeAllFiles()
                if self.Sig_Convert in signal:
                    self.convert(FilesList)

    def loadApplication(self):
        for percentage in range(0,101):
            self.signals.progress.emit(percentage)
            time.sleep(0.03)
        self.signals.hidewidgets.emit('hide_welcomeScreen')


    def createProcess(self, name, data=None):
        process = {name:data}
        self.SignalsList.insert(0,process)
        
    def loadFiles(self, paths=[]):
        global SupportedExtantion
        self.Sig_LoadingProcess = True
        self.signals.hidewidgets.emit('show_loadingButton')
        for path in paths:
            if self.Sig_LoadingProcess:
                if isDir(path):
                    list = getListOfDirWithBasePath(path, SupportedExtantion)
                    for filedict in list:
                        if self.Sig_LoadingProcess:
                            self.signals.insert_File.emit(filedict)
                            time.sleep(Loadingdilay)
                        else:
                            self.signals.hidewidgets.emit('hide_loadingButton')
                            self.Sig_LoadingProcess = False
                            return False
                elif isFile(path, SupportedExtantion):
                    filedict = {'file': os.path.basename(path),
                                'path': path}
                    self.signals.insert_File.emit(filedict)
                    time.sleep(Loadingdilay)
            else:
                self.signals.hidewidgets.emit('hide_loadingButton')
                self.Sig_LoadingProcess = False
                return False
        self.signals.hidewidgets.emit('hide_loadingButton')
        self.Sig_LoadingProcess = False
        return True