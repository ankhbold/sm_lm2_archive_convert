__author__ = 'ankhaa'

from sqlalchemy import exc, or_
from sqlalchemy.sql import text
from inspect import currentframe

from ..view.Ui_LandOfficeAdministrativeSettingsDialog import *
from ..utils.PluginUtils import *
from ..model import Constants
from ..model.DatabaseHelper import *
from ..model.ClApplicationStatus import *
from ..model.AuLevel1 import *
from ..model.AuLevel2 import *
from ..model.ClBank import *
from ..model.ClContractCancellationReason import *
from ..model.ClContractCondition import *
from ..model.ClContractStatus import *
from ..model.ClPositionType import *
from ..model.ClDecisionLevel import *
from ..model.ClDocumentRole import *
from ..model.ClGender import *
from ..model.SetCertificate import *
from ..model.ClPersonRole import *
from ..model.ClPersonType import *
from ..model.ClRecordCancellationReason import *
from ..model.ClRecordRightType import *
from ..model.ClRecordStatus import *
from ..model.ClRightType import *
from ..model.ClEquipmentList import *
from ..model.SetFeeZone import *
from ..model.SetBaseFee import *
from ..model.SetTaxAndPriceZone import *
from ..model.SetBaseTaxAndPrice import *
from ..model.SetSurveyCompany import *
from ..model.SetOfficialDocument import *
from ..model.CtContractApplicationRole import *
from ..model.CtArchivedFee import *
from ..model.CtArchivedTaxAndPrice import *
from ..model.VaTypeParcel import *
from ..model.VaTypeAgriculture import *
from ..model.VaTypeDesign import *
from ..model.VaTypeHeat import *
from ..model.VaTypeLanduseBuilding import *
from ..model.VaTypeMaterial import *
from ..model.VaTypePurchaseOrLease import *
from ..model.VaTypeSource import *
from ..model.VaTypeStatusBuilding import *
from ..model.VaTypeStove import *
from ..model.VaTypeSideFence import *
from ..model.SetEquipment import *
from ..model.SetEquipmentDocument import *
from ..model.SetDocument import *
from ..utils.FileUtils import FileUtils

from .qt_classes.OfficialDocumentDelegate import OfficialDocumentDelegate
from .qt_classes.DoubleSpinBoxDelegate import DoubleSpinBoxDelegate
from .qt_classes.IntegerSpinBoxDelegate import IntegerSpinBoxDelegate
from .qt_classes.LandUseComboBoxDelegate import LandUseComboBoxDelegate

FEE_LAND_USE = 0
FEE_BASE_FEE_PER_M2 = 1
FEE_SUBSIDIZED_AREA = 2
FEE_SUBSIDIZED_FEE_RATE = 3

TAX_LAND_USE = 0
TAX_BASE_VALUE_PER_M2 = 1
TAX_BASE_TAX_RATE = 2
TAX_SUBSIDIZED_AREA = 3
TAX_SUBSIDIZED_TAX_RATE = 4

CODELIST_CODE = 0
CODELIST_DESC = 1

COMPANY_NAME = 0
COMPANY_ADDRESS = 1

SURVEYOR_SURNAME = 0
SURVEYOR_FIRST_NAME = 1
SURVEYOR_PHONE = 2

DOC_VISIBLE_COLUMN = 0
DOC_NAME_COLUMN = 1
DOC_DESCRIPTION_COLUMN = 2
DOC_OPEN_FILE_COLUMN = 3
DOC_VIEW_COLUMN = 4


