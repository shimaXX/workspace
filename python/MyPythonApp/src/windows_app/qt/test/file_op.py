# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'file_op.ui'
#
# Created: Wed Aug 20 16:30:53 2014
#      by: PyQt4 UI code generator 4.11.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(436, 165)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.button_open = QtGui.QPushButton(self.centralwidget)
        self.button_open.setGeometry(QtCore.QRect(320, 20, 101, 23))
        self.button_open.setObjectName(_fromUtf8("button_open"))
        self.open_file_path_editor = QtGui.QTextBrowser(self.centralwidget)
        self.open_file_path_editor.setGeometry(QtCore.QRect(20, 20, 291, 21))
        self.open_file_path_editor.setObjectName(_fromUtf8("open_file_path_editor"))
        self.save_file_path_editor = QtGui.QTextBrowser(self.centralwidget)
        self.save_file_path_editor.setGeometry(QtCore.QRect(20, 50, 291, 21))
        self.save_file_path_editor.setObjectName(_fromUtf8("save_file_path_editor"))
        self.button_save = QtGui.QPushButton(self.centralwidget)
        self.button_save.setGeometry(QtCore.QRect(320, 50, 101, 23))
        self.button_save.setObjectName(_fromUtf8("button_save"))
        self.button_calculate = QtGui.QPushButton(self.centralwidget)
        self.button_calculate.setEnabled(False)
        self.button_calculate.setGeometry(QtCore.QRect(20, 90, 75, 23))
        self.button_calculate.setObjectName(_fromUtf8("button_calculate"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 436, 24))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.button_open.setText(_translate("MainWindow", "OpenFileRef", None))
        self.button_save.setText(_translate("MainWindow", "SaveFileRef", None))
        self.button_calculate.setText(_translate("MainWindow", "calculate", None))

