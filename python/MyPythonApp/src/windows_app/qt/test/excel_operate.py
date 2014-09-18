# coding: utf-8

import sys
from PyQt4 import QtCore, QtGui
from file_op import Ui_MainWindow
from get_excel_value import calculate

class StartQT4(QtGui.QMainWindow):
    openfilename = ''
    savefilename = ''
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # here we connect signals with our slots
        QtCore.QObject.connect(self.ui.button_open,QtCore.SIGNAL("clicked()"), self.get_open_file_path)
        QtCore.QObject.connect(self.ui.button_save,QtCore.SIGNAL("clicked()"), self.get_save_file_path)
        QtCore.QObject.connect(self.ui.button_calculate,QtCore.SIGNAL("clicked()"), self.operate)
        
    def get_open_file_path(self):
        fd = QtGui. QFileDialog(self)
        self.openfilename = fd.getOpenFileName()
        self.ui.open_file_path_editor.setText(self.openfilename)
        self.enable_calculate()
        
    def get_save_file_path(self):
        fd = QtGui. QFileDialog(self)
        self.savefilename = fd.getSaveFileName()
        self.ui.save_file_path_editor.setText(self.savefilename)
        self.enable_calculate()
    
    def enable_calculate(self):
        if len(self.openfilename)>0 and len(self.savefilename)>0:
            self.ui.button_calculate.setEnabled(True)
        else:
            self.ui.button_calculate.setEnabled(False)
    
    def operate(self):
        calculate(self.openfilename, self.savefilename)
        message = QtGui.QMessageBox(self)
        message.setText(u'正常終了')
        message.exec_();
        
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())