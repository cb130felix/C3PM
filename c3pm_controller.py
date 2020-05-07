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
from PyQt5.QtCore import QObject, pyqtSignal

def open_file(path):
    if platform.system() == "Windows":
        os.startfile(path)
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class c3pm_app:

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

        self.msg = QMessageBox()

    def setSlots(self):
        self.ui.button_searchExportPath.clicked.connect(self.searchExportPath)
        self.ui.checkBox_folderProject.stateChanged.connect(self.checkBox_folderProjectStateChanged)
        self.ui.button_searchMainProject.clicked.connect(self.searchMainProject)
        self.ui.button_searchMergeProject.clicked.connect(self.searchMergeProject)
        self.ui.button_mergeProjects.clicked.connect(self.mergeProjects)
        

    # pyqt slots --------------------------------------------------------


    def test(self):
        print("test")

    

    def checkBox_folderProjectStateChanged(self):
        if self.ui.checkBox_folderProject.isChecked():
            self.ui.lineEdir_fileName.setEnabled(False)
        else:
            self.ui.lineEdir_fileName.setEnabled(True)

    def searchMainProject(self):
        filePath = ""
        fileData = QtWidgets.QFileDialog.getOpenFileName(directory=self.lastDir, filter='*.c3p')
        
        self.lastDir = fileData[0]
        filePath = fileData[0]
        fileName = os.path.basename(filePath).split('.')[0]
        if filePath != "":
            self.ui.lineEdit_mainProject.setText(filePath)
            self.ui.lineEdir_fileName.setText(fileName)

    def searchMergeProject(self):
        filename = ""
        fileData = QtWidgets.QFileDialog.getOpenFileName(directory=self.lastDir, filter='*.c3p')
        
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

            
    def mergeProjects(self):
        
        self.MainWindow.setEnabled(False)
        self.ui.button_mergeProjects.setText("Merging projects, please wait...")

        try:
            c3pm_model.C3PM(self.ui.lineEdit_mainProject.text(), self.ui.lineEdit_mergeProject.text(),
            overwriteFiles=self.ui.checkBox_overwriteFiles.checkState()).packedProject.exportProject(
            export_path=self.ui.lineEdit_exportPath.text(),
            one_file=not self.ui.checkBox_folderProject.checkState(),
            name=self.ui.lineEdir_fileName.text())
            
            self.msg.setWindowTitle("Nice!")
            self.msg.setText("The projects were merged successfully!")
            self.msg.setIcon(QMessageBox.Information)
            self.msg.exec_()
        
            open_file(self.ui.lineEdit_exportPath.text())

        except Exception as e:

            self.msg.setWindowTitle("Oops, we had a problem...")
            self.msg.setText("Not possible to merge the projects.\n\nDetails: \n " + str(e))
            self.msg.setIcon(QMessageBox.Critical)
            self.msg.exec_()
        
        finally:

            self.ui.button_mergeProjects.setText("Merge projects")
            self.MainWindow.setEnabled(True)    
    
        




if __name__ == "__main__":
    c3pm_app().startApp()
