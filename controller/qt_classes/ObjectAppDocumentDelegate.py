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

APP_DOC_PROVIDED_COLUMN = 0
APP_DOC_TYPE_COLUMN = 1
APP_DOC_NAME_COLUMN = 2
APP_DOC_VIEW_COLUMN = 3


class ObjectAppDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(ObjectAppDocumentDelegate, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

        self.viewIcon = QIcon(":/plugins/lm2/file.png")

    def paint(self, painter, option, index):

        if index.column() == APP_DOC_VIEW_COLUMN:
            self.button.setIcon(self.viewIcon)
        else:
            super(ObjectAppDocumentDelegate, self).paint(painter, option, index)
            return

        self.button.setGeometry(option.rect)
        button_picture = QPixmap.grabWidget(self.button)
        painter.drawPixmap(option.rect.x(), option.rect.y(), button_picture)

    def editorEvent(self, event, model, option, index):

        if not index is None:

            if index.isValid() and event.type() == QEvent.MouseButtonRelease:

                if event.button() == Qt.RightButton:
                    return False

                if index.column() == APP_DOC_VIEW_COLUMN:

                    application = self.parent.current_create_application()
                    person = self.parent.current_document_applicant()

                    role = self.widget.item(index.row(), APP_DOC_TYPE_COLUMN).data(Qt.UserRole)
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
                            PluginUtils.show_message(self.parent, self.tr("Error"), self.tr("No digital documents available."))
                            return False

                        qt_array = QByteArray(python_array)
                        current_bytes = QByteArray(qt_array)
                        item_file_path = FileUtils.temp_file_path() + "/" \
                                         + unicode(self.widget.item(index.row(), APP_DOC_NAME_COLUMN).text())

                        new_file = QFile(item_file_path)
                        new_file.open(QIODevice.WriteOnly)
                        new_file.write(current_bytes.data())
                        new_file.close()
                        QDesktopServices.openUrl(QUrl.fromLocalFile(item_file_path))

                    except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == APP_DOC_TYPE_COLUMN or index.column() == APP_DOC_NAME_COLUMN or index.column() == APP_DOC_PROVIDED_COLUMN:
                    return False

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
