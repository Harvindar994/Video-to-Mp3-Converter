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

    def removeAllFiles(self):
        global FilesList
        while True:
            try:
                file = FilesList.pop()
            except IndexError:
                break
            self.signals.remove_File.emit(file)
        self.ui.removeall.setText('Remove all')

    def getUnconvertedSong(self, files):
        unConverted = []
        for file in files:
            if file.convertedStatus == False:
                unConverted.append(file)
        return unConverted

    def convert(self, videoFiles):
        files = self.getUnconvertedSong(videoFiles)
        TotalFiles = len(files)
        if TotalFiles <= 0 and len(FilesList) > 0:
            self.signals.message.emit(['All song converted', 'All Song already converted into Mp3, Please load new files is you want to convert', QtWidgets.QMessageBox.Ok])
            self.ui.convert.setText('Convert to Mp3')
            return
        elif len(FilesList) <= 0:
            self.signals.message.emit(['No files',
                                       'No files available, please load files to convert.',
                                       QtWidgets.QMessageBox.Ok])
            self.ui.convert.setText('Convert to Mp3')
            return

        TotalConvertedSong = 0
        ProgressBarStepValue = 100/TotalFiles
        ProgressBarValue = 0.0
        self.ui.processname.setText('Converting 0/'+str(TotalFiles))
        self.ui.status.setText('0%')
        self.ui.progressBar.setValue(0)
        self.ui.processname.show()
        self.ui.status.show()
        self.ui.progressBar.show()
        self.Sig_ConvertingProcess = True
        self.ui.convert.setText('Stop converting')
        for file in files:
            if self.Sig_ConvertingProcess:
                outputFile = os.path.join(SavePath, getFileName(file.file) + '.mp3')
                if self.convertIntoMp3(file.path, outputFile):
                    file.setIndigator()
                else:
                    file.setIndigator('warning')
                TotalConvertedSong += 1
                ProgressBarValue += ProgressBarStepValue
                self.signals.progress.emit(int(ProgressBarValue))
                self.ui.processname.setText('Converting '+str(TotalConvertedSong)+'/'+str(TotalLoadedFiles))
        self.ui.processname.hide()
        self.ui.status.hide()
        self.ui.progressBar.hide()
        self.ui.convert.setText('Convert to Mp3')
        self.Sig_ConvertingProcess = False

    def convertIntoMp3(self, filename, outputfile):
        try:
            video = VideoFileClip(filename)
            audio = video.audio
            audio.write_audiofile(outputfile)
        except:
            return False
        return True


