# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LandTaxPaymentsDialog.ui'
#
# Created: Sun Dec  7 15:34:32 2014
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

class Ui_LandTaxPaymentsDialog(object):
    def setupUi(self, LandTaxPaymentsDialog):
        LandTaxPaymentsDialog.setObjectName(_fromUtf8("LandTaxPaymentsDialog"))
        LandTaxPaymentsDialog.resize(800, 470)
        LandTaxPaymentsDialog.setMinimumSize(QtCore.QSize(800, 470))
        LandTaxPaymentsDialog.setMaximumSize(QtCore.QSize(800, 470))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/lm2/landfeepayment.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        LandTaxPaymentsDialog.setWindowIcon(icon)
        self.tabWidget = QtGui.QTabWidget(LandTaxPaymentsDialog)
        self.tabWidget.setEnabled(True)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 781, 411))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.groupBox_2 = QtGui.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 0, 761, 111))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.record_number_edit = QtGui.QLineEdit(self.groupBox_2)
        self.record_number_edit.setGeometry(QtCore.QRect(20, 40, 216, 20))
        self.record_number_edit.setReadOnly(True)
        self.record_number_edit.setObjectName(_fromUtf8("record_number_edit"))
        self.select_owner_cbox = QtGui.QComboBox(self.groupBox_2)
        self.select_owner_cbox.setGeometry(QtCore.QRect(15, 80, 226, 22))
        self.select_owner_cbox.setObjectName(_fromUtf8("select_owner_cbox"))
        self.label_3 = QtGui.QLabel(self.groupBox_2)
        self.label_3.setGeometry(QtCore.QRect(20, 25, 150, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.label_7 = QtGui.QLabel(self.groupBox_2)
        self.label_7.setGeometry(QtCore.QRect(20, 70, 231, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.label_8 = QtGui.QLabel(self.groupBox_2)
        self.label_8.setGeometry(QtCore.QRect(565, 25, 150, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.label_10 = QtGui.QLabel(self.groupBox_2)
        self.label_10.setGeometry(QtCore.QRect(300, 25, 150, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.record_status_edit = QtGui.QLineEdit(self.groupBox_2)
        self.record_status_edit.setGeometry(QtCore.QRect(565, 40, 176, 20))
        self.record_status_edit.setReadOnly(True)
        self.record_status_edit.setObjectName(_fromUtf8("record_status_edit"))
        self.record_begin_edit = QtGui.QLineEdit(self.groupBox_2)
        self.record_begin_edit.setGeometry(QtCore.QRect(300, 40, 206, 20))
        self.record_begin_edit.setReadOnly(True)
        self.record_begin_edit.setObjectName(_fromUtf8("record_begin_edit"))
        self.grace_period_edit = QtGui.QLineEdit(self.groupBox_2)
        self.grace_period_edit.setGeometry(QtCore.QRect(565, 80, 176, 20))
        self.grace_period_edit.setText(_fromUtf8(""))
        self.grace_period_edit.setReadOnly(True)
        self.grace_period_edit.setObjectName(_fromUtf8("grace_period_edit"))
        self.label_9 = QtGui.QLabel(self.groupBox_2)
        self.label_9.setGeometry(QtCore.QRect(565, 65, 150, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.groupBox_3 = QtGui.QGroupBox(self.tab)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 110, 761, 261))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.groupBox_4 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_4.setGeometry(QtCore.QRect(20, 53, 251, 201))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.tax_per_year_edit = QtGui.QLineEdit(self.groupBox_4)
        self.tax_per_year_edit.setGeometry(QtCore.QRect(20, 40, 180, 20))
        self.tax_per_year_edit.setReadOnly(True)
        self.tax_per_year_edit.setObjectName(_fromUtf8("tax_per_year_edit"))
        self.tax_paid_edit = QtGui.QLineEdit(self.groupBox_4)
        self.tax_paid_edit.setGeometry(QtCore.QRect(20, 80, 180, 20))
        self.tax_paid_edit.setReadOnly(True)
        self.tax_paid_edit.setObjectName(_fromUtf8("tax_paid_edit"))
        self.surplus_from_last_years_edit = QtGui.QLineEdit(self.groupBox_4)
        self.surplus_from_last_years_edit.setGeometry(QtCore.QRect(20, 120, 180, 20))
        self.surplus_from_last_years_edit.setReadOnly(True)
        self.surplus_from_last_years_edit.setObjectName(_fromUtf8("surplus_from_last_years_edit"))
        self.tax_to_pay_edit = QtGui.QLineEdit(self.groupBox_4)
        self.tax_to_pay_edit.setGeometry(QtCore.QRect(20, 160, 180, 20))
        self.tax_to_pay_edit.setReadOnly(True)
        self.tax_to_pay_edit.setObjectName(_fromUtf8("tax_to_pay_edit"))
        self.label_13 = QtGui.QLabel(self.groupBox_4)
        self.label_13.setGeometry(QtCore.QRect(20, 25, 180, 13))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.label_14 = QtGui.QLabel(self.groupBox_4)
        self.label_14.setGeometry(QtCore.QRect(20, 65, 180, 13))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.label_15 = QtGui.QLabel(self.groupBox_4)
        self.label_15.setGeometry(QtCore.QRect(20, 105, 216, 16))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.label_16 = QtGui.QLabel(self.groupBox_4)
        self.label_16.setGeometry(QtCore.QRect(20, 145, 180, 13))
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.groupBox_5 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_5.setGeometry(QtCore.QRect(290, 53, 226, 201))
        self.groupBox_5.setObjectName(_fromUtf8("groupBox_5"))
        self.effective_fine_edit = QtGui.QLineEdit(self.groupBox_5)
        self.effective_fine_edit.setGeometry(QtCore.QRect(20, 80, 180, 20))
        self.effective_fine_edit.setReadOnly(True)
        self.effective_fine_edit.setObjectName(_fromUtf8("effective_fine_edit"))
        self.fine_paid_edit = QtGui.QLineEdit(self.groupBox_5)
        self.fine_paid_edit.setGeometry(QtCore.QRect(20, 120, 180, 20))
        self.fine_paid_edit.setReadOnly(True)
        self.fine_paid_edit.setObjectName(_fromUtf8("fine_paid_edit"))
        self.fine_to_pay_edit = QtGui.QLineEdit(self.groupBox_5)
        self.fine_to_pay_edit.setGeometry(QtCore.QRect(20, 160, 180, 20))
        self.fine_to_pay_edit.setReadOnly(True)
        self.fine_to_pay_edit.setObjectName(_fromUtf8("fine_to_pay_edit"))
        self.label_18 = QtGui.QLabel(self.groupBox_5)
        self.label_18.setGeometry(QtCore.QRect(20, 65, 180, 13))
        self.label_18.setObjectName(_fromUtf8("label_18"))
        self.label_19 = QtGui.QLabel(self.groupBox_5)
        self.label_19.setGeometry(QtCore.QRect(20, 105, 180, 13))
        self.label_19.setObjectName(_fromUtf8("label_19"))
        self.label_20 = QtGui.QLabel(self.groupBox_5)
        self.label_20.setGeometry(QtCore.QRect(20, 145, 180, 13))
        self.label_20.setObjectName(_fromUtf8("label_20"))
        self.potential_fine_edit = QtGui.QLineEdit(self.groupBox_5)
        self.potential_fine_edit.setGeometry(QtCore.QRect(20, 40, 181, 20))
        self.potential_fine_edit.setReadOnly(True)
        self.potential_fine_edit.setObjectName(_fromUtf8("potential_fine_edit"))
        self.label_23 = QtGui.QLabel(self.groupBox_5)
        self.label_23.setGeometry(QtCore.QRect(20, 25, 201, 16))
        self.label_23.setObjectName(_fromUtf8("label_23"))
        self.groupBox_6 = QtGui.QGroupBox(self.groupBox_3)
        self.groupBox_6.setGeometry(QtCore.QRect(540, 52, 201, 201))
        self.groupBox_6.setObjectName(_fromUtf8("groupBox_6"))
        self.quarter_1_check_box = QtGui.QCheckBox(self.groupBox_6)
        self.quarter_1_check_box.setEnabled(False)
        self.quarter_1_check_box.setGeometry(QtCore.QRect(10, 40, 181, 20))
        self.quarter_1_check_box.setObjectName(_fromUtf8("quarter_1_check_box"))
        self.quarter_2_check_box = QtGui.QCheckBox(self.groupBox_6)
        self.quarter_2_check_box.setEnabled(False)
        self.quarter_2_check_box.setGeometry(QtCore.QRect(10, 70, 181, 20))
        self.quarter_2_check_box.setObjectName(_fromUtf8("quarter_2_check_box"))
        self.quarter_3_check_box = QtGui.QCheckBox(self.groupBox_6)
        self.quarter_3_check_box.setEnabled(False)
        self.quarter_3_check_box.setGeometry(QtCore.QRect(10, 100, 181, 20))
        self.quarter_3_check_box.setObjectName(_fromUtf8("quarter_3_check_box"))
        self.quarter_4_check_box = QtGui.QCheckBox(self.groupBox_6)
        self.quarter_4_check_box.setEnabled(False)
        self.quarter_4_check_box.setGeometry(QtCore.QRect(10, 130, 181, 20))
        self.quarter_4_check_box.setObjectName(_fromUtf8("quarter_4_check_box"))
        self.label_11 = QtGui.QLabel(self.groupBox_3)
        self.label_11.setGeometry(QtCore.QRect(40, 20, 150, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.label_22 = QtGui.QLabel(self.groupBox_3)
        self.label_22.setGeometry(QtCore.QRect(545, 20, 150, 16))
        self.label_22.setObjectName(_fromUtf8("label_22"))
        self.payment_frequency_edit = QtGui.QLineEdit(self.groupBox_3)
        self.payment_frequency_edit.setGeometry(QtCore.QRect(545, 33, 176, 20))
        self.payment_frequency_edit.setText(_fromUtf8(""))
        self.payment_frequency_edit.setReadOnly(True)
        self.payment_frequency_edit.setObjectName(_fromUtf8("payment_frequency_edit"))
        self.year_sbox = QtGui.QSpinBox(self.groupBox_3)
        self.year_sbox.setGeometry(QtCore.QRect(40, 35, 186, 24))
        self.year_sbox.setObjectName(_fromUtf8("year_sbox"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.groupBox = QtGui.QGroupBox(self.tab_2)
        self.groupBox.setGeometry(QtCore.QRect(5, 10, 766, 366))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.label_6 = QtGui.QLabel(self.groupBox)
        self.label_6.setGeometry(QtCore.QRect(25, 25, 200, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.label_5 = QtGui.QLabel(self.groupBox)
        self.label_5.setGeometry(QtCore.QRect(490, 25, 277, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.payment_type_cbox = QtGui.QComboBox(self.groupBox)
        self.payment_type_cbox.setGeometry(QtCore.QRect(485, 40, 260, 26))
        self.payment_type_cbox.setObjectName(_fromUtf8("payment_type_cbox"))
        self.register_payment_button = QtGui.QPushButton(self.groupBox)
        self.register_payment_button.setGeometry(QtCore.QRect(640, 70, 106, 23))
        self.register_payment_button.setObjectName(_fromUtf8("register_payment_button"))
        self.payment_date_edit = QtGui.QDateEdit(self.groupBox)
        self.payment_date_edit.setGeometry(QtCore.QRect(24, 40, 196, 26))
        self.payment_date_edit.setCalendarPopup(True)
        self.payment_date_edit.setObjectName(_fromUtf8("payment_date_edit"))
        self.payment_twidget = QtGui.QTableWidget(self.groupBox)
        self.payment_twidget.setGeometry(QtCore.QRect(25, 110, 720, 200))
        self.payment_twidget.setCornerButtonEnabled(True)
        self.payment_twidget.setObjectName(_fromUtf8("payment_twidget"))
        self.payment_twidget.setColumnCount(3)
        self.payment_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.payment_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.payment_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.payment_twidget.setHorizontalHeaderItem(2, item)
        self.payment_twidget.horizontalHeader().setDefaultSectionSize(250)
        self.label_4 = QtGui.QLabel(self.groupBox)
        self.label_4.setGeometry(QtCore.QRect(250, 25, 200, 16))
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_2 = QtGui.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(25, 95, 555, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.amount_paid_sbox = QtGui.QSpinBox(self.groupBox)
        self.amount_paid_sbox.setGeometry(QtCore.QRect(250, 40, 201, 24))
        self.amount_paid_sbox.setObjectName(_fromUtf8("amount_paid_sbox"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.groupBox_7 = QtGui.QGroupBox(self.tab_3)
        self.groupBox_7.setGeometry(QtCore.QRect(5, 10, 766, 366))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.label_12 = QtGui.QLabel(self.groupBox_7)
        self.label_12.setGeometry(QtCore.QRect(25, 25, 200, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.label_24 = QtGui.QLabel(self.groupBox_7)
        self.label_24.setGeometry(QtCore.QRect(490, 25, 277, 16))
        self.label_24.setObjectName(_fromUtf8("label_24"))
        self.fine_payment_type_cbox = QtGui.QComboBox(self.groupBox_7)
        self.fine_payment_type_cbox.setGeometry(QtCore.QRect(485, 40, 260, 26))
        self.fine_payment_type_cbox.setObjectName(_fromUtf8("fine_payment_type_cbox"))
        self.fine_register_payment_button = QtGui.QPushButton(self.groupBox_7)
        self.fine_register_payment_button.setGeometry(QtCore.QRect(640, 70, 106, 23))
        self.fine_register_payment_button.setObjectName(_fromUtf8("fine_register_payment_button"))
        self.fine_payment_date_edit = QtGui.QDateEdit(self.groupBox_7)
        self.fine_payment_date_edit.setGeometry(QtCore.QRect(24, 40, 196, 26))
        self.fine_payment_date_edit.setCalendarPopup(True)
        self.fine_payment_date_edit.setObjectName(_fromUtf8("fine_payment_date_edit"))
        self.fine_payment_twidget = QtGui.QTableWidget(self.groupBox_7)
        self.fine_payment_twidget.setGeometry(QtCore.QRect(25, 110, 720, 200))
        self.fine_payment_twidget.setCornerButtonEnabled(True)
        self.fine_payment_twidget.setObjectName(_fromUtf8("fine_payment_twidget"))
        self.fine_payment_twidget.setColumnCount(3)
        self.fine_payment_twidget.setRowCount(0)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fine_payment_twidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fine_payment_twidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.fine_payment_twidget.setHorizontalHeaderItem(2, item)
        self.fine_payment_twidget.horizontalHeader().setDefaultSectionSize(250)
        self.label_25 = QtGui.QLabel(self.groupBox_7)
        self.label_25.setGeometry(QtCore.QRect(250, 25, 200, 16))
        self.label_25.setObjectName(_fromUtf8("label_25"))
        self.label_26 = QtGui.QLabel(self.groupBox_7)
        self.label_26.setGeometry(QtCore.QRect(25, 95, 555, 16))
        self.label_26.setObjectName(_fromUtf8("label_26"))
        self.fine_amount_paid_sbox = QtGui.QSpinBox(self.groupBox_7)
        self.fine_amount_paid_sbox.setGeometry(QtCore.QRect(250, 40, 201, 24))
        self.fine_amount_paid_sbox.setObjectName(_fromUtf8("fine_amount_paid_sbox"))
        self.tabWidget.addTab(self.tab_3, _fromUtf8(""))
        self.close_button = QtGui.QPushButton(LandTaxPaymentsDialog)
        self.close_button.setGeometry(QtCore.QRect(680, 429, 75, 23))
        self.close_button.setObjectName(_fromUtf8("close_button"))
        self.line_2 = QtGui.QFrame(LandTaxPaymentsDialog)
        self.line_2.setGeometry(QtCore.QRect(0, 450, 801, 16))
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.apply_button = QtGui.QPushButton(LandTaxPaymentsDialog)
        self.apply_button.setGeometry(QtCore.QRect(590, 429, 75, 23))
        self.apply_button.setObjectName(_fromUtf8("apply_button"))
        self.help_button = QtGui.QPushButton(LandTaxPaymentsDialog)
        self.help_button.setGeometry(QtCore.QRect(540, 429, 30, 23))
        self.help_button.setObjectName(_fromUtf8("help_button"))
        self.status_label = QtGui.QLabel(LandTaxPaymentsDialog)
        self.status_label.setGeometry(QtCore.QRect(20, 430, 491, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Century Gothic"))
        font.setBold(True)
        font.setWeight(75)
        self.status_label.setFont(font)
        self.status_label.setObjectName(_fromUtf8("status_label"))

        self.retranslateUi(LandTaxPaymentsDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(LandTaxPaymentsDialog)
        LandTaxPaymentsDialog.setTabOrder(self.tabWidget, self.record_number_edit)
        LandTaxPaymentsDialog.setTabOrder(self.record_number_edit, self.select_owner_cbox)
        LandTaxPaymentsDialog.setTabOrder(self.select_owner_cbox, self.record_begin_edit)
        LandTaxPaymentsDialog.setTabOrder(self.record_begin_edit, self.record_status_edit)
        LandTaxPaymentsDialog.setTabOrder(self.record_status_edit, self.grace_period_edit)
        LandTaxPaymentsDialog.setTabOrder(self.grace_period_edit, self.year_sbox)
        LandTaxPaymentsDialog.setTabOrder(self.year_sbox, self.tax_per_year_edit)
        LandTaxPaymentsDialog.setTabOrder(self.tax_per_year_edit, self.tax_paid_edit)
        LandTaxPaymentsDialog.setTabOrder(self.tax_paid_edit, self.surplus_from_last_years_edit)
        LandTaxPaymentsDialog.setTabOrder(self.surplus_from_last_years_edit, self.tax_to_pay_edit)
        LandTaxPaymentsDialog.setTabOrder(self.tax_to_pay_edit, self.potential_fine_edit)
        LandTaxPaymentsDialog.setTabOrder(self.potential_fine_edit, self.effective_fine_edit)
        LandTaxPaymentsDialog.setTabOrder(self.effective_fine_edit, self.fine_paid_edit)
        LandTaxPaymentsDialog.setTabOrder(self.fine_paid_edit, self.fine_to_pay_edit)
        LandTaxPaymentsDialog.setTabOrder(self.fine_to_pay_edit, self.payment_frequency_edit)
        LandTaxPaymentsDialog.setTabOrder(self.payment_frequency_edit, self.quarter_1_check_box)
        LandTaxPaymentsDialog.setTabOrder(self.quarter_1_check_box, self.quarter_2_check_box)
        LandTaxPaymentsDialog.setTabOrder(self.quarter_2_check_box, self.quarter_3_check_box)
        LandTaxPaymentsDialog.setTabOrder(self.quarter_3_check_box, self.quarter_4_check_box)
        LandTaxPaymentsDialog.setTabOrder(self.quarter_4_check_box, self.apply_button)
        LandTaxPaymentsDialog.setTabOrder(self.apply_button, self.help_button)
        LandTaxPaymentsDialog.setTabOrder(self.help_button, self.close_button)
        LandTaxPaymentsDialog.setTabOrder(self.close_button, self.payment_date_edit)
        LandTaxPaymentsDialog.setTabOrder(self.payment_date_edit, self.amount_paid_sbox)
        LandTaxPaymentsDialog.setTabOrder(self.amount_paid_sbox, self.payment_type_cbox)
        LandTaxPaymentsDialog.setTabOrder(self.payment_type_cbox, self.register_payment_button)
        LandTaxPaymentsDialog.setTabOrder(self.register_payment_button, self.payment_twidget)
        LandTaxPaymentsDialog.setTabOrder(self.payment_twidget, self.fine_payment_date_edit)
        LandTaxPaymentsDialog.setTabOrder(self.fine_payment_date_edit, self.fine_amount_paid_sbox)
        LandTaxPaymentsDialog.setTabOrder(self.fine_amount_paid_sbox, self.fine_payment_type_cbox)
        LandTaxPaymentsDialog.setTabOrder(self.fine_payment_type_cbox, self.fine_register_payment_button)
        LandTaxPaymentsDialog.setTabOrder(self.fine_register_payment_button, self.fine_payment_twidget)

    def retranslateUi(self, LandTaxPaymentsDialog):
        LandTaxPaymentsDialog.setWindowTitle(_translate("LandTaxPaymentsDialog", "Register Payments", None))
        self.groupBox_2.setTitle(_translate("LandTaxPaymentsDialog", "Ownership Record And Owner", None))
        self.label_3.setText(_translate("LandTaxPaymentsDialog", "Record Number", None))
        self.label_7.setText(_translate("LandTaxPaymentsDialog", "Select Owner", None))
        self.label_8.setText(_translate("LandTaxPaymentsDialog", "Record Status", None))
        self.label_10.setText(_translate("LandTaxPaymentsDialog", "Ownership Begin", None))
        self.label_9.setText(_translate("LandTaxPaymentsDialog", "Grace Period [days]", None))
        self.groupBox_3.setTitle(_translate("LandTaxPaymentsDialog", "Taxes And Fines", None))
        self.groupBox_4.setTitle(_translate("LandTaxPaymentsDialog", "Tax", None))
        self.label_13.setText(_translate("LandTaxPaymentsDialog", "Tax To Pay For Year [₮]", None))
        self.label_14.setText(_translate("LandTaxPaymentsDialog", "Tax Paid [₮]", None))
        self.label_15.setText(_translate("LandTaxPaymentsDialog", "Surplus From Previous Year(s) [₮]", None))
        self.label_16.setText(_translate("LandTaxPaymentsDialog", "Tax Left To Be Paid [₮]", None))
        self.groupBox_5.setTitle(_translate("LandTaxPaymentsDialog", "Fine", None))
        self.label_18.setText(_translate("LandTaxPaymentsDialog", "Effective Fine [₮]", None))
        self.label_19.setText(_translate("LandTaxPaymentsDialog", "Fine Paid [₮]", None))
        self.label_20.setText(_translate("LandTaxPaymentsDialog", "Fine To Pay [₮]", None))
        self.label_23.setText(_translate("LandTaxPaymentsDialog", "Potential Fine [₮]", None))
        self.groupBox_6.setTitle(_translate("LandTaxPaymentsDialog", "Paid By Quarters", None))
        self.quarter_1_check_box.setText(_translate("LandTaxPaymentsDialog", "Q1", None))
        self.quarter_2_check_box.setText(_translate("LandTaxPaymentsDialog", "Q2", None))
        self.quarter_3_check_box.setText(_translate("LandTaxPaymentsDialog", "Q3", None))
        self.quarter_4_check_box.setText(_translate("LandTaxPaymentsDialog", "Q4", None))
        self.label_11.setText(_translate("LandTaxPaymentsDialog", "Effective Year", None))
        self.label_22.setText(_translate("LandTaxPaymentsDialog", "Payment Frequency", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("LandTaxPaymentsDialog", "Summary", None))
        self.tab_2.setToolTip(_translate("LandTaxPaymentsDialog", "<html><head/><body><p><br/></p></body></html>", None))
        self.groupBox.setTitle(_translate("LandTaxPaymentsDialog", "Taxes", None))
        self.label_6.setText(_translate("LandTaxPaymentsDialog", "Date", None))
        self.label_5.setText(_translate("LandTaxPaymentsDialog", "Payment Type", None))
        self.register_payment_button.setText(_translate("LandTaxPaymentsDialog", "Register", None))
        self.payment_date_edit.setDisplayFormat(_translate("LandTaxPaymentsDialog", "yyyy-MM-dd", None))
        item = self.payment_twidget.horizontalHeaderItem(0)
        item.setText(_translate("LandTaxPaymentsDialog", "Date", None))
        item = self.payment_twidget.horizontalHeaderItem(1)
        item.setText(_translate("LandTaxPaymentsDialog", "Amount [₮]", None))
        item = self.payment_twidget.horizontalHeaderItem(2)
        item.setText(_translate("LandTaxPaymentsDialog", "Payment Type", None))
        self.label_4.setText(_translate("LandTaxPaymentsDialog", "Amount [₮]", None))
        self.label_2.setText(_translate("LandTaxPaymentsDialog", "Registered Payments", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("LandTaxPaymentsDialog", "Taxes", None))
        self.groupBox_7.setTitle(_translate("LandTaxPaymentsDialog", "Fines", None))
        self.label_12.setText(_translate("LandTaxPaymentsDialog", "Date", None))
        self.label_24.setText(_translate("LandTaxPaymentsDialog", "Payment Type", None))
        self.fine_register_payment_button.setText(_translate("LandTaxPaymentsDialog", "Register", None))
        self.fine_payment_date_edit.setDisplayFormat(_translate("LandTaxPaymentsDialog", "yyyy-MM-dd", None))
        item = self.fine_payment_twidget.horizontalHeaderItem(0)
        item.setText(_translate("LandTaxPaymentsDialog", "Date", None))
        item = self.fine_payment_twidget.horizontalHeaderItem(1)
        item.setText(_translate("LandTaxPaymentsDialog", "Amount [₮]", None))
        item = self.fine_payment_twidget.horizontalHeaderItem(2)
        item.setText(_translate("LandTaxPaymentsDialog", "Payment Type", None))
        self.label_25.setText(_translate("LandTaxPaymentsDialog", "Amount [₮]", None))
        self.label_26.setText(_translate("LandTaxPaymentsDialog", "Registered Payments", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("LandTaxPaymentsDialog", "Fines", None))
        self.close_button.setText(_translate("LandTaxPaymentsDialog", "Close", None))
        self.apply_button.setText(_translate("LandTaxPaymentsDialog", "Apply", None))
        self.help_button.setText(_translate("LandTaxPaymentsDialog", "?", None))
        self.status_label.setText(_translate("LandTaxPaymentsDialog", "Messages", None))

import resources_rc
