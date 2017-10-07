import os

__author__ = 'ankhbold'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, or_, extract
from ..view.Ui_ParcelRecordDialog import *
from ..utils.PluginUtils import *
from ..utils.SessionHandler import SessionHandler
from ..model.CaParcel import *
from ..model.CtDecisionApplication import *
from ..model.CtDecision import *
from ..model.AuLevel3 import *
from ..model.CaBuilding import *
from ..model.VaTypeSource import *
from ..model.VaTypeLanduseBuilding import *
from ..model.VaTypeMaterial import *
from ..model.VaTypeHeat import *
from ..model.VaTypeStove import *
from ..model.VaTypeStatusBuilding import *
from ..model.VaInfoHomeParcel import *
from ..model.VaInfoHomePurchase import *
from ..model.VaTypePurchaseOrLease import *
from ..model.VaInfoHomeLease import *
from ..model.VaInfoHomeBuilding import *

class ParcelRecordDialog(QDialog, Ui_ParcelRecordDialog):

    def __init__(self, parcel_type, register_no,parcel_id, record, parent=None):

        super(ParcelRecordDialog,  self).__init__(parent)
        self.setupUi(self)
        self.parcel_type = parcel_type
        self.parcel_id = parcel_id
        self.register_no = register_no
        self.record = record
        self.cancel_button.clicked.connect(self.reject)
        self.__set_visible_tabs()
        self.__parcel_populate()
        self.home_purchase_rbutton.setChecked(True)
        self.b_status_good_rbutton.setChecked(True)
        self.__setup_validators()
        self.__setup_purchase_widget()
        self.session = SessionHandler().session_instance()
        self.year_sbox.setMinimum(1950)
        self.year_sbox.setMaximum(2200)
        self.year_sbox.setSingleStep(1)
        self.year_sbox.setValue(QDate.currentDate().year())
        self.cost_year_checkbox.setChecked(True)
        self.side_fence_1_2_rbutton.setChecked(True)
        self.quarter_gbox.setDisabled(True)
        self.electricity_yes_rbutton.setChecked(True)
        self.heating_yes_rbutton.setChecked(True)
        self.water_yes_rbutton.setChecked(True)
        self.sewage_yes_rbutton.setChecked(True)
        self.well_yes_rbutton.setChecked(True)
        self.finance_yes_rbutton.setChecked(True)
        self.phone_yes_rbutton.setChecked(True)
        self.flood_yes_rbutton.setChecked(True)
        self.plot_yes_rbutton.setChecked(True)
        self.slope_yes_rbutton.setChecked(True)

        self.__setup_mapping()

    @pyqtSlot(int)
    def on_cost_year_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.quarter_gbox.setEnabled(False)
            self.q1_checkbox.setChecked(False)
            self.q2_checkbox.setChecked(False)
            self.q3_checkbox.setChecked(False)
            self.q4_checkbox.setChecked(False)
        else:
            self.quarter_gbox.setEnabled(True)

    @pyqtSlot(int)
    def on_q1_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.q2_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(False)
            self.q4_checkbox.setEnabled(False)
            self.q3_checkbox.setChecked(False)
            self.q4_checkbox.setChecked(False)
        else:
            self.q1_checkbox.setEnabled(True)
            self.q2_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(True)

    @pyqtSlot(int)
    def on_q2_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.q1_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(False)
            self.q4_checkbox.setChecked(False)
        else:
            self.q1_checkbox.setEnabled(True)
            self.q2_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(True)

    @pyqtSlot(int)
    def on_q3_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.q2_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(True)
            self.q1_checkbox.setEnabled(False)
            self.q1_checkbox.setChecked(False)
        else:
            self.q1_checkbox.setEnabled(True)
            self.q2_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(True)

    @pyqtSlot(int)
    def on_q4_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.q3_checkbox.setEnabled(True)
            self.q2_checkbox.setEnabled(False)
            self.q1_checkbox.setEnabled(False)
            self.q2_checkbox.setChecked(False)
            self.q1_checkbox.setChecked(False)
        else:
            self.q1_checkbox.setEnabled(True)
            self.q2_checkbox.setEnabled(True)
            self.q3_checkbox.setEnabled(True)
            self.q4_checkbox.setEnabled(True)

    def __setup_purchase_widget(self):

        self.purchase_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.purchase_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.purchase_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.lease_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.lease_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.lease_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.home_building_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.home_building_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.home_building_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def __setup_validators(self):

        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+\\.[0-9]{3}"), None)
        self.int_validator = QRegExpValidator(QRegExp("[0-9][0-9]"), None)

        self.purchase_price_edit.setValidator(self.numbers_validator)
        self.lease_rent_edit.setValidator(self.numbers_validator)
        self.purchase_area_edit.setValidator(self.numbers_validator)
        self.lease_area_edit.setValidator(self.numbers_validator)
        self.building_area_edit.setValidator(self.numbers_validator)
        self.lease_duration_edit.setValidator(self.int_validator)
        self.lease_area_edit.setValidator(self.numbers_validator)
        self.lease_rent_edit.setValidator(self.numbers_validator)

        self.electricity_distancel_edit.setValidator(self.numbers_validator)
        self.electricity_connection_cost_edit.setValidator(self.numbers_validator)
        self.central_heat_distancel_edit.setValidator(self.numbers_validator)
        self.central_heat_connection_cost_edit.setValidator(self.numbers_validator)

        self.water_distancel_edit.setValidator(self.numbers_validator)
        self.water_connection_cost_edit.setValidator(self.numbers_validator)
        self.sewage_distancel_edit.setValidator(self.numbers_validator)
        self.sewage_connection_cost_edit.setValidator(self.numbers_validator)
        self.well_distancel_edit.setValidator(self.numbers_validator)
        self.phone_distancel_edit.setValidator(self.numbers_validator)
        self.flood_channel_distancel_edit.setValidator(self.numbers_validator)
        self.vegetable_plot_size_edit.setValidator(self.numbers_validator)

    @pyqtSlot(str)
    def on_purchase_area_edit_textChanged(self, text):

        session = SessionHandler().session_instance()
        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+\\.[0-9]{3}"), None)
        self.purchase_area_edit.setValidator(self.numbers_validator)
        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        if parcel.documented_area_m2 == None:
            area = parcel.area_m2
        else:
            area = parcel.documented_area_m2
        if text == "":
            self.purchase_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        if float(text) > area:
            self.purchase_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.purchase_area_edit.setStyleSheet(self.styleSheet())

    @pyqtSlot(str)
    def on_lease_area_edit_textChanged(self, text):

        session = SessionHandler().session_instance()
        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+\\.[0-9]{3}"), None)
        self.lease_area_edit.setValidator(self.numbers_validator)
        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        if parcel.documented_area_m2 == None:
            area = parcel.area_m2
        else:
            area = parcel.documented_area_m2
        if text == "":
            self.lease_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        if float(text) > area:
            self.lease_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.lease_area_edit.setStyleSheet(self.styleSheet())

    @pyqtSlot(str)
    def on_building_area_edit_textChanged(self, text):

        session = SessionHandler().session_instance()
        self.numbers_validator = QRegExpValidator(QRegExp("[1-9][0-9]+\\.[0-9]{3}"), None)
        self.building_area_edit.setValidator(self.numbers_validator)
        building_id = self.building_no_cbox.itemData(self.building_no_cbox.currentIndex())
        building = session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()

        area = building.area_m2
        if text == "":
            self.building_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        if float(text) > area:
            self.building_area_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
        else:
            self.building_area_edit.setStyleSheet(self.styleSheet())

    @pyqtSlot(str)
    def on_purchase_price_edit_textChanged(self, text):

         if text == "":
            self.purchase_price_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
         else:
            self.purchase_price_edit.setStyleSheet(self.styleSheet())
            value = round(float(self.purchase_price_edit.text())/float(self.purchase_area_edit.text()))
            self.purchase_price_if_m2.setText(str(value))

    @pyqtSlot(str)
    def on_lease_rent_edit_textChanged(self, text):

         if text == "":
            self.lease_rent_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            return
         else:
            self.lease_rent_edit.setStyleSheet(self.styleSheet())
            value = round(float(self.lease_rent_edit.text())/float(self.lease_area_edit.text()))
            self.lease_rent_of_m2.setText(str(value))

    def __setup_mapping(self):

        session = SessionHandler().session_instance()
        if self.record.register_no == None:
            return
        #Detail
        self.cadastreId_edit.setText(self.record.parcel_id)
        self.registration_date.setDateTime(QDateTime.fromString(self.record.info_date.strftime(Constants.PYTHON_DATE_FORMAT),
                                                                Constants.DATABASE_DATE_FORMAT))

        if self.record.purchase_or_lease_type_ref:
            if self.record.purchase_or_lease_type_ref.code == 10:
                self.home_purchase_rbutton.setChecked(True)
            else:
                self.home_lease_rbutton.setChecked(True)
        self.calculated_area_edit.setText(str(self.record.area_m2))

        if self.record.app_type_ref:
            self.right_type_cbox.setCurrentIndex(self.right_type_cbox.findData(self.record.app_type_ref.code))
        if self.record.source_type_ref:
            self.source_cbox.setCurrentIndex(self.source_cbox.findData(self.record.source_type_ref.code))

        self.decision_date_edit.setText(self.record.decision_date)
        self.duration_year_edit.setText(str(self.record.approved_duration))

        register_no = self.record.register_no
        parts_register_no = register_no.split("-")

        self.home_num_first_edit.setText(parts_register_no[0])
        self.home_num_type_edit.setText(parts_register_no[1])
        self.home_num_middle_edit.setText(parts_register_no[2])
        self.home_num_last_edit.setText(parts_register_no[3])

        if self.record.is_electricity:
            self.electricity_yes_rbutton.setChecked(True)
        else:
            self.electricity_no_rbutton.setChecked(True)

        if self.record.electricity_distancel != None:
            self.electricity_distancel_edit.setText(str(float(self.record.electricity_distancel)))

        if self.record.electricity_conn_cost != None:
            self.electricity_connection_cost_edit.setText(str(float(self.record.electricity_conn_cost)))

        if self.record.is_central_heating:
            self.heating_yes_rbutton.setChecked(True)
        else:
            self.heating_no_rbutton.setChecked(False)

        if self.record.central_heating_distancel != None:
            self.central_heat_distancel_edit.setText(str(float(self.record.central_heating_distancel)))

        if self.record.central_heating_conn_cost != None:
            self.central_heat_connection_cost_edit.setText(str(float(self.record.central_heating_conn_cost)))

        if self.record.is_fresh_water:
            self.water_yes_rbutton.setChecked(True)
        else:
            self.water_no_rbutton.setChecked(True)

        if self.record.fresh_water_distancel != None:
            self.water_distancel_edit.setText(str(float(self.record.fresh_water_distancel)))

        if self.record.fresh_water_conn_cost != None:
            self.water_connection_cost_edit.setText(str(float(self.record.fresh_water_conn_cost)))

        if self.record.is_sewage:
            self.sewage_yes_rbutton.setChecked(True)
        else:
            self.sewage_no_rbutton.setChecked(True)

        if self.record.sewage_distancel != None:
            self.sewage_distancel_edit.setText(str(float(self.record.sewage_distancel)))

        if self.record.sewage_conn_cost != None:
            self.sewage_connection_cost_edit.setText(str(float(self.record.sewage_conn_cost)))

        if self.record.is_well:
            self.well_yes_rbutton.setChecked(True)
        else:
            self.water_no_rbutton.setChecked(True)

        if self.record.well_distancel != None:
            self.well_distancel_edit.setText(str(float(self.record.well_distancel)))

        if self.record.is_self_financed_system:
            self.finance_yes_rbutton.setChecked(True)
        else:
            self.finance_no_rbutton.setChecked(True)

        if self.record.is_telephone:
            self.phone_yes_rbutton.setChecked(True)
        else:
            self.phone_no_rbutton.setChecked(True)

        if self.record.telephone_distancel != None:
            self.phone_distancel_edit.setText(str(float(self.record.telephone_distancel)))

        if self.record.is_flood_channel:
            self.flood_yes_rbutton.setChecked(True)
        else:
            self.flood_no_rbutton.setChecked(True)

        if self.record.flood_channel_distancel != None:
            self.flood_channel_distancel_edit.setText(str(float(self.record.flood_channel_distancel)))

        if self.record.is_vegetable_plot:
            self.plot_yes_rbutton.setChecked(True)
        else:
            self.plot_no_rbutton.setChecked(True)

        if self.record.vegetable_plot_size != None:
            self.vegetable_plot_size_edit.setText(str(float(self.record.vegetable_plot_size)))

        if self.record.is_land_slope:
            self.slope_yes_rbutton.setChecked(True)
        else:
            self.slope_no_rbutton.setChecked(True)

        if self.record.other_info != None:
            self.other_information_edit.setText(self.record.other_info)

        #Purchase
        purchase_count = session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.record.register_no).count()
        if self.home_purchase_rbutton.isChecked():
            if purchase_count != 0:

                purchase = session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.record.register_no).one()
                if purchase.landuse_ref:
                    self.purchase_use_type_cbox.setCurrentIndex(self.purchase_use_type_cbox.findData(purchase.landuse_ref.code))
                self.purchase_area_edit.setText(str(purchase.area_m2))
                self.purchase_dateEdit.setDateTime(QDateTime.fromString(purchase.purchase_date.strftime(Constants.PYTHON_DATE_FORMAT),
                                                                        Constants.DATABASE_DATE_FORMAT))
                self.purchase_price_edit.setText(str(purchase.price))
                self.purchase_price_if_m2.setText(str(purchase.price_m2))

                self.__home_purchase_add()
        else:
        #lease
            lease_count = session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.record.register_no).count()

            if lease_count != 0:

                lease = session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.record.register_no).one()

                if lease.landuse_ref:
                    self.lease_use_type_cbox.setCurrentIndex(self.lease_use_type_cbox.findData(lease.landuse_ref.code))
                self.lease_area_edit.setText(str(lease.area_m2))
                self.lease_dateEdit.setDateTime(QDateTime.fromString(lease.lease_date.strftime(Constants.PYTHON_DATE_FORMAT),
                                                                     Constants.DATABASE_DATE_FORMAT))
                self.lease_duration_edit.setText(str(lease.duration_month))
                self.lease_rent_edit.setText(str(lease.monthly_rent))
                self.lease_rent_of_m2.setText(str(lease.rent_m2))

                self.__home_lease_add()

        building_count = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.register_no == self.record.register_no).count()
        if building_count == 0:
            return
        building = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.register_no == self.record.register_no).all()

        for build in building:
            landuse = session.query(VaTypeLanduseBuilding).filter(VaTypeLanduseBuilding.code == build.landuse_building).one()
            landuse_item = QTableWidgetItem(landuse.description)
            landuse_item.setData(Qt.UserRole, landuse.code)
            building_text = build.building_id[-3:]
            building_item = QTableWidgetItem(str(building_text))
            building_item.setData(Qt.UserRole, build.building_id)
            stove = session.query(VaTypeStove).filter(VaTypeStove.code == build.stove_type).one()
            stove_item = QTableWidgetItem(stove.description)
            stove_item.setData(Qt.UserRole, stove.code)
            material = session.query(VaTypeMaterial).filter(VaTypeMaterial.code == build.material_type).one()
            material_item = QTableWidgetItem(material.description)
            material_item.setData(Qt.UserRole, material.code)
            heat = session.query(VaTypeHeat).filter(VaTypeHeat.code == build.heat_type).one()
            heat_item = QTableWidgetItem(heat.description)
            heat_item.setData(Qt.UserRole, heat.code)
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == build.building_status).one()
            status_item = QTableWidgetItem(status.description)
            status_item.setData(Qt.UserRole, status.code)

            area_item = QTableWidgetItem(str(build.area_m2))
            area_item.setData(Qt.UserRole, build.area_m2)
            construction_item = QTableWidgetItem(str(build.construction_year))
            construction_item.setData(Qt.UserRole, build.construction_year)
            floor_item = QTableWidgetItem(str(build.floor))
            floor_item.setData(Qt.UserRole, build.floor)
            status_year_item = QTableWidgetItem(str(build.status_year))
            status_year_item.setData(Qt.UserRole, build.status_year)

            row = self.home_building_twidget.rowCount()
            self.home_building_twidget.insertRow(row)

            self.home_building_twidget.setItem(row, 0, building_item)
            self.home_building_twidget.setItem(row, 1, landuse_item)
            self.home_building_twidget.setItem(row, 2, area_item)
            self.home_building_twidget.setItem(row, 3, material_item)
            self.home_building_twidget.setItem(row, 4, construction_item)
            self.home_building_twidget.setItem(row, 5, floor_item)
            self.home_building_twidget.setItem(row, 6, stove_item)
            self.home_building_twidget.setItem(row, 7, heat_item)
            self.home_building_twidget.setItem(row, 8, status_item)
            self.home_building_twidget.setItem(row, 9, status_year_item)


    def __set_visible_tabs(self):

        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.home_info_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.condominium_info_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.condominium_other_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.industrial_info_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.industrial_other_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.agriculture_info_tab))
        self.parcel_record_tab_widget.removeTab(self.parcel_record_tab_widget.indexOf(self.agriculture_other_tab))

        if self.parcel_type == 10:
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() - 1, self.home_info_tab,
                                                    self.tr("Home Parcel Information"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() + 1, self.infrastructure_other_tab,
                                                    self.tr("Infrastructure Other"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() - 1, self.specia_costs_tab,
                                                    self.tr("Special Costs"))
        elif self.parcel_type == 20:
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count(), self.condominium_info_tab,
                                                    self.tr("Commercial Information"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() + 1, self.condominium_other_tab,
                                                    self.tr("Commercial Other"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() - 1, self.specia_costs_tab,
                                                    self.tr("Special Costs"))
        elif self.parcel_type == 30:
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count(), self.industrial_info_tab,
                                                    self.tr("Industrial Information"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() + 1, self.industrial_other_tab,
                                                    self.tr("Industrial Other"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() - 1, self.specia_costs_tab,
                                                    self.tr("Special Costs"))
        elif self.parcel_type == 40:
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count(), self.agriculture_info_tab,
                                                    self.tr("Agriculture Information"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() + 1, self.agriculture_other_tab,
                                                    self.tr("Agriculture Other"))
            self.parcel_record_tab_widget.insertTab(self.parcel_record_tab_widget.count() - 1, self.specia_costs_tab,
                                                    self.tr("Special Costs"))
    def __special_costs_populate(self):

        bag_working_list = []
        session = SessionHandler().session_instance()
        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        aimag = session.query(AuLevel1).filter(AuLevel1.geometry.ST_Contains(parcel.geometry)).one()
        sum = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()

        self.aimag_working_edit.setText(aimag.name)
        self.sum_working_edit.setText(sum.name)

        self.bag_working_cbox.addItem("*", -1)
        if sum.code == None:
            return
        else:
            try:
                PluginUtils.populate_au_level3_cbox(self.bag_working_cbox, sum.code)
            except SQLAlchemyError, e:
                PluginUtils.show_message(self, self.tr("Sql Error"), e.message)

    def __home_combo_setup(self):

        applicationTypeList = []
        landuseTypeList = []
        sourceTypeList = []
        landuseBuildingList = []
        materialList = []
        stoveList = []
        heatList = []

        session = SessionHandler().session_instance()
        try:
            applicationTypeList = session.query(ClApplicationType.description, ClApplicationType.code).all()
            landuseTypeList = session.query(ClLanduseType.description, ClLanduseType.code).all()
            if self.parcel_type == 10:
                landuseTypeList = session.query(ClLanduseType.description, ClLanduseType.code)\
                    .filter(or_(ClLanduseType.code == 2204,ClLanduseType.code == 2205, ClLanduseType.code == 2206)).all()
            sourceTypeList = session.query(VaTypeSource.description, VaTypeSource.code).all()
            landuseBuildingList = session.query(VaTypeLanduseBuilding.description, VaTypeLanduseBuilding.code)
            materialList = session.query(VaTypeMaterial.description, VaTypeMaterial.code).all()
            stoveList = session.query(VaTypeStove.description, VaTypeStove.code).all()
            heatList = session.query(VaTypeHeat.description, VaTypeHeat.code).all()

        except SQLAlchemyError, e:
            QMessageBox.information(self, QApplication.translate("LM2", "Sql Error"), e.message)

        self.building_use_type_cbox.addItem("*", -1)
        self.building_material_cbox.addItem("*", -1)
        self.building_stove_type_cbox.addItem("*", -1)
        self.building_heat_Insulation_cbox.addItem("*", -1)

        if self.parcel_type == 10:
            for app_type in applicationTypeList:
                if app_type.code == 1 or app_type.code == 2 or app_type.code == 3 or app_type.code == 5 or app_type.code == 7 \
                    or app_type.code == 8 or app_type.code == 11 or app_type.code == 13 or app_type.code == 14 \
                    or app_type.code == 15:
                    self.right_type_cbox.addItem(app_type.description, app_type.code)

            for landuse in landuseTypeList:
                code = str(landuse.code)
                if code[:1] == '2':
                    self.purchase_use_type_cbox.addItem(landuse.description, str(landuse.code))
                    self.lease_use_type_cbox.addItem(landuse.description, str(landuse.code))

            for source in sourceTypeList:
                self.source_cbox.addItem(source.description, source.code)

            for landuse in landuseBuildingList:
                self.building_use_type_cbox.addItem(landuse.description, landuse.code)

            for material in materialList:
                self.building_material_cbox.addItem(material.description, material.code)

            for stove in stoveList:
                self.building_stove_type_cbox.addItem(stove.description, stove.code)

            for heat in heatList:
                self.building_heat_Insulation_cbox.addItem(heat.description, heat.code)
        elif self.parcel_type == 20:
            for app_type in applicationTypeList:
                if app_type.code == 2 or app_type.code == 4 or app_type.code == 5 or app_type.code == 7 or \
                    app_type.code == 8 or app_type.code == 11 or app_type.code == 13 or app_type.code == 14:
                    self.c_right_type_cbox.addItem(app_type.description, app_type.code)
        elif self.parcel_type == 30:
            for app_type in applicationTypeList:
                if app_type.code == 5 or app_type.code == 7 or app_type.code == 8 or app_type.code == 11 or \
                    app_type.code == 13 or app_type.code == 14:
                    self.i_right_type_cbox.addItem(app_type.description, app_type.code)
        elif self.parcel_type == 40:
            for app_type in applicationTypeList:
                if app_type.code == 4 or app_type.code == 5 or app_type.code == 7 or app_type.code == 8 or \
                    app_type.code == 11 or app_type.code == 13 or app_type.code == 14 or app_type.code == 15:
                    self.a_right_type_cbox.addItem(app_type.description, app_type.code)

    def __parcel_home_populate(self):

        now = QDateTime.currentDateTime()
        self.purchase_dateEdit.setDateTime(now)
        self.lease_dateEdit.setDateTime(now)
        self.registration_date.setDateTime(now)
        self.__home_combo_setup()
        self.__special_costs_populate()
        session = SessionHandler().session_instance()
        count = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).count()
        if count == 0:
            return
        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()

        if session.query(CtApplication).filter(CtApplication.parcel == parcel.parcel_id).count() == 0:
            #PluginUtils.show_message(self, self.tr("no"), self.tr("no application"))
            self.decision_date_edit.setText("")
            self.duration_year_edit.setText("")
        else:
            application = session.query(CtApplication).filter(CtApplication.parcel == parcel.parcel_id).all()
            for application in application:
                self.duration_year_edit.setText(str(application.approved_duration))
                if session.query(CtDecisionApplication).filter(CtDecisionApplication.application == application.app_no).count() == 0:
                    PluginUtils.show_message(self, self.tr(""), self.tr("no decision"))
                    self.decision_date_edit.setText("")
                else:
                    decision_application = session.query(CtDecisionApplication).filter(CtDecisionApplication.application == application.app_no).one()
                    if session.query(CtDecision).filter(CtDecision.decision_no == decision_application.decision).count() == 0:
                        PluginUtils.show_message(self, self.tr("no"), self.tr("no decision"))
                        self.decision_date_edit.setText("")
                    else:
                        decision = session.query(CtDecision).filter(CtDecision.decision_no == decision_application.decision).one()
                        self.decision_date_edit.setText(str(decision.decision_date))

        self.cadastreId_edit.setText(self.parcel_id)
        self.calculated_area_edit.setText(str(parcel.area_m2))

        if parcel.documented_area_m2 == None:
            self.purchase_area_edit.setText(str(parcel.area_m2))
            self.lease_area_edit.setText(str(parcel.area_m2))
        else:
            self.purchase_area_edit.setText(str(parcel.documented_area_m2))
            self.lease_area_edit.setText(str(parcel.documented_area_m2))
        address_streetname = ""
        address_khashaa = ""
        bag_name = ""
        if parcel.address_streetname != None:
            address_streetname = parcel.address_streetname
        if parcel.address_khashaa != None:
            address_khashaa = parcel.address_khashaa
        bags = session.query(AuLevel3).filter(AuLevel3.geometry.ST_Overlaps((parcel.geometry))).all()
        for bag in bags:
            bag_name = bag.name
        # bag = session.query(AuLevel3).filter( AuLevel3.geometry.ST_Within(func.ST_Centroid(parcel.geometry))).one()
        address = bag_name +", "+ address_streetname +", "+ address_khashaa

        self.address_edit.setText(address)
        sum = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()

        self.home_num_first_edit.setText(sum.code)
        self.home_num_type_edit.setText(str(self.parcel_type).zfill(2))
        self.home_num_last_edit.setText(QDate.currentDate().toString("yy"))

        parcel_type_filter = "%-" + str(self.parcel_type) + "-%"
        soum_filter = str(sum.code) + "-%"
        year_filter = "%-" + str(QDate.currentDate().toString("yy"))

        try:
            count = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no != self.register_no)\
                    .filter(VaInfoHomeParcel.register_no.like("%-%"))\
                    .filter(VaInfoHomeParcel.register_no.like(parcel_type_filter))\
                    .filter(VaInfoHomeParcel.register_no.like(soum_filter))\
                    .filter(VaInfoHomeParcel.register_no.like(year_filter))\
                .order_by(func.substr(VaInfoHomeParcel.register_no, 10, 13).desc()).count()
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Error"), e.message)
            return

        if count > 0:
            try:
                maxRegisterNo = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no != self.register_no)\
                    .filter(VaInfoHomeParcel.register_no.like("%-%"))\
                    .filter(VaInfoHomeParcel.register_no.like(parcel_type_filter))\
                    .filter(VaInfoHomeParcel.register_no.like(soum_filter))\
                    .filter(VaInfoHomeParcel.register_no.like(year_filter))\
                .order_by(func.substr(VaInfoHomeParcel.register_no, 10, 13).desc()).first()
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Database Error"), e.message)
                return

            register_no = maxRegisterNo.register_no.split("-")
            self.home_num_middle_edit.setText(str(int(register_no[2]) + 1).zfill(4))
        else:
            self.home_num_middle_edit.setText("0001")

        if session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).count() != 0:
            building = session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).all()
            for build in building:
                build_no = build.building_id[-3:]
                self.building_no_cbox.addItem(build_no, build.building_id)

    @pyqtSlot(int)
    def on_building_no_cbox_currentIndexChanged(self, index):

        session = SessionHandler().session_instance()
        building_id = self.building_no_cbox.itemData(index)

        building = session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
        self.building_area_edit.setText(str(building.area_m2))

    @pyqtSlot(int)
    def on_c_building_no_cbox_currentIndexChanged(self, index):

        session = SessionHandler().session_instance()
        building_id = self.c_building_no_cbox.itemData(index)

        building = session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
        self.c_building_area_edit.setText(str(building.area_m2))

    @pyqtSlot(int)
    def on_i_building_no_cbox_currentIndexChanged(self, index):

        session = SessionHandler().session_instance()
        building_id = self.i_building_no_cbox.itemData(index)

        building = session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
        self.i_building_area_edit.setText(str(building.area_m2))

    @pyqtSlot(int)
    def on_a_building_no_cbox_currentIndexChanged(self, index):

        session = SessionHandler().session_instance()
        building_id = self.a_building_no_cbox.itemData(index)

        building = session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
        self.a_building_area_edit.setText(str(building.area_m2))

    def __parcel_condominium_populate(self):

        now = QDateTime.currentDateTime()
        self.c_purchase_dateEdit.setDateTime(now)
        self.c_lease_dateEdit.setDateTime(now)
        self.__home_combo_setup()
        session = SessionHandler().session_instance()
        applicationTypeList = []
        landuseTypeList = []
        landuseBuildingList = []

        try:

            landuseTypeList = session.query(ClLanduseType.description, ClLanduseType.code).all()
            landuseBuildingList = session.query(VaTypeLanduseBuilding.description, VaTypeLanduseBuilding.code)

        except SQLAlchemyError, e:
            QMessageBox.information(self, QApplication.translate("LM2", "Sql Error"), e.message)

        for landuse in landuseTypeList:
            self.c_purchase_use_type_cbox.addItem(landuse.description, landuse.code)
            self.c_lease_use_type_cbox.addItem(landuse.description, landuse.code)

        for landuse in landuseBuildingList:
            self.c_building_use_type_cbox.addItem(landuse.description, landuse.code)

        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        sum = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()
        year_filter = "%-" + str(QDate.currentDate().toString("yy"))
        self.commercial_num_first_edit.setText(sum.code)
        self.commercial_num_type_edit.setText(str(self.parcel_type).zfill(2))
        self.commercial_num_last_edit.setText(QDate.currentDate().toString("yy"))

        if session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).count() != 0:
            building = session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).all()
            for build in building:
                build_no = build.building_id[-3:]
                self.c_building_no_cbox.addItem(build_no, build.building_id)

    def __parcel_industrial_populate(self):

        now = QDateTime.currentDateTime()
        self.i_purchase_date_edit.setDateTime(now)
        self.i_lease_dateEdit.setDateTime(now)
        self.__home_combo_setup()
        session = SessionHandler().session_instance()
        landuseTypeList = []

        try:
            landuseTypeList = session.query(ClLanduseType.description, ClLanduseType.code).all()

        except SQLAlchemyError, e:
            QMessageBox.information(self, QApplication.translate("LM2", "Sql Error"), e.message)


        for landuse in landuseTypeList:
            self.i_purchase_use_type_cbox.addItem(landuse.description, landuse.code)
            self.i_lease_use_type_cbox.addItem(landuse.description, landuse.code)
            self.i_building_use_type_cbox.addItem(landuse.description, landuse.code)

        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        sum = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()
        year_filter = "%-" + str(QDate.currentDate().toString("yy"))
        self.industrial_num_first_edit.setText(sum.code)
        self.industrial_num_type_edit.setText(str(self.parcel_type).zfill(2))
        self.industrial_num_last_edit.setText(QDate.currentDate().toString("yy"))

        if session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).count() != 0:
            building = session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).all()
            for build in building:
                build_no = build.building_id[-3:]
                self.i_building_no_cbox.addItem(build_no, build.building_id)

    def __parcel_agriculture_populate(self):

        now = QDateTime.currentDateTime()
        self.a_purchase_dateEdit.setDateTime(now)
        self.a_lease_dateEdit.setDateTime(now)
        self.__home_combo_setup()
        session = SessionHandler().session_instance()
        landuseTypeList = []

        try:
            landuseTypeList = session.query(ClLanduseType.description, ClLanduseType.code).all()

        except SQLAlchemyError, e:
            QMessageBox.information(self, QApplication.translate("LM2", "Sql Error"), e.message)

        for landuse in landuseTypeList:
            self.a_use_type_cbox.addItem(landuse.description, landuse.code)

        parcel = session.query(CaParcel).filter(CaParcel.parcel_id == self.parcel_id).one()
        sum = session.query(AuLevel2).filter(AuLevel2.geometry.ST_Contains(parcel.geometry)).one()
        year_filter = "%-" + str(QDate.currentDate().toString("yy"))
        self.agriculture_num_first_edit.setText(sum.code)
        self.agriculture_num_type_edit.setText(str(self.parcel_type).zfill(2))
        self.agriculture_num_last_edit.setText(QDate.currentDate().toString("yy"))

        if session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).count() != 0:
            building = session.query(CaBuilding).filter(parcel.geometry.ST_Contains(CaBuilding.geometry)).all()
            for build in building:
                build_no = build.building_id[-3:]
                self.a_building_no_cbox.addItem(build_no, build.building_id)


    @pyqtSlot(bool)
    def on_home_purchase_rbutton_toggled(self, state):

        if state:
            self.home_purchase_gbox.setEnabled(True)
            self.home_lease_gbox.setEnabled(False)
        else:
            self.home_purchase_gbox.setEnabled(False)
            self.home_lease_gbox.setEnabled(True)

    @pyqtSlot(bool)
    def on_home_lease_rbutton_toggled(self, state):

        if state:
            self.home_purchase_gbox.setEnabled(False)
            self.home_lease_gbox.setEnabled(True)
        else:
            self.home_purchase_gbox.setEnabled(True)
            self.home_lease_gbox.setEnabled(False)

    def __home_purchase_add(self):

        landuse_code = self.purchase_use_type_cbox.itemData(self.purchase_use_type_cbox.currentIndex())
        landuse_text = self.purchase_use_type_cbox.currentText()

        if self.purchase_price_edit.text() == "" or self.purchase_price_edit.text() == None:
            self.purchase_price_edit.setStyleSheet(Constants.ERROR_LINEEDIT_STYLESHEET)
            PluginUtils.show_message(self, self.tr("No Price"), self.tr("No Price"))
            return
        if self.purchase_area_edit.text() == "" or self.purchase_area_edit.text() == None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Area"))
            return
        if self.purchase_twidget.rowCount() != 0:
            PluginUtils.show_message(self, self.tr("Row"), self.tr("Already inserted row"))
            return
        usetype_item = QTableWidgetItem(landuse_text)
        usetype_item.setData(Qt.UserRole, landuse_code)
        date_item = QTableWidgetItem(self.purchase_dateEdit.text())
        date_item.setData(Qt.UserRole, self.purchase_dateEdit.text())
        area_item = QTableWidgetItem(self.purchase_area_edit.text())
        area_item.setData(Qt.UserRole, self.purchase_area_edit.text())
        price_item = QTableWidgetItem(self.purchase_price_edit.text())
        price_item.setData(Qt.UserRole, self.purchase_price_edit.text())
        price_m2_item = QTableWidgetItem(self.purchase_price_if_m2.text())
        price_m2_item.setData(Qt.UserRole, self.purchase_price_if_m2.text())

        row = self.purchase_twidget.rowCount()
        self.purchase_twidget.insertRow(row)

        self.purchase_twidget.setItem(row, 0, usetype_item)
        self.purchase_twidget.setItem(row, 1, date_item)
        self.purchase_twidget.setItem(row, 2, area_item)
        self.purchase_twidget.setItem(row, 3, price_item)
        self.purchase_twidget.setItem(row, 4, price_m2_item)

    def __home_lease_add(self):

        landuse_code = self.lease_use_type_cbox.itemData(self.lease_use_type_cbox.currentIndex())
        landuse_text = self.lease_use_type_cbox.currentText()
        if self.lease_duration_edit.text() == "" or self.lease_duration_edit.text() == None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Duration Month"))
            return
        if self.lease_rent_edit.text() == "" or self.lease_rent_edit.text() == None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Rent"))
            return
        if self.lease_twidget.rowCount() != 0:
            PluginUtils.show_message(self, self.tr("Row"), self.tr("Already inserted row"))
            return

        usetype_item = QTableWidgetItem(landuse_text)
        usetype_item.setData(Qt.UserRole, landuse_code)
        date_item = QTableWidgetItem(self.lease_dateEdit.text())
        date_item.setData(Qt.UserRole, self.lease_dateEdit.text())
        duration_item = QTableWidgetItem(self.lease_duration_edit.text())
        duration_item.setData(Qt.UserRole, self.lease_duration_edit.text())
        area_item = QTableWidgetItem(self.lease_area_edit.text())
        area_item.setData(Qt.UserRole, self.lease_area_edit.text())
        rent_item = QTableWidgetItem(self.lease_rent_edit.text())
        rent_item.setData(Qt.UserRole, self.lease_rent_edit.text())
        rent_m2_item = QTableWidgetItem(self.lease_rent_of_m2.text())
        rent_m2_item.setData(Qt.UserRole, self.lease_rent_of_m2.text())

        row = self.lease_twidget.rowCount()
        self.lease_twidget.insertRow(row)

        self.lease_twidget.setItem(row, 0, usetype_item)
        self.lease_twidget.setItem(row, 1, date_item)
        self.lease_twidget.setItem(row, 2, duration_item)
        self.lease_twidget.setItem(row, 3, area_item)
        self.lease_twidget.setItem(row, 4, rent_item)
        self.lease_twidget.setItem(row, 5, rent_m2_item)

    def __home_building_add(self):

        session = SessionHandler().session_instance()
        if self.building_use_type_cbox.itemData(self.building_use_type_cbox.currentIndex()) == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Use Type"))
            return
        if self.building_stove_type_cbox.itemData(self.building_stove_type_cbox.currentIndex()) == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Stove Type"))
            return
        if self.building_material_cbox.itemData(self.building_material_cbox.currentIndex()) == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Material Type"))
            return
        if self.building_heat_Insulation_cbox.itemData(self.building_heat_Insulation_cbox.currentIndex()) == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Heat Insulation Type"))
            return
        if self.no_floor_sbox.value() == 0:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Floor"))
            return
        all_rows = self.home_building_twidget.rowCount()
        for row in xrange(0,all_rows):
            building_id = self.home_building_twidget.item(row, 0)
            if building_id.text() == str(self.building_no_cbox.currentText()):
                PluginUtils.show_message(self, self.tr("Error"), self.tr("Already added"))
                return
        landuse_code = self.building_use_type_cbox.itemData(self.building_use_type_cbox.currentIndex())
        landuse_text = self.building_use_type_cbox.currentText()

        building_code = self.building_no_cbox.itemData(self.building_no_cbox.currentIndex())
        buidling_text = self.building_no_cbox.currentText()

        stove_code = self.building_stove_type_cbox.itemData(self.building_stove_type_cbox.currentIndex())
        stove_text = self.building_stove_type_cbox.currentText()

        material_code = self.building_material_cbox.itemData(self.building_material_cbox.currentIndex())
        material_text = self.building_material_cbox.currentText()

        heat_code = self.building_heat_Insulation_cbox.itemData(self.building_heat_Insulation_cbox.currentIndex())
        heat_text = self.building_heat_Insulation_cbox.currentText()

        if self.b_status_good_rbutton.isChecked():
            status_code = 10
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 10).one()
            status_text = status.description
        elif self.b_status_medium_rbutton.isChecked():
            status_code = 20
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 20).one()
            status_text = status.description
        elif self.b_status_bad_rbutton.isChecked():
            status_code = 30
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 30).one()
            status_text = status.description

        landuse_item = QTableWidgetItem(landuse_text)
        landuse_item.setData(Qt.UserRole, landuse_code)
        building_item = QTableWidgetItem(buidling_text)
        building_item.setData(Qt.UserRole, building_code)
        stove_item = QTableWidgetItem(stove_text)
        stove_item.setData(Qt.UserRole, stove_code)
        material_item = QTableWidgetItem(material_text)
        material_item.setData(Qt.UserRole, material_code)
        heat_item = QTableWidgetItem(heat_text)
        heat_item.setData(Qt.UserRole, heat_code)
        status_item = QTableWidgetItem(status_text)
        status_item.setData(Qt.UserRole, status_code)
        area_item = QTableWidgetItem(self.building_area_edit.text())
        area_item.setData(Qt.UserRole, self.building_area_edit.text())
        construction_item = QTableWidgetItem(self.building_construction_year_edit.text())
        construction_item.setData(Qt.UserRole, self.building_construction_year_edit.text())
        floor_item = QTableWidgetItem(str(self.no_floor_sbox.value()))
        floor_item.setData(Qt.UserRole, self.no_floor_sbox.value())
        status_year_item = QTableWidgetItem(self.building_status_year_date.text())
        status_year_item.setData(Qt.UserRole, self.building_status_year_date.text())

        row = self.home_building_twidget.rowCount()
        self.home_building_twidget.insertRow(row)

        self.home_building_twidget.setItem(row, 0, building_item)
        self.home_building_twidget.setItem(row, 1, landuse_item)
        self.home_building_twidget.setItem(row, 2, area_item)
        self.home_building_twidget.setItem(row, 3, material_item)
        self.home_building_twidget.setItem(row, 4, construction_item)
        self.home_building_twidget.setItem(row, 5, floor_item)
        self.home_building_twidget.setItem(row, 6, stove_item)
        self.home_building_twidget.setItem(row, 7, heat_item)
        self.home_building_twidget.setItem(row, 8, status_item)
        self.home_building_twidget.setItem(row, 9, status_year_item)

    def __home_general_save(self):

        session = SessionHandler().session_instance()
        home_count = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no == self.register_no).count()
        if home_count > 0:
            home_info = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no == self.register_no).one()
        else:
            home_info = VaInfoHomeParcel()

        register_no = self.home_num_first_edit.text() + "-" + self.home_num_type_edit.text() \
                       + "-" + self.home_num_middle_edit.text() + "-" + self.home_num_last_edit.text()
        # register_count = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no == register_no).count()
        # if register_count > 0:
        #     PluginUtils.show_message(self, self.tr("Error"), self.tr("Already registred"))
        #     return
        home_info.register_no = register_no
        home_info.parcel_id = self.cadastreId_edit.text()
        if self.home_purchase_rbutton.isChecked():
            ok = DatabaseUtils.class_instance_by_code(VaTypePurchaseOrLease, 10)
            home_info.purchase_or_lease_type_ref = ok
        else:
            ok = DatabaseUtils.class_instance_by_code(VaTypePurchaseOrLease, 20)
            home_info.purchase_or_lease_type_ref = ok
        home_info.area_m2 = float(self.calculated_area_edit.text())
        home_info.info_date = DatabaseUtils.convert_date(self.registration_date.date())
        if self.decision_date_edit.text() == "" or self.decision_date_edit.text() == None:
            home_info.decision_date = None
        else:
            self.decision_date_edit = (self.decision_date_edit.text())
        if self.duration_year_edit.text() == "" or self.duration_year_edit.text() == None or self.duration_year_edit.text() == 'None':
            home_info.approved_duration = None
        else:
            if self.duration_year_edit.text() == 'None':
                home_info.approved_duration = 0
            else:
                home_info.approved_duration = int(self.duration_year_edit.text())

        app_type_code = self.right_type_cbox.itemData(self.right_type_cbox.currentIndex())
        if app_type_code == -1:
            home_info.app_type = None
        else:
            app = DatabaseUtils.class_instance_by_code(ClApplicationType, app_type_code)
            home_info.app_type_ref = app
        source_type_code = self.source_cbox.itemData(self.source_cbox.currentIndex())
        if source_type_code == -1:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Source Type"))
            return
        else:
            source = DatabaseUtils.class_instance_by_code(VaTypeSource, source_type_code)
            home_info.source_type_ref = source

        if self.electricity_yes_rbutton.isChecked():
            home_info.is_electricity = True
        elif self.electricity_no_rbutton.isChecked():
            home_info.is_electricity = False

        if self.heating_yes_rbutton.isChecked():
            home_info.is_central_heating = True
        elif self.heating_no_rbutton.isChecked():
            home_info.is_central_heating = False

        if self.water_yes_rbutton.isChecked():
            home_info.is_fresh_water = True
        elif self.water_no_rbutton.isChecked():
            home_info.is_fresh_water = False

        if self.sewage_yes_rbutton.isChecked():
            home_info.is_sewage = True
        elif self.sewage_no_rbutton.isChecked():
            home_info.is_sewage = False

        if self.well_yes_rbutton.isChecked():
            home_info.is_well = True
        elif self.well_no_rbutton.isChecked():
            home_info.is_well = False

        if self.finance_yes_rbutton.isChecked():
            home_info.is_self_financed_system = True
        elif self.finance_no_rbutton.isChecked():
            home_info.is_self_financed_system = False

        if self.phone_yes_rbutton.isChecked():
            home_info.is_telephone = True
        elif self.phone_no_rbutton.isChecked():
            home_info.is_telephone = False

        if self.flood_yes_rbutton.isChecked():
            home_info.is_flood_channel = True
        elif self.flood_no_rbutton.isChecked():
            home_info.is_flood_channel = False

        if self.plot_yes_rbutton.isChecked():
            home_info.is_vegetable_plot = True
        elif self.plot_no_rbutton.isChecked():
            home_info.is_vegetable_plot = False

        if self.slope_yes_rbutton.isChecked():
            home_info.is_land_slope = True
        elif self.slope_no_rbutton.isChecked():
            home_info.is_land_slope = False

        if self.side_fence_1_2_rbutton.isChecked():
            home_info.side_fence_type = 10
        elif self.side_fence_3_rbutton.isChecked():
            home_info.side_fence_type = 20
        elif self.side_fence_4_rbutton.isChecked():
            home_info.side_fence_type = 30
        elif self.side_fence_5_rbutton.isChecked():
            home_info.side_fence_type = 40

        if self.electricity_distancel_edit.text() != '':
            home_info.electricity_distancel = float(self.electricity_distancel_edit.text())
        else:
            home_info.electricity_distancel = None

        if self.electricity_connection_cost_edit.text() != '':
            home_info.electricity_conn_cost = float(self.electricity_connection_cost_edit.text())
        else:
            home_info.electricity_conn_cost = None

        if self.central_heat_distancel_edit.text() != '':
            home_info.central_heating_distancel = float(self.central_heat_distancel_edit.text())
        else:
            home_info.central_heating_distancel = None

        if self.central_heat_connection_cost_edit.text() != '':
            home_info.central_heating_conn_cost = float(self.central_heat_connection_cost_edit.text())
        else:
            home_info.central_heating_conn_cost = None

        if self.water_distancel_edit.text() != '':
            home_info.fresh_water_distancel = float(self.water_distancel_edit.text())
        else:
            home_info.fresh_water_distancel = None

        if self.water_connection_cost_edit.text() != '':
            home_info.fresh_water_conn_cost = float(self.water_connection_cost_edit.text())
        else:
            home_info.fresh_water_conn_cost = None

        if self.sewage_distancel_edit.text() != '':
            home_info.sewage_distancel = float(self.sewage_distancel_edit.text())
        else:
            home_info.sewage_distancel = None

        if self.sewage_connection_cost_edit.text() != '':
            home_info.sewage_conn_cost = float(self.sewage_connection_cost_edit.text())
        else:
            home_info.sewage_conn_cost = None

        if self.well_distancel_edit.text() != '':
            home_info.well_distancel = float(self.well_distancel_edit.text())
        else:
            home_info.well_distancel = None

        if self.phone_distancel_edit.text() != '':
            home_info.telephone_distancel = float(self.phone_distancel_edit.text())
        else:
            home_info.telephone_distancel = None

        if self.flood_channel_distancel_edit.text() != '':
            home_info.flood_channel_distancel = float(self.flood_channel_distancel_edit.text())
        else:
            home_info.flood_channel_distancel = None

        if self.vegetable_plot_size_edit.text() != '':
            home_info.vegetable_plot_size = float(self.vegetable_plot_size_edit.text())
        else:
            home_info.vegetable_plot_size = None

        if self.other_information_edit.toPlainText() != '':
            home_info.other_info = self.other_information_edit.toPlainText()
        else:
            home_info.other_info = None

        session.add(home_info)

    def __home_purchase_save(self):

        session = SessionHandler().session_instance()
        row_count = self.purchase_twidget.rowCount()
        if row_count == 0:
            return
        purchase_count = session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.register_no).count()
        if purchase_count > 0:
            purchase = session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.register_no).one()
        else:
            purchase = VaInfoHomePurchase()
        landuse_code = self.purchase_use_type_cbox.itemData(self.purchase_use_type_cbox.currentIndex())
        purchase_date = DatabaseUtils.convert_date(self.purchase_dateEdit.date())
        if landuse_code == -1:
            purchase.landuse_ref = None
        else:
            landuse = DatabaseUtils.class_instance_by_code(ClLanduseType, landuse_code)
            purchase.landuse_ref = landuse

        register_no = self.home_num_first_edit.text() + "-" + self.home_num_type_edit.text() \
                       + "-" + self.home_num_middle_edit.text() + "-" + self.home_num_last_edit.text()

        purchase.register_no = register_no
        purchase.area_m2 = float(self.purchase_area_edit.text())
        purchase.purchase_date = purchase_date
        purchase.price = float(self.purchase_price_edit.text())
        purchase.price_m2 = float(self.purchase_price_if_m2.text())

        session.add(purchase)

    def __home_lease_save(self):

        session = SessionHandler().session_instance()
        lease_count = session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.register_no).count()
        if lease_count > 0:
            lease = session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.register_no).one()
        else:
            lease = VaInfoHomeLease()
        landuse_code = self.lease_use_type_cbox.itemData(self.lease_use_type_cbox.currentIndex())
        lease_date = DatabaseUtils.convert_date(self.lease_dateEdit.date())
        if landuse_code == -1:
            lease.landuse_ref = None
        else:
            landuse = DatabaseUtils.class_instance_by_code(ClLanduseType, landuse_code)
            lease.landuse_ref = landuse

        register_no = self.home_num_first_edit.text() + "-" + self.home_num_type_edit.text() \
                       + "-" + self.home_num_middle_edit.text() + "-" + self.home_num_last_edit.text()
        lease.register_no = register_no
        lease.area_m2 = float(self.lease_area_edit.text())
        lease.lease_date = lease_date
        lease.duration_month = int(self.lease_duration_edit.text())
        lease.monthly_rent = float(self.lease_rent_edit.text())
        lease.rent_m2 = float(self.lease_rent_of_m2.text())

        session.add(lease)

    def __home_building_save(self):

        if self.home_building_twidget.rowCount() == 0:
            return

        register_no = self.home_num_first_edit.text() + "-" + self.home_num_type_edit.text() \
                       + "-" + self.home_num_middle_edit.text() + "-" + self.home_num_last_edit.text()
        session = SessionHandler().session_instance()
        #loop save
        all_rows = self.home_building_twidget.rowCount()
        for row in xrange(0,all_rows):
            building_count = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.register_no == self.register_no).count()
            if building_count > 0:
                building = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.register_no == self.register_no).one()
            else:
                building = VaInfoHomeBuilding()
            id_item = self.home_building_twidget.item(row, 0)
            building_id = id_item.data(Qt.UserRole)

            landuse_item = self.home_building_twidget.item(row, 1)
            landuse_type = landuse_item.data(Qt.UserRole)

            area_item = self.home_building_twidget.item(row, 2)
            area = area_item.data(Qt.UserRole)

            material_item = self.home_building_twidget.item(row, 3)
            material = material_item.data(Qt.UserRole)

            constraction_item = self.home_building_twidget.item(row, 4)
            constraction = constraction_item.data(Qt.UserRole)

            floor_item = self.home_building_twidget.item(row, 5)
            floor = floor_item.data(Qt.UserRole)

            stove_item = self.home_building_twidget.item(row, 6)
            stove = stove_item.data(Qt.UserRole)

            heat_item = self.home_building_twidget.item(row, 7)
            heat = heat_item.data(Qt.UserRole)

            status_item = self.home_building_twidget.item(row, 8)
            status = status_item.data(Qt.UserRole)

            status_year_item = self.home_building_twidget.item(row, 9)
            status_year = status_year_item.data(Qt.UserRole)

            if landuse_type == -1:
                building.landuse_building_ref = None
            else:
                landuse = DatabaseUtils.class_instance_by_code(VaTypeLanduseBuilding, int(landuse_type))
                building.landuse_building_ref = landuse
            if stove == -1:
                building.stove_type_ref = None
            else:
                stove = DatabaseUtils.class_instance_by_code(VaTypeStove, int(stove))
                building.stove_type_ref = stove
            if material == -1:
                building.material_type_ref = None
            else:
                material = DatabaseUtils.class_instance_by_code(VaTypeMaterial, int(material))
                building.material_type_ref = material
            if heat == -1:
                building.heat_type_ref = None
            else:
                heat = DatabaseUtils.class_instance_by_code(VaTypeHeat, int(heat))
                building.heat_type_ref = heat
            ok = DatabaseUtils.class_instance_by_code(VaTypeStatusBuilding, int(status))
            building.building_status_ref = ok

            building.building_id = building_id
            building.area_m2 = float(area)
            building.floor = float(floor)
            building.status_year = int(status_year)
            building.construction_year = int(constraction)
            building.register_no = register_no
            session.add(building)

    @pyqtSlot()
    def on_purchase_add_button_clicked(self):

        self.__home_purchase_add()

    @pyqtSlot()
    def on_lease_add_button_clicked(self):

        self.__home_lease_add()

    @pyqtSlot()
    def on_building_add_button_clicked(self):

        self.__home_building_add()

    @pyqtSlot()
    def on_purchase_delete_button_clicked(self):

        selected_row = self.purchase_twidget.currentRow()
        self.purchase_twidget.removeRow(selected_row)

    @pyqtSlot()
    def on_lease_delete_button_clicked(self):

        selected_row = self.lease_twidget.currentRow()
        self.lease_twidget.removeRow(selected_row)

    @pyqtSlot()
    def on_building_delete_button_clicked(self):

        selected_row = self.home_building_twidget.currentRow()
        self.home_building_twidget.removeRow(selected_row)

    @pyqtSlot()
    def on_purchase_update_button_clicked(self):

        selected_row = self.purchase_twidget.currentRow()

        use_item = self.purchase_twidget.item(selected_row, 0)
        date_item = self.purchase_twidget.item(selected_row, 1)
        area_item = self.purchase_twidget.item(selected_row, 2)
        price_item = self.purchase_twidget.item(selected_row, 3)

        landuse_code = self.purchase_use_type_cbox.itemData(self.purchase_use_type_cbox.currentIndex())
        landuse_text = self.purchase_use_type_cbox.currentText()
        if use_item == None:
            PluginUtils.show_message(self, self.tr("Selection Error"), self.tr("Select one item to start editing."))
            return
        use_item.setText(landuse_text)
        use_item.setData(Qt.UserRole, landuse_code)
        date_item.setText(self.purchase_dateEdit.text())
        date_item.setData(Qt.UserRole,self.purchase_dateEdit.text())
        area_item.setText(self.purchase_area_edit.text())
        area_item.setData(Qt.UserRole, self.purchase_area_edit.text())
        price_item.setText(self.purchase_price_edit.text())
        price_item.setData(Qt.UserRole, self.purchase_price_edit.text())

    @pyqtSlot()
    def on_lease_update_button_clicked(self):

        selected_row = self.lease_twidget.currentRow()
        usetype_item = self.lease_twidget.item(selected_row, 0)
        date_item = self.lease_twidget.item(selected_row, 1)
        duration_item = self.lease_twidget.item(selected_row, 2)
        area_item = self.lease_twidget.item(selected_row, 3)
        rent_item = self.lease_twidget.item(selected_row, 4)

        landuse_code = self.lease_use_type_cbox.itemData(self.lease_use_type_cbox.currentIndex())
        landuse_text = self.lease_use_type_cbox.currentText()
        if usetype_item == None:
            PluginUtils.show_message(self, self.tr("Selection Error"), self.tr("Select one item to start editing."))
            return
        if self.lease_duration_edit.text() == "" or self.lease_duration_edit.text() == None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Duration Month"))
            return
        if self.lease_rent_edit.text() == "" or self.lease_rent_edit.text() == None:
            PluginUtils.show_message(self, self.tr("Error"), self.tr("No Rent"))
            return

        usetype_item.setText(landuse_text)
        usetype_item.setData(Qt.UserRole, landuse_code)
        date_item.setText(self.lease_dateEdit.text())
        date_item.setData(Qt.UserRole, self.lease_dateEdit.text())
        duration_item.setText(self.lease_duration_edit.text())
        duration_item.setData(Qt.UserRole, self.lease_duration_edit.text())
        area_item.setText(self.lease_area_edit.text())
        area_item.setData(Qt.UserRole, self.lease_area_edit.text())
        rent_item.setText(self.lease_rent_edit.text())
        rent_item.setData(Qt.UserRole, self.lease_rent_edit.text())

    @pyqtSlot()
    def on_building_update_button_clicked(self):

        session = SessionHandler().session_instance()

        selected_row = self.home_building_twidget.currentRow()

        building_item = self.home_building_twidget.item(selected_row, 0)
        landuse_item = self.home_building_twidget.item(selected_row, 1)
        area_item = self.home_building_twidget.item(selected_row, 2)
        material_item = self.home_building_twidget.item(selected_row, 3)
        construction_item = self.home_building_twidget.item(selected_row, 4)
        floor_item = self.home_building_twidget.item(selected_row, 5)
        stove_item = self.home_building_twidget.item(selected_row, 6)
        heat_item = self.home_building_twidget.item(selected_row, 7)
        status_item = self.home_building_twidget.item(selected_row, 8)
        status_year_item = self.home_building_twidget.item(selected_row, 9)

        landuse_code = self.building_use_type_cbox.itemData(self.building_use_type_cbox.currentIndex())
        landuse_text = self.building_use_type_cbox.currentText()

        building_code = self.building_no_cbox.itemData(self.building_no_cbox.currentIndex())
        buidling_text = self.building_no_cbox.currentText()

        stove_code = self.building_stove_type_cbox.itemData(self.building_stove_type_cbox.currentIndex())
        stove_text = self.building_stove_type_cbox.currentText()

        material_code = self.building_material_cbox.itemData(self.building_material_cbox.currentIndex())
        material_text = self.building_material_cbox.currentText()

        heat_code = self.building_heat_Insulation_cbox.itemData(self.building_heat_Insulation_cbox.currentIndex())
        heat_text = self.building_heat_Insulation_cbox.currentText()

        if self.b_status_good_rbutton.isChecked():
            status_code = 10
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 10).one()
            status_text = status.description
        elif self.b_status_medium_rbutton.isChecked():
            status_code = 20
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 20).one()
            status_text = status.description
        elif self.b_status_bad_rbutton.isChecked():
            status_code = 30
            status = session.query(VaTypeStatusBuilding).filter(VaTypeStatusBuilding.code == 30).one()
            status_text = status.description

        if landuse_item == None:
            PluginUtils.show_message(self, self.tr("Selection Error"), self.tr("Select one item to start editing."))
            return

        landuse_item.setText(landuse_text)
        landuse_item.setData(Qt.UserRole, landuse_code)
        building_item.setText(buidling_text)
        building_item.setData(Qt.UserRole, building_code)
        stove_item.setText(stove_text)
        stove_item.setData(Qt.UserRole, stove_code)
        material_item.setText(material_text)
        material_item.setData(Qt.UserRole, material_code)
        heat_item.setText(heat_text)
        heat_item.setData(Qt.UserRole, heat_code)
        status_item.setText(status_text)
        status_item.setData(Qt.UserRole, status_code)
        area_item.setText(self.building_area_edit.text())
        area_item.setData(Qt.UserRole, self.building_area_edit.text())
        construction_item.setText(self.building_construction_year_edit.text())
        construction_item.setData(Qt.UserRole, self.building_construction_year_edit.text())
        floor_item.setText(str(self.no_floor_sbox.value()))
        floor_item.setData(Qt.UserRole, self.no_floor_sbox.value())
        status_year_item.setText(self.building_status_year_date.text())
        status_year_item.setData(Qt.UserRole, self.building_status_year_date.text())

    @pyqtSlot()
    def on_ok_button_clicked(self):

        session = SessionHandler().session_instance()
        register_no = self.home_num_first_edit.text() + "-" + self.home_num_type_edit.text() \
                       + "-" + self.home_num_middle_edit.text() + "-" + self.home_num_last_edit.text()
        # register_count = session.query(VaInfoHomeParcel).filter(VaInfoHomeParcel.register_no == register_no).count()
        # if register_count > 0:
        #     PluginUtils.show_message(self, self.tr("Error"), self.tr("Already registred"))
        #     return
        # if self.home_purchase_rbutton.isChecked():
        #     if self.purchase_twidget.rowCount() == 0:
        #         PluginUtils.show_message(self, self.tr("Error"), self.tr("No Purchase Data"))
        #         return
        # elif self.home_lease_rbutton.isChecked():
        #     if self.lease_twidget.rowCount() == 0:
        #         PluginUtils.show_message(self, self.tr("Error"), self.tr("No Lease Data"))
        #         return
        msgBox = QMessageBox()
        msgBox.setText(self.tr("Do you want to finish?"))
        okButton = msgBox.addButton(self.tr("Yes"), QMessageBox.ActionRole)
        msgBox.addButton(self.tr("No"), QMessageBox.ActionRole)
        msgBox.setWindowFlags(Qt.WindowStaysOnTopHint)
        msgBox.exec_()
        if msgBox.clickedButton() == okButton:
            if self.parcel_type == 10:
                self.__home_general_save()
                if self.home_purchase_rbutton.isChecked():
                    self.__home_purchase_save()
                    self.__purchase_delete()
                elif self.home_lease_rbutton.isChecked():
                    self.__home_lease_save()

                self.__home_building_save()
                self.__building_delete()
                session.commit()
                self.accept()
                PluginUtils.show_message(self,self.tr("Successfully"),self.tr("Successfully inserted"))

    @pyqtSlot(QTableWidgetItem)
    def on_home_building_twidget_itemClicked(self, item):

        current_row = self.home_building_twidget.currentRow()

        building_item = self.home_building_twidget.item(current_row, 0)
        building_id = building_item.data(Qt.UserRole)

        use_item = self.home_building_twidget.item(current_row, 1)
        use_id = use_item.data(Qt.UserRole)

        area_item = self.home_building_twidget.item(current_row, 2)
        area = area_item.data(Qt.UserRole)

        material_item = self.home_building_twidget.item(current_row, 3)
        material_id = material_item.data(Qt.UserRole)

        const_item = self.home_building_twidget.item(current_row, 4)
        const_year = const_item.data(Qt.UserRole)

        floor_item = self.home_building_twidget.item(current_row, 5)
        floor = floor_item.data(Qt.UserRole)

        stove_item = self.home_building_twidget.item(current_row, 6)
        stove_id = stove_item.data(Qt.UserRole)

        heat_item = self.home_building_twidget.item(current_row, 7)
        heat_id = heat_item.data(Qt.UserRole)

        status_item = self.home_building_twidget.item(current_row, 8)
        status_id = status_item.data(Qt.UserRole)

        status_year_item = self.home_building_twidget.item(current_row, 9)
        status_year = status_year_item.data(Qt.UserRole)

        session = SessionHandler().session_instance()
        building = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.building_id == building_id).\
                                                        filter(VaInfoHomeBuilding.register_no == self.register_no).one()
        if building.building_id:
            self.building_no_cbox.setCurrentIndex(self.building_no_cbox.findData(building.building_id))

        if building.landuse_building_ref:
            self.building_use_type_cbox.setCurrentIndex(self.building_use_type_cbox.findData(building.landuse_building_ref.code))

        self.building_area_edit.setText(str(area))

        if building.material_type_ref:
            self.building_material_cbox.setCurrentIndex(self.building_material_cbox.findData(building.material_type_ref.code))

        #self.building_construction_year_edit.setDateTime(building.construction_year)
        # self.building_construction_year_edit.setDateTime(QDateTime.fromTime_t(const_year))
        self.no_floor_sbox.setValue(floor)
        if building.stove_type_ref:
            self.building_stove_type_cbox.setCurrentIndex(self.building_stove_type_cbox.findData(building.stove_type_ref.code))
        if building.heat_type_ref:
            self.building_heat_Insulation_cbox.setCurrentIndex(self.building_heat_Insulation_cbox.findData(building.heat_type_ref.code))
        if building.building_status_ref:
            if building.building_status_ref.code == 10:
                self.b_status_good_rbutton.setChecked(True)
            elif building.building_status_ref.code == 20:
                self.b_status_medium_rbutton.setChecked(True)
            elif building.building_status_ref.code == 30:
                self.b_status_bad_rbutton.setChecked(True)
        # self.building_status_year_date.setDate(QDateTime.fromString((str((building.status_year +"."+ 01 +"."+ 01))).strftime(Constants.PYTHON_DATE_FORMAT),
        #                                                             Constants.DATABASE_DATE_FORMAT))

    def __parcel_populate(self):

        if self.parcel_type == 10:
            self.__parcel_home_populate()
        elif self.parcel_type == 20:
            self.__parcel_condominium_populate()
        elif self.parcel_type == 30:
            self.__parcel_industrial_populate()
        elif self.parcel_type == 40:
            self.__parcel_agriculture_populate()

    def __purchase_delete(self):

        session = SessionHandler().session_instance()
        purchase_count = session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.register_no).count()
        row_count = self.purchase_twidget.rowCount()
        if purchase_count != 0:
            if row_count == 0:
                session.query(VaInfoHomePurchase).filter(VaInfoHomePurchase.register_no == self.register_no).delete()

    def __lease_delete(self):

        session = SessionHandler().session_instance()
        lease_count = session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.register_no).count()
        row_count = self.lease_twidget.rowCount()
        if lease_count != 0:
            if row_count == 0:
                session.query(VaInfoHomeLease).filter(VaInfoHomeLease.register_no == self.register_no).delete()

    def __building_delete(self):

        session = SessionHandler().session_instance()
        building_id = self.building_no_cbox.itemData(self.building_no_cbox.currentIndex())
        building_count = session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.register_no == self.register_no).\
                                                        filter(VaInfoHomeBuilding.register_no == self.register_no).count()
        row_count = self.home_building_twidget.rowCount()
        if building_count != 0:
            if row_count == 0:
                session.query(VaInfoHomeBuilding).filter(VaInfoHomeBuilding.building_id == building_id).one()

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe C:\Users\User\.qgis2\python\plugins\lm2\help\output\help_lm2.chm::/html/Create_New_Postgis_Connection.htm")

    @pyqtSlot()
    def on_calculate_button_clicked(self):

        parcel_area_max = 0
        parcel_area_min = 0
        parcel_area_avg = 0

        parcel_price_max = 0
        parcel_price_min = 0
        parcel_price_avg = 0

        if self.cost_purchase_rbutton.isChecked() == False and self.cost_lease_rbutton.isChecked() == False:
            PluginUtils.show_message(self, self.tr("Is Checked"), self.tr("Purchase or Lease ???"))
            return

        if self.cost_purchase_rbutton.isChecked():

            parcel_max_area = self.session.query(func.max(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomePurchase, VaInfoHomeParcel.register_no == VaInfoHomePurchase.register_no)\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())
            parcel_max = parcel_max_area.one()
            print parcel_max

            parcel_min_area = self.session.query(func.min(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomePurchase, VaInfoHomeParcel.register_no == VaInfoHomePurchase.register_no)\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())
            parcel_min = parcel_min_area.one()

            parcel_avg_area = self.session.query(func.avg(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomePurchase, VaInfoHomeParcel.register_no == VaInfoHomePurchase.register_no)\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())
            parcel_avg = parcel_avg_area.one()

            parcel_purchase_max_price = self.session.query(func.max(VaInfoHomePurchase.price))\
                .join(VaInfoHomeParcel, VaInfoHomePurchase.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomePurchase.purchase_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomePurchase.landuse == 2205, VaInfoHomePurchase.landuse == 2204, VaInfoHomePurchase.landuse == 2206))
            parcel_purchase_max = parcel_purchase_max_price.one()


            parcel_purchase_min_price = self.session.query(func.min(VaInfoHomePurchase.price))\
                .join(VaInfoHomeParcel, VaInfoHomePurchase.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomePurchase.purchase_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomePurchase.landuse == 2205, VaInfoHomePurchase.landuse == 2204, VaInfoHomePurchase.landuse == 2206))
            parcel_purchase_min = parcel_purchase_min_price.one()

            parcel_purchase_avg_price = self.session.query(func.avg(VaInfoHomePurchase.price))\
                .join(VaInfoHomeParcel, VaInfoHomePurchase.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomePurchase.purchase_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomePurchase.landuse == 2205, VaInfoHomePurchase.landuse == 2204, VaInfoHomePurchase.landuse == 2206))
            parcel_purchase_avg = parcel_purchase_avg_price.one()

            if self.bag_working_cbox.currentIndex() > 0:
                au_code = self.bag_working_cbox.itemData(self.bag_working_cbox.currentIndex())
                parcel_max_area = parcel_max_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_max = parcel_max_area.one()

                parcel_min_area = parcel_min_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_min = parcel_min_area.one()

                parcel_avg_area = parcel_avg_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_avg = parcel_avg_area.one()

                parcel_purchase_max_price = parcel_purchase_max_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_purchase_max = parcel_purchase_max_price.one()

                parcel_purchase_min_price = parcel_purchase_min_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_purchase_min = parcel_purchase_min_price.one()

                parcel_purchase_avg_price = parcel_purchase_avg_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_purchase_avg = parcel_purchase_avg_price.one()
            if self.cost_year_checkbox.checkState() == False:
                if self.q1_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()

                elif self.q1_checkbox.isChecked() and self.q2_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 1,extract('month',VaInfoHomePurchase.purchase_date) == 2,extract('month',VaInfoHomePurchase.purchase_date) == 3,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()

                elif self.q2_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()
                elif self.q2_checkbox.isChecked() and self.q3_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 4,extract('month',VaInfoHomePurchase.purchase_date) == 5,extract('month',VaInfoHomePurchase.purchase_date) == 6))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()
                elif self.q3_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()
                elif self.q3_checkbox.isChecked() and self.q4_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 7,extract('month',VaInfoHomePurchase.purchase_date) == 8,extract('month',VaInfoHomePurchase.purchase_date) == 9,\
                                    extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()
                elif self.q4_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_avg = parcel_avg_area.one()

                    parcel_purchase_max_price = parcel_purchase_max_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_max = parcel_purchase_max_price.one()

                    parcel_purchase_min_price = parcel_purchase_min_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_min = parcel_purchase_min_price.one()

                    parcel_purchase_avg_price = parcel_purchase_avg_price\
                        .filter(or_(extract('month',VaInfoHomePurchase.purchase_date) == 10,extract('month',VaInfoHomePurchase.purchase_date) == 11,extract('month',VaInfoHomePurchase.purchase_date) == 12))
                    parcel_purchase_avg = parcel_purchase_avg_price.one()

            for area in parcel_avg:
                if area == None:
                    parcel_area_avg = 0
                else:
                    parcel_area_avg = int(area)
            for area in parcel_max:
                if area == None:
                    parcel_area_max = 0
                else:
                    parcel_area_max = int(area)
            for area in parcel_min:
                if area == None:
                    parcel_area_min = 0
                else:
                    parcel_area_min = int(area)

            for price in parcel_purchase_max:
                if price == None:
                    parcel_price_max = 0
                else:
                    parcel_price_max = int(price)
            for price in parcel_purchase_min:
                if price == None:
                    parcel_price_min = 0
                else:
                    parcel_price_min = int(price)
            for price in parcel_purchase_avg:
                if price == None:
                    parcel_price_avg = 0
                else:
                    parcel_price_avg = int(price)
        elif self.cost_lease_rbutton.isChecked():
            parcel_max_area = self.session.query(func.max(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomeLease, VaInfoHomeParcel.register_no == VaInfoHomeLease.register_no)\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))
            parcel_max = parcel_max_area.one()

            parcel_min_area = self.session.query(func.min(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomeLease, VaInfoHomeParcel.register_no == VaInfoHomeLease.register_no)\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))
            parcel_min = parcel_min_area.one()

            parcel_avg_area = self.session.query(func.avg(CaParcel.area_m2))\
                .join(VaInfoHomeParcel, CaParcel.parcel_id == VaInfoHomeParcel.parcel_id)\
                .join(VaInfoHomeLease, VaInfoHomeParcel.register_no == VaInfoHomeLease.register_no)\
                .filter(extract('year',VaInfoHomeParcel.info_date) == self.year_sbox.value())\
                .filter(or_(CaParcel.landuse == 2205, CaParcel.landuse == 2204, CaParcel.landuse == 2206))
            parcel_avg = parcel_avg_area.one()

            parcel_lease_max_price = self.session.query(func.max(VaInfoHomeLease.monthly_rent))\
                .join(VaInfoHomeParcel, VaInfoHomeLease.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomeLease.lease_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomeLease.landuse == 2205, VaInfoHomeLease.landuse == 2204, VaInfoHomeLease.landuse == 2206))
            parcel_lease_max = parcel_lease_max_price.one()

            parcel_lease_min_price = self.session.query(func.min(VaInfoHomeLease.monthly_rent))\
                .join(VaInfoHomeParcel, VaInfoHomeLease.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomeLease.lease_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomeLease.landuse == 2205, VaInfoHomeLease.landuse == 2204, VaInfoHomeLease.landuse == 2206))
            parcel_lease_min = parcel_lease_min_price.one()

            parcel_lease_avg_price = self.session.query(func.avg(VaInfoHomeLease.monthly_rent))\
                .join(VaInfoHomeParcel, VaInfoHomeLease.register_no == VaInfoHomeParcel.register_no)\
                .join(CaParcel, VaInfoHomeParcel.parcel_id == CaParcel.parcel_id)\
                .filter(extract('year',VaInfoHomeLease.lease_date) == self.year_sbox.value())\
                .filter(or_(VaInfoHomeLease.landuse == 2205, VaInfoHomeLease.landuse == 2204, VaInfoHomeLease.landuse == 2206))
            parcel_lease_avg = parcel_lease_avg_price.one()

            if self.bag_working_cbox.currentIndex() > 0:
                au_code = self.bag_working_cbox.itemData(self.bag_working_cbox.currentIndex())
                parcel_max_area = parcel_max_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_max = parcel_max_area.one()

                parcel_min_area = parcel_min_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_min = parcel_min_area.one()

                parcel_avg_area = parcel_avg_area\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_avg = parcel_avg_area.one()

                parcel_lease_max_price = parcel_lease_max_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_lease_max = parcel_lease_max_price.one()

                parcel_lease_min_price = parcel_lease_min_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_lease_min = parcel_lease_min_price.one()

                parcel_lease_avg_price = parcel_lease_avg_price\
                    .filter(CaParcel.geometry.ST_Within(AuLevel3.geometry))\
                    .filter(AuLevel3.code == au_code)
                parcel_lease_avg = parcel_lease_avg_price.one()

            if self.cost_year_checkbox.checkState() == False:
                if self.q1_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3))
                    parcel_lease_avg = parcel_lease_avg_price.one()

                elif self.q1_checkbox.isChecked() and self.q2_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 1,extract('month',VaInfoHomeParcel.info_date) == 2,extract('month',VaInfoHomeParcel.info_date) == 3,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 1,extract('month',VaInfoHomeLease.lease_date) == 2,extract('month',VaInfoHomeLease.lease_date) == 3,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_avg = parcel_lease_avg_price.one()

                elif self.q2_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_avg = parcel_lease_avg_price.one()
                elif self.q2_checkbox.isChecked() and self.q3_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 4,extract('month',VaInfoHomeParcel.info_date) == 5,extract('month',VaInfoHomeParcel.info_date) == 6))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 4,extract('month',VaInfoHomeLease.lease_date) == 5,extract('month',VaInfoHomeLease.lease_date) == 6))
                    parcel_lease_avg = parcel_lease_avg_price.one()
                elif self.q3_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9))
                    parcel_lease_avg = parcel_lease_avg_price.one()
                elif self.q3_checkbox.isChecked() and self.q4_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 7,extract('month',VaInfoHomeParcel.info_date) == 8,extract('month',VaInfoHomeParcel.info_date) == 9,\
                                    extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 7,extract('month',VaInfoHomeLease.lease_date) == 8,extract('month',VaInfoHomeLease.lease_date) == 9,\
                                    extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_avg = parcel_lease_avg_price.one()
                elif self.q4_checkbox.isChecked():
                    parcel_max_area = parcel_max_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_max = parcel_max_area.one()

                    parcel_min_area = parcel_min_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_min = parcel_min_area.one()

                    parcel_avg_area = parcel_avg_area\
                        .filter(or_(extract('month',VaInfoHomeParcel.info_date) == 10,extract('month',VaInfoHomeParcel.info_date) == 11,extract('month',VaInfoHomeParcel.info_date) == 12))
                    parcel_avg = parcel_avg_area.one()

                    parcel_lease_max_price = parcel_lease_max_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_max = parcel_lease_max_price.one()

                    parcel_lease_min_price = parcel_lease_min_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_min = parcel_lease_min_price.one()

                    parcel_lease_avg_price = parcel_lease_avg_price\
                        .filter(or_(extract('month',VaInfoHomeLease.lease_date) == 10,extract('month',VaInfoHomeLease.lease_date) == 11,extract('month',VaInfoHomeLease.lease_date) == 12))
                    parcel_lease_avg = parcel_lease_avg_price.one()

            for area in parcel_avg:
                if area == None:
                    parcel_area_avg = 0
                else:
                    parcel_area_avg = int(area)
            for area in parcel_max:
                if area == None:
                    parcel_area_max = 0
                else:
                    parcel_area_max = int(area)
            for area in parcel_min:
                if area == None:
                    parcel_area_min = 0
                else:
                    parcel_area_min = int(area)

            for price in parcel_lease_max:
                if price == None:
                    parcel_price_max = 0
                else:
                    parcel_price_max = int(price)
            for price in parcel_lease_min:
                if price == None:
                    parcel_price_max = 0
                else:
                    parcel_price_min = int(price)
            for price in parcel_lease_avg:
                if price == None:
                    parcel_price_max = 0
                else:
                    parcel_price_avg = int(price)

        if parcel_price_max != 0 and parcel_area_max != 0:
            price_max = int(parcel_price_max/parcel_area_max)
        else:
            price_max = 0
        if parcel_price_min != 0 and parcel_area_min != 0:
            price_min = int(parcel_price_min/parcel_area_min)
        else:
            price_min = 0
        if parcel_price_avg != 0 and parcel_area_avg != 0:
            price_avg = int(parcel_price_avg/parcel_area_avg)
        else:
            price_avg = 0

        item = QTableWidgetItem(str(parcel_area_max))
        item.setData(Qt.UserRole, parcel_area_max)
        self.calculate_twidget.setItem(1,1,item)

        item = QTableWidgetItem(str(parcel_area_min))
        item.setData(Qt.UserRole, parcel_area_min)
        self.calculate_twidget.setItem(2,1,item)

        item = QTableWidgetItem(str(parcel_area_avg))
        item.setData(Qt.UserRole, parcel_area_avg)
        self.calculate_twidget.setItem(0,1,item)

        #purchase
        item = QTableWidgetItem(str(parcel_price_max))
        item.setData(Qt.UserRole, parcel_price_max)
        self.calculate_twidget.setItem(1,2,item)

        item = QTableWidgetItem(str(parcel_price_min))
        item.setData(Qt.UserRole, parcel_price_min)
        self.calculate_twidget.setItem(2,2,item)

        item = QTableWidgetItem(str(parcel_price_avg))
        item.setData(Qt.UserRole, parcel_price_avg)
        self.calculate_twidget.setItem(0,2,item)

        #div
        item = QTableWidgetItem(str(price_max))
        item.setData(Qt.UserRole, price_max)
        self.calculate_twidget.setItem(1,0,item)

        item = QTableWidgetItem(str(price_min))
        item.setData(Qt.UserRole, price_min)
        self.calculate_twidget.setItem(2,0,item)

        item = QTableWidgetItem(str(price_avg))
        item.setData(Qt.UserRole, price_avg)
        self.calculate_twidget.setItem(0,0,item)

    @pyqtSlot(bool)
    def on_electricity_no_rbutton_toggled(self, state):

        if state:
            self.electricity_distancel_edit.setEnabled(False)
            self.electricity_connection_cost_edit.setEnabled(False)
            self.electricity_distancel_edit.setText(None)
            self.electricity_connection_cost_edit.setText(None)
        else:
            self.electricity_distancel_edit.setEnabled(True)
            self.electricity_connection_cost_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_heating_no_rbutton_toggled(self, state):

        if state:
            self.central_heat_distancel_edit.setEnabled(False)
            self.central_heat_connection_cost_edit.setEnabled(False)
            self.central_heat_distancel_edit.setText(None)
            self.central_heat_connection_cost_edit.setText(None)
        else:
            self.central_heat_distancel_edit.setEnabled(True)
            self.central_heat_connection_cost_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_water_no_rbutton_toggled(self, state):

        if state:
            self.water_distancel_edit.setEnabled(False)
            self.water_connection_cost_edit.setEnabled(False)
            self.water_distancel_edit.setText(None)
            self.water_connection_cost_edit.setText(None)
        else:
            self.water_distancel_edit.setEnabled(True)
            self.water_connection_cost_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_sewage_no_rbutton_toggled(self, state):

        if state:
            self.sewage_distancel_edit.setEnabled(False)
            self.sewage_connection_cost_edit.setEnabled(False)
            self.sewage_distancel_edit.setText(None)
            self.sewage_connection_cost_edit.setText(None)
        else:
            self.sewage_distancel_edit.setEnabled(True)
            self.sewage_connection_cost_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_well_no_rbutton_toggled(self, state):

        if state:
            self.well_distancel_edit.setEnabled(False)
            self.well_distancel_edit.setText(None)
        else:
            self.well_distancel_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_phone_no_rbutton_toggled(self, state):

        if state:
            self.phone_distancel_edit.setEnabled(False)
            self.phone_distancel_edit.setText(None)
        else:
            self.phone_distancel_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_flood_no_rbutton_toggled(self, state):

        if state:
            self.flood_channel_distancel_edit.setEnabled(False)
            self.flood_channel_distancel_edit.setText(None)
        else:
            self.flood_channel_distancel_edit.setEnabled(True)

    @pyqtSlot(bool)
    def on_plot_no_rbutton_toggled(self, state):

        if state:
            self.vegetable_plot_size_edit.setEnabled(False)
            self.vegetable_plot_size_edit.setText(None)
        else:
            self.vegetable_plot_size_edit.setEnabled(True)