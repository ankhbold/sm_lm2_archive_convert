__author__ = 'anna'

from ..view.Ui_OfficialDocumentsDialog import *
from .qt_classes.OfficialDocumentViewDelegate import *
from ..utils.PluginUtils import *
from ..model.BsPerson import *
from ..model.CtFee import *
from ..model.DatabaseHelper import *
from sqlalchemy.sql import func
from sqlalchemy import text

NAME_COLUMN = 0
DESCRIPTION_COLUMN = 1
VIEW_COLUMN = 2


class OfficialDocumentsDialog(QDialog, Ui_OfficialDocumentsDialog, DatabaseHelper):

    def __init__(self, parent=None):

        super(OfficialDocumentsDialog,  self).__init__(parent)
        DatabaseHelper.__init__(self)
        self.setupUi(self)

        self.__setup_twidget()

        self.close_button.clicked.connect(self.reject)

    def __setup_twidget(self):

        self.doc_twidget.setAlternatingRowColors(True)
        self.doc_twidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.doc_twidget.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.doc_twidget.horizontalHeader().resizeSection(0, 200)
        self.doc_twidget.horizontalHeader().resizeSection(1, 450)
        self.doc_twidget.horizontalHeader().resizeSection(2, 50)

        delegate = OfficialDocumentDelegate(self.doc_twidget, self)
        self.doc_twidget.setItemDelegate(delegate)

        self.__load_data()

    def __load_data(self):

        session = SessionHandler().session_instance()

        documents = session.query(SetOfficialDocument.id, SetOfficialDocument.name, SetOfficialDocument.description).all()

        for document in documents:
            row = self.doc_twidget.rowCount()
            self.doc_twidget.insertRow(row)

            item_name = QTableWidgetItem()
            item_name.setText(document.name)
            item_name.setData(Qt.UserRole, document.id)

            item_description = QTableWidgetItem()
            item_description.setText(document.description)

            item_view = QTableWidgetItem()

            self.doc_twidget.setItem(row, NAME_COLUMN, item_name)
            self.doc_twidget.setItem(row, DESCRIPTION_COLUMN, item_description)
            self.doc_twidget.setItem(row, VIEW_COLUMN, item_view)