class LandOfficeAdministrativeSettingsDialog(QDialog, Ui_LandOfficeAdministrativeSettingsDialog, DatabaseHelper):

    def __init__(self, parent=None):

        super(LandOfficeAdministrativeSettingsDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)
        self.setupUi(self)
        self.time_counter = None
        self.old_codelist_index = -1
        self.company_search_str = ''
        self.surveyor_search_str = ''

        self.__setup_combo_boxes()
        self.__load_settings()
        self.__setup_codelist_table_widget()

        self.close_button.clicked.connect(self.reject)
        self.apply_button.setDefault(True)
        self.status_label.clear()
        self.initial_date.setDate(QDate().currentDate())
        self.given_date.setDate(QDate().currentDate())
        self.duration_date.setDate(QDate().currentDate())

        self.landuse_code_list = list()
        self.__set_up_land_fee_tab()
        self.__set_up_land_tax_tab()
        self.__set_up_company_tab()
        self.__set_up_surveyor_tab()
        self.__setup_doc_twidget()
        self.__set_up_equipment_tab()

    def __setup_codelist_table_widget(self):

        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_widget.setSelectionMode(QTableWidget.SingleSelection)
        delegate = IntegerSpinBoxDelegate(CODELIST_CODE, 1, 10000, 1000, 10, self.table_widget)
        self.table_widget.setItemDelegateForColumn(CODELIST_CODE, delegate)

    def __setup_combo_boxes(self):

        bank_list = DatabaseUtils.codelist_by_name("codelists", "cl_bank", "code", "description")
        for key, value in bank_list.iteritems():
            self.bank_cbox.addItem(value, key)

        code_lists = self.__codelist_names()
        for key, value in code_lists.iteritems():
            self.select_codelist_cbox.addItem(value, key)

        l1_codes = DatabaseUtils.l1_restriction_array()
        l2_codes = DatabaseUtils.l2_restriction_array()

        self.__set_up_feezone_cbox(l1_codes, l2_codes)
        self.__set_up_taxzone_cbox(l1_codes, l2_codes)

        self.__set_equipment_cbox()

    def __set_equipment_cbox(self):

        equipment_list = []
        users_list = []

        session = SessionHandler().session_instance()
        try:
            equipment_list = session.query(ClEquipmentList).all()
            users_list = session.query(SetRole).all()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

        self.equipment_list_cbox.addItem("*", -1)
        self.users_list_cbox.addItem("*", -1)
        for item in equipment_list:
            self.equipment_list_cbox.addItem(item.description, item.code)
        for item in users_list:
            display_name = item.user_name + u": "+ item.surname[:1] + u"."+ item.first_name
            self.users_list_cbox.addItem(display_name, item.user_name)

    @pyqtSlot(int)
    def on_register_search_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.add_equipment_button.setDisabled(True)
            self.edit_equipment_button.setDisabled(True)
            self.delete_equipment_button.setDisabled(True)
            self.add_equip_doc_button.setDisabled(True)
            self.view_equip_doc_button.setDisabled(True)
            self.delete_equip_doc_button.setDisabled(True)
            self.equipment_find_button.setDisabled(False)
        else:
            self.add_equipment_button.setDisabled(False)
            self.edit_equipment_button.setDisabled(False)
            self.delete_equipment_button.setDisabled(False)
            self.add_equip_doc_button.setDisabled(False)
            self.view_equip_doc_button.setDisabled(False)
            self.delete_equip_doc_button.setDisabled(False)
            self.equipment_find_button.setDisabled(True)

    def __set_up_feezone_cbox(self, l1_codes, l2_codes):

        session = SessionHandler().session_instance()
        locations1 = session.query(SetFeeZone.location).distinct(). \
            filter(SetFeeZone.geometry.ST_Within(AuLevel1.geometry)). \
            filter(AuLevel1.code.in_(l1_codes)). \
            filter(or_(AuLevel1.code.startswith('01'), AuLevel1.code.startswith('1'))). \
            order_by(SetFeeZone.location)
        locations2 = session.query(SetFeeZone.location).distinct(). \
            filter(SetFeeZone.geometry.ST_Within(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetFeeZone.location)
        locations3 = session.query(SetFeeZone.location).distinct(). \
            filter(SetFeeZone.geometry.ST_Contains(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetFeeZone.location)
        locations4 = session.query(SetFeeZone.location).distinct(). \
            filter(SetFeeZone.geometry.ST_Overlaps(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetFeeZone.location)

        for location in locations1:
            self.zone_location_cbox.addItem(location[0])
        for location in locations2:
            self.zone_location_cbox.addItem(location[0])
        for location in locations3:
            self.zone_location_cbox.addItem(location[0])
        for location in locations4:
            self.zone_location_cbox.addItem(location[0])

    def __set_up_taxzone_cbox(self, l1_codes, l2_codes):

        session = SessionHandler().session_instance()
        locations1 = session.query(SetTaxAndPriceZone.location).distinct(). \
            filter(SetTaxAndPriceZone.geometry.ST_Within(AuLevel1.geometry)). \
            filter(AuLevel1.code.in_(l1_codes)). \
            filter(or_(AuLevel1.code.startswith('01'), AuLevel1.code.startswith('1'))). \
            order_by(SetTaxAndPriceZone.location)
        locations2 = session.query(SetTaxAndPriceZone.location).distinct(). \
            filter(SetTaxAndPriceZone.geometry.ST_Within(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetTaxAndPriceZone.location)
        locations3 = session.query(SetTaxAndPriceZone.location).distinct(). \
            filter(SetTaxAndPriceZone.geometry.ST_Contains(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetTaxAndPriceZone.location)
        locations4 = session.query(SetTaxAndPriceZone.location).distinct(). \
            filter(SetTaxAndPriceZone.geometry.ST_Overlaps(AuLevel2.geometry)). \
            filter(AuLevel2.code.in_(l2_codes)). \
            order_by(SetTaxAndPriceZone.location)

        for location in locations1:
            self.zone_location_tax_cbox.addItem(location[0])
        for location in locations2:
            self.zone_location_tax_cbox.addItem(location[0])
        for location in locations3:
            self.zone_location_tax_cbox.addItem(location[0])
        for location in locations4:
            self.zone_location_tax_cbox.addItem(location[0])

    def __load_settings(self):

        self.__load_report_settings()
        self.__load_certificate_settings()
        self.__load_payment_settings()
        self.__load_logging_settings()

    def __load_report_settings(self):

        report_settings = self.__admin_settings("set_report_parameter")
        if len(report_settings) == 0:
            return

        self.land_office_name_edit.setText(report_settings[Constants.REPORT_LAND_OFFICE_NAME])
        self.phone_edit.setText(report_settings[Constants.REPORT_PHONE])
        self.fax_edit.setText(report_settings[Constants.REPORT_FAX])
        self.email_address_edit.setText(report_settings[Constants.REPORT_EMAIL])
        self.web_site_edit.setText(report_settings[Constants.REPORT_WEBSITE])
        self.bank_account_num_edit.setText(report_settings[Constants.REPORT_BANK_ACCOUNT])
        self.address_edit.setText(report_settings[Constants.REPORT_ADDRESS])
        self.bank_account_num_edit.setText(report_settings[Constants.REPORT_BANK_ACCOUNT])
        self.bank_cbox.setCurrentIndex(self.bank_cbox.findText(report_settings[Constants.REPORT_BANK]))

    def __load_certificate_settings(self):

        certificate_settings = self.__certificate_range(1)
        self.mn_citizen_first_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER])
        self.mn_citizen_last_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_LAST_NUMBER])
        self.mn_citizen_current_number_ledit.setText(str(certificate_settings[Constants.CERTIFICATE_CURRENT_NUMBER]))

        certificate_settings = self.__certificate_range(2)
        self.mn_business_first_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER])
        self.mn_business_last_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_LAST_NUMBER])
        self.mn_business_current_number_ledit.setText(str(certificate_settings[Constants.CERTIFICATE_CURRENT_NUMBER]))

        certificate_settings = self.__certificate_range(3)
        self.foreign_first_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER])
        self.foreign_last_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_LAST_NUMBER])
        self.foreign_current_number_ledit.setText(str(certificate_settings[Constants.CERTIFICATE_CURRENT_NUMBER]))

        certificate_settings = self.__certificate_range(4)
        self.mn_org_first_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER])
        self.mn_org_last_number_spinbox.setValue(certificate_settings[Constants.CERTIFICATE_LAST_NUMBER])
        self.mn_org_current_number_ledit.setText(str(certificate_settings[Constants.CERTIFICATE_CURRENT_NUMBER]))

    def __load_payment_settings(self):

        payment_settings = self.__payment_settings()
        if len(payment_settings) == 0 and payment_settings == None:
            return
        if payment_settings[Constants.PAYMENT_LANDTAX_RATE] == None:
            self.fee_finerate_spinbox.setValue(0)
            self.tax_finerate_spinbox.setValue(0)
        else:
            self.fee_finerate_spinbox.setValue(payment_settings[Constants.PAYMENT_LANDFEE_RATE])
            self.tax_finerate_spinbox.setValue(payment_settings[Constants.PAYMENT_LANDTAX_RATE])

    def __load_logging_settings(self):

        logging_settings = self.__logging_settings()
        if logging_settings:
            self.logging_chk_box.setChecked(True)

    def __save_settings(self):

        try:
            self.__save_report_settings()
            self.__save_certificate_settings()
            self.__save_payment_settings()
            self.__save_logging_settings()
            self.__save_fees()
            self.__save_taxes()
            self.__save_companies()
            self.__save_surveyors()
            self.__save_codelist_entries()
            self.__save_documents()
            self.__save_equipments()

            return True
        except exc.SQLAlchemyError,  e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            return False

        except LM2Exception, e:
            return False

    def __save_equipments(self):

        num_rows = self.equipment_twidget.rowCount()
        try:
            for row in range(num_rows):
                session = SessionHandler().session_instance()
                item = self.equipment_twidget.item(row,0)
                id = item.data(Qt.UserRole)
                equipment = session.query(SetEquipment).filter(SetEquipment.id == id).one()
                item = self.equipment_twidget.item(row,1)
                equipment.type = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,2)
                equipment.officer_user = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,3)
                equipment.purchase_date = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,4)
                equipment.given_date = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,5)
                equipment.duration_date = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,6)
                equipment.description = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,7)
                equipment.mac_address = item.data(Qt.UserRole)
                item = self.equipment_twidget.item(row,8)
                equipment.seller_name = item.data(Qt.UserRole)

                session.add(equipment)

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise
        self.__equipment_clear()

    @pyqtSlot()
    def on_add_equipment_button_clicked(self):

        if self.id_equipment_edit.text() != "":
            PluginUtils.show_message(self, self.tr("Equipment save"), self.tr("Please Save Button click!!!"))
            return

        try:
            equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
            equipment_type_text = self.equipment_list_cbox.currentText()
            officer_user = self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
            officer_user_text = self.users_list_cbox.currentText()
            decsription = self.equipment_desc_text.toPlainText()
            purchase_date = PluginUtils.convert_qt_date_to_python(self.initial_date.date())
            given_date = PluginUtils.convert_qt_date_to_python(self.given_date.date())
            duration_date = PluginUtils.convert_qt_date_to_python(self.duration_date.date())
            mac_address = self.mac_address_edit.text()
            seller_name = self.seller_name_edit.text()

            if equipment_type == -1:
                PluginUtils.show_message(self, self.tr("Equipment type"), self.tr("Equipment type is none!!!"))
                return
            if officer_user == -1:
                PluginUtils.show_message(self, self.tr("officer user"), self.tr("Officer user is none!!!"))
                return

             #session add
            session = SessionHandler().session_instance()
            user = session.query(SetRole).filter(SetRole.user_name == officer_user).one()

            set_equipment = SetEquipment()
            set_equipment.type = equipment_type
            set_equipment.officer_user = officer_user
            set_equipment.officer_user_ref = user
            set_equipment.description = decsription
            set_equipment.purchase_date = purchase_date
            set_equipment.given_date = given_date
            set_equipment.duration_date = duration_date
            set_equipment.mac_address = mac_address
            set_equipment.seller_name = seller_name

            session.add(set_equipment)
            session.commit()
            id = set_equipment.id

            id_item = QTableWidgetItem(str(id))
            id_item.setData(Qt.UserRole, id)

            equipment_type_item = QTableWidgetItem(equipment_type_text)
            equipment_type_item.setData(Qt.UserRole, equipment_type)

            officer_user_item = QTableWidgetItem(officer_user_text)
            officer_user_item.setData(Qt.UserRole, officer_user)

            decsription_item = QTableWidgetItem(decsription)
            decsription_item.setData(Qt.UserRole, decsription)

            purchase_date_item = QTableWidgetItem(str(purchase_date))
            purchase_date_item.setData(Qt.UserRole, purchase_date)

            given_date_item = QTableWidgetItem(str(given_date))
            given_date_item.setData(Qt.UserRole, given_date)

            duration_date_item = QTableWidgetItem(str(duration_date))
            duration_date_item.setData(Qt.UserRole, duration_date)

            mac_address_item = QTableWidgetItem(mac_address)
            mac_address_item.setData(Qt.UserRole, mac_address)

            seller_name_item = QTableWidgetItem(seller_name)
            seller_name_item.setData(Qt.UserRole, seller_name)

            row = self.equipment_twidget.rowCount()
            self.equipment_twidget.insertRow(row)

            self.equipment_twidget.setItem(row, 0, id_item)
            self.equipment_twidget.setItem(row, 1, equipment_type_item)
            self.equipment_twidget.setItem(row, 2, officer_user_item)
            self.equipment_twidget.setItem(row, 3, purchase_date_item)
            self.equipment_twidget.setItem(row, 4, given_date_item)
            self.equipment_twidget.setItem(row, 5, duration_date_item)
            self.equipment_twidget.setItem(row, 6, decsription_item)
            self.equipment_twidget.setItem(row, 7, mac_address_item)
            self.equipment_twidget.setItem(row, 8, seller_name_item)

            self.__equipment_clear()

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise

    # @pyqtSlot()
    # def on_equipment_twidget_itemSelectionChanged(self):

    @pyqtSlot(QTableWidgetItem)
    def on_equipment_twidget_itemClicked(self, item):

        self.equipment_twidget.selectAll()
        self.add_equipment_button.setDisabled(True)
        self.add_equip_doc_button.setEnabled(True)
        self.view_equip_doc_button.setEnabled(True)
        self.delete_equip_doc_button.setEnabled(True)

        current_row = self.equipment_twidget.currentRow()
        id_item = self.equipment_twidget.item(current_row, 0)
        id = ""
        if id_item is not None:
            id = id_item.data(Qt.UserRole)

        equipment_type_item = self.equipment_twidget.item(current_row, 1)
        user_item = self.equipment_twidget.item(current_row, 2)
        purchase_date_item = self.equipment_twidget.item(current_row, 3)
        given_date_item = self.equipment_twidget.item(current_row, 4)
        duration_date_item = self.equipment_twidget.item(current_row, 5)
        description_item = self.equipment_twidget.item(current_row, 6)
        mac_address_item = self.equipment_twidget.item(current_row, 7)
        seller_name_item = self.equipment_twidget.item(current_row, 8)

        self.id_equipment_edit.setText(str(id))
        equipment_type = None
        user = None
        purchase_date = None
        if equipment_type_item is not None:
             equipment_type = equipment_type_item.data(Qt.UserRole)
        if user_item is not None:
            user = user_item.data(Qt.UserRole)
        if purchase_date_item is not None:
            purchase_date = purchase_date_item.data(Qt.UserRole)
        if given_date_item is not None:
            given_date = given_date_item.data(Qt.UserRole)
        if duration_date_item is not None:
            duration_date = duration_date_item.data(Qt.UserRole)
        if description_item is not None:
            description = description_item.data(Qt.UserRole)
        if mac_address_item is not None:
            mac_address = mac_address_item.data(Qt.UserRole)
        if seller_name_item is not None:
            seller_name = seller_name_item.data(Qt.UserRole)
        self.equipment_list_cbox.setCurrentIndex(self.equipment_list_cbox.findData(equipment_type))
        self.users_list_cbox.setCurrentIndex(self.users_list_cbox.findData(user))
        self.initial_date.setDate(purchase_date)
        self.given_date.setDate(given_date)
        self.duration_date.setDate(duration_date)
        self.equipment_desc_text.setText(description)
        self.mac_address_edit.setText(mac_address)
        self.seller_name_edit.setText(seller_name)

        self.equipment_doc_twidget.clear()

        try:
            session = SessionHandler().session_instance()
            equipment = session.query(SetEquipment)
            if not self.id_equipment_edit.text() == "":
                filter_is_set = True
                equipment = equipment.filter(SetEquipment.id == id)
            self.equipment_twidget.setRowCount(0)
            row = 0
            for items in equipment:
                self.equipment_twidget.insertRow(row)

                item = QTableWidgetItem(str(items.id))
                item.setData(Qt.UserRole, items.id)
                self.equipment_twidget.setItem(row, 0, item)

                equipment_type = session.query(ClEquipmentList).filter(ClEquipmentList.code == items.type).one()
                item = QTableWidgetItem(equipment_type.description)
                item.setData(Qt.UserRole, items.type)
                self.equipment_twidget.setItem(row, 1, item)

                user = session.query(SetRole).filter(SetRole.user_name == items.officer_user).one()
                display_name = items.officer_user +": "+ user.surname[:1] + u"."+ user.first_name
                item = QTableWidgetItem(display_name)
                item.setData(Qt.UserRole, items.officer_user)
                self.equipment_twidget.setItem(row, 2, item)

                item = QTableWidgetItem(str(items.purchase_date))
                item.setData(Qt.UserRole, items.purchase_date)
                self.equipment_twidget.setItem(row, 3, item)

                item = QTableWidgetItem(str(items.given_date))
                item.setData(Qt.UserRole, items.given_date)
                self.equipment_twidget.setItem(row, 4, item)

                item = QTableWidgetItem(str(items.duration_date))
                item.setData(Qt.UserRole, items.duration_date)
                self.equipment_twidget.setItem(row, 5, item)

                item = QTableWidgetItem(items.description)
                item.setData(Qt.UserRole, items.description)
                self.equipment_twidget.setItem(row, 6, item)

                item = QTableWidgetItem(items.mac_address)
                item.setData(Qt.UserRole, items.mac_address)
                self.equipment_twidget.setItem(row, 7, item)

                item = QTableWidgetItem(items.seller_name)
                item.setData(Qt.UserRole, items.seller_name)
                self.equipment_twidget.setItem(row, 8, item)

                row += 1
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        try:
            session = SessionHandler().session_instance()

            equipment_doc = session.query(SetEquipmentDocument).filter(SetEquipmentDocument.equipment == id).all()
            row = 0
            for item in equipment_doc:
                document_id = item.document
                document = session.query(SetDocument).filter(SetDocument.id == document_id).one()

                item = QListWidgetItem(document.name, self.equipment_doc_twidget)
                item.setData(Qt.UserRole, document_id)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        # print self.equipment_twidget.selectRow(0)
        self.equipment_twidget.selectRow(0)

    def __seller_name_auto_choose(self):

        try:
            session = SessionHandler().session_instance()
            seller_list = session.query(SetEquipment.seller_name).order_by(SetEquipment.seller_name.desc()).all()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))
            self.reject()

        seller_slist = []

        for seller in seller_list:
            if seller[0]:
                seller_slist.append(seller[0])

        seller_model = QStringListModel(seller_slist)
        self.sellerProxyModel = QSortFilterProxyModel()
        self.sellerProxyModel.setSourceModel(seller_model)
        self.sellerCompleter = QCompleter(self.sellerProxyModel, self, activated=self.on_seller_completer_activated)
        self.sellerCompleter.setCompletionMode(QCompleter.PopupCompletion)
        self.seller_name_edit.setCompleter(self.sellerCompleter)

    @pyqtSlot(str)
    def on_seller_completer_activated(self, text):

        if not text:
            return
        self.sellerCompleter.activated[str].emit(text)

    def __set_up_equipment_tab(self):

        self.__seller_name_auto_choose()
        self.equipment_twidget.setRowCount(0)
        try:
            session = SessionHandler().session_instance()
            equipment = session.query(SetEquipment).all()
            row = 0
            for items in equipment:
                self.equipment_twidget.insertRow(row)

                item = QTableWidgetItem(str(items.id))
                item.setData(Qt.UserRole, items.id)
                self.equipment_twidget.setItem(row, 0, item)

                equipment_type = session.query(ClEquipmentList).filter(ClEquipmentList.code == items.type).one()
                item = QTableWidgetItem(equipment_type.description)
                item.setData(Qt.UserRole, items.type)
                self.equipment_twidget.setItem(row, 1, item)

                user = session.query(SetRole).filter(SetRole.user_name == items.officer_user).one()
                display_name = items.officer_user +": "+ user.surname[:1] + u"."+ user.first_name
                item = QTableWidgetItem(display_name)
                item.setData(Qt.UserRole, items.officer_user)
                self.equipment_twidget.setItem(row, 2, item)

                item = QTableWidgetItem(str(items.purchase_date))
                item.setData(Qt.UserRole, items.purchase_date)
                self.equipment_twidget.setItem(row, 3, item)

                item = QTableWidgetItem(str(items.given_date))
                item.setData(Qt.UserRole, items.given_date)
                self.equipment_twidget.setItem(row, 4, item)

                item = QTableWidgetItem(str(items.duration_date))
                item.setData(Qt.UserRole, items.duration_date)
                self.equipment_twidget.setItem(row, 5, item)

                item = QTableWidgetItem(items.description)
                item.setData(Qt.UserRole, items.description)
                self.equipment_twidget.setItem(row, 6, item)

                item = QTableWidgetItem(items.mac_address)
                item.setData(Qt.UserRole, items.mac_address)
                self.equipment_twidget.setItem(row, 7, item)

                item = QTableWidgetItem(items.seller_name)
                item.setData(Qt.UserRole, items.seller_name)
                self.equipment_twidget.setItem(row, 8, item)

                row += 1

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    @pyqtSlot()
    def on_edit_equipment_button_clicked(self):

        if self.equipment_twidget.rowCount() == 0:
            PluginUtils.show_message(self, self.tr("No row"), self.tr("Equipment no row!!!"))
            return

        self.add_equipment_button.setEnabled(True)
        self.equipment_doc_twidget.clear()
        self.add_equip_doc_button.setDisabled(True)
        self.view_equip_doc_button.setDisabled(True)
        self.delete_equip_doc_button.setDisabled(True)

        selected_row = self.equipment_twidget.currentRow()

        equipment_type_item = self.equipment_twidget.item(selected_row, 1)
        officer_user_item = self.equipment_twidget.item(selected_row, 2)
        purchase_date_item = self.equipment_twidget.item(selected_row, 3)
        given_date_item = self.equipment_twidget.item(selected_row, 4)
        duration_date_item = self.equipment_twidget.item(selected_row, 5)
        decsription_item = self.equipment_twidget.item(selected_row, 6)
        mac_address_item = self.equipment_twidget.item(selected_row, 7)
        seller_name_item = self.equipment_twidget.item(selected_row, 8)

        equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
        equipment_type_text = self.equipment_list_cbox.currentText()
        officer_user = self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
        officer_user_text = self.users_list_cbox.currentText()
        decsription = self.equipment_desc_text.toPlainText()
        purchase_date = PluginUtils.convert_qt_date_to_python(self.initial_date.date())
        given_date = PluginUtils.convert_qt_date_to_python(self.given_date.date())
        duration_date = PluginUtils.convert_qt_date_to_python(self.duration_date.date())
        mac_address = self.mac_address_edit.text()
        seller_name = self.seller_name_edit.text()

        if equipment_type == -1:
            PluginUtils.show_message(self, self.tr("Equipment type"), self.tr("Equipment type is none!!!"))
            return
        if officer_user == -1:
            PluginUtils.show_message(self, self.tr("officer user"), self.tr("Officer user is none!!!"))
            return

        equipment_type_item.setText(equipment_type_text)
        equipment_type_item.setData(Qt.UserRole, equipment_type)
        officer_user_item.setText(officer_user_text)
        officer_user_item.setData(Qt.UserRole, officer_user)
        purchase_date_item.setText(str(purchase_date))
        purchase_date_item.setData(Qt.UserRole, purchase_date)
        given_date_item.setText(str(given_date))
        given_date_item.setData(Qt.UserRole, given_date)
        duration_date_item.setText(str(duration_date))
        duration_date_item.setData(Qt.UserRole, duration_date)
        decsription_item.setText(decsription)
        decsription_item.setData(Qt.UserRole, decsription)
        mac_address_item.setText(mac_address)
        mac_address_item.setData(Qt.UserRole, mac_address)
        seller_name_item.setText(seller_name)
        seller_name_item.setData(Qt.UserRole, seller_name)

        # self.__equipment_clear()

    @pyqtSlot()
    def on_add_equip_doc_button_clicked(self):

        current_row = self.equipment_twidget.currentRow()
        id_item = self.equipment_twidget.item(current_row, 0)
        id = id_item.data(Qt.UserRole)

        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Decision Files (*.img *.png *.xls *.xlsx *.pdf)"))

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            file_name = QFileInfo(file_path).fileName()

            self.create_savepoint()

            try:
                session = SessionHandler().session_instance()
                equipment = session.query(SetEquipment).filter(SetEquipment.id == id).one()

                equipment_doc = SetEquipmentDocument()
                equipment_doc.equipment = id
                equipment_doc.equipment_ref = equipment

                doc = SetDocument()
                doc.name = file_name
                data = DatabaseUtils.file_data(file_path)
                doc.content = bytes(data)
                session.add(doc)

                equipment_doc.document_ref = doc
                equipment_doc.document = doc.id
                session.add(equipment_doc)

                item = QListWidgetItem(file_name, self.equipment_doc_twidget)
                item.setData(Qt.UserRole, doc.id)

            except SQLAlchemyError, e:
                self.rollback_to_savepoint()
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

    @pyqtSlot()
    def on_view_equip_doc_button_clicked(self):

        current_row = self.equipment_doc_twidget.currentRow()
        if current_row == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("Select Item."))
            return
        byte_array_item = self.equipment_doc_twidget.selectedItems()[0]
        doc = byte_array_item.data(Qt.UserRole)
        session = SessionHandler().session_instance()
        byte_array = session.query(SetDocument).filter(SetDocument.id == doc).one()
        # byte_array = dec_doc.document_ref.content

        if byte_array is None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No digital documents available."))
            return False
        else:
            current_bytes = QByteArray(byte_array.content)
            new_file_path = FileUtils.temp_file_path() + "/" + unicode(byte_array_item.text())

            new_file = QFile(new_file_path)
            new_file.open(QIODevice.WriteOnly)
            new_file.write(current_bytes.data())
            new_file.close()
            QDesktopServices.openUrl(QUrl.fromLocalFile(new_file_path))

    @pyqtSlot()
    def on_delete_equip_doc_button_clicked(self):

        byte_array_item = self.equipment_doc_twidget.selectedItems()[0]
        item_index = self.equipment_doc_twidget.selectedIndexes()[0]
        doc = byte_array_item.data(Qt.UserRole)

        self.create_savepoint()

        try:
            session = SessionHandler().session_instance()
            equipment_document = session.query(SetEquipmentDocument).filter(SetEquipmentDocument.document == doc).one()
            document = session.query(SetDocument).filter(SetDocument.id == doc).one()
            session.delete(equipment_document)
            session.delete(document)
            self.equipment_doc_twidget.takeItem(item_index.row())

        except SQLAlchemyError, e:
            self.rollback_to_savepoint()
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    def __equipment_clear(self):

        self.id_equipment_edit.setText("")
        self.equipment_list_cbox.setCurrentIndex(0)
        self.users_list_cbox.setCurrentIndex(0)
        self.initial_date.setDate(QDate().currentDate())
        self.given_date.setDate(QDate().currentDate())
        self.duration_date.setDate(QDate().currentDate())
        self.mac_address_edit.setText("")
        self.equipment_desc_text.setText("")
        self.seller_name_edit.setText("")
        self.add_equipment_button.setEnabled(True)

    @pyqtSlot()
    def on_delete_equipment_button_clicked(self):

        current_row = self.equipment_twidget.currentRow()
        id_item = self.equipment_twidget.item(current_row, 0)
        id = id_item.data(Qt.UserRole)
        message_box = QMessageBox()
        message_box.setText(self.tr("Do you want to delete for equipment"))

        yes_button = message_box.addButton(self.tr("Yes"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("No"), QMessageBox.ActionRole)
        message_box.exec_()

        if message_box.clickedButton() == yes_button:
            try:
                session = SessionHandler().session_instance()
                equipment = session.query(SetEquipment).filter(SetEquipment.id == id).one()
                equipment_document = session.query(SetEquipmentDocument).filter(SetEquipmentDocument.equipment == id).all()
                for item in equipment_document:
                    document = session.query(SetDocument).filter(SetDocument.id == item.document).one()
                    session.delete(document)
                    session.delete(item)
                equipment = session.query(SetEquipment).filter(SetEquipment.id == id).one()
                session.delete(equipment)
                self.equipment_twidget.removeRow(current_row)

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

    @pyqtSlot()
    def on_equipment_find_button_clicked(self):

        print "ok"

    @pyqtSlot(int)
    def on_users_list_cbox_currentIndexChanged(self, idx):

        if self.id_equipment_edit.text() == "":
            self.equipment_twidget.setRowCount(0)
            if idx == -1:
                return
            equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
            officer_user = self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
            filter_is_set = False
            try:
                session = SessionHandler().session_instance()
                equipment = session.query(SetEquipment)
                if not self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex()) == -1:
                    filter_is_set = True
                    equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
                    equipment = equipment.filter(SetEquipment.type == equipment_type)

                if not self.users_list_cbox.itemData(self.users_list_cbox.currentIndex()) == -1:
                    filter_is_set = True
                    officer= self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
                    equipment = equipment.filter(SetEquipment.officer_user == officer)

                if not self.id_equipment_edit.text() == "":
                    filter_is_set = True
                    id = int(self.id_equipment_edit.text())
                    equipment = equipment.filter(SetEquipment.id == id)

                row = 0
                for items in equipment:
                    self.equipment_twidget.insertRow(row)

                    item = QTableWidgetItem(str(items.id))
                    item.setData(Qt.UserRole, items.id)
                    self.equipment_twidget.setItem(row, 0, item)

                    equipment_type = session.query(ClEquipmentList).filter(ClEquipmentList.code == items.type).one()
                    item = QTableWidgetItem(equipment_type.description)
                    item.setData(Qt.UserRole, items.type)
                    self.equipment_twidget.setItem(row, 1, item)

                    user = session.query(SetRole).filter(SetRole.user_name == items.officer_user).one()
                    display_name = items.officer_user +": "+ user.surname[:1] + u"."+ user.first_name
                    item = QTableWidgetItem(display_name)
                    item.setData(Qt.UserRole, items.officer_user)
                    self.equipment_twidget.setItem(row, 2, item)

                    item = QTableWidgetItem(str(items.purchase_date))
                    item.setData(Qt.UserRole, items.purchase_date)
                    self.equipment_twidget.setItem(row, 3, item)

                    item = QTableWidgetItem(str(items.given_date))
                    item.setData(Qt.UserRole, items.given_date)
                    self.equipment_twidget.setItem(row, 4, item)

                    item = QTableWidgetItem(str(items.duration_date))
                    item.setData(Qt.UserRole, items.duration_date)
                    self.equipment_twidget.setItem(row, 5, item)

                    item = QTableWidgetItem(items.description)
                    item.setData(Qt.UserRole, items.description)
                    self.equipment_twidget.setItem(row, 6, item)

                    item = QTableWidgetItem(items.mac_address)
                    item.setData(Qt.UserRole, items.mac_address)
                    self.equipment_twidget.setItem(row, 7, item)

                    item = QTableWidgetItem(items.seller_name)
                    item.setData(Qt.UserRole, items.seller_name)
                    self.equipment_twidget.setItem(row, 8, item)

                    row += 1

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

    @pyqtSlot(int)
    def on_equipment_list_cbox_currentIndexChanged(self, idx):

        if self.id_equipment_edit.text() == "":
            self.equipment_twidget.setRowCount(0)
            if idx == -1:
                return
            equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
            officer_user = self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
            filter_is_set = False
            try:
                session = SessionHandler().session_instance()
                equipment = session.query(SetEquipment)
                if not self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex()) == -1:
                    filter_is_set = True
                    equipment_type = self.equipment_list_cbox.itemData(self.equipment_list_cbox.currentIndex())
                    equipment = equipment.filter(SetEquipment.type == equipment_type)

                if not self.users_list_cbox.itemData(self.users_list_cbox.currentIndex()) == -1:
                    filter_is_set = True
                    officer= self.users_list_cbox.itemData(self.users_list_cbox.currentIndex())
                    equipment = equipment.filter(SetEquipment.officer_user == officer)

                if not self.id_equipment_edit.text() == "":
                    filter_is_set = True
                    id = int(self.id_equipment_edit.text())
                    equipment = equipment.filter(SetEquipment.id == id)

                row = 0
                for items in equipment:
                    self.equipment_twidget.insertRow(row)

                    item = QTableWidgetItem(str(items.id))
                    item.setData(Qt.UserRole, items.id)
                    self.equipment_twidget.setItem(row, 0, item)

                    equipment_type = session.query(ClEquipmentList).filter(ClEquipmentList.code == items.type).one()
                    item = QTableWidgetItem(equipment_type.description)
                    item.setData(Qt.UserRole, items.type)
                    self.equipment_twidget.setItem(row, 1, item)

                    user = session.query(SetRole).filter(SetRole.user_name == items.officer_user).one()
                    display_name = items.officer_user +": "+ user.surname[:1] + u"."+ user.first_name
                    item = QTableWidgetItem(display_name)
                    item.setData(Qt.UserRole, items.officer_user)
                    self.equipment_twidget.setItem(row, 2, item)

                    item = QTableWidgetItem(str(items.purchase_date))
                    item.setData(Qt.UserRole, items.purchase_date)
                    self.equipment_twidget.setItem(row, 3, item)

                    item = QTableWidgetItem(str(items.given_date))
                    item.setData(Qt.UserRole, items.given_date)
                    self.equipment_twidget.setItem(row, 4, item)

                    item = QTableWidgetItem(str(items.duration_date))
                    item.setData(Qt.UserRole, items.duration_date)
                    self.equipment_twidget.setItem(row, 5, item)

                    item = QTableWidgetItem(items.description)
                    item.setData(Qt.UserRole, items.description)
                    self.equipment_twidget.setItem(row, 6, item)

                    item = QTableWidgetItem(items.mac_address)
                    item.setData(Qt.UserRole, items.mac_address)
                    self.equipment_twidget.setItem(row, 7, item)

                    item = QTableWidgetItem(items.seller_name)
                    item.setData(Qt.UserRole, items.seller_name)
                    self.equipment_twidget.setItem(row, 8, item)

                    row += 1

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("File Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return


    def __save_report_settings(self):

        report_settings = {Constants.REPORT_LAND_OFFICE_NAME: self.land_office_name_edit.text(),
                           Constants.REPORT_ADDRESS: self.address_edit.toPlainText(),
                           Constants.REPORT_BANK: self.bank_cbox.currentText(),
                           Constants.REPORT_BANK_ACCOUNT: self.bank_account_num_edit.text(),
                           Constants.REPORT_PHONE: self.phone_edit.text(), Constants.REPORT_FAX: self.fax_edit.text(),
                           Constants.REPORT_EMAIL: self.email_address_edit.text(),
                           Constants.REPORT_WEBSITE: self.web_site_edit.text()}

        self.__write_report_settings(report_settings)

    def __save_certificate_settings(self):

        certificate_settings = {Constants.CERTIFICATE_FIRST_NUMBER: self.mn_citizen_first_number_spinbox.value(),
                                Constants.CERTIFICATE_LAST_NUMBER: self.mn_citizen_last_number_spinbox.value()}

        self.__write_certificate_settings(certificate_settings, 1)

        certificate_settings = {Constants.CERTIFICATE_FIRST_NUMBER: self.mn_business_first_number_spinbox.value(),
                                Constants.CERTIFICATE_LAST_NUMBER: self.mn_business_last_number_spinbox.value()}

        self.__write_certificate_settings(certificate_settings, 2)

        certificate_settings = {Constants.CERTIFICATE_FIRST_NUMBER: self.foreign_first_number_spinbox.value(),
                                Constants.CERTIFICATE_LAST_NUMBER: self.foreign_last_number_spinbox.value()}

        self.__write_certificate_settings(certificate_settings, 3)

        certificate_settings = {Constants.CERTIFICATE_FIRST_NUMBER: self.mn_org_first_number_spinbox.value(),
                                Constants.CERTIFICATE_LAST_NUMBER: self.mn_org_last_number_spinbox.value()}

        self.__write_certificate_settings(certificate_settings, 4)

    def __save_payment_settings(self):

        payment_settings = {Constants.PAYMENT_LANDFEE_RATE: self.fee_finerate_spinbox.value(),
                            Constants.PAYMENT_LANDTAX_RATE: self.tax_finerate_spinbox.value()}

        self.__write_payment_settings(payment_settings)

    def __save_logging_settings(self):

        self.__write_logging_settings(self.logging_chk_box.isChecked())

    @pyqtSlot()
    def on_apply_button_clicked(self):

        if not self.__save_settings():
            return

        self.commit()
        self.__start_fade_out_timer()

    def __start_fade_out_timer(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.__fade_status_message)
        self.time_counter = 500
        self.timer.start(10)

    def __fade_status_message(self):

        opacity = int(self.time_counter * 0.5)
        self.status_label.setStyleSheet("QLabel {color: rgba(255,0,0," + str(opacity) + ");}")
        self.status_label.setText(self.tr('Changes applied successfully.'))
        if self.time_counter == 0:
            self.timer.stop()
        self.time_counter -= 1

    @pyqtSlot(int)
    def on_select_codelist_cbox_currentIndexChanged(self, idx):

        if idx == -1:
            return

        if self.old_codelist_index == idx:
            return

        if self.old_codelist_index == -1:
            self.__read_codelist_entries()
        else:
            try:
                self.__save_codelist_entries()
            except exc.SQLAlchemyError, e:
                PluginUtils.show_error(None, self.tr("SQL Error"), e.message)
                self.select_codelist_cbox.setCurrentIndex(self.old_codelist_index)
                return

        self.old_codelist_index = idx

    def __read_codelist_entries(self):

        self.table_widget.clearContents()
        self.table_widget.setRowCount(0)
        session = SessionHandler().session_instance()

        codelist_name = self.select_codelist_cbox.itemData(self.select_codelist_cbox.currentIndex())
        codelist_class = self.__codelist_class(codelist_name)
        codelist_entries = session.query(codelist_class).order_by(codelist_class.code).all()
        self.table_widget.setRowCount(len(codelist_entries))
        row = 0
        for entry in codelist_entries:
            self.__add_codelist_row(row, entry.code, entry.description)
            row += 1

        self.table_widget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)


    def __add_codelist_row(self, row, code, description, lock_item=True):

        if lock_item:
            item = QTableWidgetItem('{0}'.format(code))
            item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        else:
            item = QTableWidgetItem()

        item.setData(Qt.UserRole, code)
        self.table_widget.setItem(row, CODELIST_CODE, item)
        item = QTableWidgetItem(description)
        self.table_widget.setItem(row, CODELIST_DESC, item)

    def __save_codelist_entries(self):

        codelist_name = self.select_codelist_cbox.itemData(self.old_codelist_index, Qt.UserRole)
        codelist_class = self.__codelist_class(codelist_name)

        session = SessionHandler().session_instance()
        self.create_savepoint()

        try:
            for row in range(self.table_widget.rowCount()):
                new_row = False

                code = self.table_widget.item(row, CODELIST_CODE).data(Qt.UserRole)

                if self.table_widget.item(row, CODELIST_CODE).text() == -1:
                    self.status_label.setText(self.tr("-1 is not allowed for code in codelists."))
                    self.rollback_to_savepoint()

                if code == -1:
                    new_row = True
                    # noinspection PyCallingNonCallable
                    codelist_entry = codelist_class()
                else:
                    codelist_entry = session.query(codelist_class).get(code)

                try:
                    code_int = int(self.table_widget.item(row, CODELIST_CODE).text())

                except ValueError:
                    self.status_label.setText(self.tr("A code in the codelist has a wrong value."))
                    self.rollback_to_savepoint()
                    raise LM2Exception(self.tr("Error"), self.tr("A code in the codelist has a wrong value."))

                description = self.table_widget.item(row, CODELIST_DESC).text()
                codelist_entry.code = code_int
                codelist_entry.description = description

                if new_row:
                    session.add(codelist_entry)

        except exc.SQLAlchemyError:
            self.rollback_to_savepoint()
            raise

        self.__read_codelist_entries()

    def __save_documents(self):

        session = SessionHandler().session_instance()

        for i in range(self.doc_twidget.rowCount()):

            item_name = self.doc_twidget.item(i, DOC_NAME_COLUMN)
            item_description = self.doc_twidget.item(i, DOC_DESCRIPTION_COLUMN)
            item_visible = self.doc_twidget.item(i, DOC_VISIBLE_COLUMN)
            item_open = self.doc_twidget.item(i, DOC_OPEN_FILE_COLUMN)
            current_id = item_name.data(Qt.UserRole)

            if current_id == -1:
                document = SetOfficialDocument()
                session.add(document)
                session.flush()

                item_name.setData(Qt.UserRole, document.id)
                self.doc_twidget.setItem(i, DOC_NAME_COLUMN, item_name)
            else:
                document = session.query(SetOfficialDocument).get(current_id)

            document.name = item_name.text()
            document.description = item_description.text()
            if item_visible.checkState() == Qt.Checked:
                document.visible = True
            else:
                document.visible = False

            path = item_open.data(Qt.UserRole)
            #if file path is -1 it is an existing one & untouched
            if path != -1:
                file_info = QFileInfo(path)
                file_content = DatabaseUtils.file_data(file_info.filePath())
                document.content = bytes(file_content)

    @pyqtSlot()
    def on_add_button_clicked(self):

        if self.select_codelist_cbox.currentIndex() == -1:
            return

        row = self.table_widget.rowCount()
        self.table_widget.insertRow(row)

        self.__add_codelist_row(row, -1, None, False)

    @pyqtSlot()
    def on_delete_button_clicked(self):

        row = self.table_widget.currentRow()
        if row == -1:
            return

        codelist_name = self.select_codelist_cbox.itemData(self.select_codelist_cbox.currentIndex(), Qt.UserRole)
        codelist_class = self.__codelist_class(codelist_name)

        code = self.table_widget.item(row, CODELIST_CODE).data(Qt.UserRole)
        session = SessionHandler().session_instance()
        count = session.query(codelist_class).filter(codelist_class.code == code).count()
        if count > 0:
            entry = session.query(codelist_class).get(code)
            self.create_savepoint()
            try:
                session.delete(entry)

            except exc.SQLAlchemyError, e:
                self.rollback_to_savepoint()
                PluginUtils.show_error(None, self.tr("SQL Error"), e.message)
                return

        self.table_widget.removeRow(row)

    def __codelist_names(self):

        lookup = {}
        session = SessionHandler().session_instance()

        try:
            sql = text("select description, relname from pg_description join pg_class on pg_description.objoid = pg_class.oid join pg_namespace on pg_namespace.oid = pg_class.relnamespace where pg_namespace.nspname = 'codelists';")
            result = session.execute(sql).fetchall()

            for row in result:
                lookup[row[1]] = row[0]

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

        return lookup

    def __write_logging_settings(self, log_level):

        session = SessionHandler().session_instance()

        try:
            sql = text("UPDATE settings.set_logging SET log_enabled = :logLevel;")
            session.execute(sql, {'logLevel': log_level})

        except exc.SQLAlchemyError:
            raise

    def __write_payment_settings(self, payment_settings):

        session = SessionHandler().session_instance()

        try:
            sql = text(
                "UPDATE settings.set_payment SET landfee_fine_rate_per_day = :landfee, landtax_fine_rate_per_day = :landtax;")
            session.execute(sql, {'landfee': payment_settings[Constants.PAYMENT_LANDFEE_RATE],
                                  'landtax': payment_settings[Constants.PAYMENT_LANDTAX_RATE]})

        except exc.SQLAlchemyError:
            raise

    def __write_certificate_settings(self, certificate_settings, certificate_type):

        session = SessionHandler().session_instance()

        try:
            certificate_set = session.query(SetCertificate).get(certificate_type)
            certificate_set.range_first_no = certificate_settings[Constants.CERTIFICATE_FIRST_NUMBER]
            certificate_set.range_last_no = certificate_settings[Constants.CERTIFICATE_LAST_NUMBER]
            session.flush()

        except exc.SQLAlchemyError:
            raise

    def __write_report_settings(self, report_settings):

        session = SessionHandler().session_instance()

        for key_name, value in report_settings.iteritems():

            try:
                sql = text("UPDATE settings.set_report_parameter SET value = :bindValue WHERE name = :bindKey;")
                session.execute(sql, {'bindValue': value, 'bindKey': key_name})

            except exc.SQLAlchemyError:
                raise

    def __logging_settings(self):

        session = SessionHandler().session_instance()
        enabled = False

        try:
            sql = text("SELECT * FROM settings.set_logging;")
            result = session.execute(sql).fetchall()

            for row in result:
                return row[0]

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)


    def __payment_settings(self):

        session = SessionHandler().session_instance()
        lookup = {}

        try:
            sql = text("SELECT * FROM settings.set_payment;")
            result = session.execute(sql).fetchall()

            for row in result:
                lookup[Constants.PAYMENT_LANDTAX_RATE] = row[2]
                lookup[Constants.PAYMENT_LANDFEE_RATE] = row[1]

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

        return lookup

    def __certificate_range(self, certificate_type):

        session = SessionHandler().session_instance()
        first_no, last_no, current_no = session.query(SetCertificate.range_first_no, SetCertificate.range_last_no, SetCertificate.current_no).filter(SetCertificate.type == certificate_type).one()
        return {Constants.CERTIFICATE_FIRST_NUMBER: first_no, Constants.CERTIFICATE_LAST_NUMBER: last_no, Constants.CERTIFICATE_CURRENT_NUMBER: current_no}

    def __admin_settings(self, table_name):

        session = SessionHandler().session_instance()
        lookup = {}
        try:
            sql = "SELECT * FROM settings.{0};".format(table_name)
            result = session.execute(sql).fetchall()
            for row in result:
                lookup[row[0]] = row[1]

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

        return lookup

    def __codelist_class(self, table_name):

        if table_name == 'cl_application_role':
            cls = ClApplicationRole
        elif table_name == "cl_application_status":
            cls = ClApplicationStatus
        elif table_name == "cl_application_type":
            cls = ClApplicationType
        elif table_name == "cl_bank":
            cls = ClBank
        elif table_name == "cl_contract_cancellation_reason":
            cls = ClContractCancellationReason
        elif table_name == "cl_contract_status":
            cls = ClContractStatus
        elif table_name == "cl_contract_condition":
            cls = ClContractCondition
        elif table_name == "cl_decision":
            cls = ClDecision
        elif table_name == "cl_decision_level":
            cls = ClDecisionLevel
        elif table_name == "cl_document_role":
            cls = ClDocumentRole
        elif table_name == "cl_gender":
            cls = ClGender
        elif table_name == "cl_landuse_type":
            cls = ClLanduseType
        #elif table_name == "cl_log_level":
        #    cls = ClLogLevel
        elif table_name == "cl_mortgage_type":
            cls = ClMortgageType
        elif table_name == "cl_payment_frequency":
            cls = ClPaymentFrequency
        elif table_name == "cl_person_role":
            cls = ClPersonRole
        elif table_name == "cl_person_type":
            cls = ClPersonType
        elif table_name == "cl_record_cancellation_reason":
            cls = ClRecordCancellationReason
        elif table_name == "cl_record_status":
            cls = ClRecordStatus
        elif table_name == "cl_record_right_type":
            cls = ClRecordRightType
        elif table_name == "cl_transfer_type":
            cls = ClTransferType
        elif table_name == "cl_right_type":
            cls = ClRightType
        elif table_name == "cl_equipment_list":
            cls = ClEquipmentList
        elif table_name == "va_type_agriculture":
            cls = VaTypeAgriculture
        elif table_name == "va_type_design":
            cls = VaTypeDesign
        elif table_name == "va_type_heat":
            cls = VaTypeHeat
        elif table_name == "va_type_landuse_building":
            cls = VaTypeLanduseBuilding
        elif table_name == "va_type_material":
            cls = VaTypeMaterial
        elif table_name == "va_type_parcel":
            cls = VaTypeParcel
        elif table_name == "va_type_purchase_or_lease":
            cls = VaTypePurchaseOrLease
        elif table_name == "va_type_side_fence":
            cls = VaTypeSideFence
        elif table_name == "va_type_source":
            cls = VaTypeSource
        elif table_name == "va_type_status_building":
            cls = VaTypeStatusBuilding
        elif table_name == "va_type_stove":
            cls = VaTypeStove
        elif table_name == "cl_position_type":
            cls = ClPositionType
        else:
            return None

        return cls

    @pyqtSlot(int)
    def on_zone_location_cbox_currentIndexChanged(self, idx):

        self.zones_lwidget.clear()
        self.from_zone_cbox.clear()
        self.to_zone_cbox.clear()
        session = SessionHandler().session_instance()
        location = self.zone_location_cbox.currentText()

        if idx == -1:
            return

        zones = session.query(SetFeeZone.fid, SetFeeZone.zone_no). \
            filter(SetFeeZone.location == location).order_by(SetFeeZone.zone_no)

        for fid, zone_no in zones:
            item = QListWidgetItem('{0}'.format(zone_no), self.zones_lwidget)
            item.setData(Qt.UserRole, fid)
            self.from_zone_cbox.addItem(str(zone_no), fid)
            self.to_zone_cbox.addItem(str(zone_no), fid)

        if self.zones_lwidget.count() > 0:
            self.zones_lwidget.setCurrentRow(0)
        if self.to_zone_cbox.count() > 1:
            self.to_zone_cbox.setCurrentIndex(1)

        zone_fid = self.zones_lwidget.item(self.zones_lwidget.currentRow()).data(Qt.UserRole)
        zone = session.query(SetFeeZone).filter(SetFeeZone.fid == zone_fid).one()

        zone_no = zone.zone_no
        self.landuse_code_list = list()
        del self.landuse_code_list[:]

        if zone_no == 50 or zone_no == 60 or zone_no == 70 or zone_no == 80:
            for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                    filter(ClLanduseType.code2.in_([11,12,13,14,15])).all():
                self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            delegate = LandUseComboBoxDelegate(FEE_LAND_USE, self.landuse_code_list, self.land_fee_twidget)
            self.land_fee_twidget.setItemDelegateForColumn(FEE_LAND_USE, delegate)
        else:
            for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                    filter(ClLanduseType.code2 != 11, ClLanduseType.code2 != 12, ClLanduseType.code2 != 13 \
                               , ClLanduseType.code2 != 14, ClLanduseType.code2 != 15).all():
                self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            delegate = LandUseComboBoxDelegate(FEE_LAND_USE, self.landuse_code_list, self.land_fee_twidget)
            self.land_fee_twidget.setItemDelegateForColumn(FEE_LAND_USE, delegate)

    @pyqtSlot(int)
    def on_zone_location_tax_cbox_currentIndexChanged(self, idx):

        self.zones_tax_lwidget.clear()
        self.from_zone_tax_cbox.clear()
        self.to_zone_tax_cbox.clear()

        if idx == -1:
            return

        location = self.zone_location_tax_cbox.currentText()

        session = SessionHandler().session_instance()
        zones = session.query(SetTaxAndPriceZone.fid, SetTaxAndPriceZone.zone_no). \
            filter(SetTaxAndPriceZone.location == location).order_by(SetTaxAndPriceZone.zone_no)

        for fid, zone_no in zones:
            item = QListWidgetItem('{0}'.format(zone_no), self.zones_tax_lwidget)
            item.setData(Qt.UserRole, fid)
            self.from_zone_tax_cbox.addItem(str(zone_no), fid)
            self.to_zone_tax_cbox.addItem(str(zone_no), fid)
        if self.zones_tax_lwidget.count() > 0:
            self.zones_tax_lwidget.setCurrentRow(0)
        if self.to_zone_tax_cbox.count() > 1:
            self.to_zone_tax_cbox.setCurrentIndex(1)

        zone_fid = self.zones_tax_lwidget.item(self.zones_tax_lwidget.currentRow()).data(Qt.UserRole)

        zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == zone_fid).one()

        zone_no = zone.zone_no
        self.landuse_code_list = list()
        del self.landuse_code_list[:]

        if zone_no == 50 or zone_no == 60 or zone_no == 70 or zone_no == 80:
            for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                    filter(ClLanduseType.code2.in_([11,12,13,14,15])).all():
                self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            delegate = LandUseComboBoxDelegate(TAX_LAND_USE, self.landuse_code_list, self.land_tax_twidget)
            self.land_tax_twidget.setItemDelegateForColumn(TAX_LAND_USE, delegate)
        else:
            for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                    filter(ClLanduseType.code2 != 11, ClLanduseType.code2 != 12, ClLanduseType.code2 != 13 \
                               , ClLanduseType.code2 != 14, ClLanduseType.code2 != 15).all():
                self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            delegate = LandUseComboBoxDelegate(TAX_LAND_USE, self.landuse_code_list, self.land_tax_twidget)
            self.land_tax_twidget.setItemDelegateForColumn(TAX_LAND_USE, delegate)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_zones_lwidget_currentItemChanged(self, current_item, previous_item):

        if previous_item is not None:
            prev_zone_fid = previous_item.data(Qt.UserRole)
            self.__save_fees(prev_zone_fid)

        if current_item is not None:
            curr_zone_fid = current_item.data(Qt.UserRole)
            self.__read_fees(curr_zone_fid)

    @pyqtSlot(QListWidgetItem, QListWidgetItem)
    def on_zones_tax_lwidget_currentItemChanged(self, current_item, previous_item):

        if previous_item is not None:
            prev_zone_fid = previous_item.data(Qt.UserRole)
            self.__save_taxes(prev_zone_fid)

        if current_item is not None:
            curr_zone_fid = current_item.data(Qt.UserRole)
            self.__read_taxes(curr_zone_fid)

    def __read_fees(self, zone_fid):

        self.land_fee_twidget.clearContents()
        self.land_fee_twidget.setRowCount(0)
        session = SessionHandler().session_instance()

        zone = session.query(SetFeeZone).filter(SetFeeZone.fid == zone_fid).one()
        self.land_fee_twidget.setRowCount(len(zone.fees))
        row = 0
        for fee in zone.fees:
            self.__add_fee_row(row, fee.id, fee.landuse_ref.code, fee.landuse_ref.description, fee.base_fee_per_m2,
                               fee.subsidized_area, fee.subsidized_fee_rate)
            row += 1

        self.land_fee_twidget.sortItems(0, Qt.AscendingOrder)
        self.land_fee_twidget.resizeColumnToContents(1)
        self.land_fee_twidget.resizeColumnToContents(2)
        self.land_fee_twidget.horizontalHeader().setResizeMode(3, QHeaderView.Stretch)

    def __read_taxes(self, zone_fid):

        self.land_tax_twidget.clearContents()
        self.land_tax_twidget.setRowCount(0)
        session = SessionHandler().session_instance()

        zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == zone_fid).one()
        self.land_tax_twidget.setRowCount(len(zone.taxes))
        row = 0
        for tax in zone.taxes:
            self.__add_tax_row(row, tax.id, tax.landuse_ref.code, tax.landuse_ref.description, tax.base_value_per_m2,
                               tax.base_tax_rate, tax.subsidized_area, tax.subsidized_tax_rate)
            row += 1

        self.land_tax_twidget.sortItems(0, Qt.AscendingOrder)
        self.land_tax_twidget.resizeColumnToContents(1)
        self.land_tax_twidget.resizeColumnToContents(2)
        self.land_tax_twidget.resizeColumnToContents(3)
        self.land_tax_twidget.horizontalHeader().setResizeMode(4, QHeaderView.Stretch)

    def __set_up_land_fee_tab(self):

        self.update_date.setDate(QDate.currentDate())
        session = SessionHandler().session_instance()

        zone_fid = self.zones_lwidget.item(self.zones_lwidget.currentRow()).data(Qt.UserRole)

        zone = session.query(SetFeeZone).filter(SetFeeZone.fid == zone_fid).one()

        zone_no = zone.zone_no
        if len(self.landuse_code_list) == 0:
            if zone_no != 50 or zone_no != 60 or zone_no != 70 or zone_no != 80:
                for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                        filter(ClLanduseType.code2 != 11, ClLanduseType.code2 != 12, ClLanduseType.code2 != 13 \
                               , ClLanduseType.code2 != 14, ClLanduseType.code2 != 15).all():
                    self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            else:
                for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                        filter(ClLanduseType.code2.in_([11,12,13,14,15])).all():
                    self.landuse_code_list.append(u'{0}: {1}'.format(code, description))

        self.__set_up_twidget(self.land_fee_twidget)

        delegate = LandUseComboBoxDelegate(FEE_LAND_USE, self.landuse_code_list, self.land_fee_twidget)
        self.land_fee_twidget.setItemDelegateForColumn(FEE_LAND_USE, delegate)
        # delegate = IntegerSpinBoxDelegate(FEE_BASE_FEE_PER_M2, 0, 10000, 0, 5, self.land_fee_twidget)
        delegate = DoubleSpinBoxDelegate(FEE_BASE_FEE_PER_M2, 0, 100000.0000, 0.0001, 0.001, self.land_fee_twidget)
        self.land_fee_twidget.setItemDelegateForColumn(FEE_BASE_FEE_PER_M2, delegate)
        delegate = IntegerSpinBoxDelegate(FEE_SUBSIDIZED_AREA, 0, 10000, 0, 5, self.land_fee_twidget)
        self.land_fee_twidget.setItemDelegateForColumn(FEE_SUBSIDIZED_AREA, delegate)
        delegate = DoubleSpinBoxDelegate(FEE_SUBSIDIZED_FEE_RATE, 0, 100, 0, 0.01, self.land_fee_twidget)
        self.land_fee_twidget.setItemDelegateForColumn(FEE_SUBSIDIZED_FEE_RATE, delegate)

    def __set_up_land_tax_tab(self):

        self.update_tax_date.setDate(QDate.currentDate())

        session = SessionHandler().session_instance()

        zone_fid = self.zones_tax_lwidget.item(self.zones_tax_lwidget.currentRow()).data(Qt.UserRole)

        zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == zone_fid).one()

        zone_no = zone.zone_no
        if len(self.landuse_code_list) == 0:
            if zone_no != 50 or zone_no != 60 or zone_no != 70 or zone_no != 80:
                for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                        filter(ClLanduseType.code2 != 11, ClLanduseType.code2 != 12, ClLanduseType.code2 != 13 \
                               , ClLanduseType.code2 != 14, ClLanduseType.code2 != 15).all():
                    self.landuse_code_list.append(u'{0}: {1}'.format(code, description))
            else:
                for code, description in session.query(ClLanduseType.code, ClLanduseType.description). \
                        filter(ClLanduseType.code2.in_([11,12,13,14,15])).all():
                    self.landuse_code_list.append(u'{0}: {1}'.format(code, description))

        self.__set_up_twidget(self.land_tax_twidget)

        delegate = LandUseComboBoxDelegate(TAX_LAND_USE, self.landuse_code_list, self.land_tax_twidget)
        self.land_tax_twidget.setItemDelegateForColumn(TAX_LAND_USE, delegate)
        # delegate = IntegerSpinBoxDelegate(TAX_BASE_VALUE_PER_M2, 0, 10000, 0, 5, self.land_tax_twidget)
        delegate = DoubleSpinBoxDelegate(TAX_BASE_VALUE_PER_M2, 0, 10000, 0, 0.01, self.land_tax_twidget)
        self.land_tax_twidget.setItemDelegateForColumn(TAX_BASE_VALUE_PER_M2, delegate)
        delegate = DoubleSpinBoxDelegate(TAX_BASE_TAX_RATE, 0, 100, 0, 0.01, self.land_tax_twidget)
        self.land_tax_twidget.setItemDelegateForColumn(TAX_BASE_TAX_RATE, delegate)
        delegate = IntegerSpinBoxDelegate(TAX_SUBSIDIZED_AREA, 0, 10000, 0, 5, self.land_tax_twidget)
        self.land_tax_twidget.setItemDelegateForColumn(TAX_SUBSIDIZED_AREA, delegate)
        delegate = DoubleSpinBoxDelegate(TAX_SUBSIDIZED_TAX_RATE, 0, 100, 0, 0.01, self.land_tax_twidget)
        self.land_tax_twidget.setItemDelegateForColumn(TAX_SUBSIDIZED_TAX_RATE, delegate)

    def __setup_doc_twidget(self):

        self.doc_twidget.setAlternatingRowColors(True)
        self.doc_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.doc_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.equipment_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.equipment_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.equipment_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.doc_twidget.horizontalHeader().resizeSection(0, 50)
        self.doc_twidget.horizontalHeader().resizeSection(1, 270)
        self.doc_twidget.horizontalHeader().resizeSection(2, 250)
        self.doc_twidget.horizontalHeader().resizeSection(3, 50)
        self.doc_twidget.horizontalHeader().resizeSection(4, 50)

        delegate = OfficialDocumentDelegate(self.doc_twidget, self)
        self.doc_twidget.setItemDelegate(delegate)

        self.__load_documents()

    def __load_documents(self):

        session = SessionHandler().session_instance()
        try:
            documents = session.query(SetOfficialDocument.id, SetOfficialDocument.visible, SetOfficialDocument.name, SetOfficialDocument.description).all()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        for document in documents:

            row = self.doc_twidget.rowCount()
            self.doc_twidget.insertRow(row)
            item_visible = QTableWidgetItem()
            if document.visible is True:
                item_visible.setCheckState(Qt.Checked)
            else:
                item_visible.setCheckState(Qt.Unchecked)

            item_name = QTableWidgetItem()
            item_name.setText(document.name)
            item_name.setData(Qt.UserRole, document.id)

            item_open = QTableWidgetItem()
            item_open.setData(Qt.UserRole, -1)

            item_description = QTableWidgetItem()
            item_description.setText(document.description)

            self.doc_twidget.setItem(row, DOC_VISIBLE_COLUMN, item_visible)
            self.doc_twidget.setItem(row, DOC_NAME_COLUMN, item_name)
            self.doc_twidget.setItem(row, DOC_DESCRIPTION_COLUMN, item_description)
            self.doc_twidget.setItem(row, DOC_OPEN_FILE_COLUMN, item_open)

    def __set_up_twidget(self, table_widget):

        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SingleSelection)
        table_widget.setColumnWidth(0, 300)

    @pyqtSlot()
    def on_add_fee_button_clicked(self):

        if self.zones_lwidget.currentRow() == -1:
            return

        used_codes = self.__collect_used_codes(self.land_fee_twidget)
        unused_code = '0000'
        for code in self.landuse_code_list:
            if code[0:4] not in used_codes:
                unused_code = code[0:4]
                break
        if unused_code == '0000':
            PluginUtils.show_error(self, self.tr("Add Row"), self.tr('The maximum number of rows is reached.'))
            return
        row = self.land_fee_twidget.rowCount()
        self.land_fee_twidget.insertRow(row)
        self.__add_fee_row(row, -1, unused_code, self.tr('Review entry!'), 0, 0, 0)

    @pyqtSlot()
    def on_add_tax_button_clicked(self):

        if self.zones_tax_lwidget.currentRow() == -1:
            return

        used_codes = self.__collect_used_codes(self.land_tax_twidget)
        unused_code = '0000'
        for code in self.landuse_code_list:
            if code[0:4] not in used_codes:
                unused_code = code[0:4]
                break
        if unused_code == '0000':
            PluginUtils.show_error(self, self.tr("Add Row"), self.tr('The maximum number of rows is reached.'))
            return
        row = self.land_tax_twidget.rowCount()
        self.land_tax_twidget.insertRow(row)
        self.__add_tax_row(row, -1, unused_code, self.tr('Review entry!'), 0, 0, 0, 0)

    def __collect_used_codes(self, fee_or_tax_twidget):

        used_codes = list()
        for row in range(fee_or_tax_twidget.rowCount()):
            landuse_code = fee_or_tax_twidget.item(row, 0).text()[0:4]
            used_codes.append(landuse_code)
        return used_codes

    @pyqtSlot()
    def on_delete_fee_button_clicked(self):

        row = self.land_fee_twidget.currentRow()
        if row == -1:
            return

        fee_id = self.land_fee_twidget.item(row, 0).data(Qt.UserRole)
        if fee_id != -1:  # already has a row in the database
            session = SessionHandler().session_instance()
            fee = session.query(SetBaseFee).filter(SetBaseFee.id == fee_id).one()
            session.delete(fee)

        self.land_fee_twidget.removeRow(row)

    @pyqtSlot()
    def on_delete_tax_button_clicked(self):

        row = self.land_tax_twidget.currentRow()
        if row == -1:
            return

        tax_id = self.land_tax_twidget.item(row, 0).data(Qt.UserRole)
        if tax_id != -1:  # already has a row in the database
            session = SessionHandler().session_instance()
            tax = session.query(SetBaseTaxAndPrice).filter(SetBaseTaxAndPrice.id == tax_id).one()
            session.delete(tax)

        self.land_tax_twidget.removeRow(row)

    def __add_fee_row(self, row, fee_id, landuse_code, landuse_desc, base_fee_per_m2, subsidized_area,
                      subsidized_fee_rate):

        item = QTableWidgetItem(u'{0}: {1}'.format(landuse_code, landuse_desc))
        item.setData(Qt.UserRole, fee_id)
        self.land_fee_twidget.setItem(row, FEE_LAND_USE, item)
        item = QTableWidgetItem('{0}'.format(base_fee_per_m2))
        self.land_fee_twidget.setItem(row, FEE_BASE_FEE_PER_M2, item)
        item = QTableWidgetItem('{0}'.format(subsidized_area))
        self.land_fee_twidget.setItem(row, FEE_SUBSIDIZED_AREA, item)
        item = QTableWidgetItem('{0}'.format(subsidized_fee_rate))
        self.land_fee_twidget.setItem(row, FEE_SUBSIDIZED_FEE_RATE, item)

    def __add_tax_row(self, row, tax_id, landuse_code, landuse_desc, base_value_per_m2, base_tax_rate, subsidized_area,
                      subsidized_tax_rate):

        item = QTableWidgetItem(u'{0}: {1}'.format(landuse_code, landuse_desc))
        item.setData(Qt.UserRole, tax_id)
        self.land_tax_twidget.setItem(row, TAX_LAND_USE, item)
        item = QTableWidgetItem('{0}'.format(base_value_per_m2))
        self.land_tax_twidget.setItem(row, TAX_BASE_VALUE_PER_M2, item)
        item = QTableWidgetItem('{0}'.format(base_tax_rate))
        self.land_tax_twidget.setItem(row, TAX_BASE_TAX_RATE, item)
        item = QTableWidgetItem('{0}'.format(subsidized_area))
        self.land_tax_twidget.setItem(row, TAX_SUBSIDIZED_AREA, item)
        item = QTableWidgetItem('{0}'.format(subsidized_tax_rate))
        self.land_tax_twidget.setItem(row, TAX_SUBSIDIZED_TAX_RATE, item)

    def reject(self):

        self.rollback()
        SessionHandler().destroy_session()
        QDialog.reject(self)

    def __save_fees(self, zone_fid=None):

        try:
            session = SessionHandler().session_instance()
            if zone_fid is None:
                zone_fid = self.zones_lwidget.item(self.zones_lwidget.currentRow()).data(Qt.UserRole)
            zone = session.query(SetFeeZone).filter(SetFeeZone.fid == zone_fid).one()

            for row in range(self.land_fee_twidget.rowCount()):
                new_row = False
                fee_id = self.land_fee_twidget.item(row, FEE_LAND_USE).data(Qt.UserRole)
                if fee_id == -1:
                    new_row = True
                    fee = SetBaseFee()
                else:
                    fee = session.query(SetBaseFee).filter(SetBaseFee.id == fee_id).one()

                landuse_code = self.land_fee_twidget.item(row, FEE_LAND_USE).text()[0:4]
                landuse = session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).one()
                fee.landuse_ref = landuse

                fee.base_fee_per_m2 = float(self.land_fee_twidget.item(row, FEE_BASE_FEE_PER_M2).text())
                fee.subsidized_area = int(self.land_fee_twidget.item(row, FEE_SUBSIDIZED_AREA).text())
                fee.subsidized_fee_rate = float(self.land_fee_twidget.item(row, FEE_SUBSIDIZED_FEE_RATE).text())

                if new_row:
                    zone.fees.append(fee)

            self.__read_fees(zone_fid)

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise

    def __save_taxes(self, zone_fid=None):

        try:
            session = SessionHandler().session_instance()
            if zone_fid is None:
                zone_fid = self.zones_tax_lwidget.item(self.zones_tax_lwidget.currentRow()).data(Qt.UserRole)
            zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == zone_fid).one()

            for row in range(self.land_tax_twidget.rowCount()):
                new_row = False
                tax_id = self.land_tax_twidget.item(row, TAX_LAND_USE).data(Qt.UserRole)
                if tax_id == -1:
                    new_row = True
                    tax = SetBaseTaxAndPrice()
                else:
                    tax = session.query(SetBaseTaxAndPrice).filter(SetBaseTaxAndPrice.id == tax_id).one()

                landuse_code = self.land_tax_twidget.item(row, TAX_LAND_USE).text()[0:4]
                landuse = session.query(ClLanduseType).filter(ClLanduseType.code == landuse_code).one()
                tax.landuse_ref = landuse

                tax.base_value_per_m2 = int(self.land_tax_twidget.item(row, TAX_BASE_VALUE_PER_M2).text())
                tax.base_tax_rate = float(self.land_tax_twidget.item(row, TAX_BASE_TAX_RATE).text())
                tax.subsidized_area = int(self.land_tax_twidget.item(row, TAX_SUBSIDIZED_AREA).text())
                tax.subsidized_tax_rate = float(self.land_tax_twidget.item(row, TAX_SUBSIDIZED_TAX_RATE).text())

                if new_row:
                    zone.taxes.append(tax)

            self.__read_taxes(zone_fid)

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise

    @pyqtSlot()
    def on_copy_fees_button_clicked(self):

        from_zone_idx = self.from_zone_cbox.currentIndex()
        to_zone_idx = self.to_zone_cbox.currentIndex()
        if from_zone_idx == -1 or to_zone_idx == -1:
            return

        if from_zone_idx == to_zone_idx:
            PluginUtils.show_error(self, self.tr('Copy Fee Entries'),
                                    self.tr('Fee entries cannot be copied among the same zone!'))
            return

        # In case of rows just added make sure they get written before the copying
        if from_zone_idx == self.zones_lwidget.currentRow():
            self.__save_fees()

        from_zone_fid = self.from_zone_cbox.itemData(from_zone_idx, Qt.UserRole)

        try:
            session = SessionHandler().session_instance()
            from_zone = session.query(SetFeeZone).filter(SetFeeZone.fid == from_zone_fid).one()
            fee_count = len(from_zone.fees)

            message = self.tr("{0} fee entries will be copied from Zone {1} to"
                              " Zone {2} and overwrite all existing entries in Zone {2}."
                              " Do you want to continue?".format(fee_count, self.from_zone_cbox.currentText(),
                                                                self.to_zone_cbox.currentText()))

            if QMessageBox.No == QMessageBox.question(None, self.tr("Copy Fee Entries"), message,
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
                return

            to_zone_fid = self.to_zone_cbox.itemData(to_zone_idx, Qt.UserRole)
            to_zone = session.query(SetFeeZone).filter(SetFeeZone.fid == to_zone_fid).one()
            fee_count = len(to_zone.fees)
            for idx in reversed(xrange(fee_count)):
                del to_zone.fees[idx]
            session.flush()

            for fee in from_zone.fees:
                new_fee = SetBaseFee(landuse=fee.landuse, base_fee_per_m2=fee.base_fee_per_m2,
                                     subsidized_area=fee.subsidized_area,
                                     subsidized_fee_rate=fee.subsidized_fee_rate)
                to_zone.fees.append(new_fee)

            if self.zones_lwidget.currentRow() == to_zone_idx:
                self.__read_fees(to_zone_fid)
            else:
                self.zones_lwidget.setCurrentRow(to_zone_idx)

            PluginUtils.show_message(self, self.tr('Copy Fee Entries'), self.tr('Copying successfully completed.'))

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

    @pyqtSlot()
    def on_copy_taxes_button_clicked(self):

        from_zone_idx = self.from_zone_tax_cbox.currentIndex()
        to_zone_idx = self.to_zone_tax_cbox.currentIndex()
        if from_zone_idx == -1 or to_zone_idx == -1:
            return

        if from_zone_idx == to_zone_idx:
            PluginUtils.show_error(self, self.tr('Copy Fee Entries'),
                                    self.tr('Tax entries cannot be copied among the same zone!'))
            return

        # In case of rows just added make sure they get written before the copying
        if from_zone_idx == self.zones_tax_lwidget.currentRow():
            self.__save_taxes()

        from_zone_fid = self.from_zone_tax_cbox.itemData(from_zone_idx, Qt.UserRole)

        try:
            session = SessionHandler().session_instance()
            from_zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == from_zone_fid).one()
            tax_count = len(from_zone.taxes)

            message = self.tr("{0} tax entries will be copied from Zone {1} to"
                              " Zone {2} and overwrite all existing entries in Zone {2}."
                              " Do you want to continue?".format(tax_count, self.from_zone_tax_cbox.currentText(),
                                                                self.to_zone_tax_cbox.currentText()))

            if QMessageBox.No == QMessageBox.question(None, self.tr("Copy Tax Entries"), message,
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
                return

            to_zone_fid = self.to_zone_tax_cbox.itemData(to_zone_idx, Qt.UserRole)
            to_zone = session.query(SetTaxAndPriceZone).filter(SetTaxAndPriceZone.fid == to_zone_fid).one()
            tax_count = len(to_zone.taxes)
            for idx in reversed(xrange(tax_count)):
                del to_zone.taxes[idx]
            session.flush()

            for tax in from_zone.taxes:
                new_tax = SetBaseTaxAndPrice(landuse=tax.landuse, base_value_per_m2=tax.base_value_per_m2,
                                             base_tax_rate=tax.base_tax_rate,
                                             subsidized_area=tax.subsidized_area,
                                             subsidized_tax_rate=tax.subsidized_tax_rate)
                to_zone.taxes.append(new_tax)

            if self.zones_tax_lwidget.currentRow() == to_zone_idx:
                self.__read_taxes(to_zone_fid)
            else:
                self.zones_tax_lwidget.setCurrentRow(to_zone_idx)

            PluginUtils.show_message(self, self.tr('Copy Tax Entries'), self.tr('Copying successfully completed.'))

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

    @pyqtSlot("QDate")
    def on_update_date_dateChanged(self, update_date):

        day = update_date.day()
        if day != 1:
            self.update_date.setDate(QDate(update_date.year(), update_date.month(), 1))

    @pyqtSlot("QDate")
    def on_update_tax_date_dateChanged(self, update_date):

        day = update_date.day()
        if day != 1:
            self.update_tax_date.setDate(QDate(update_date.year(), update_date.month(), 1))

    @pyqtSlot()
    def on_update_contracts_button_clicked(self):

        message = 'Are you sure you want to update all contracts based on the new fees?'
        if QMessageBox.No == QMessageBox.question(None, self.tr("Update Contracts"), message,
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
            return

        update_date = PluginUtils.convert_qt_date_to_python(self.update_date.date()).date()
        # Warning if update date <= current date
        if update_date <= date.today():
            message = "The update date should be later than the current date. Are you sure you want to update the contracts?"
            if QMessageBox.No == QMessageBox.question(None, self.tr("Update Contracts"), message,
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
                return

        self.create_savepoint()
        session = SessionHandler().session_instance()

        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            self.__save_fees()

            update_count = 0

            # Loop over restriction array
            l2_units = DatabaseUtils.l2_restriction_array()
            for l2_unit in l2_units:

                session.execute("SET search_path to s{0}, base, codelists, admin_units, settings, public".format(l2_unit))
                # Get active contracts only
                contracts = session.query(CtContract).\
                    filter(update_date < func.coalesce(CtContract.cancellation_date, CtContract.contract_end)).all()

                for contract in contracts:
                    application_role = contract.application_roles.\
                        filter(CtContractApplicationRole.role == Constants.APPLICATION_ROLE_CREATES).one()
                    application = application_role.application_ref
                    parcel_id = application.parcel
                    if len(parcel_id) == 0:
                        # TODO: log something
                        # should never happen
                        continue

                    count = session.query(SetBaseFee).filter(SetFeeZone.geometry.ST_Contains(CaParcel.geometry)).\
                        filter(CaParcel.parcel_id == parcel_id).\
                        filter(SetBaseFee.fee_zone == SetFeeZone.fid).\
                        filter(SetBaseFee.landuse == CaParcel.landuse).\
                        count()

                    if count == 0:
                        # TODO: log something
                        # can happen
                        continue

                    base_fee = session.query(SetBaseFee).filter(SetFeeZone.geometry.ST_Contains(CaParcel.geometry)).\
                        filter(CaParcel.parcel_id == parcel_id).\
                        filter(SetBaseFee.fee_zone == SetFeeZone.fid).\
                        filter(SetBaseFee.landuse == CaParcel.landuse).\
                        one()

                    new_base_fee_per_m2 = base_fee.base_fee_per_m2
                    new_subsidized_area = base_fee.subsidized_area
                    new_subsidized_fee_rate = base_fee.subsidized_fee_rate

                    # Get latest archived fee
                    latest_archived_fee = contract.archived_fees.order_by(CtArchivedFee.valid_till.desc()).first()
                    if latest_archived_fee is None:
                        valid_from = date(2010, 1, 1)
                    else:
                        valid_from = latest_archived_fee.valid_till

                    count = 0
                    for fee in contract.fees:

                        if fee.base_fee_per_m2 != new_base_fee_per_m2 or\
                                fee.subsidized_area != new_subsidized_area or\
                                fee.subsidized_fee_rate != new_subsidized_fee_rate:

                            self.__archive_fee(contract, fee, valid_from, update_date)
                            self.__update_fee(fee, new_base_fee_per_m2, new_subsidized_area, new_subsidized_fee_rate)

                            if count == 0:
                                count += 1

                    update_count += count

                session.flush()

            QApplication.restoreOverrideCursor()
            PluginUtils.show_message(self, self.tr("Update Contracts"),
                                     self.tr('Updated {0} contracts. Click Apply to save the changes!'
                                             .format(update_count)))

        except exc.SQLAlchemyError, e:
            QApplication.restoreOverrideCursor()
            self.rollback_to_savepoint()
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

    def __archive_fee(self, contract, fee, valid_from, valid_till):

        archived_fee = CtArchivedFee()
        archived_fee.person = fee.person
        archived_fee.share = fee.share
        archived_fee.area = fee.area
        archived_fee.fee_calculated = fee.fee_calculated
        archived_fee.fee_contract = fee.fee_contract
        archived_fee.grace_period = fee.grace_period
        archived_fee.base_fee_per_m2 = fee.base_fee_per_m2
        archived_fee.subsidized_area = fee.subsidized_area
        archived_fee.subsidized_fee_rate = fee.subsidized_fee_rate
        archived_fee.valid_from = valid_from
        archived_fee.valid_till = valid_till
        archived_fee.payment_frequency = fee.payment_frequency
        contract.archived_fees.append(archived_fee)

    def __update_fee(self, fee, new_base_fee_per_m2, new_subsidized_area, new_subsidized_fee_rate):

        fee.base_fee_per_m2 = new_base_fee_per_m2
        fee.subsidized_area = new_subsidized_area
        fee.subsidized_fee_rate = new_subsidized_fee_rate

        contractor_subsidized_area = int(round(float(fee.share) * new_subsidized_area))
        fee_subsidized = contractor_subsidized_area * new_base_fee_per_m2 * (float(new_subsidized_fee_rate) / 100)
        fee_standard = (fee.area - contractor_subsidized_area) * new_base_fee_per_m2
        fee_calculated = int(round(fee_subsidized if fee_standard < 0 else fee_subsidized + fee_standard))

        fee.fee_calculated = fee_calculated
        fee.fee_contract = fee_calculated

    @pyqtSlot()
    def on_update_records_button_clicked(self):

        message = 'Are you sure you want to update all records based on the new taxes?'
        if QMessageBox.No == QMessageBox.question(None, self.tr("Update Ownership Records"), message,
                                                  QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
            return

        update_date = PluginUtils.convert_qt_date_to_python(self.update_tax_date.date()).date()
        # Warning if update date <= current date
        if update_date <= date.today():
            message = "The update date should be later than the current date. Are you sure you want to update the records?"
            if QMessageBox.No == QMessageBox.question(None, self.tr("Update Ownership Records"), message,
                                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
                return

        self.create_savepoint()
        session = SessionHandler().session_instance()

        try:
            QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))

            self.__save_taxes()

            update_count = 0

            # Loop over restriction array
            l2_units = DatabaseUtils.l2_restriction_array()
            for l2_unit in l2_units:

                session.execute("SET search_path to s{0}, base, codelists, admin_units, settings, public".format(l2_unit))
                # Get active records only
                records = session.query(CtOwnershipRecord).\
                    filter(or_(CtOwnershipRecord.cancellation_date.is_(None), update_date < CtOwnershipRecord.cancellation_date)).all()
                print "Record count per L2Unit: {0}".format(len(records))

                for record in records:
                    count = record.application_roles.\
                        filter(CtContractApplicationRole.role == Constants.APPLICATION_ROLE_CREATES).count()
                    if count == 0:
                        # TODO: log something
                        # should never happen
                        continue
                    application_role = record.application_roles.\
                        filter(CtContractApplicationRole.role == Constants.APPLICATION_ROLE_CREATES).one()
                    application = application_role.application_ref
                    parcel_id = application.parcel
                    if len(parcel_id) == 0:
                        # TODO: log something
                        # should never happen
                        continue

                    count = session.query(SetBaseTaxAndPrice).filter(SetTaxAndPriceZone.geometry.ST_Contains(CaParcel.geometry)).\
                        filter(CaParcel.parcel_id == parcel_id).\
                        filter(SetBaseTaxAndPrice.tax_zone == SetTaxAndPriceZone.fid).\
                        filter(SetBaseTaxAndPrice.landuse == CaParcel.landuse).\
                        count()

                    if count == 0:
                        # TODO: log something
                        # can happen
                        continue

                    base_tax_and_price = session.query(SetBaseTaxAndPrice).filter(SetTaxAndPriceZone.geometry.ST_Contains(CaParcel.geometry)).\
                        filter(CaParcel.parcel_id == parcel_id).\
                        filter(SetBaseTaxAndPrice.tax_zone == SetTaxAndPriceZone.fid).\
                        filter(SetBaseTaxAndPrice.landuse == CaParcel.landuse).\
                        one()

                    new_base_value_per_m2 = base_tax_and_price.base_value_per_m2
                    new_base_tax_rate = base_tax_and_price.base_tax_rate
                    new_subsidized_area = base_tax_and_price.subsidized_area
                    new_subsidized_tax_rate = base_tax_and_price.subsidized_tax_rate

                    # Get latest archived tax
                    latest_archived_tax = record.archived_taxes.\
                        order_by(CtArchivedTaxAndPrice.valid_till.desc()).first()
                    if latest_archived_tax is None:
                        valid_from = date(2010, 1, 1)
                    else:
                        valid_from = latest_archived_tax.valid_till

                    count = 0
                    for tax in record.taxes:

                        if tax.base_value_per_m2 != new_base_value_per_m2 or\
                                tax.base_tax_rate != new_base_tax_rate or\
                                tax.subsidized_area != new_subsidized_area or\
                                tax.subsidized_tax_rate != new_subsidized_tax_rate:

                            self.__archive_tax(record, tax, valid_from, update_date)
                            self.__update_tax(tax, new_base_value_per_m2, new_base_tax_rate, new_subsidized_area,
                                              new_subsidized_tax_rate)

                            if count == 0:
                                count += 1

                    update_count += count

                session.flush()

            QApplication.restoreOverrideCursor()
            PluginUtils.show_message(self, self.tr("Update Ownership Records"),
                                     self.tr('Updated {0} records. Click Apply to save the changes!'
                                             .format(update_count)))

        except exc.SQLAlchemyError, e:
            QApplication.restoreOverrideCursor()
            self.rollback_to_savepoint()
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)

    def __archive_tax(self, record, tax, valid_from, valid_till):

        archived_tax = CtArchivedTaxAndPrice()
        archived_tax.person = tax.person
        archived_tax.share = tax.share
        archived_tax.area = tax.area
        archived_tax.value_calculated = tax.value_calculated
        archived_tax.price_paid = tax.price_paid
        archived_tax.land_tax = tax.land_tax
        archived_tax.grace_period = tax.grace_period
        archived_tax.base_value_per_m2 = tax.base_value_per_m2
        archived_tax.base_tax_rate = tax.base_tax_rate
        archived_tax.subsidized_area = tax.subsidized_area
        archived_tax.subsidized_tax_rate = tax.subsidized_tax_rate
        archived_tax.valid_from = valid_from
        archived_tax.valid_till = valid_till
        archived_tax.payment_frequency = tax.payment_frequency
        record.archived_taxes.append(archived_tax)

    def __update_tax(self, tax, new_base_value_per_m2, new_base_tax_rate, new_subsidized_area, new_subsidized_tax_rate):

        tax.base_value_per_m2 = new_base_value_per_m2
        tax.base_tax_rate = new_base_tax_rate
        tax.subsidized_area = new_subsidized_area
        tax.subsidized_tax_rate = new_subsidized_tax_rate

        value_calculated = tax.area * new_base_value_per_m2
        owner_subsidized_area = int(round(float(tax.share) * new_subsidized_area))
        tax_subsidized = owner_subsidized_area * new_base_value_per_m2 * (float(new_base_tax_rate) / 100) \
            * (float(new_subsidized_tax_rate) / 100)
        tax_standard = (tax.area - owner_subsidized_area) * new_base_value_per_m2 * (float(new_base_tax_rate) / 100)
        tax_calculated = int(round(tax_subsidized if tax_standard < 0 else tax_subsidized + tax_standard))

        tax.value_calculated = value_calculated
        tax.land_tax = tax_calculated

    @pyqtSlot()
    def on_add_company_button_clicked(self):

        row = self.company_twidget.rowCount()
        self.company_twidget.insertRow(row)
        self.__add_company_row(row, -1, self.tr('Review entry!'), self.tr('Review entry!'))

    @pyqtSlot()
    def on_add_surveyor_button_clicked(self):

        if self.company_twidget.currentRow() == -1:
            return

        if self.company_twidget.item(self.company_twidget.currentRow(), 0).data(Qt.UserRole) == -1:
            PluginUtils.show_error(self, self.tr('Add Surveyor'), self.tr('Apply your changes first!'))
            return

        row = self.surveyor_twidget.rowCount()
        self.surveyor_twidget.insertRow(row)
        self.__add_surveyor_row(row, -1, self.tr('Review entry!'), self.tr('Review entry!'), self.tr('Review entry!'))

    def __set_up_company_tab(self):

        self.__set_up_twidget(self.company_twidget)
        self.__read_companies()

    def __set_up_surveyor_tab(self):

        self.__set_up_twidget(self.surveyor_twidget)
        self.surveyor_twidget.setColumnWidth(SURVEYOR_SURNAME, 250)
        self.surveyor_twidget.setColumnWidth(SURVEYOR_FIRST_NAME, 250)

    def __read_companies(self):

        self.company_twidget.clearContents()
        self.company_twidget.setRowCount(0)
        session = SessionHandler().session_instance()

        companies = session.query(SetSurveyCompany).order_by(SetSurveyCompany.name).all()
        self.company_twidget.setRowCount(len(companies))
        row = 0
        for company in companies:
            self.__add_company_row(row, company.id, company.name, company.address)
            row += 1

        self.company_twidget.horizontalHeader().setResizeMode(1, QHeaderView.Stretch)

        if self.company_twidget.rowCount() > 0:
            self.company_twidget.setCurrentCell(0, 0)

    def __read_surveyors(self, company_id):

        self.surveyor_twidget.clearContents()
        self.surveyor_twidget.setRowCount(0)

        if company_id == -1:
            return

        session = SessionHandler().session_instance()
        company = session.query(SetSurveyCompany).filter(SetSurveyCompany.id == company_id).one()
        self.surveyor_twidget.setRowCount(len(company.surveyors))
        row = 0
        for surveyor in company.surveyors:
            self.__add_surveyor_row(row, surveyor.id, surveyor.surname, surveyor.first_name, surveyor.phone)
            row += 1

        self.surveyor_twidget.horizontalHeader().setResizeMode(2, QHeaderView.Stretch)

    def __add_surveyor_row(self, row, surveyor_id, surveyor_surname, surveyor_first_name, surveyor_phone):

        item = QTableWidgetItem(u'{0}'.format(surveyor_surname))
        item.setData(Qt.UserRole, surveyor_id)
        self.surveyor_twidget.setItem(row, SURVEYOR_SURNAME, item)
        item = QTableWidgetItem(u'{0}'.format(surveyor_first_name))
        self.surveyor_twidget.setItem(row, SURVEYOR_FIRST_NAME, item)
        item = QTableWidgetItem(u'{0}'.format(surveyor_phone))
        self.surveyor_twidget.setItem(row, SURVEYOR_PHONE, item)

    def __add_company_row(self, row, company_id, company_name, company_address):

        item = QTableWidgetItem(u'{0}'.format(company_name))
        item.setData(Qt.UserRole, company_id)
        self.company_twidget.setItem(row, COMPANY_NAME, item)
        item = QTableWidgetItem(u'{0}'.format(company_address))
        self.company_twidget.setItem(row, COMPANY_ADDRESS, item)

    @pyqtSlot()
    def on_delete_company_button_clicked(self):

        row = self.company_twidget.currentRow()
        if row == -1:
            return
        if QMessageBox.No == QMessageBox.question(None, self.tr("Delete Company"), self.tr('Deleting a company will also delete the relating surveyors. Continue?'), QMessageBox.Yes | QMessageBox.No, QMessageBox.No):
            return

        company_id = self.company_twidget.item(row, 0).data(Qt.UserRole)
        if company_id != -1:  # already has a row in the database
            session = SessionHandler().session_instance()
            company = session.query(SetSurveyCompany).filter(SetSurveyCompany.id == company_id).one()
            session.delete(company)

        self.company_twidget.removeRow(row)

    def __save_companies(self):

        try:
            session = SessionHandler().session_instance()
            for row in range(self.company_twidget.rowCount()):
                new_row = False
                company_id = self.company_twidget.item(row, COMPANY_NAME).data(Qt.UserRole)
                if company_id == -1:
                    new_row = True
                    company = SetSurveyCompany()
                else:
                    company = session.query(SetSurveyCompany).filter(SetSurveyCompany.id == company_id).one()

                company.name = self.company_twidget.item(row, COMPANY_NAME).text()
                company.address = self.company_twidget.item(row, COMPANY_ADDRESS).text()

                if new_row:
                    session.add(company)

            self.__read_companies()

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise

    @pyqtSlot()
    def on_find_company_button_clicked(self):

        search_text = self.company_ledit.text().strip()
        if search_text is None or len(search_text) == 0:
            return

        items = self.company_twidget.findItems(search_text, Qt.MatchContains)

        for item in items:
            row = self.company_twidget.row(item)
            if search_text != self.company_search_str:
                self.company_twidget.setCurrentCell(row, 0)
                self.company_search_str = search_text
                break
            if row > self.company_twidget.currentRow():
                self.company_twidget.setCurrentCell(row, 0)
                break

    @pyqtSlot(QTableWidgetItem, QTableWidgetItem)
    def on_company_twidget_currentItemChanged(self, current_item, previous_item):

        if previous_item is not None:
            print 'P:{0}'.format(previous_item.column())
            prev_company_id = self.company_twidget.item(previous_item.row(), 0).data(Qt.UserRole)
            self.__save_surveyors(prev_company_id)

        if current_item is not None:
            print 'C:{0}'.format(current_item.column())
            prev_company_id = self.company_twidget.item(current_item.row(), 0).data(Qt.UserRole)
            self.__read_surveyors(prev_company_id)

    @pyqtSlot()
    def on_delete_surveyor_button_clicked(self):

        row = self.surveyor_twidget.currentRow()
        if row == -1:
            return

        surveyor_id = self.surveyor_twidget.item(row, 0).data(Qt.UserRole)
        if surveyor_id != -1:  # already has a row in the database
            session = SessionHandler().session_instance()
            surveyor = session.query(SetSurveyor).filter(SetSurveyor.id == surveyor_id).one()
            session.delete(surveyor)

        self.surveyor_twidget.removeRow(row)

    def __save_surveyors(self, company_id=None):

        if company_id == -1 or self.company_twidget.rowCount() == 0:
            return

        try:
            session = SessionHandler().session_instance()
            if company_id is None:
                company_id = self.company_twidget.item(self.company_twidget.currentRow(), 0).data(Qt.UserRole)
            # In case this method was called because a company has been deleted:
            count = session.query(SetSurveyCompany).filter(SetSurveyCompany.id == company_id).count()
            if count == 0:
                return
            company = session.query(SetSurveyCompany).filter(SetSurveyCompany.id == company_id).one()

            for row in range(self.surveyor_twidget.rowCount()):
                new_row = False
                surveyor_id = self.surveyor_twidget.item(row, SURVEYOR_SURNAME).data(Qt.UserRole)
                if surveyor_id == -1:
                    new_row = True
                    surveyor = SetSurveyor()
                else:
                    surveyor = session.query(SetSurveyor).filter(SetSurveyor.id == surveyor_id).one()

                surveyor.surname = self.surveyor_twidget.item(row, SURVEYOR_SURNAME).text()
                surveyor.first_name = self.surveyor_twidget.item(row, SURVEYOR_FIRST_NAME).text()
                surveyor.phone = self.surveyor_twidget.item(row, SURVEYOR_PHONE).text()

                if new_row:
                    company.surveyors.append(surveyor)

            self.__read_surveyors(company_id)

        except exc.SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("SQL Error"), e.message)
            raise

    @pyqtSlot()
    def on_add_document_button_clicked(self):

        row = self.doc_twidget.rowCount()
        self.doc_twidget.insertRow(row)
        item_visible = QTableWidgetItem()
        item_visible.setCheckState(Qt.Checked)

        item_name = QTableWidgetItem()
        item_name.setText("Undefined")
        item_name.setData(Qt.UserRole, -1)

        item_open = QTableWidgetItem()
        item_open.setData(Qt.UserRole, -1)

        item_description = QTableWidgetItem()
        item_description.setText("Undefined")
        self.doc_twidget.setItem(row, DOC_VISIBLE_COLUMN, item_visible)
        self.doc_twidget.setItem(row, DOC_NAME_COLUMN, item_name)
        self.doc_twidget.setItem(row, DOC_DESCRIPTION_COLUMN, item_description)
        self.doc_twidget.setItem(row, DOC_OPEN_FILE_COLUMN, item_open)

    @pyqtSlot()
    def on_remove_document_button_clicked(self):

        message_box = QMessageBox()
        message_box.setText(self.tr("Do you want to delete the selected document?"))

        delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
        message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
        message_box.exec_()

        if message_box.clickedButton() == delete_button:
            try:
                row = self.doc_twidget.currentRow()
                item = self.doc_twidget.item(row, DOC_NAME_COLUMN)

                if item.data(Qt.UserRole) != -1:
                    session = SessionHandler().session_instance()
                    session.query(SetOfficialDocument).filter(SetOfficialDocument.id == item.data(Qt.UserRole)).delete()

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            self.doc_twidget.removeRow(row)

    @pyqtSlot()
    def on_help_button_clicked(self):

        if self.tabWidget.currentIndex() == 0:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/report_parameters.htm")
        elif self.tabWidget.currentIndex() == 1:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/land_fee_base_values.htm")
        elif self.tabWidget.currentIndex() == 2:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/land_tax_values.htm")
        elif self.tabWidget.currentIndex() == 3:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/certificates.htm")
        elif self.tabWidget.currentIndex() == 4:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/land_office_administrative_settings_official_doments.htm")
        elif self.tabWidget.currentIndex() == 5:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/payments.htm")
        elif self.tabWidget.currentIndex() == 7:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/survey_company.htm")
        elif self.tabWidget.currentIndex() == 8:
                os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/land_office_administrative_settings_other.htm")
