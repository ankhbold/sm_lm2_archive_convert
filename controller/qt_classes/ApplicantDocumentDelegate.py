__author__ = 'anna'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError

from ...model.LM2Exception import LM2Exception
from ...model.CtApplicationDocument import CtApplicationDocument
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


class ApplicationDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(ApplicationDocumentDelegate, self).__init__(parent)
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
            super(ApplicationDocumentDelegate, self).paint(painter, option, index)
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

                        application = self.parent.current_application()
                        person = self.parent.current_document_applicant()
                        role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                        try:
                            count = self.session.query(CtApplicationDocument)\
                                .filter(CtApplicationDocument.application_ref == application)\
                                .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).count()

                            if count == 0:
                                application_doc = CtApplicationDocument()
                                application_doc.document_ref = CtDocument()
                                application_doc.document_ref.name = self.widget.item(index.row(), FILE_NAME_COLUMN).text()
                                application_doc.document_ref.content = None

                                application_doc.application_ref = application
                                application_doc.role = role
                                application_doc.person = person

                                item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                item.setCheckState(Qt.Checked)

                            app_doc = self.session.query(CtApplicationDocument)\
                                .filter(CtApplicationDocument.application_ref == application)\
                                .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).one()

                            app_doc.document_ref.content = bytes(file_content)
                            app_doc.document_ref.name = str(self.parent.current_application_no()) + "-" + str(role) + "." + file_info.suffix()
                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText(app_doc.document_ref.name)

                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == VIEW_COLUMN:

                    application = self.parent.current_application()
                    person = self.parent.current_document_applicant()
                    role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                    try:
                        count = self.session.query(CtApplicationDocument)\
                            .filter(CtApplicationDocument.application_ref == application)\
                            .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).count()

                        if count == 0:
                            PluginUtils.show_message(self.parent, self.tr("Could not open file"),
                                                 self.tr("No file found for this record."))
                            return False

                        app_doc = self.session.query(CtApplicationDocument)\
                            .filter(CtApplicationDocument.application_ref == application)\
                            .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).one()

                        python_array = app_doc.document_ref.content
                        if python_array is None:
                            PluginUtils.show_message(self, self.tr("Error"), self.tr("No digital documents available."))
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
                            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == DELETE_COLUMN:

                    message_box = QMessageBox()
                    message_box.setText(self.tr("Do you want to delete the selected document?"))

                    delete_button = message_box.addButton(self.tr("Delete"), QMessageBox.ActionRole)
                    message_box.addButton(self.tr("Cancel"), QMessageBox.ActionRole)
                    message_box.exec_()

                    if message_box.clickedButton() == delete_button:
                        try:
                            application = self.parent.current_application()
                            person = self.parent.current_document_applicant()
                            role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)

                            self.session.query(CtApplicationDocument)\
                            .filter(CtApplicationDocument.application_ref == application)\
                            .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).delete()

                            check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                            check_item.setCheckState(False)
                            self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")
                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == PROVIDED_COLUMN:
                    if index.data(Qt.CheckStateRole) == Qt.Unchecked:

                        application_doc = CtApplicationDocument()
                        application_doc.document_ref = CtDocument()
                        application_doc.document_ref.name = self.widget.item(index.row(), FILE_NAME_COLUMN).text()
                        application_doc.document_ref.content = None

                        application_doc.application_ref = self.parent.current_application()
                        application_doc.role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                        application_doc.person = self.parent.current_document_applicant()

                        item = self.widget.item(index.row(), PROVIDED_COLUMN)
                        item.setCheckState(Qt.Checked)

                    else:

                        application = self.parent.current_application()
                        person = self.parent.current_document_applicant()
                        role = self.widget.item(index.row(), FILE_TYPE_COLUMN).data(Qt.UserRole)
                        try:
                            count = self.session.query(CtApplicationDocument.document)\
                                .filter(CtApplicationDocument.application_ref == application)\
                                .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).count()

                            if count == 0:
                                PluginUtils.show_error(self.parent, self.tr("Error removing file"), self.tr("Could not find the file to remove."))
                                item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                item.setCheckState(Qt.Unchecked)
                                self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")

                            elif count == 1:

                                app_doc = self.session.query(CtApplicationDocument)\
                                .filter(CtApplicationDocument.application_ref == application)\
                                .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).one()

                                if app_doc.document_ref.content is None:
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

                                        self.session.query(CtApplicationDocument)\
                                        .filter(CtApplicationDocument.application_ref == application)\
                                        .filter(CtApplicationDocument.person == person).filter(CtApplicationDocument.role == role).delete()

                                        check_item = self.widget.item(index.row(), PROVIDED_COLUMN)
                                        check_item.setCheckState(False)
                                        self.widget.item(index.row(), FILE_NAME_COLUMN).setText("")

                        except SQLAlchemyError, e:
                            PluginUtils.show_error(self, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == FILE_TYPE_COLUMN or index.column() == FILE_NAME_COLUMN:
                    return False

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
