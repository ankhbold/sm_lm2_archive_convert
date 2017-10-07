__author__ = 'anna'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError
from inspect import currentframe

from ...model.LM2Exception import LM2Exception
from ...model.CtContractDocument import CtContractDocument
from ...model.CtDocument import CtDocument
from ...utils.FileUtils import FileUtils
from ...utils.PluginUtils import PluginUtils
from ...utils.DatabaseUtils import DatabaseUtils
from ...utils.SessionHandler import SessionHandler


PROVIDED_COLUMN = 0
FILE_TYPE_COLUMN = 1
FILE_NAME_COLUMN = 2
OPEN_FILE_COLUMN = 3
DELETE_COLUMN = 4
VIEW_COLUMN = 5


class ContractDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(ContractDocumentDelegate, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

        self.remove = QIcon(":/plugins/lm2/remove.png")
        self.openIcon = QIcon(":/plugins/lm2/open.png")
        self.viewIcon = QIcon(":/plugins/lm2/file.png")

    def paint(self, painter, option, index):

        if index.column() == OPEN_FILE_COLUMN:
            self.button.setIcon(self.openIcon)
        elif index.column() == DELETE_COLUMN:
            self.button.setIcon(self.remove)
        elif index.column() == VIEW_COLUMN:
            self.button.setIcon(self.viewIcon)
        else:
            super(ContractDocumentDelegate, self).paint(painter, option, index)
            return

        self.button.setGeometry(option.rect)
        button_picture = QPixmap.grabWidget(self.button)
        painter.drawPixmap(option.rect.x(), option.rect.y(), button_picture)

    def editorEvent(self, event, model, option, index):

        if not index is None:

            if index.isValid() and event.type() == QEvent.MouseButtonRelease:

                if event.button() == Qt.RightButton:
                    return False

                if index.column() == OPEN_FILE_COLUMN:

                    file_dialog = QFileDialog()
                    file_dialog.setModal(True)
                    file_dialog.setFileMode(QFileDialog.ExistingFile)

                    if file_dialog.exec_():

                        selected_file = file_dialog.selectedFiles()[0]
                        file_info = QFileInfo(selected_file)

                        if QFileInfo(file_info).size()/(1024*1024) > 5:
                            PluginUtils.show_error(self, self.tr("File size exceeds limit!"), self.tr("The maximum size of documents to be attached is 5 MB."))
                            return False

                        file_content = DatabaseUtils.file_data(selected_file)

                        contract = self.parent.current_parent_object()
                        role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                        try:
                            count = self.session.query(CtContractDocument)\
                                .filter(CtContractDocument.contract == contract.contract_no)\
                                .filter(CtContractDocument.role == role).count()

                            if count == 0:
                                contract_doc = CtContractDocument()
                                contract_doc.document_ref = CtDocument()
                                contract_doc.document_ref.name = self.widget.item(index.row(), FILE_NAME_COLUMN).text()
                                contract_doc.document_ref.content = None

                                contract_doc.contract_ref = contract
                                contract_doc.role = role

                                item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                item.setCheckState(Qt.Checked)

                            con_doc = self.session.query(CtContractDocument)\
                                .filter(CtContractDocument.contract_ref == contract)\
                                .filter(CtContractDocument.role == role).one()

                            con_doc.document_ref.content = bytes(file_content)
                            contract_no = self.parent.current_parent_object_no()
                            contract_no = contract_no.replace("/", "-")

                            con_doc.document_ref.name =  contract_no + "-" + str(role) + "." + file_info.suffix()
                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText(con_doc.document_ref.name)

                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("Query Error"), self.tr("Error in line {0}: {1}").format(currentframe().f_lineno, e.message))
                            return True

                elif index.column() == VIEW_COLUMN:

                    contract = self.parent.current_parent_object()
                    role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                    try:
                        count = self.session.query(CtContractDocument)\
                            .filter(CtContractDocument.contract == contract.contract_no)\
                            .filter(CtContractDocument.role == role).count()

                        if count == 0:
                            PluginUtils.show_message(self.parent, self.tr("Could not open file"),
                                                 self.tr("No file found for this record."))
                            return False

                        con_doc = self.session.query(CtContractDocument)\
                            .filter(CtContractDocument.contract == contract.contract_no)\
                            .filter(CtContractDocument.role == role).one()

                        python_array = con_doc.document_ref.content
                        if python_array is None:
                            PluginUtils.show_message(self.parent, self.tr("Error"), self.tr("No digital documents available."))
                            return False

                        qt_array = QByteArray(python_array)
                        current_bytes = QByteArray(qt_array)
                        item_file_path = FileUtils.temp_file_path() + "/" \
                                         + unicode(self.widget.item(index.row(), FILE_NAME_COLUMN).text())

                        new_file = QFile(item_file_path)
                        new_file.open(QIODevice.WriteOnly)
                        new_file.write(current_bytes.data())
                        new_file.close()
                        QDesktopServices.openUrl(QUrl.fromLocalFile(item_file_path))

                    except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == DELETE_COLUMN:

                    message_box = QMessageBox()
                    message_box.setText(self.tr("Do you want to delete the selected document?"))

                    delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
                    message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
                    message_box.exec_()

                    if message_box.clickedButton() == delete_button:
                        try:
                            contract = self.parent.current_parent_object()
                            role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)

                            self.session.query(CtContractDocument)\
                            .filter(CtContractDocument.contract == contract.contract_no)\
                                .filter(CtContractDocument.role == role).delete()

                            check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                            check_item.setCheckState(False)
                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")
                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == PROVIDED_COLUMN:
                    if index.data(Qt.CheckStateRole) == Qt.Unchecked:

                        contract_doc = CtContractDocument()
                        contract_doc.document_ref = CtDocument()
                        contract_doc.document_ref.name = self.widget.item(index.row(), FILE_NAME_COLUMN).text()
                        contract_doc.document_ref.content = None

                        contract_doc.contract_ref = self.parent.current_parent_object()
                        contract_doc.role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)

                        item = self.widget.item(index.row(), PROVIDED_COLUMN)
                        item.setCheckState(Qt.Checked)

                    else:

                        contract = self.parent.current_parent_object()
                        role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                        try:
                            count = self.session.query(CtContractDocument.document)\
                                .filter(CtContractDocument.contract == contract.contract_no)\
                                .filter(CtContractDocument.role == role).count()

                            if count == 0:
                                PluginUtils.show_error(self.parent, self.tr("Error removing file"), self.tr("Could not find the file to remove."))
                                item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                item.setCheckState(Qt.Unchecked)
                                self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")

                            elif count == 1:

                                con_doc = self.session.query(CtContractDocument)\
                                .filter(CtContractDocument.contract == contract.contract_no)\
                                    .filter(CtContractDocument.role == role).one()

                                if con_doc.document_ref.content is None:
                                    item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                    item.setCheckState(Qt.Unchecked)
                                    self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")
                                else:

                                    message_box = QMessageBox()
                                    message_box.setText(self.tr("Do you want to delete the selected document?"))

                                    delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
                                    message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
                                    message_box.exec_()

                                    if message_box.clickedButton() == delete_button:
                                        item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                        item.setCheckState(Qt.Unchecked)

                                        self.session.query(CtContractDocument)\
                                        .filter(CtContractDocument.contract == contract.contract_no)\
                                            .filter(CtContractDocument.role == role).delete()

                                        check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                        check_item.setCheckState(False)
                                        self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")

                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == FILE_TYPE_COLUMN or index.column() == FILE_NAME_COLUMN:
                    return False

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
