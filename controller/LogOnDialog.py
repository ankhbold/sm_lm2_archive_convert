import os

__author__ = 'Topmap'

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from inspect import currentframe

from ..view.Ui_LogOnDialog import *
from ..model.Enumerations import UserRight
from ..model import SettingsConstants
from ..model import Constants
from ..utils.SessionHandler import SessionHandler
from ..utils.PluginUtils import PluginUtils


class LogOnDialog(QDialog, Ui_LogOnDialog):

    def __init__(self, protected_dialog, parent=None):

        super(LogOnDialog,  self).__init__(parent)
        self.setupUi(self)
        if protected_dialog == 10:
            self.setWindowTitle(self.tr("Log On To Database"))
        elif protected_dialog == 20:
            self.setWindowTitle(self.tr("Land Officer Settings"))
        self.__has_contracting_update_privilege = False

        database_name = QSettings().value(SettingsConstants.DATABASE_NAME, "")
        host = QSettings().value(SettingsConstants.HOST, "")
        port = QSettings().value(SettingsConstants.PORT, "5432")
        self.port_edit.setText(port)
        self.database_edit.setText(database_name)
        self.server_edit.setText(host)

        self.port_edit.setValidator(QIntValidator(1000,  6000, self.port_edit))

        if len(self.database_edit.text()) > 0 and len(self.port_edit.text()) > 0 and len(self.server_edit.text()) > 0:
            self.user_edit.setFocus()
        self.logon_button.setDefault(True)

        self.__protected_dialog = protected_dialog
        self.close_button.clicked.connect(self.reject)

    @pyqtSignature("")
    def on_logon_button_clicked(self):

        host = self.server_edit.text().strip()
        port = self.port_edit.text().strip()

        database = self.database_edit.text().strip()
        user = self.user_edit.text().strip()
        password = self.password_edit.text().strip()

        if not self.__validate_user_input(host, port, database, user, password):
            return

        try:
            if not SessionHandler().create_session(user, password, host, port, database):
                return

            session = SessionHandler().session_instance()
            session.execute("SET search_path to base, codelists, admin_units, settings, public")
            sql = "select rolname from pg_user join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) " \
                  "join pg_roles on (pg_roles.oid=pg_auth_members.roleid) where pg_user.usename=:bindName"

            result = session.execute(sql, {'bindName': user}).fetchall()
            if len(result) == 0:
                PluginUtils.show_error(self, self.tr("Invalid input"), self.tr("The user {0} does not exist.").format(user))
                return

            has_privilege = False
            self.__has_contracting_update_privilege = False

            for group in result:

                if self.__protected_dialog == Constants.ROLE_MANAGEMENT_DLG:
                    if group[0] == UserRight.role_management:
                        has_privilege = True
                        break
                else:
                    if group[0] == UserRight.land_office_admin:
                        has_privilege = True
                        break

            if not has_privilege:

                SessionHandler().destroy_session()
                if self.__protected_dialog == Constants.ROLE_MANAGEMENT_DLG:
                    PluginUtils.show_error(self, self.tr("No Privilege"),
                                           self.tr("The user has no privileges to manage user roles!"))
                else:
                    PluginUtils.show_error(self, self.tr("No Privilege"),
                                           self.tr("The user has no privileges to perform "
                                                   "land administration settings!"))
                return

            session.commit()

            QDialog.accept(self)

        except (DatabaseError, SQLAlchemyError), e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    @pyqtSignature("")
    def reject(self):

        QDialog.reject(self)

    def __validate_user_input(self, host, port, database, user, password):

        # TODO: all the tests
        #the username, database needs to be checked in the create_session function
        if not port.isdigit():
            PluginUtils.show_error(self, self.tr("Wrong Parameter"), self.tr("Enter a valid port number!"))
            return False
        return True

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/connection_to_main_database.htm")