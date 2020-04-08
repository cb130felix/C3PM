# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'c3pm.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox
import c3pm

class Ui_MainWindow(object):

    version = '0.3'

    def getInfo(self):
        return "Version: " + self.version + "\nCreated by Relixes"

    def searchC3Pack(self):
        filename = ""
        filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.c3pack')[0]
        if filename != "":
            self.lineEdit_c3pack.setText(filename)
        
    
    def searchProject(self):
        filename = ""
        filename = QtWidgets.QFileDialog.getOpenFileName(filter='*.c3p;*.c3proj')[0]
        if filename != "":
            self.lineEdit_c3project.setText(filename)

    def importPack(self):
        msgBox = QMessageBox()
        overwriteRepeatedFiles = self.checkBox.isChecked()
        result = c3pm.importPack(self.lineEdit_c3pack.text(), self.lineEdit_c3project.text(), True, overwriteRepeatedFiles)
        
        if(result['status'] == 'sucess'):
            msgBox.setWindowTitle("Pack imported!")
            msgBox.setText("The pack was imported into the project sucessfully!")
            msgBox.setIcon(QMessageBox.Information)
            print("Pack imported succesfully")

        else:
            
            msgBox.setWindowTitle("Oops... We had a problem")
            msgBox.setText("Error:\n" + str(result['error']))
            msgBox.setIcon(QMessageBox.Critical)

            print("Error importing pack:")
            print(result['error'])
            
        msgBox.exec_()
        

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(535, 322)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        #labels
        
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(80, 70, 300, 16))
        self.label.setObjectName("label")
        
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(80, 130, 300, 16))
        self.label_2.setObjectName("label_2")
        
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(45, 20, 461, 31))
        font = QtGui.QFont()
        font.setPointSize(24)
        self.label_3.setFont(font)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(400, 240, 100, 41))
        self.label_4.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.label_4.setObjectName("label_4")
        

        #buttons
        self.pushButton_searchPack = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_searchPack.setGeometry(QtCore.QRect(380, 150, 81, 21))
        self.pushButton_searchPack.setObjectName("pushButton_searchPack")
        self.pushButton_searchPack.clicked.connect(self.searchC3Pack)
        
        self.pushButton_searchProject = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_searchProject.setGeometry(QtCore.QRect(380, 90, 81, 21))
        self.pushButton_searchProject.setObjectName("pushButton_searchProject")
        self.pushButton_searchProject.clicked.connect(self.searchProject)
        
        self.pushButton_importPack = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_importPack.setGeometry(QtCore.QRect(140, 210, 241, 41))
        self.pushButton_importPack.setObjectName("pushButton_importPack")
        self.pushButton_importPack.clicked.connect(self.importPack)
        
        
        #check box

        self.checkBox = QtWidgets.QCheckBox(self.centralwidget)
        self.checkBox.setGeometry(QtCore.QRect(80, 180, 501, 17))
        self.checkBox.setObjectName("checkBox")

        
        
        #line edits
        self.lineEdit_c3project = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_c3project.setGeometry(QtCore.QRect(80, 90, 291, 21))
        self.lineEdit_c3project.setObjectName("lineEdit_c3project")
        self.lineEdit_c3pack = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_c3pack.setGeometry(QtCore.QRect(80, 150, 291, 21))
        self.lineEdit_c3pack.setObjectName("lineEdit_c3pack")
        

        MainWindow.setCentralWidget(self.centralwidget)
        

        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 535, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "C3PM"))
        self.pushButton_searchProject.setText(_translate("MainWindow", "Search file"))
        self.pushButton_importPack.setText(_translate("MainWindow", "Apply pack into project"))
        self.label.setText(_translate("MainWindow", "Set the path of Construct 3 project to import pack into"))
        self.pushButton_searchPack.setText(_translate("MainWindow", "Search file"))
        self.label_2.setText(_translate("MainWindow", "Set the path of a C3 Pack file to import into the project"))
        self.label_3.setText(_translate("MainWindow", "Construct 3 Pack Manager"))
        self.label_4.setText(_translate("MainWindow", self.getInfo()))
        self.checkBox.setText(_translate("MainWindow", "Overwrite duplicate files (check this option if you\'re updating a pack for a new version)"))


if __name__ == "__main__":
    print("Starting C3PM...")
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
