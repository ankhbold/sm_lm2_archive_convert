# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\PdfInsertDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_PdfInsertDialog(object):
    def setupUi(self, PdfInsertDialog):
        PdfInsertDialog.setObjectName(_fromUtf8("PdfInsertDialog"))
        PdfInsertDialog.resize(450, 549)
        self.tabWidget = QtGui.QTabWidget(PdfInsertDialog)
        self.tabWidget.setGeometry(QtCore.QRect(10, 5, 431, 441))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.tableWidget = QtGui.QTableWidget(self.tab_2)
        self.tableWidget.setGeometry(QtCore.QRect(10, 125, 401, 281))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(200)
        self.count = QtGui.QLabel(self.tab_2)
        self.count.setGeometry(QtCore.QRect(65, 101, 91, 16))
        self.count.setObjectName(_fromUtf8("count"))
        self.label_3 = QtGui.QLabel(self.tab_2)
        self.label_3.setGeometry(QtCore.QRect(10, 101, 41, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.select_file_button = QtGui.QPushButton(self.tab_2)
        self.select_file_button.setGeometry(QtCore.QRect(310, 30, 100, 23))
        self.select_file_button.setObjectName(_fromUtf8("select_file_button"))
        self.decision_file_edit = QtGui.QLineEdit(self.tab_2)
        self.decision_file_edit.setGeometry(QtCore.QRect(10, 31, 291, 20))
        self.decision_file_edit.setReadOnly(True)
        self.decision_file_edit.setObjectName(_fromUtf8("decision_file_edit"))
        self.label_4 = QtGui.QLabel(self.tab_2)
        self.label_4.setGeometry(QtCore.QRect(205, 101, 63, 13))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.parcel_count_lbl = QtGui.QLabel(self.tab_2)
        self.parcel_count_lbl.setGeometry(QtCore.QRect(285, 100, 91, 16))
        self.parcel_count_lbl.setObjectName(_fromUtf8("parcel_count_lbl"))
        self.output_file_button = QtGui.QPushButton(self.tab_2)
        self.output_file_button.setGeometry(QtCore.QRect(310, 75, 100, 23))
        self.output_file_button.setObjectName(_fromUtf8("output_file_button"))
        self.output_file_edit = QtGui.QLineEdit(self.tab_2)
        self.output_file_edit.setGeometry(QtCore.QRect(10, 76, 291, 20))
        self.output_file_edit.setReadOnly(True)
        self.output_file_edit.setObjectName(_fromUtf8("output_file_edit"))
        self.label = QtGui.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(10, 57, 291, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.import_button = QtGui.QPushButton(PdfInsertDialog)
        self.import_button.setGeometry(QtCore.QRect(270, 454, 75, 23))
        self.import_button.setObjectName(_fromUtf8("import_button"))
        self.close_button = QtGui.QPushButton(PdfInsertDialog)
        self.close_button.setGeometry(QtCore.QRect(360, 454, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.progressBar = QtGui.QProgressBar(PdfInsertDialog)
        self.progressBar.setGeometry(QtCore.QRect(10, 527, 431, 15))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.label_2 = QtGui.QLabel(PdfInsertDialog)
        self.label_2.setGeometry(QtCore.QRect(20, 39, 291, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.rename_button = QtGui.QPushButton(PdfInsertDialog)
        self.rename_button.setGeometry(QtCore.QRect(180, 454, 75, 23))
        self.rename_button.setObjectName(_fromUtf8("rename_button"))
        self.export_button = QtGui.QPushButton(PdfInsertDialog)
        self.export_button.setGeometry(QtCore.QRect(10, 454, 113, 23))
        self.export_button.setObjectName(_fromUtf8("export_button"))
        self.conver_version_button = QtGui.QPushButton(PdfInsertDialog)
        self.conver_version_button.setGeometry(QtCore.QRect(10, 484, 211, 23))
        self.conver_version_button.setObjectName(_fromUtf8("conver_version_button"))
        self.darkhan_button = QtGui.QPushButton(PdfInsertDialog)
        self.darkhan_button.setGeometry(QtCore.QRect(360, 485, 75, 23))
        self.darkhan_button.setObjectName(_fromUtf8("darkhan_button"))

        self.retranslateUi(PdfInsertDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PdfInsertDialog)

    def retranslateUi(self, PdfInsertDialog):
        PdfInsertDialog.setWindowTitle(_translate("PdfInsertDialog", "Dialog", None))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("PdfInsertDialog", "Name", None))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("PdfInsertDialog", "Description", None))
        self.count.setText(_translate("PdfInsertDialog", "count:", None))
        self.label_3.setText(_translate("PdfInsertDialog", "count:", None))
        self.select_file_button.setText(_translate("PdfInsertDialog", "Select Path", None))
        self.label_4.setText(_translate("PdfInsertDialog", "parcel count:", None))
        self.parcel_count_lbl.setText(_translate("PdfInsertDialog", "count:", None))
        self.output_file_button.setText(_translate("PdfInsertDialog", "Output Path", None))
        self.label.setText(_translate("PdfInsertDialog", "Output path", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PdfInsertDialog", "Insert Pdf", None))
        self.import_button.setText(_translate("PdfInsertDialog", "Import", None))
        self.close_button.setText(_translate("PdfInsertDialog", "Close", None))
        self.label_2.setText(_translate("PdfInsertDialog", "Input path", None))
        self.rename_button.setText(_translate("PdfInsertDialog", "Rename", None))
        self.export_button.setText(_translate("PdfInsertDialog", "Export from database", None))
        self.conver_version_button.setText(_translate("PdfInsertDialog", "convert new version", None))
        self.darkhan_button.setText(_translate("PdfInsertDialog", "Darkhan", None))
