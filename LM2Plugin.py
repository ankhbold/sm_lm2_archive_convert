import os.path

from controller.ConnectionToMainDatabaseDialog import *
from controller.OfficialDocumentsDialog import OfficialDocumentsDialog
from controller.LandOfficeAdministrativeSettingsDialog import *
from controller.UserRoleManagementDialog import *
from controller.NavigatorWidget import *
from controller.ApplicationsDialog import *
from controller.ContractDialog import *
from controller.OwnRecordDialog import *
from controller.ImportDecisionDialog import *
from controller.LogOnDialog import *
from controller.CreateCaseDialog import CreateCaseDialog
from controller.FinalizeCaseDialog import *
from controller.PrintCadastreExtractMapTool import *
from controller.AboutDialog import *
from utils.DatabaseUtils import *
from utils.PluginUtils import PluginUtils
from utils.SessionHandler import SessionHandler
from utils.LM2Logger import LM2Logger
from model import SettingsConstants
from model.SetRightTypeApplicationType import *
from model.DialogInspector import DialogInspector
from view.resources_rc import *
from controller.ManageParcelRecordsDialog import *
from controller.PdfInsertDialog import *

class LM2Plugin:

    def __init__(self, iface):

        # Save reference to the QGIS interface
        self.iface = iface
        self.activeAction = None

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        override_locale = QSettings().value("locale/overrideFlag", False, type=bool)
        if not override_locale:
            locale = QLocale.system().name()
        else:
            locale = QSettings().value("locale/userLocale", "", type=str)

        self.translator = QTranslator()
        if self.translator.load("LM2Plugin_" + locale, self.plugin_dir):
            QApplication.installTranslator(self.translator)

        self.__add_repository()

    def __add_repository(self):

        repository = QSettings().value(SettingsConstants.REPOSITORY_URL, None)
        if repository is None:
            QSettings().setValue(SettingsConstants.REPOSITORY_URL, Constants.REPOSITORY_URL)
            QSettings().setValue(SettingsConstants.REPOSITORY_ENABLED, True)

    def __create_db_session(self, password):

        user = QSettings().value(SettingsConstants.USER)
        db = QSettings().value(SettingsConstants.DATABASE_NAME)
        host = QSettings().value(SettingsConstants.HOST)
        port = QSettings().value(SettingsConstants.PORT, "5432")

        SessionHandler().create_session(user, password, host, port, db)

    def __destroy_db_session(self):

        SessionHandler().destroy_session()

    def initGui(self):

        # Create action that will start plugin configuration
        self.set_db_connection = QAction(QIcon(":/plugins/lm2/database_con.png"), QApplication.translate("Plugin", "Set Connection To Main Database"), self.iface.mainWindow())
        self.help_action = QAction(QIcon(":/plugins/lm2/help_button.png"), QApplication.translate("Plugin", "Help"), self.iface.mainWindow())
        self.navigator_action = QAction(QIcon(":/plugins/lm2/search_nav.png"), QApplication.translate("Plugin", "Show/Hide Navigator"), self.iface.mainWindow())
        self.navigator_action.setCheckable(True)
        self.about_action = QAction(QIcon(":/plugins/lm2/about.png"), QApplication.translate("Plugin", "About"), self.iface.mainWindow())
        self.manage_parcel_records_action = QAction(QIcon(":/plugins/lm2/start_editing.png"), QApplication.translate("Plugin", "Manage Parcel Record"), self.iface.mainWindow())
        self.pdf_insert_action = QAction(QIcon(":/plugins/lm2/convert_data.png"), QApplication.translate("Plugin", "Pdf Insert"), self.iface.mainWindow())

        # connect the action to the run method
        self.set_db_connection.triggered.connect(self.__show_connection_to_main_database_dialog)
        self.help_action.triggered.connect(self.__show_help)
        # self.navigator_action.triggered.connect(self.__show_navigator_widget)
        self.about_action.triggered.connect(self.__show_about_dialog)

        self.manage_parcel_records_action.triggered.connect(self.__show_manage_parcel_records_dialog)
        self.pdf_insert_action.triggered.connect(self.__show_pdf_insert_dialog)

        # Add toolbar button and menu item
        self.lm_toolbar = self.iface.addToolBar(QApplication.translate("Plugin", "TopMap tool"))

        self.lm_toolbar.addSeparator()
        self.lm_toolbar.addAction(self.pdf_insert_action)
        # self.lm_toolbar.addAction(self.manage_parcel_records_action)
        self.lm_toolbar.addAction(self.navigator_action)
        self.lm_toolbar.addSeparator()

        self.lm_toolbar.addAction(self.set_db_connection)

        # Retrieve main menu bar
        menu_bar = self.iface.mainWindow().menuBar()
        actions = menu_bar.actions()

        # Create menus
        self.lm_menu = QMenu()
        self.lm_menu.setTitle(QApplication.translate("Plugin", "&TM tool"))
        menu_bar.addMenu(self.lm_menu)

        # Add actions and menus to LM2 menu

        self.lm_menu.addAction(self.set_db_connection)
        self.lm_menu.addAction(self.pdf_insert_action)
        # self.lm_menu.addAction(self.manage_parcel_records_action)
        self.lm_menu.addSeparator()
        self.lm_menu.addAction(self.navigator_action)
        self.lm_menu.addAction(self.help_action)
        self.lm_menu.addAction(self.about_action)

        self.navigatorWidget = None

        self.__set_menu_visibility()
        self.__setup_slots()

    def unload(self):

        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.navigator_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.set_db_connection)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.help_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.pdf_insert_action)
        self.iface.removePluginMenu(QApplication.translate("Plugin", "&LM2"), self.manage_parcel_records_action)

        del self.lm_toolbar

        if self.navigatorWidget:
            self.iface.removeDockWidget(self.navigatorWidget)
            del self.navigatorWidget

    def __setup_slots(self):

        QObject.connect(QgsMapLayerRegistry.instance(), SIGNAL("layerWasAdded(QgsMapLayer*)"), self.__update_database_connection)

    def __show_connection_to_main_database_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = ConnectionToMainDatabaseDialog(self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)
        dlg.exec_()

        SessionHandler().destroy_session()
        self.__update_database_connection()

    def __show_manage_parcel_records_dialog(self):

        dlg = ManageParcelRecordsDialog()
        dlg.exec_()

    def __show_pdf_insert_dialog(self):

        dlg = PdfInsertDialog()
        dlg.exec_()

    def __show_create_case_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        m_case = PluginUtils.create_new_m_case()
        self.create_case_dialog = CreateCaseDialog(self, m_case, False, self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        self.create_case_dialog.rejected.connect(self.on_current_dialog_rejected)

        self.create_case_dialog.setModal(False)
        self.create_case_dialog.show()

    def __show_land_office_admin_settings_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = LogOnDialog(Constants.LAND_ADMIN_SETTINGS_DLG)

        if dlg.exec_():
            dlg2 = LandOfficeAdministrativeSettingsDialog()
            DialogInspector().set_dialog_visible(True)
            dlg2.rejected.connect(self.on_current_dialog_rejected)

            dlg2.exec_()

        self.__update_database_connection()

    def __show_user_role_management_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = LogOnDialog(Constants.ROLE_MANAGEMENT_DLG)

        if dlg.exec_():
            dlg2 = UserRoleManagementDialog()
            DialogInspector().set_dialog_visible(True)
            dlg2.rejected.connect(self.on_current_dialog_rejected)

            dlg2.exec_()

        self.__update_database_connection()

    def __show_person_dialog(self):

        if DialogInspector().dialog_visible():
            return

        person = BsPerson()
        dialog = PersonDialog(person)
        DialogInspector().set_dialog_visible(True)
        dialog.rejected.connect(self.on_current_dialog_rejected)
        dialog.exec_()

    # def __show_navigator_widget(self):
    #
    #     if self.navigatorWidget.isVisible():
    #         self.navigatorWidget.hide()
    #     else:
    #         self.navigatorWidget.show()

    # def __navigatorVisibilityChanged(self):
    #
    #     if self.navigatorWidget.isVisible():
    #         self.navigator_action.setChecked(True)
    #     else:
    #         self.navigator_action.setChecked(False)

    def __show_applications_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        application = PluginUtils.create_new_application()

        self.dlg = ApplicationsDialog(application, self.navigatorWidget, False, self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __mark_apps_as_send_to_govenor(self):

        soum = DatabaseUtils.current_working_soum_schema()
        DatabaseUtils.set_working_schema()

        msg_box = QMessageBox()
        app_count = ""
        try:
            session = SessionHandler().session_instance()
            app_count = session.query(CtApplicationStatus.application, func.max(CtApplicationStatus.status_date))\
                .group_by(CtApplicationStatus.application)\
                .having(func.max(CtApplicationStatus.status) == Constants.APP_STATUS_WAITING).distinct().count()

        except SQLAlchemyError, e:
            PluginUtils.show_error(self.iface.mainWindow(), QApplication.translate("Plugin", "Error executing"), e.message)

        msg_box.setText(QApplication.translate("Plugin", "Do you want to update {0} applications in working soum {1} to "
                                                         "the status \"send to the governor\"?").format(app_count, soum))
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        result = msg_box.exec_()
        if result == QMessageBox.Ok:
            DatabaseUtils.update_application_status()

    def __show_contract_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        contract = PluginUtils.create_new_contract()

        self.dlg = ContractDialog(contract, self.navigatorWidget, False, self.iface.mainWindow())
        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __show_ownership_dialog(self):

        if DialogInspector().dialog_visible():
            return

        DatabaseUtils.set_working_schema()
        record = PluginUtils.create_new_record()

        self.dlg = OwnRecordDialog(record, self, False, self.iface.mainWindow())

        DialogInspector().set_dialog_visible(True)
        self.dlg.rejected.connect(self.on_current_dialog_rejected)
        self.dlg.setModal(False)
        self.dlg.show()

    def __show_documents_dialog(self):

        dialog = OfficialDocumentsDialog()
        dialog.exec_()

    def __show_import_decision_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = ImportDecisionDialog(False)
        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)

        dlg.exec_()

    def __show_about_dialog(self):

        if DialogInspector().dialog_visible():
            return

        dlg = AboutDialog()
        DialogInspector().set_dialog_visible(True)
        dlg.rejected.connect(self.on_current_dialog_rejected)
        dlg.exec_()


    def __show_help(self):

        #session = SessionHandler().session_instance()
        #test = session.query(SetRightTypeApplicationType).count()
        #LM2Logger().log_message("testing further with the help button")
        #LM2Logger().log_message("second test with the help button")
        PluginUtils.show_message(self.iface.mainWindow(), "help", "help ")

        #from model.ClPaymentFrequency import *
        #session = SessionHandler().session_instance()

        # try:
        #     pf = ClPaymentFrequency(code=30, description='XXX')
        #     session.add(pf)
        #     pf2 = session.query(ClPaymentFrequency).filter(ClPaymentFrequency.code == 88).one()
        # except SQLAlchemyError, e:
        #     QMessageBox.information(None, "Database Error", e.message)
        #
        # QMessageBox.information(None, "Before commit", 'before commit')
        # session.commit()

    @pyqtSlot()
    def __update_database_connection(self):

        if not SessionHandler().session_instance():

            database_name = QSettings().value(SettingsConstants.DATABASE_NAME)
            port = QSettings().value(SettingsConstants.PORT, "5432")
            user_name = QSettings().value(SettingsConstants.USER)
            server = QSettings().value(SettingsConstants.HOST)

            for key in QgsMapLayerRegistry.instance().mapLayers():
                layer = QgsMapLayerRegistry.instance().mapLayers()[key]
                if layer.type() == QgsMapLayer.VectorLayer and layer.dataProvider().name() == "postgres":
                    uri = QgsDataSourceURI(layer.source())
                    if uri.database() == database_name and user_name == uri.username() \
                            and server == uri.host() and port == uri.port():
                        self.__create_db_session(uri.password())
                        self.__set_menu_visibility()
                        break

    def __set_menu_visibility(self):

        user_name = QSettings().value(SettingsConstants.USER)

        if not user_name:
            self.__disable_menu()
            return

        if not SessionHandler().session_instance():
            self.__disable_menu()
            return

        user_right = DatabaseUtils.userright_by_name(user_name)

        if user_right:
            self.__enable_menu(user_right)

    # def __create_navigator(self):
    #
    #     # create widget
    #     if self.navigatorWidget:
    #         self.iface.removeDockWidget(self.navigatorWidget)
    #         del self.navigatorWidget
    #
    #     self.navigatorWidget = NavigatorWidget(self)
    #     self.iface.addDockWidget(Qt.RightDockWidgetArea, self.navigatorWidget)
    #     QObject.connect(self.navigatorWidget, SIGNAL("visibilityChanged(bool)"), self.__navigatorVisibilityChanged)
    #     self.navigatorWidget.show()

    def __enable_menu(self, user_rights):

        self.manage_parcel_records_action.setEnabled(True)
        self.pdf_insert_action.setEnabled(True)
        self.navigator_action.setEnabled(True)
        self.about_action.setEnabled(True)
        # self.__create_navigator()

    def __disable_menu(self):

        self.pdf_insert_action.setEnabled(False)
        self.manage_parcel_records_action.setEnabled(False)
        self.about_action.setEnabled(False)
        # self.navigator_action.setEnabled(False)

    def transformPoint(self, point, layer_postgis_srid):

        # If On-the-Fly transformation is enabled in the QGIS project settings
        # transform from map coordinates (destinationSrs()) to layer coordinates
        renderer = self.iface.mapCanvas().mapRenderer()
        if renderer.hasCrsTransformEnabled() and renderer.destinationCrs().postgisSrid() != layer_postgis_srid:
            transformation = QgsCoordinateTransform(renderer.destinationCrs(), QgsCoordinateReferenceSystem(layer_postgis_srid))
            point = transformation.transform(point)

        return point

    def on_current_dialog_rejected(self):

        DialogInspector().set_dialog_visible(False)