class WelcomeScreen(QtWidgets.QFrame):
    def __init__(self):
        super(WelcomeScreen, self).__init__()
        self.setupUi(self)
        self.show()


    def setupUi(self, Form):
        WindowFlag = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowFlags(WindowFlag)
        Form.setObjectName("Form")
        self.setStyleSheet("QFrame{\n"
                           "border: 0px solid Green;\n"
                           "border-bottom: 4px solid #2B2B2B;\n"
                           "background-image: url(media/image/background/wsb.jpg)"
                           "}")
        Form.resize(715, 328)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_2.setContentsMargins(-1, 9, -1, 38)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setStyleSheet("QFrame{\n"
                                 "border: 0px;\n"
                                 "background: transparent;\n"
                                 "}")

        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_4.setContentsMargins(5, 5, 5, 5)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem = QtWidgets.QSpacerItem(664, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.pushButton = QtWidgets.QPushButton(self.frame)
        self.pushButton.setStyleSheet("QPushButton{\n"
"background-color: #3C3F41;\n"
"border: 0px solid gray;\n"
"padding: 5px;\n"
"\n"
"}\n"
"QPushButton:hover{\n"
"background-color: #05B8CC;\n"
"}")
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Media/Image/Icon/close white.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(12, 12))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_4.addWidget(self.pushButton)
        self.verticalLayout_2.addWidget(self.frame)
        spacerItem1 = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 32, -1, -1)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setMaximumSize(QtCore.QSize(117, 117))
        self.label.setText("")
        self.label.setStyleSheet('border: 0px;\n'
                                 'background: transparent;')
        self.label.setPixmap(QtGui.QPixmap("D:/Blog/Brightgoal.in/logo/ddd.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(51)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_2.setStyleSheet("border: 0px;\n"
                                   "background: transparent;\n"
                                   "color: #2b2b2b;")
        self.label_3.setStyleSheet("border: 0px;\n"
                                   "background: transparent;\n"
                                   "color: #2b2b2b")
        font = QtGui.QFont()
        font.setPointSize(18)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        spacerItem5 = QtWidgets.QSpacerItem(20, 71, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem5)
        self.progressBar = QtWidgets.QProgressBar(Form)
        self.progressBar.setMinimumSize(QtCore.QSize(0, 6))
        self.progressBar.setMaximumSize(QtCore.QSize(16777215, 6))
        self.progressBar.setStyleSheet("QProgressBar {\n"
"    border: 0px solid grey;\n"
"    border-radius: 0px;\n"
"}\n"
"\n"
"QProgressBar::chunk {\n"
"    background-color: #41CD52;\n"
"    width: 0.5px;\n"
"}")#05B8CC
        self.progressBar.setProperty("value", 23)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_2.addWidget(self.progressBar)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def set_percentage(self, percentage):
        self.progressBar.setValue(percentage)

    def retranslateUi(self, Form):
        self.pushButton.hide()
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_2.setText(_translate("Form", "Brightgoal"))
        self.label_3.setText(_translate("Form", "Harvindar Singh"))


class Ui_Brightgoal(QtWidgets.QWidget):
    def __init__(self):
        super(Ui_Brightgoal, self).__init__()
        self.setupUi(self)
        self.welcomeScreen = WelcomeScreen()
        self.threadpool = QtCore.QThreadPool()
        self.BackendThread = BackendThread(self)
        self.BackendThread.signals.insert_File.connect(self.insertFile_in_list)
        self.BackendThread.signals.remove_File.connect(self.removeFile)
        self.BackendThread.signals.progress.connect(self.setProgressValue)
        self.BackendThread.signals.message.connect(self.show_message)
        self.BackendThread.signals.hidewidgets.connect(self.hideWedget)
        self.threadpool.start(self.BackendThread)


    def setupUi(self, Brightgoal):
        Brightgoal.setObjectName("Brightgoal")
        Brightgoal.resize(693, 543)
        self.MainVLayout = QtWidgets.QVBoxLayout(Brightgoal)
        self.MainVLayout.setObjectName("MainVLayout")
        self.TopTitleHLyout = QtWidgets.QHBoxLayout()
        self.TopTitleHLyout.setObjectName("TopTitleHLyout")
        self.SoftwareTitle = QtWidgets.QLabel(Brightgoal)
        self.SoftwareTitle.setMaximumSize(QtCore.QSize(16777211, 20))
        self.SoftwareTitle.setObjectName("SoftwareTitle")
        self.TopTitleHLyout.addWidget(self.SoftwareTitle)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.TopTitleHLyout.addItem(spacerItem)
        self.MainVLayout.addLayout(self.TopTitleHLyout)
        self.ScrollAreaFrame = QtWidgets.QFrame(Brightgoal)
        self.ScrollAreaFrame.setMinimumSize(QtCore.QSize(338, 381))
        self.ScrollAreaFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ScrollAreaFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ScrollAreaFrame.setObjectName("ScrollAreaFrame")
        self.MainVLayout.addWidget(self.ScrollAreaFrame)

        '''------------------Making scroll area------------------'''
        self.ScrollAreaFrameLayout = QtWidgets.QVBoxLayout(self.ScrollAreaFrame)
        self.ScrollAreaFrame.setLayout(self.ScrollAreaFrameLayout)
        self.ScrollAreaFrameLayout.setContentsMargins(0, 0, 0, 0)
        self.ScrollAreaFrameLayout.setSpacing(0)

        self.ScrollareaElement = getScrollArea()
        self.ScrollAreaFrameLayout.addWidget(self.ScrollareaElement[0])
        self.ScrollAreaElementContainner = self.ScrollareaElement[3]

        '''-----------------------------------------------'''

        self.ControlAreaFrame = QtWidgets.QFrame(Brightgoal)
        self.ControlAreaFrame.setMaximumSize(QtCore.QSize(16777215, 110))
        self.ControlAreaFrame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.ControlAreaFrame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.ControlAreaFrame.setObjectName("ControlAreaFrame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.ControlAreaFrame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.ControlAreaL1 = QtWidgets.QHBoxLayout()
        self.ControlAreaL1.setObjectName("ControlAreaL1")
        self.browsefiles = QtWidgets.QPushButton(self.ControlAreaFrame)
        self.browsefiles.setObjectName("browsefiles")
        self.ControlAreaL1.addWidget(self.browsefiles)
        self.removeall = QtWidgets.QPushButton(self.ControlAreaFrame)
        self.removeall.setObjectName("removeall")
        self.ControlAreaL1.addWidget(self.removeall)
        self.Stoploading = QtWidgets.QPushButton('Stop loading')
        self.Stoploading.setObjectName('Stop loading')
        self.ControlAreaL1.addWidget(self.Stoploading)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ControlAreaL1.addItem(spacerItem1)
        self.details = QtWidgets.QLabel(self.ControlAreaFrame)
        self.details.setObjectName("details")
        self.ControlAreaL1.addWidget(self.details)
        self.verticalLayout.addLayout(self.ControlAreaL1)
        self.ControlAreaL2 = QtWidgets.QHBoxLayout()
        self.ControlAreaL2.setObjectName("ControlAreaL2")
        self.outputfolder = QtWidgets.QLabel(self.ControlAreaFrame)
        self.outputfolder.setObjectName("outputfolder")
        self.ControlAreaL2.addWidget(self.outputfolder)
        self.lineEdit = QtWidgets.QLineEdit(self.ControlAreaFrame)
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit.setDisabled(True)
        self.lineEdit.setStyleSheet("color: #000000;")
        self.ControlAreaL2.addWidget(self.lineEdit)
        self.select = QtWidgets.QPushButton(self.ControlAreaFrame)
        self.select.setObjectName("select")
        self.ControlAreaL2.addWidget(self.select)
        self.convert = QtWidgets.QPushButton(self.ControlAreaFrame)
        self.convert.setObjectName("convert")
        self.ControlAreaL2.addWidget(self.convert)
        self.verticalLayout.addLayout(self.ControlAreaL2)
        self.ControlAreaL3 = QtWidgets.QHBoxLayout()
        self.ControlAreaL3.setObjectName("ControlAreaL3")
        self.processname = QtWidgets.QLabel(self.ControlAreaFrame)
        self.processname.setObjectName("processname")
        self.ControlAreaL3.addWidget(self.processname)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.ControlAreaL3.addItem(spacerItem2)
        self.status = QtWidgets.QLabel(self.ControlAreaFrame)
        self.status.setObjectName("status")
        self.ControlAreaL3.addWidget(self.status)
        self.verticalLayout.addLayout(self.ControlAreaL3)
        self.progressBar = QtWidgets.QProgressBar(self.ControlAreaFrame)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout.addWidget(self.progressBar)
        self.MainVLayout.addWidget(self.ControlAreaFrame)

        self.retranslateUi(Brightgoal)
        QtCore.QMetaObject.connectSlotsByName(Brightgoal)
        self.connectButton()
        self.processname.hide()
        self.progressBar.hide()
        self.status.hide()
        self.Stoploading.hide()


    def connectButton(self):
        self.browsefiles.clicked.connect(self.BrowseFile)
        self.Stoploading.clicked.connect(self.stopLoadingProcess)
        self.removeall.clicked.connect(self.removeAllFile)
        self.select.clicked.connect(self.selectSavePath)
        self.convert.clicked.connect(self.converttoMp3)


    def hideWedget(self, name):
        if name == 'show_loadingButton':
            self.Stoploading.show()
        elif name == 'hide_loadingButton':
            self.Stoploading.hide()
        elif name == 'hide_welcomeScreen':
            self.welcomeScreen.hide()
            self.show()

    def show_message(self, msg):
        msgBox = QtWidgets.QMessageBox.question(self, msg[0], msg[1], msg[2])


    def setProgressValue(self, value):
        if self.isHidden():
            self.welcomeScreen.progressBar.setValue(value)
        else:
            self.progressBar.setValue(value)
            self.status.setText(str(value)+'%')


    def BrowseFile(self):
        settingData.readSettings()
        frame = QtWidgets.QFileDialog.getOpenFileNames(self, 'Select Video Files', settingData.lastFileLoadingPath, '(*.mp4)')
        if len(frame[0]) > 0:
            path = frame[0][0]
            if not os.path.isdir(path):
                path = os.path.split(path)
                path = path[0]
            settingData.lastFileLoadingPath = path
            settingData.saveSettings()
            self.BackendThread.createProcess(self.BackendThread.Sig_LoadFile, frame[0])

    def converttoMp3(self):
        global SavePath
        if self.convert.text() == 'Please wait':
            return
        if self.convert.text() == 'Stop converting':
            self.BackendThread.Sig_ConvertingProcess = False
            self.convert.setText('Please wait')
            return
        if TotalLoadedFiles > 0:
            if os.path.isdir(SavePath):
                if self.BackendThread.Sig_LoadingProcess and self.convert.text() != 'Conversion active please wait':
                    self.convert.setText('Conversion active please wait')
                    self.BackendThread.createProcess(self.BackendThread.Sig_Convert)
                elif not self.BackendThread.Sig_LoadingProcess and self.convert.text() == 'Convert to Mp3':
                    self.BackendThread.createProcess(self.BackendThread.Sig_Convert)
                else:
                    return
            else:
                msgBox = QtWidgets.QMessageBox.question(self, 'Select Ouput Folder', "No selected output folder. "
                                                        "Do you want to select Output Folder ?")
                if msgBox == QtWidgets.QMessageBox.Yes:
                    self.selectSavePath()
                else:
                    return
        else:
            msgBox = QtWidgets.QMessageBox.question(self, 'No Files', "No loaded File."
                                                    " Do you want to browse files.")
            if msgBox == QtWidgets.QMessageBox.Yes:
                self.BrowseFile()
            else:
                return

    def selectSavePath(self):
        global SavePath
        settingData.readSettings()
        dilog = QtWidgets.QFileDialog(self, 'Video Files', settingData.lastOuputPath, '(*.mp4)')
        dilog.setFileMode(QtWidgets.QFileDialog.Directory)
        if dilog.exec_() == QtWidgets.QDialog.Accepted:
            SavePath = dilog.selectedFiles()[0]
            settingData.lastOuputPath = SavePath
            settingData.saveSettings()
            self.lineEdit.setText(SavePath)

    def retranslateUi(self, Brightgoal):
        global SavePath
        _translate = QtCore.QCoreApplication.translate
        Brightgoal.setWindowTitle(_translate("Brightgoal", "Video to Mp3 Converter"))
        self.SoftwareTitle.setText(_translate("Brightgoal", "Video to Mp3 Converter By Harvindar Singh (www.brightgoal.in)"))
        self.browsefiles.setText(_translate("Brightgoal", "Browse Files"))
        self.removeall.setText(_translate("Brightgoal", "Remove all"))
        self.details.setText(_translate("Brightgoal", "Total Song : 0"))
        self.outputfolder.setText(_translate("Brightgoal", "Output folder"))
        self.select.setText(_translate("Brightgoal", "Select"))
        self.convert.setText(_translate("Brightgoal", "Convert to Mp3"))
        self.processname.setText(_translate("Brightgoal", "Process Name"))
        self.status.setText(_translate("Brightgoal", "Status"))
        settingData.readSettings()
        SavePath = settingData.lastOuputPath
        self.lineEdit.setText(settingData.lastOuputPath)