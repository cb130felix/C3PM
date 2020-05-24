import c3pm_view
import c3pm_model

import sys
import os
import platform
import subprocess
import threading
import time

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from PyQt5.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])



class MergeProjectThread(QThread):

    app = None
    
    def run(self):

        try:
            c3pm_model.C3PM(self.app.ui.lineEdit_mainProject.text(), self.app.ui.lineEdit_mergeProject.text(),
            overwriteFiles=self.app.ui.checkBox_overwriteFiles.checkState(),
            setDefaultFolders=self.app.ui.checkBox_createFolders.checkState()).mergedProject.exportProject(
            export_path=self.app.ui.lineEdit_exportPath.text(),
            one_file=not self.app.ui.checkBox_folderProject.checkState(),
            name=self.app.ui.lineEdir_fileName.text())
            
            open_file(self.app.ui.lineEdit_exportPath.text())

            self.app.msg.setWindowTitle("Nice!")
            self.app.msg.setText("The projects were merged successfully!")
            
            self.mergedSucess = True

        except Exception as e:
                        
            self.app.msg.setWindowTitle("Oops, we had a problem...")
            self.app.msg.setText("Not possible to merge the projects.\n\nDetails: \n " + str(e))

            self.mergedSucess = False



class c3pm_controller:

    version = "version"
    lastDir = ''

    def __init__(self):
        pass

    def startApp(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()

        self.ui = c3pm_view.Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self.setSlots()
        self.startValues()
        
        self.MainWindow.setFixedSize(self.MainWindow.width(), self.MainWindow.height())        
        self.MainWindow.show()
        sys.exit(self.app.exec_())

    def startValues(self):
        self.ui.lineEdit_exportPath.setText(os.path.join(os.getcwd(), "export"))
        self.ui.label_version.setText(self.version)


        self.mergeThread = MergeProjectThread()
        self.mergeThread.app = self
        self.mergeThread.finished.connect(self.finishedMerge)

        self.msg = QMessageBox()


    def setSlots(self):
        self.ui.button_searchExportPath.clicked.connect(self.searchExportPath)
        self.ui.checkBox_folderProject.stateChanged.connect(self.checkBox_folderProjectStateChanged)
        self.ui.button_searchMainProject.clicked.connect(self.searchMainProject)
        self.ui.button_searchMergeProject.clicked.connect(self.searchMergeProject)
        self.ui.button_mergeProjects.clicked.connect(self.mergeProjects)
        

    # pyqt slots --------------------------------------------------------
    def mergeProjects(self):
        
        self.ui.button_mergeProjects.setText("Merging projects, please wait...")
        self.MainWindow.setEnabled(False)
        self.mergeThread.start()

    def finishedMerge(self):
        
        if self.mergeThread.mergedSucess:
            self.msg.setIcon(QMessageBox.Information)
        else:
            self.msg.setIcon(QMessageBox.Critical)

        self.msg.exec_()
        self.MainWindow.setEnabled(True)
        self.ui.button_mergeProjects.setText("Merge projects")

    def test(self):
        print("test")

    

    def checkBox_folderProjectStateChanged(self):
        if self.ui.checkBox_folderProject.isChecked():
            self.ui.lineEdir_fileName.setEnabled(False)
        else:
            self.ui.lineEdir_fileName.setEnabled(True)

    def searchMainProject(self):
        filePath = ""
        fileData = QtWidgets.QFileDialog.getOpenFileName(directory=self.lastDir, filter='*.c3p;*.c3proj')
        
        self.lastDir = fileData[0]
        filePath = fileData[0]
        fileName = os.path.basename(filePath).split('.')[0]
        if filePath != "":
            self.ui.lineEdit_mainProject.setText(filePath)
            self.ui.lineEdir_fileName.setText(fileName)

    def searchMergeProject(self):
        filename = ""
        fileData = QtWidgets.QFileDialog.getOpenFileName(directory=self.lastDir, filter='*.c3p;*.c3proj')
        
        self.lastDir = fileData[0]
        filename = fileData[0]

        if filename != "":
            self.ui.lineEdit_mergeProject.setText(filename)
    
    def searchExportPath(self):
        dirName = ""
        
        dirName = QtWidgets.QFileDialog.getExistingDirectory(directory=self.lastDir)

        self.lastDir = dirName

        if dirName != "":
            self.ui.lineEdit_exportPath.setText(dirName)




if __name__ == "__main__":
    c3pm_controller().startApp()
