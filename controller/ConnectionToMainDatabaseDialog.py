import os

__author__ = 'ankhaa'
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from ..view.Ui_ConnectionToMainDatabaseDialog import *
from ..model import SettingsConstants


class ConnectionToMainDatabaseDialog(QDialog, Ui_ConnectionToMainDatabaseDialog):

    def __init__(self, parent=None):

        super(ConnectionToMainDatabaseDialog,  self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(self.tr("Connection to main database dialog"))
        self.load_settings()

    def load_settings(self):

        database = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")
        user = QSettings().value(SettingsConstants.USER)

        self.database_edit.setText(database)
        self.server_name_edit.setText(host)
        self.port_edit.setText(str(port))
        self.user_name_edit.setText(user)

    @pyqtSlot()
    def on_ok_button_clicked(self):

        QSettings().setValue(SettingsConstants.DATABASE_NAME, self.database_edit.text())
        QSettings().setValue(SettingsConstants.HOST, self.server_name_edit.text())
        QSettings().setValue(SettingsConstants.PORT, self.port_edit.text())
        QSettings().setValue(SettingsConstants.USER, self.user_name_edit.text())

        self.reject()

    @pyqtSlot()
    def on_cancel_button_clicked(self):
        self.reject()

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/connection_to_main_database.htm")

