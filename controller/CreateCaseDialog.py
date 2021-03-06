__author__ = 'Ankhaa'
# -*- encoding: utf-8 -*-
from qgis.core import *
from geoalchemy2.elements import WKTElement

from ..view.Ui_CreateCaseDialog import *
from ..utils.LayerUtils import LayerUtils
from ..model.CaTmpParcel import *
from ..model.CaMaintenanceCase import *
from ..model.CaBuilding import *
from ..model.CaTmpBuilding import *
from ..model.CtApplicationStatus import *
from ..model.ClLanduseType import *
from ..model.DatabaseHelper import DatabaseHelper
from ..model import Constants
from .qt_classes.ApplicationCmbBoxDelegate import *
from ..controller.ApplicationsDialog import *
from ..model.ApplicationSearch import *

class CreateCaseDialog(QDialog, Ui_CreateCaseDialog, DatabaseHelper):

    def __init__(self, plugin, m_case, attribute_update=False, parent=None):

        super(CreateCaseDialog, self).__init__(parent)
        DatabaseHelper.__init__(self)

        self.setupUi(self)
        self.timer = None
        self.close_button.clicked.connect(self.reject)

        self.plugin = plugin
        self.ca_maintenance_case = m_case
        self.attribute_update = attribute_update
        self.session = SessionHandler().session_instance()
        self.is_file_import = False
        self.buildings_item = None
        self.parcels_item = None
        self.filling = False
        self.exclude_list = []
        self.application_list = list()
        self.start_date.setDateTime(QDateTime().currentDateTime())

        self.maintenance_parcels = []
        self.maintenance_buildings = []

        self.__setup_twidgets()
        self.__setup_context_menu()

        try:

            if self.__check_requirements():
                if self.attribute_update:
                    self.__setup_mapping()
                else:
                    user = DatabaseUtils.current_user()
                    self.created_by_edit.setText(user.surname + "-" + user.first_name)

                    self.__parcel_touch_select()

        except LM2Exception, e:
            PluginUtils.show_error(self, e.title(), e.message())

    def __setup_mapping(self):

        self.__set_up_twidget(self.applications_twidget)
        completion_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.completion_date)
        if completion_date:
            converted_date = completion_date.toString(completion_date.toString(Constants.DATABASE_DATE_FORMAT))
            self.completion_date_edit.setText(converted_date)

        survey_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.survey_date)
        if survey_date:
            self.survey_date_edit.setText(survey_date.toString(Constants.DATABASE_DATE_FORMAT))

        creation_date = PluginUtils.convert_python_date_to_qt(self.ca_maintenance_case.creation_date)
        if creation_date:
            self.start_date.setDate(creation_date)

        if self.ca_maintenance_case.created_by is not None:
            created_by_role = self.session.query(SetRole)\
                                    .filter(SetRole.user_name == self.ca_maintenance_case.created_by).one()
            self.created_by_edit.setText((created_by_role.first_name + " " + created_by_role.surname))

        if self.ca_maintenance_case.surveyed_by_land_office is not None:
            surveyed_land_office_role = self.session.query(SetRole)\
                                            .filter(SetRole.user_name == self.ca_maintenance_case.surveyed_by_land_office)\
                                            .one()
            self.surveyed_by_land_office_edit.setText((surveyed_land_office_role.first_name +" "+
                                                              surveyed_land_office_role.surname))

        if self.ca_maintenance_case.surveyed_by_surveyor is not None:
            surveyed_by_surveyor_role = self.session.query(SetSurveyor)\
                                            .filter(SetSurveyor.id == self.ca_maintenance_case.surveyed_by_surveyor)\
                                            .one()
            self.surveyed_by_surveyor_edit.setText((surveyed_by_surveyor_role.first_name+" "+
                                                           surveyed_by_surveyor_role.surname))

        if self.ca_maintenance_case.completed_by:
            completed_by_role = self.session.query(SetRole)\
                                                .filter(SetRole.user_name == self.ca_maintenance_case.completed_by).one()
            self.completed_by_edit.setText((completed_by_role.first_name +" "+ completed_by_role.surname))

        applications = self.session.query(CtApplication.app_no)\
            .filter(CtApplication.parcel == None).all()

        for app_result in applications:

            item = QTableWidgetItem()
            item.setText(app_result[0])

            row = self.applications_twidget.rowCount()
            self.applications_twidget.insertRow(row)

            self.applications_twidget.setItem(row, 0, item)

        self.buildings_item = QTreeWidgetItem()
        self.buildings_item.setExpanded(True)
        self.buildings_item.setText(0, self.tr("Buildings"))

        self.parcels_item = QTreeWidgetItem()
        self.parcels_item.setExpanded(True)
        self.parcels_item.setText(0, self.tr("Parcels"))

        self.result_twidget.addTopLevelItem(self.parcels_item)
        self.result_twidget.addTopLevelItem(self.buildings_item)

        parcel_count = 0
        khashaa = ""
        street = ""

        for parcel in self.ca_maintenance_case.parcels:
            touch_item = QTreeWidgetItem()
            touch_item.setText(0, parcel.parcel_id)
            khashaa = parcel.address_khashaa
            street = parcel.address_streetname
            touch_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_grey.png")))
            touch_item.setData(0, Qt.UserRole, parcel.parcel_id)
            touch_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            self.parcels_item.addChild(touch_item)
            parcel_count += 1

        building_count = 0
        for building in self.ca_maintenance_case.buildings:
            building_item = QTreeWidgetItem()
            building_item.setText(0, building.building_id)
            building_item.setData(0, Qt.UserRole, building.building_id)
            building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
            building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
            self.buildings_item.addChild(building_item)
            building_count += 1

        self.parcel_count_label.setText(str(parcel_count))
        self.building_count_label.setText(str(building_count))
        self.street_label.setText(street)
        self.khashaa_label.setText(khashaa)

    @staticmethod
    def __check_requirements():

        #parcel layer and tmp parcel layer should be added
        #building layer and tmp building layer should be added
        root = QgsProject.instance().layerTreeRoot()

        LayerUtils.refresh_layer()
        restrictions = DatabaseUtils.working_l2_code()

        parcel_layer = LayerUtils.layer_by_data_source("s" + restrictions, "ca_parcel")
        if parcel_layer is None:
            LayerUtils.load_layer_by_name("ca_parcel", "parcel_id", restrictions)

        building_layer = LayerUtils.layer_by_data_source("s" + restrictions, "ca_building")
        if building_layer is None:
            LayerUtils.load_layer_by_name("ca_building", "building_id", restrictions)

        tmp_parcel_layer = LayerUtils.layer_by_data_source("s" + restrictions, "ca_tmp_parcel")

        if tmp_parcel_layer is None:
            mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
            vlayer = LayerUtils.load_layer_by_name_report("ca_tmp_parcel", "parcel_id", restrictions)
            vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"template\style/ca_tmp_parcel.qml")
            mygroup.addLayer(vlayer)

        tmp_building_layer = LayerUtils.layer_by_data_source("s" + restrictions, "ca_tmp_building")
        if tmp_building_layer is None:
            mygroup = root.findGroup(u"Кадастрын өөрчлөлт")
            vlayer = LayerUtils.load_layer_by_name_report("ca_tmp_building", "building_id", restrictions)
            vlayer.loadNamedStyle(str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"template\style/ca_tmp_building.qml")
            mygroup.addLayer(vlayer)

        return True

    def __setup_twidgets(self):

        self.__set_up_twidget(self.applications_twidget)

        self.result_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.result_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.result_twidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.result_twidget.setContextMenuPolicy(Qt.CustomContextMenu)

        working_soum = DatabaseUtils.working_l2_code()
        parcel_layer = LayerUtils.layer_by_data_source("s" + working_soum, "ca_parcel")
        selected_features = parcel_layer.selectedFeatures()
        selected_features_count = parcel_layer.selectedFeatureCount()
        parcel_id_index = parcel_layer.dataProvider().fieldNameIndex("parcel_id")
        applications = ''
        app_no_parcel = ''
        try:
            for feature in selected_features:
                # parcel_count += 1
                parcel_id = feature.attributes()[parcel_id_index]
                app_contract_count = self.session.query(CtContractApplicationRole)\
                    .join(CtApplication, CtContractApplicationRole.application == CtApplication.app_no)\
                    .filter(CtContractApplicationRole.contract != None)\
                    .filter(CtApplication.parcel == parcel_id).count()
                app_record_count = self.session.query(CtRecordApplicationRole)\
                    .join(CtApplication, CtRecordApplicationRole.application == CtApplication.app_no)\
                    .filter(CtRecordApplicationRole.record != None)\
                    .filter(CtApplication.parcel == parcel_id).count()
                app_count = self.session.query(CtApplication.parcel == parcel_id).count()
                if app_contract_count > 0:
                    contracts = self.session.query(CtContract)\
                        .join(CtContractApplicationRole, CtContract.contract_no == CtContractApplicationRole.contract)\
                        .join(CtApplication, CtContractApplicationRole.application == CtApplication.app_no)\
                        .filter(CtContract.contract_no != None)\
                        .filter(CtApplication.parcel == parcel_id).all()
                    for contract in contracts:
                        if contract.status != 40:
                            PluginUtils.show_error(self, self.tr("Invalid Parcel"),
                                                self.tr("This parcel connected active possess contract!!!"))
                            self.apply_button.setEnabled(False)
                            return
                if app_record_count > 0:
                    records = self.session.query(CtOwnershipRecord)\
                        .join(CtRecordApplicationRole, CtOwnershipRecord.record_no == CtRecordApplicationRole.record)\
                        .join(CtApplication, CtRecordApplicationRole.application == CtApplication.app_no)\
                        .filter(CtOwnershipRecord.record_no != None)\
                        .filter(CtApplication.parcel == parcel_id).all()
                    for record in records:
                        if record.status != 30:
                            PluginUtils.show_error(self, self.tr("Invalid Parcel"),
                                                self.tr("This parcel connected active ownership record!!!"))
                            self.apply_button.setEnabled(False)
                            return
                # if app_count > 0:
                #     app = self.session.query(CtApplicationStatus.status)\
                #         .join(CtApplication, CtApplication.app_no == CtApplicationStatus.application)\
                #         .filter(CtApplication.parcel == parcel_id).all()
                #     for application in app:
                #         if application.status != 9:
                #             if application.status >= 5 and application.status != 8:
                #                 PluginUtils.show_error(self, self.tr("Invalid Parcel"),
                #                                     self.tr("This parcel sent to decision draft!!!"))
                #                 self.apply_button.setEnabled(False)
                #                 return

                applications = self.session.query(CtApplication.app_no).join(CtApplicationStatus)\
                    .filter(CtApplication.parcel == parcel_id)\
                    .filter(CtApplicationStatus.status < Constants.APP_STATUS_SEND)\
                    .filter(CtApplication.maintenance_case.is_(None)).distinct(CtApplication.app_no).all()
                applications_count = self.session.query(CtApplication.app_no).join(CtApplicationStatus)\
                    .filter(CtApplication.parcel == parcel_id)\
                    .filter(CtApplicationStatus.status < Constants.APP_STATUS_SEND)\
                    .filter(CtApplication.maintenance_case.is_(None)).distinct(CtApplication.app_no).count()

                if applications_count != 0:
                    for app_result in applications:

                        item = QTableWidgetItem()
                        item.setText(app_result[0])
                        row = self.applications_twidget.rowCount()
                        self.applications_twidget.insertRow(row)

                        self.applications_twidget.setItem(row, 0, item)

            app_no_parcel = self.session.query(CtApplication.app_no).filter(CtApplication.parcel == None).all()
            app_no_parcel_count = self.session.query(CtApplication).filter(CtApplication.parcel == None).count()

            if selected_features_count == 0 and app_no_parcel_count != 0:

                for app_result in app_no_parcel:

                    item = QTableWidgetItem()
                    item.setText(app_result[0])
                    row = self.applications_twidget.rowCount()
                    self.applications_twidget.insertRow(row)

                    self.applications_twidget.setItem(row, 0, item)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return


        self.application_list = list()
        del self.application_list[:]
        for app in applications:
            self.application_list.append(app.app_no)
        if applications != "" and applications_count != 0:
            delegate = ApplicationCmbBoxDelegate(0, self.application_list, self.applications_twidget)
            self.applications_twidget.setItemDelegateForColumn(0, delegate)
        else:
            for app in app_no_parcel:
                self.application_list.append(app.app_no)
            if selected_features_count == 0 and app_no_parcel_count > 0:
                delegate = ApplicationCmbBoxDelegate(0, self.application_list, self.applications_twidget)
                self.applications_twidget.setItemDelegateForColumn(0, delegate)

    def __set_up_twidget(self, table_widget):

        table_widget.setAlternatingRowColors(True)
        table_widget.setSelectionBehavior(QTableWidget.SelectRows)
        table_widget.setSelectionMode(QTableWidget.SingleSelection)

    def __setup_context_menu(self):

        self.menu = QMenu()
        self.zoom_to_selected = QAction(QIcon("zoom.png"), "Zoom to item", self)
        self.menu.addAction(self.zoom_to_selected)
        self.zoom_to_selected.triggered.connect(self.zoom_to_selected_clicked)

    @pyqtSlot()
    def zoom_to_selected_clicked(self):

        selected_item = self.result_twidget.selectedItems()[0]

        if selected_item is None:
            return

        if selected_item.data(0, Qt.UserRole + 1) == Constants.CASE_PARCEL_IDENTIFIER:
            working_soum = DatabaseUtils.working_l2_code()
            parcel_layer = LayerUtils.layer_by_data_source("s" + working_soum, "ca_parcel")
            selection_features = []

            for f in LayerUtils.where(parcel_layer, "parcel_id={0}".format(selected_item.data(0, Qt.UserRole))):
                selection_features.append(f.id())

            parcel_layer.setSelectedFeatures(selection_features)

            self.plugin.iface.mapCanvas().zoomToSelected(parcel_layer)
            self.plugin.iface.mapCanvas().zoomOut()

        elif selected_item.data(0, Qt.UserRole + 1) == Constants.CASE_BUILDING_IDENTIFIER:
            working_soum = DatabaseUtils.working_l2_code()
            building_layer = LayerUtils.layer_by_data_source("s" + working_soum, "ca_building")
            selection_features = []

            for f in LayerUtils.where(building_layer, "building_id={0}".format(selected_item.data(0, Qt.UserRole))):
                selection_features.append(f.id())

            building_layer.setSelectedFeatures(selection_features)

            self.plugin.iface.mapCanvas().zoomToSelected(building_layer)
            self.plugin.iface.mapCanvas().zoomOut()
            self.plugin.iface.mapCanvas().zoomOut()


    def __setup_file_import(self):

        self.import_groupbox.setEnabled(True)
        self.parcels_item = QTreeWidgetItem()
        parcels_caption = self.tr("Parcels")
        self.parcels_item.setText(0, parcels_caption)

        self.buildings_item = QTreeWidgetItem()
        buildings_caption = self.tr("Buildings")
        self.buildings_item.setText(0, buildings_caption)

        self.result_twidget.addTopLevelItem(self.buildings_item)
        self.result_twidget.addTopLevelItem(self.parcels_item)

    def __parcel_touch_select(self):

        working_soum = DatabaseUtils.working_l2_code()
        parcel_layer = LayerUtils.layer_by_data_source("s" + working_soum, "ca_parcel")
        self.maintenance_parcels = []
        self.maintenance_buildings = []

        if not parcel_layer:
            PluginUtils.show_error(self, self.tr("Error"),
                                   self.tr("Could not identify parcel layer. "
                                           "Please load the parcel layer for the working soum."))
            self.apply_button.setEnabled(False)
            return

        count = parcel_layer.selectedFeatureCount()
        if count == 0:
            #enable file import
            self.is_file_import = True
            self.__setup_file_import()
            return

        selected_features = parcel_layer.selectedFeatures()
        parcel_id_index = parcel_layer.dataProvider().fieldNameIndex("parcel_id")

        parcel_count = 0
        building_count = 0

        for feature in selected_features:
            parcel_count += 1
            parcel_id = feature.attributes()[parcel_id_index]

            #checks if the parcel is already in the tmp layer
            try:
                count = self.session.query(CaTmpParcel).filter(CaTmpParcel.parcel_id == parcel_id).count()

            except SQLAlchemyError, e:
                raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))

            if count > 0:
                PluginUtils.show_error(self, "Selection Error",
                                       self.tr("One of selected parcel is already in an active case. "
                                               "First finalize or revert from active case. Close dialog window"))
                self.apply_button.setEnabled(False)
                return

            if parcel_id in self.maintenance_parcels:
                continue

            self.maintenance_parcels.append(parcel_id)

            #Add main parcel to the tree
            main_parcel_item = QTreeWidgetItem()
            main_parcel_item.setText(0, parcel_id)
            main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
            main_parcel_item.setData(0, Qt.UserRole, parcel_id)
            main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
            self.result_twidget.addTopLevelItem(main_parcel_item)

            try:
                parcel_geometry = self.session.query(CaParcel.geometry).filter(CaParcel.parcel_id == parcel_id).one()

                touching_parcels = self.session.query(CaParcel)\
                    .filter(CaParcel.geometry.ST_Intersects(parcel_geometry[0]))\
                    .filter(CaParcel.parcel_id != parcel_id).all()

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            for touching_parcel in touching_parcels:

                try:
                    count = self.session.query(CaTmpParcel)\
                        .filter(CaTmpParcel.parcel_id == touching_parcel.parcel_id).count()
                except SQLAlchemyError, e:
                    PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                if count > 0:
                    PluginUtils.show_error(self, self.tr("Selection Error"),
                                           self.tr("One of selected parcel is already in active case. "
                                                   "First finalize or revert from active case. Close dialog window"))

                    self.apply_button.setEnabled(False)
                    self.reject()
                    return

                if touching_parcel.parcel_id in self.maintenance_parcels:
                    continue

                parcel_count += 1
                touch_item = QTreeWidgetItem()
                touch_item.setText(0, touching_parcel.parcel_id)
                touch_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_grey.png")))
                touch_item.setData(0, Qt.UserRole, touching_parcel.parcel_id)
                touch_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
                self.result_twidget.addTopLevelItem(touch_item)

                self.maintenance_parcels.append(touching_parcel.parcel_id)

                #building features for touching parcels
                try:
                    buildings = self.session.query(CaBuilding.building_id)\
                                    .filter(CaBuilding.geometry.ST_Within(touching_parcel.geometry))\
                                    .filter(CaBuilding.building_id.ilike(touching_parcel.parcel_id + "%")).all()

                except SQLAlchemyError, e:
                    raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                    return

                for building in buildings:

                    if building[0] in self.maintenance_buildings:
                        continue

                    building_count += 1
                    building_item = QTreeWidgetItem()
                    building_item.setText(0, building[0])
                    building_item.setData(0, Qt.UserRole, building[0])
                    building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
                    building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                    touch_item.addChild(building_item)

                    self.maintenance_buildings.append(building[0])

            #gets the containing building features
            try:
                buildings = self.session.query(CaBuilding.building_id)\
                                .filter(CaBuilding.geometry.ST_Within(parcel_geometry[0]))\
                                .filter(CaBuilding.building_id.contains(parcel_id)).all()

                for building in buildings:

                    if building[0] in self.maintenance_buildings:
                        continue

                    building_count += 1
                    building_item = QTreeWidgetItem()
                    building_item.setText(0, building[0])
                    building_item.setData(0, Qt.UserRole, building[0])
                    building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)
                    building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
                    main_parcel_item.addChild(building_item)

                    self.maintenance_buildings.append(building[0])

            except SQLAlchemyError, e:
                raise LM2Exception(self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

        self.parcel_count_label.setText(str(parcel_count))
        self.building_count_label.setText(str(building_count))

    @pyqtSlot()
    def on_result_twidget_itemSelectionChanged(self):

        if self.is_file_import:
            return

        current_item = self.result_twidget.selectedItems()[0]
        object_type = current_item.data(0, Qt.UserRole + 1)
        object_id = current_item.data(0, Qt.UserRole)

        if object_type == Constants.CASE_PARCEL_IDENTIFIER:
            try:
                parcel = self.session.query(CaParcel.address_khashaa, CaParcel.address_streetname)\
                    .filter(CaParcel.parcel_id == object_id).one()

                self.khashaa_label.setText(parcel[0])
                self.street_label.setText(parcel[1])
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

        elif object_type == Constants.CASE_BUILDING_IDENTIFIER:
            try:
                building = self.session.query(CaBuilding.address_khashaa, CaBuilding.address_streetname)\
                    .filter(CaBuilding.building_id == object_id).one()

                self.khashaa_label.setText(building[0])
                self.street_label.setText(building[1])
            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

    @pyqtSlot()
    def on_open_parcel_file_button_clicked(self):

        default_path = r'D:/TM_LM2/cad_maintenance'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.parcel_shape_edit.setText(file_path)
            self.__import_new_parcels(file_path)
            self.open_parcel_file_button.setEnabled(False)

    @pyqtSlot()
    def on_open_building_file_button_clicked(self):

        default_path = r'D:/TM_LM2/cad_maintenance'
        default_parent_path = r'D:/TM_LM2'
        if not os.path.exists(default_parent_path):
            os.makedirs('D:/TM_LM2')
            os.makedirs('D:/TM_LM2/application_response')
            os.makedirs('D:/TM_LM2/application_list')
            os.makedirs('D:/TM_LM2/approved_decision')
            os.makedirs('D:/TM_LM2/cad_maintenance')
            os.makedirs('D:/TM_LM2/cad_maps')
            os.makedirs('D:/TM_LM2/contracts')
            os.makedirs('D:/TM_LM2/decision_draft')
            os.makedirs('D:/TM_LM2/dumps')
            os.makedirs('D:/TM_LM2/q_data')
            os.makedirs('D:/TM_LM2/refused_decision')
            os.makedirs('D:/TM_LM2/reports')
            os.makedirs('D:/TM_LM2/training')
        if not os.path.exists(default_path):
            os.makedirs(default_path)

        file_dialog = QFileDialog()
        file_dialog.setModal(True)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setFilter(self.tr("Shapefiles (*.shp)"))
        file_dialog.setDirectory(default_path)

        if file_dialog.exec_():
            selected_file = file_dialog.selectedFiles()[0]
            file_path = QFileInfo(selected_file).filePath()
            self.building_shape_edit.setText(file_path)
            if not self.__import_new_buildings(file_path):
                self.apply_button.setEnabled(False)

            self.open_building_file_button.setEnabled(False)

    def __import_new_parcels(self, file_path):

        parcel_shape_layer = QgsVectorLayer(file_path, "tmp_parcel_shape", "ogr")

        if not parcel_shape_layer.isValid():
            PluginUtils.show_error(self,  self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return

        if parcel_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"),
                                   self.tr("The crs of the layer has to be 4326."))
            return

        iterator = parcel_shape_layer.getFeatures()
        count = 0
        try:
            for parcel in iterator:
                count += 1
                new_parcel = CaTmpParcel()
                new_parcel.parcel_id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
                new_parcel.initial_insert = None
                new_parcel.maintenance_case = self.ca_maintenance_case.id
                new_parcel.geometry = WKTElement(parcel.geometry().exportToWkt(), srid=4326)
                new_parcel = self.__copy_parcel_attributes(parcel, new_parcel, parcel_shape_layer)

                self.session.add(new_parcel)

                #Add main parcel to the tree
                main_parcel_item = QTreeWidgetItem()
                main_parcel_item.setText(0, new_parcel.parcel_id)
                main_parcel_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/parcel_red.png")))
                main_parcel_item.setData(0, Qt.UserRole, new_parcel.parcel_id)
                main_parcel_item.setData(0, Qt.UserRole + 1, Constants.CASE_PARCEL_IDENTIFIER)
                self.parcels_item.addChild(main_parcel_item)

        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

    def __copy_parcel_attributes(self, parcel_feature, parcel_object, layer):

        column_name_old_parcel = "old_parcel"
        column_name_geo_id = "geo_id"
        column_name_landuse = "landuse"
        column_name_documented = "documented"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_neighbourhood = "address_ne"

        column_names = {column_name_old_parcel: "", column_name_geo_id: "", column_name_landuse: "",
                        column_name_documented: "", column_name_khashaa: "", column_name_street: "",
                        column_name_neighbourhood: ""}

        provider = layer.dataProvider()

        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = parcel_feature.attributes()[index]
                column_names[key] = value
        landuse_invalid = False
        try:
            count = self.session.query(ClLanduseType).filter(ClLanduseType.code == column_names[column_name_landuse]).count()
            if count == 0:
                PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))
                column_names[column_name_landuse] = ""
                landuse_invalid = True

        except SQLAlchemyError, e:
            landuse_invalid = True
            PluginUtils.show_error(self, self.tr("Shapefile error"), self.tr("The landuse is not available in the database."))

        if landuse_invalid:
            self.apply_button.setEnabled(False)
        else:
            self.apply_button.setEnabled(True)

        old_parcel_id = 0
        geo_id = 0
        documented_area_m2 = 0
        address_khashaa = 0
        address_streetname = ''
        address_neighbourhood = ''

        if column_names[column_name_old_parcel] != None:
            old_parcel_id = column_names[column_name_old_parcel]
        if column_names[column_name_geo_id] != None:
            geo_id = column_names[column_name_geo_id]
        if column_names[column_name_documented] != None:
            documented_area_m2 = column_names[column_name_documented]
        if column_names[column_name_khashaa] != None:
            address_khashaa = column_names[column_name_khashaa]
        if column_names[column_name_street] != None:
            address_streetname = column_names[column_name_street]
        if column_names[column_name_neighbourhood] != None:
            address_neighbourhood = column_names[column_name_neighbourhood]
        parcel_object.old_parcel_id = old_parcel_id
        parcel_object.geo_id = geo_id
        parcel_object.landuse = column_names[column_name_landuse]
        parcel_object.documented_area_m2 = documented_area_m2
        parcel_object.address_khashaa = address_khashaa
        parcel_object.address_streetname = address_streetname
        parcel_object.address_neighbourhood = address_neighbourhood

        return parcel_object

    def __copy_building_attributes(self, building_feature, building_object, layer):

        column_name_building_no = "building_n"
        column_name_geo_id = "geo_id"
        column_name_khashaa = "address_kh"
        column_name_street = "address_st"
        column_name_neighbourhood = "address_ne"

        column_names = {column_name_building_no: "", column_name_geo_id: "", column_name_khashaa: "", column_name_street: "", column_name_neighbourhood: ""}

        provider = layer.dataProvider()

        for key, item in column_names.iteritems():
            index = provider.fieldNameIndex(key)
            if index != -1:
                value = building_feature.attributes()[index]
                column_names[key] = value

        geo_id = 0
        building_no = 0
        address_khashaa = ''
        address_streetname = ''
        address_neighbourhood = ''
        if column_names[column_name_geo_id] != None:
            geo_id = column_names[column_name_geo_id]
        if column_names[column_name_building_no] != None:
            building_no = column_names[column_name_building_no]
        if column_names[column_name_khashaa] != None:
            address_khashaa = column_names[column_name_khashaa]
        if column_names[column_name_street] != None:
            address_streetname = column_names[column_name_street]
        if column_names[column_name_neighbourhood] != None:
            address_streetname = column_names[column_name_neighbourhood]
        building_object.geo_id = geo_id
        building_object.building_no = building_no
        building_object.address_khashaa = address_khashaa
        building_object.address_streetname = address_streetname
        building_object.address_neighbourhood = address_neighbourhood

        return building_object

    def __import_new_buildings(self, file_path):

        building_shape_layer = QgsVectorLayer(file_path, "tmp_building_shape", "ogr")

        if not building_shape_layer.isValid():
            PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The layer is invalid."))
            return False

        if building_shape_layer.crs().postgisSrid() != 4326:
            PluginUtils.show_error(self, self.tr("Error loading layer"), self.tr("The crs of the has to be 32648."))
            return False

        iterator = building_shape_layer.getFeatures()
        count = 0

        for building in iterator:
            count += 1

            try:
                new_building = CaTmpBuilding()
                new_building.building_id = QDateTime().currentDateTime().toString("MMddhhmmss") + str(count)
                new_building.initial_insert = None
                new_building.maintenance_case = self.ca_maintenance_case.id
                new_building.geometry = WKTElement(building.geometry().exportToWkt(), srid=4326)
                self.__copy_building_attributes(building, new_building, building_shape_layer)
                self.session.add(new_building)

            except SQLAlchemyError, e:
                PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                return

            #Add main parcel to the tree
            main_building_item = QTreeWidgetItem()
            main_building_item.setText(0, new_building.building_id)
            main_building_item.setIcon(0, QIcon(QPixmap(":/plugins/lm2/building.gif")))
            main_building_item.setData(0, Qt.UserRole, new_building.building_id)
            main_building_item.setData(0, Qt.UserRole + 1, Constants.CASE_BUILDING_IDENTIFIER)

            self.buildings_item.addChild(main_building_item)

        return True

    def reject(self):

        self.rollback()
        QDialog.reject(self)

    @pyqtSlot()
    def on_apply_button_clicked(self):

        try:
            self.ca_maintenance_case.creation_date = PluginUtils.convert_qt_date_to_python(self.start_date.date())
            self.create_savepoint()

            if self.connect_app_checkbox.isChecked():
                count = self.applications_twidget.rowCount()
                if count == 0:
                    PluginUtils.show_error(self, self.tr("Maintenance case Error"), self.tr("Select an application to create an maintenance case"))
                    return

                for i in range(self.applications_twidget.rowCount()):

                    item = self.applications_twidget.item(i, 0)

                    if item is None:
                        continue
                    app_no = item.text()
                    application_count = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).count()
                    if application_count != 0:
                        application = self.session.query(CtApplication).filter(CtApplication.app_no == app_no).one()
                        application.maintenance_case = self.ca_maintenance_case.id

            for parcel_id in self.maintenance_parcels:

                self.create_savepoint()

                parcel = self.session.query(CaParcel).filter(CaParcel.parcel_id == parcel_id).one()
                if parcel in self.ca_maintenance_case.parcels:
                    continue

                self.ca_maintenance_case.parcels.append(parcel)
                temp_parcel = CaTmpParcel()
                temp_parcel.parcel_id = parcel.parcel_id
                temp_parcel.old_parcel_id = parcel.old_parcel_id
                temp_parcel.geo_id = parcel.geo_id
                temp_parcel.address_khashaa = parcel.address_khashaa
                temp_parcel.address_streetname = parcel.address_streetname
                temp_parcel.address_neighbourhood = parcel.address_neighbourhood
                temp_parcel.valid_from = parcel.valid_from
                temp_parcel.valid_till = parcel.valid_till
                temp_parcel.documented_area_m2 = parcel.documented_area_m2
                temp_parcel.area_m2 = parcel.area_m2
                temp_parcel.geometry = parcel.geometry
                temp_parcel.maintenance_case = self.ca_maintenance_case.id
                temp_parcel.initial_insert = True

                self.session.add(temp_parcel)

            for building_id in self.maintenance_buildings:

                self.create_savepoint()

                building = self.session.query(CaBuilding).filter(CaBuilding.building_id == building_id).one()
                if building in self.ca_maintenance_case.buildings:
                    continue
                python_date = PluginUtils.convert_qt_date_to_python(QDateTime().currentDateTime())
                self.ca_maintenance_case.buildings.append(building)
                temp_building = CaTmpBuilding()

                temp_building.building_id = building.building_id
                temp_building.geo_id = building.geo_id
                temp_building.valid_from = building.valid_from
                temp_building.valid_till = building.valid_till
                temp_building.address_streetname = building.address_streetname
                temp_building.address_neighbourhood = building.address_neighbourhood
                temp_building.address_khashaa = building.address_khashaa
                temp_building.area_m2 = building.area_m2
                temp_building.geometry = building.geometry#.ST_SetSRID(32648)
                temp_building.maintenance_case = self.ca_maintenance_case.id

                self.session.add(temp_building)

            self.commit()

        except SQLAlchemyError, e:
            self.rollback()
            PluginUtils.show_error(self, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
            return

        self.__start_fade_out_timer()
        self.plugin.iface.mapCanvas().refresh()

    @pyqtSlot(QPoint)
    def on_result_twidget_customContextMenuRequested(self, point):

        if self.is_file_import:
            return

        point = self.result_twidget.viewport().mapToGlobal(point)
        self.menu.exec_(point)

    def __collect_used_codes(self, application_twidget):

        used_codes = list()
        for row in range(application_twidget.rowCount()):
            application_no = application_twidget.item(row, 0).text()
            used_codes.append(application_no)
        return used_codes

    @pyqtSlot()
    def on_add_button_clicked(self):

        used_codes = self.__collect_used_codes(self.applications_twidget)
        unused_code = ''
        for code in self.application_list:
            if code not in used_codes:
                unused_code = code
                break
        # if unused_code == '':
        #     PluginUtils.show_error(self, self.tr("Add Row"), self.tr('No application!!!.'))
        #     return
        row = self.applications_twidget.rowCount()
        self.applications_twidget.insertRow(row)
        self.__add_application_row(row, -1, unused_code)

    def __add_application_row(self, row, id, app_no):

        item = QTableWidgetItem(app_no)
        item.setData(Qt.UserRole, id)
        self.applications_twidget.setItem(row, 0, item)

    @pyqtSlot()
    def on_delete_button_clicked(self):

        self.applications_twidget.removeRow(self.applications_twidget.currentRow())

    def exclude_list(self):

        return self.exclude_list

    def add_to_exclude_list(self, item):

        self.exclude_list.append(item)

    def __fade_status_message(self):

        opacity = int(self.time_counter * 0.5)
        self.status_label.setStyleSheet("QLabel {color: rgba(255,0,0," + str(opacity) + ");}")
        self.status_label.setText(self.tr('Changes applied successfully.'))
        if self.time_counter == 0:
            self.timer.stop()
        self.time_counter -= 1

    def __start_fade_out_timer(self):

        self.timer = QTimer()
        self.timer.timeout.connect(self.__fade_status_message)
        self.time_counter = 500
        self.timer.start(10)

    @pyqtSlot()
    def on_help_button_clicked(self):

        os.system("hh.exe "+ str(os.path.dirname(os.path.realpath(__file__))[:-10]) +"help\output\help_lm2.chm::/html/create_case.htm")

    @pyqtSlot(int)
    def on_connect_app_checkbox_stateChanged(self, state):

        if state == Qt.Checked:
            self.applications_twidget.setEnabled(True)
            self.add_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.person_id_label.setEnabled(True)
            self.app_person_id.setEnabled(True)
        else:
            self.applications_twidget.setEnabled(False)
            self.add_button.setEnabled(False)
            self.delete_button.setEnabled(False)
            self.person_id_label.setEnabled(False)
            self.app_person_id.setEnabled(False)
            self.applications_twidget.setRowCount(0)

    @pyqtSlot(str)
    def on_app_person_id_textChanged(self, text):

        value = "%" + text + "%"
        self.applications_twidget.setRowCount(0)
        try:
            applications = self.session.query(ApplicationSearch).\
                filter(ApplicationSearch.status == 1).\
                filter(ApplicationSearch.person_id.ilike(value)).all()

            count = 0
            for application in applications:

                item = QTableWidgetItem(application.app_no)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, application.app_no)
                self.applications_twidget.insertRow(count)
                self.applications_twidget.setItem(count, 0, item)
                count +=1
        except SQLAlchemyError, e:
            PluginUtils.show_error(self, self.tr("Database Query Error"), self.tr("Could not execute: {0}").format(e.message))
            return