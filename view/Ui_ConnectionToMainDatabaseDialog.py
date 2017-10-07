# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ConnectionToMainDatabaseDialog.ui'
#
# Created: Wed Aug 20 09:15:02 2014
#      by: PyQt4 UI code generator 4.9.6
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

class Ui_ConnectionToMainDatabaseDialog(object):
    def setupUi(self, ConnectionToMainDatabaseDialog):
        ConnectionToMainDatabaseDialog.setObjectName(_fromUtf8("ConnectionToMainDatabaseDialog"))
        ConnectionToMainDatabaseDialog.resize(320, 310)
        ConnectionToMainDatabaseDialog.setMinimumSize(QtCore.QSize(320, 310))
        ConnectionToMainDatabaseDialog.setMaximumSize(QtCore.QSize(320, 310))
        ConnectionToMainDatabaseDialog.setBaseSize(QtCore.QSize(320, 310))
        self.server_name_edit = QtGui.QLineEdit(ConnectionToMainDatabaseDialog)
        self.server_name_edit.setGeometry(QtCore.QRect(60, 60, 200, 20))
        self.server_name_edit.setObjectName(_fromUtf8("server_name_edit"))
        self.port_edit = QtGui.QLineEdit(ConnectionToMainDatabaseDialog)
        self.port_edit.setGeometry(QtCore.QRect(60, 110, 200, 20))
        self.port_edit.setObjectName(_fromUtf8("port_edit"))
        self.database_edit = QtGui.QLineEdit(ConnectionToMainDatabaseDialog)
        self.database_edit.setGeometry(QtCore.QRect(60, 160, 200, 20))
        self.database_edit.setObjectName(_fromUtf8("database_edit"))
        self.user_name_edit = QtGui.QLineEdit(ConnectionToMainDatabaseDialog)
        self.user_name_edit.setGeometry(QtCore.QRect(60, 210, 200, 20))
        self.user_name_edit.setObjectName(_fromUtf8("user_name_edit"))
        self.label = QtGui.QLabel(ConnectionToMainDatabaseDialog)
        self.label.setGeometry(QtCore.QRect(60, 40, 200, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(ConnectionToMainDatabaseDialog)
        self.label_2.setGeometry(QtCore.QRect(60, 90, 200, 17))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(ConnectionToMainDatabaseDialog)
        self.label_3.setGeometry(QtCore.QRect(60, 140, 200, 17))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_4 = QtGui.QLabel(ConnectionToMainDatabaseDialog)
        self.label_4.setGeometry(QtCore.QRect(60, 190, 200, 17))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.ok_button = QtGui.QPushButton(ConnectionToMainDatabaseDialog)
        self.ok_button.setGeometry(QtCore.QRect(153, 260, 70, 23))
        self.ok_button.setObjectName(_fromUtf8("ok_button"))
        self.cancel_button = QtGui.QPushButton(ConnectionToMainDatabaseDialog)
        self.cancel_button.setGeometry(QtCore.QRect(230, 260, 70, 23))
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.line = QtGui.QFrame(ConnectionToMainDatabaseDialog)
        self.line.setGeometry(QtCore.QRect(0, 20, 321, 20))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.line_2 = QtGui.QFrame(ConnectionToMainDatabaseDialog)
        self.line_2.setGeometry(QtCore.QRect(0, 290, 321, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.label_5 = QtGui.QLabel(ConnectionToMainDatabaseDialog)
        self.label_5.setGeometry(QtCore.QRect(10, 10, 371, 17))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.help_button = QtGui.QPushButton(ConnectionToMainDatabaseDialog)
        self.help_button.setGeometry(QtCore.QRect(110, 260, 30, 23))
        self.help_button.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/help_button.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.help_button.setIcon(icon)
        self.help_button.setObjectName(_fromUtf8("help_button"))

        self.retranslateUi(ConnectionToMainDatabaseDialog)
        QtCore.QMetaObject.connectSlotsByName(ConnectionToMainDatabaseDialog)
        ConnectionToMainDatabaseDialog.setTabOrder(self.server_name_edit, self.port_edit)
        ConnectionToMainDatabaseDialog.setTabOrder(self.port_edit, self.database_edit)
        ConnectionToMainDatabaseDialog.setTabOrder(self.database_edit, self.user_name_edit)
        ConnectionToMainDatabaseDialog.setTabOrder(self.user_name_edit, self.help_button)
        ConnectionToMainDatabaseDialog.setTabOrder(self.help_button, self.ok_button)
        ConnectionToMainDatabaseDialog.setTabOrder(self.ok_button, self.cancel_button)

    def retranslateUi(self, ConnectionToMainDatabaseDialog):
        ConnectionToMainDatabaseDialog.setWindowTitle(_translate("ConnectionToMainDatabaseDialog", "Dialog", None))
        self.label.setText(_translate("ConnectionToMainDatabaseDialog", "Server Name / IP Address", None))
        self.label_2.setText(_translate("ConnectionToMainDatabaseDialog", "Port", None))
        self.label_3.setText(_translate("ConnectionToMainDatabaseDialog", "Database", None))
        self.label_4.setText(_translate("ConnectionToMainDatabaseDialog", "User Name", None))
        self.ok_button.setText(_translate("ConnectionToMainDatabaseDialog", "Ok", None))
        self.cancel_button.setText(_translate("ConnectionToMainDatabaseDialog", "Cancel", None))
        self.label_5.setText(_translate("ConnectionToMainDatabaseDialog", "Connection To Main Database (Working DB)", None))

import resources_rc
