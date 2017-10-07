__author__ = 'ankhaa'

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from sqlalchemy.exc import DatabaseError, SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from inspect import currentframe
from ..view.Ui_UserRoleManagementDialog import *
from ..model.SetRole import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.LM2Exception import LM2Exception
from ..model.ClPositionType import *
from ..utils.PluginUtils import *

import datetime


class UserRoleManagementDialog(QDialog, Ui_UserRoleManagementDialog):

    GROUP_SEPARATOR = '-----'
    PW_PLACEHOLDER = '0123456789'

    def __init__(self, parent=None):

        super(UserRoleManagementDialog,  self).__init__(parent)
        self.setupUi(self)

        self.db_session = SessionHandler().session_instance()

        self.__setup_combo_boxes()
        self.__populate_user_role_lwidget()

        self.__populate_group_lwidget()

        self.__populate_au_level1_cbox()

        self.close_button.clicked.connect(self.reject)

        # permit only alphanumeric characters for the username
        reg_ex = QRegExp(u"[_a-zA-Z][_a-zA-Z0-9]+")
        validator = QRegExpValidator(reg_ex, None)
        self.username_edit.setValidator(validator)

        self.selected_user = None

    def __setup_combo_boxes(self):

        try:
            positions = self.db_session.query(ClPositionType).all()

            for position in positions:
                self.position_cbox.addItem(position.description, position.code)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    def __populate_user_role_lwidget(self):

        self.user_role_lwidget.clear()

        try:
            for user in self.db_session.query(SetRole).order_by(SetRole.user_name):
                item = QListWidgetItem(QIcon(":/plugins/lm2/person.png"), user.user_name)
                if user.user_name == self.__logged_on_user():
                    item.setForeground(Qt.blue)
                if self.__is_db_role(user.user_name):
                    self.user_role_lwidget.addItem(item)

        except (DatabaseError, SQLAlchemyError), e:
            PluginUtils.show_error(self,  self.tr("Database Error"), e.message)

    def __is_db_role(self, user_name):

        try:
            sql = "SELECT count(*) FROM pg_roles WHERE rolname = '{0}' and rolcanlogin = true".format(user_name)
            count = self.db_session.execute(sql).fetchone()
            return True if count[0] == 1 else False
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    def __populate_group_lwidget(self):

        self.group_lwidget.clear()
        self.member_lwidget.clear()

        QListWidgetItem("land_office_administration", self.group_lwidget)
        QListWidgetItem("db_creation", self.group_lwidget)
        QListWidgetItem("role_management", self.group_lwidget)
        QListWidgetItem(self.GROUP_SEPARATOR, self.group_lwidget)
        QListWidgetItem("application_view", self.group_lwidget)
        QListWidgetItem("application_update", self.group_lwidget)
        QListWidgetItem("cadastre_view", self.group_lwidget)
        QListWidgetItem("cadastre_update", self.group_lwidget)
        QListWidgetItem("contracting_view", self.group_lwidget)
        QListWidgetItem("contracting_update", self.group_lwidget)
        QListWidgetItem("reporting", self.group_lwidget)
        QListWidgetItem("log_view", self.member_lwidget)

    def __populate_au_level1_cbox(self):

        try:
            PluginUtils.populate_au_level1_cbox(self.aimag_cbox, True, False, False)
        except DatabaseError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    @pyqtSlot()
    def on_aimag_lwidget_itemSelectionChanged(self):

        try:
            self.soum_cbox.clear()
            self.soum_cbox.addItem("*", "*")
            if self.aimag_lwidget.currentItem() is None:
                return
            # if self.aimag_lwidget.count() > 1:
            #     return

            au_level1_code = self.aimag_lwidget.currentItem().data(Qt.UserRole)

            PluginUtils.populate_au_level2_cbox(self.soum_cbox, au_level1_code, True, False, False)

        except DatabaseError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    @pyqtSlot()
    def on_user_role_lwidget_itemSelectionChanged(self):

        self.selected_user = self.user_role_lwidget.currentItem().text()
        user_name = self.user_role_lwidget.currentItem().text()

        try:
            user = self.db_session.query(SetRole).filter(SetRole.user_name == user_name).one()
        except NoResultFound:
            return

        self.username_edit.setText(user.user_name)
        self.surname_edit.setText(user.surname)
        self.firstname_edit.setText(user.first_name)
        self.position_cbox.setCurrentIndex(self.position_cbox.findData(user.position))
        # self.position_edit.setText(user.position)
        self.phone_edit.setText(user.phone)
        self.mac_address_edit.setText(user.mac_addresses)
        self.password_edit.setText(self.PW_PLACEHOLDER)
        self.retype_password_edit.setText(self.PW_PLACEHOLDER)

        # populate groups
        self.__populate_group_lwidget()

        groups = self.__groupsByUser(user_name)
        for group in groups:

            group_name = group[0]
            items = self.group_lwidget.findItems(group_name, Qt.MatchExactly)
            if len(items) > 0:
                item = items[0]
                self.member_lwidget.addItem(item.text())
                self.group_lwidget.takeItem(self.group_lwidget.row(item))

        # populate admin units
        self.aimag_lwidget.clear()
        self.soum_lwidget.clear()
        restriction_au_level1 = user.restriction_au_level1
        aimag_codes = restriction_au_level1.split(',')

        try:
            if len(aimag_codes) == self.db_session.query(AuLevel1).count():  # all Aimags
                item = QListWidgetItem("*")
                item.setData(Qt.UserRole, "*")
                self.aimag_lwidget.addItem(item)
                self.soum_lwidget.addItem(item)
            else:
                for code in aimag_codes:
                    code = code.strip()
                    aimag = self.db_session.query(AuLevel1).filter(AuLevel1.code == code).one()
                    item = QListWidgetItem(aimag.name)
                    item.setData(Qt.UserRole, aimag.code)
                    self.aimag_lwidget.addItem(item)

                restriction_au_level2 = user.restriction_au_level2
                soum_codes = restriction_au_level2.split(',')

                # Find districts among the Aimags:
                l1_district_entries = filter(lambda x: x.startswith('1') or x.startswith('01'), aimag_codes)
                l2_district_entries = filter(lambda x: x.startswith('1') or x.startswith('01'), soum_codes)

                true_aimags = filter(lambda x: not x.startswith('1') and not x.startswith('01'), aimag_codes)

                if len(aimag_codes)-len(l1_district_entries) == 1 and \
                        len(soum_codes)-len(l2_district_entries) == self.db_session.query(AuLevel2)\
                                                                    .filter(AuLevel2.code.startswith(true_aimags[0]))\
                                                                    .count():
                    item = QListWidgetItem("*")
                    item.setData(Qt.UserRole, "*")
                    self.soum_lwidget.addItem(item)
                else:
                    for code in soum_codes:
                        code = code.strip()
                        soum = self.db_session.query(AuLevel2).filter(AuLevel2.code == code).one()
                        item = QListWidgetItem(soum.name)
                        item.setData(Qt.UserRole, soum.code)
                        self.soum_lwidget.addItem(item)
        except NoResultFound:
            pass

    def reject(self):

        SessionHandler().destroy_session()
        QDialog.reject(self)

    @pyqtSlot()
    def on_add_button_clicked(self):

        try:
            if self.__add_or_update_role():
                PluginUtils.show_message(self, self.tr("User Role Management"), self.tr('New user created.'))
        except DatabaseError, e:
            self.db_session.rollback()
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    @pyqtSlot()
    def on_update_button_clicked(self):

        try:
            if self.__add_or_update_role('UPDATE'):
                PluginUtils.show_message(self, self.tr("User Role Management"), self.tr('User information updated.'))
        except DatabaseError, e:
            self.db_session.rollback()
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    def __add_or_update_role(self, mode='ADD'):

        if not self.__validate_user_input(mode):
            return False
        user_name = self.username_edit.text().strip()
        surname = self.surname_edit.text().strip()
        first_name = self.firstname_edit.text().strip()
        phone = self.phone_edit.text().strip()
        # position = self.position_edit.text().strip()
        position = self.position_cbox.itemData(self.position_cbox.currentIndex())
        mac_addresses = self.mac_address_edit.text().strip()
        password = self.password_edit.text().strip()

        self.db_session.execute("SET ROLE role_management")

        if mode == 'ADD':

            sql = "SELECT count(*) FROM pg_roles WHERE rolname = '{0}' and rolcanlogin = true".format(user_name)
            count = self.db_session.execute(sql).fetchone()
            if count[0] == 0:
                self.db_session.execute(u"CREATE ROLE {0} login PASSWORD '{1}'".format(user_name, password))
            else:
                message_box = QMessageBox()
                message_box.setText(self.tr("Could not execute: {0} already exists. Do you want to connect selected soums?").format(user_name))
                yes_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
                message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)

                message_box.exec_()

                if not message_box.clickedButton() == yes_button:
                    return
        else:
            if password != self.PW_PLACEHOLDER:
                self.db_session.execute(u"ALTER ROLE {0} PASSWORD '{1}'".format(user_name, password))

        groups = self.__groupsByUser(user_name)
        for group in groups:
            self.db_session.execute(u"REVOKE {0} FROM {1}".format(group[0], user_name))

        for index in range(self.member_lwidget.count()):
            item = self.member_lwidget.item(index)
            print item.text()
            self.db_session.execute(u"GRANT {0} TO {1}".format(item.text(), user_name))
        self.db_session.execute("RESET ROLE")

        restriction_au_level1 = ''
        restriction_au_level2 = ''
        is_first = 0
        for index in range(self.aimag_lwidget.count()):
            item = self.aimag_lwidget.item(index)
            if item.text() == '*':  # all Aimags
                for index2 in range(self.aimag_cbox.count()):
                    au_level1_code = str(self.aimag_cbox.itemData(index2, Qt.UserRole))
                    if au_level1_code != '*':
                        restriction_au_level1 += au_level1_code + ','
                        # Special treatment for UB's districts:
                        if au_level1_code.startswith('1') or au_level1_code.startswith('01'):
                            restriction_au_level2 += au_level1_code + '00' + ','
                            self.db_session.execute("SET ROLE role_management")
                            self.db_session.execute(u"GRANT s{0}00 TO {1}".format(au_level1_code, user_name))
                            self.db_session.execute("RESET ROLE")

                    for au_level2 in self.db_session.query(AuLevel2).filter(AuLevel2.code.startswith(au_level1_code))\
                            .order_by(AuLevel2.code):

                        restriction_au_level2 += au_level2.code + ','
                        self.db_session.execute("SET ROLE role_management")
                        self.db_session.execute(u"GRANT s{0} TO {1}".format(au_level2.code, user_name))
                        self.db_session.execute("RESET ROLE")
                break
            else:
                au_level1_code = str(item.data(Qt.UserRole))
                restriction_au_level1 += au_level1_code + ','
                # Special treatment for UB's districts:
                # if au_level1_code.startswith('1') or au_level1_code.startswith('01'):
                #     restriction_au_level2 += au_level1_code + '00' + ','
                #     self.db_session.execute("SET ROLE role_management")
                #     self.db_session.execute(u"GRANT s{0}00 TO {1}".format(au_level1_code, user_name))
                #     self.db_session.execute("RESET ROLE")
                if is_first == 0:
                    is_first = 1
                    for index2 in range(self.soum_lwidget.count()):
                        item = self.soum_lwidget.item(index2)
                        if item.text() == '*':
                            for au_level2 in self.db_session.query(AuLevel2).filter(AuLevel2.code.startswith(au_level1_code))\
                                    .order_by(AuLevel2.code):
                                restriction_au_level2 += au_level2.code + ','
                                self.db_session.execute("SET ROLE role_management")
                                self.db_session.execute(u"GRANT s{0} TO {1}".format(au_level2.code, user_name))
                                self.db_session.execute("RESET ROLE")
                        else:
                            au_level2_code = str(item.data(Qt.UserRole))
                            restriction_au_level2 += au_level2_code + ','
                            self.db_session.execute("SET ROLE role_management")
                            self.db_session.execute(u"GRANT s{0} TO {1}".format(au_level2_code, user_name))
                            self.db_session.execute("RESET ROLE")

        restriction_au_level1 = restriction_au_level1[:len(restriction_au_level1)-1]
        restriction_au_level2 = restriction_au_level2[:len(restriction_au_level2)-1]

        pa_from = datetime.datetime.today()
        pa_till = datetime.date.max
        role_c = self.db_session.query(SetRole).filter(SetRole.user_name == user_name).count()

        if mode == 'ADD' and role_c == 0:
            role = SetRole(user_name=user_name, surname=surname, first_name=first_name, phone=phone,
                           mac_addresses=mac_addresses, position=position, restriction_au_level1=restriction_au_level1,
                           restriction_au_level2=restriction_au_level2, pa_from=pa_from, pa_till=pa_till)
            self.db_session.add(role)
        else:
            role = self.db_session.query(SetRole).filter(SetRole.user_name == user_name).one()
            role.surname = surname
            role.first_name = first_name
            role.phone = phone
            role.mac_addresses = mac_addresses
            role.position = position
            role.restriction_au_level1 = restriction_au_level1
            role.restriction_au_level2 = restriction_au_level2

        self.db_session.commit()
        self.__populate_user_role_lwidget()
        item = self.user_role_lwidget.findItems(user_name, Qt.MatchExactly)[0]
        row = self.user_role_lwidget.row(item)
        self.user_role_lwidget.setCurrentRow(row)

        return True

    def __validate_user_input(self, mode='ADD'):

        if mode == 'UPDATE':
            if self.username_edit.text().strip() != self.selected_user:
                PluginUtils.show_message(None, self.tr("Username can't be modified"),
                                        self.tr("The username of an existing user cannot be modified!"))
                self.username_edit.setText(self.selected_user)
                return False

        if self.username_edit.text().strip() == 'role_manager' \
                and not self.member_lwidget.findItems('role_management', Qt.MatchExactly):
            PluginUtils.show_message(self, self.tr("Required group"),
                                    self.tr("The user 'role_manager' must be member of group 'role_management'."))
            return False

        if len(self.username_edit.text().strip()) == 0:
            PluginUtils.show_message(self, self.tr("No Username"), self.tr("Provide a valid username!"))
            return False

        if len(self.password_edit.text().strip()) < 8:
            PluginUtils.show_message(self, self.tr("Invalid Password"),
                                    self.tr("Provide a valid password that consists of 8 characters or more!"))
            return False

        if self.password_edit.text().strip() != self.retype_password_edit.text().strip():
            PluginUtils.show_message(self, self.tr("Passwords Not Matching"),
                                    self.tr("Password and retyped password are not identical!"))
            return False

        if len(self.surname_edit.text().strip()) == 0:
            PluginUtils.show_message(self, self.tr("No Surname"), self.tr("Provide a valid surname!"))
            return False

        if len(self.firstname_edit.text().strip()) == 0:
            PluginUtils.show_message(self, self.tr("No First Name"), self.tr("Provide a valid first name!"))
            return False

        if len(self.firstname_edit.text().strip()) == 0:
            PluginUtils.show_message(self, self.tr("No Position"), self.tr("Provide a valid position!"))
            return False

        if self.member_lwidget.count() == 0:
            PluginUtils.show_message(self, self.tr("No Group Membership"),
                                    self.tr("The user must be member of at least one group!"))
            return False

        if not self.member_lwidget.findItems('role_management', Qt.MatchExactly) \
                and not self.member_lwidget.findItems('db_creation', Qt.MatchExactly):

                if self.aimag_lwidget.count() == 0:
                    PluginUtils.show_message(self, self.tr("No Aimag/Duureg"),
                                            self.tr("The user must be granted at least one Aimag/Duureg!"))
                    return False

                if self.soum_lwidget.count() == 0:
                    PluginUtils.show_message(self, self.tr("No Soum"),
                                            self.tr("The user must granted at least one Soum!"))
                    return False

        return True

    @pyqtSlot()
    def on_down_groups_button_clicked(self):

        if not self.group_lwidget.currentItem():
            return
        group = self.group_lwidget.currentItem().text()
        if group.find(self.GROUP_SEPARATOR) != -1:
            return

        self.group_lwidget.takeItem(self.group_lwidget.row(self.group_lwidget.currentItem()))
        self.member_lwidget.addItem(group)

        if group == 'land_office_administration':
            item_list = self.member_lwidget.findItems('contracting_update', Qt.MatchExactly)
            if len(item_list) == 0:
                contracting_update_item = self.group_lwidget.findItems('contracting_update', Qt.MatchExactly)[0]
                self.group_lwidget.takeItem(self.group_lwidget.row(contracting_update_item))
                self.member_lwidget.addItem(contracting_update_item.text())
        elif group == 'contracting_update':
            item_list = self.member_lwidget.findItems('cadastre_update', Qt.MatchExactly)
            if len(item_list) == 0:
                cadastre_update_item = self.group_lwidget.findItems('cadastre_update', Qt.MatchExactly)[0]
                self.group_lwidget.takeItem(self.group_lwidget.row(cadastre_update_item))
                self.member_lwidget.addItem(cadastre_update_item.text())

    @pyqtSlot()
    def on_up_groups_button_clicked(self):

        if not self.member_lwidget.currentItem():
            return
        group = self.member_lwidget.currentItem().text()
        if group == 'log_view':  # cannot be removed from member widget
            return
        self.member_lwidget.takeItem(self.member_lwidget.row(self.member_lwidget.currentItem()))
        if group == 'role_management' or group == 'db_creation' or group == 'land_office_administration':
            self.group_lwidget.insertItem(0, group)
        else:
            self.group_lwidget.addItem(group)

        if group == 'contracting_update':
            item_list = self.group_lwidget.findItems('land_office_administration', Qt.MatchExactly)
            if len(item_list) == 0:
                land_office_admin_item = self.member_lwidget.findItems('land_office_administration', Qt.MatchExactly)[0]
                self.member_lwidget.takeItem(self.member_lwidget.row(land_office_admin_item))
                self.group_lwidget.insertItem(0, land_office_admin_item.text())
        elif group == 'cadastre_update':
            item_list = self.group_lwidget.findItems('contracting_update', Qt.MatchExactly)
            if len(item_list) == 0:
                contracting_update_item = self.member_lwidget.findItems('contracting_update', Qt.MatchExactly)[0]
                self.member_lwidget.takeItem(self.member_lwidget.row(contracting_update_item))
                self.group_lwidget.addItem(contracting_update_item.text())

    @pyqtSlot()
    def on_down_aimag_button_clicked(self):

        au_level1_name = self.aimag_cbox.currentText()
        au_level1_code = self.aimag_cbox.itemData(self.aimag_cbox.currentIndex(), Qt.UserRole)

        if len(self.aimag_lwidget.findItems(au_level1_name, Qt.MatchExactly)) == 0:
            if len(self.aimag_lwidget.findItems("*", Qt.MatchExactly)) == 0:
                if au_level1_name == '*':
                    self.aimag_lwidget.clear()
                    self.soum_lwidget.clear()
                    item = QListWidgetItem("*")
                    item.setData(Qt.UserRole, "*")
                    self.soum_lwidget.addItem(item)
                item = QListWidgetItem(au_level1_name)
                item.setData(Qt.UserRole, au_level1_code)
                self.aimag_lwidget.addItem(item)
                self.aimag_lwidget.setCurrentItem(item)

        if self.aimag_lwidget.count() > 1:
            self.soum_lwidget.clear()
            item = QListWidgetItem("*")
            item.setData(Qt.UserRole, "*")
            self.soum_lwidget.addItem(item)

    @pyqtSlot()
    def on_up_aimag_button_clicked(self):

        self.aimag_lwidget.takeItem(self.aimag_lwidget.row(self.aimag_lwidget.currentItem()))
        if self.aimag_lwidget.count() > 0:
            self.aimag_lwidget.setItemSelected(self.aimag_lwidget.item(0), False)
            self.aimag_lwidget.setCurrentItem(self.aimag_lwidget.item(0))
        self.soum_lwidget.clear()

    @pyqtSlot()
    def on_down_soum_button_clicked(self):

        au_level2_name = self.soum_cbox.currentText()
        au_level2_code = self.soum_cbox.itemData(self.soum_cbox.currentIndex(), Qt.UserRole)
        itemsList = self.aimag_lwidget.selectedItems()
        if len(self.soum_lwidget.findItems(au_level2_name, Qt.MatchExactly)) == 0:
            if len(self.soum_lwidget.findItems("*", Qt.MatchExactly)) == 0:
                if au_level2_name == '*':
                    self.soum_lwidget.clear()
                item = QListWidgetItem(au_level2_name)
                item.setData(Qt.UserRole, au_level2_code)
                self.soum_lwidget.addItem(item)

    @pyqtSlot()
    def on_up_soum_button_clicked(self):

        self.soum_lwidget.takeItem(self.soum_lwidget.row(self.soum_lwidget.currentItem()))

    @pyqtSlot()
    def on_delete_button_clicked(self):

        item = self.user_role_lwidget.currentItem()
        if item is None:
            return

        user_name = item.text()

        if user_name == 'role_manager':
            PluginUtils.show_message(self, self.tr("Delete User"),
                                     self.tr("The user 'role_manager' is a required role and cannot be deleted."))
            return

        # The user logged on must not delete himself:
        if self.__logged_on_user() == user_name:
            PluginUtils.show_message(self, self.tr("Delete User"),
                                     self.tr("The user currently logged on cannot be deleted."))
            return

        message = "Delete user role {0}".format(user_name)
        if QMessageBox.No == QMessageBox.question(self, self.tr("Delete User Role"),
                                                  message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
            return

        try:
            user_role = self.db_session.query(SetRole).filter(SetRole.user_name == user_name).one()
            self.db_session.delete(user_role)
            self.db_session.execute("SET ROLE role_management")
            self.db_session.execute(u"DROP ROLE {0}".format(user_name))
            self.db_session.execute("RESET ROLE")
            self.db_session.commit()
            self.__populate_user_role_lwidget()
            PluginUtils.show_message(self, self.tr("User Role Management"), self.tr('User role deleted.'))

        except DatabaseError, e:
            self.db_session.rollback()
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))

    def __groupsByUser(self, user_name):

        sql = "select rolname from pg_user join pg_auth_members on (pg_user.usesysid=pg_auth_members.member) " \
              "join pg_roles on (pg_roles.oid=pg_auth_members.roleid) where pg_user.usename=:bindName"
        result = self.db_session.execute(sql, {'bindName': user_name}).fetchall()

        return result

    def __logged_on_user(self):

        result = self.db_session.execute("SELECT USER")
        current_user = result.fetchone()
        return current_user[0]

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/user_role_management.htm")