__author__ = 'anna'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError

from ...model.SetOfficialDocument import SetOfficialDocument
from ...utils.FileUtils import FileUtils
from ...utils.PluginUtils import PluginUtils
from ...utils.SessionHandler import SessionHandler

NAME_COLUMN = 0
DESCRIPTION_COLUMN = 1
VIEW_COLUMN = 2


class OfficialDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(OfficialDocumentDelegate, self).__init__(parent)
        self.widget = widget
        self.parent = parent
        self.session = SessionHandler().session_instance()
        self.button = QPushButton("", parent)
        self.button.hide()

        self.viewIcon = QIcon(":/plugins/lm2/file.png")

    def paint(self, painter, option, index):

        if index.column() == VIEW_COLUMN:
            self.button.setIcon(self.viewIcon)
        else:
            super(OfficialDocumentDelegate, self).paint(painter, option, index)
            return

        self.button.setGeometry(option.rect)
        button_picture = QPixmap.grabWidget(self.button)
        painter.drawPixmap(option.rect.x(), option.rect.y(), button_picture)

    def editorEvent(self, event, model, option, index):

        if index is not None:

            if index.isValid() and event.type() == QEvent.MouseButtonRelease:

                if event.button() == Qt.RightButton:
                    return False

                if index.column() == VIEW_COLUMN:

                    try:
                        current_id = self.widget.item(index.row(), NAME_COLUMN).data(Qt.UserRole)
                        if current_id is not None:

                            count = self.session.query(SetOfficialDocument).filter(SetOfficialDocument.id == current_id).count()

                            if count == 0:
                                PluginUtils.show_message(self.parent, self.tr("Could not open file"),
                                                     self.tr("No file found for this record."))
                                return False

                            document = self.session.query(SetOfficialDocument).get(current_id)

                            python_array = document.content
                            if python_array is None:
                                PluginUtils.show_message(self.parent, self.tr("Error"), self.tr("No digital documents available."))
                                return False

                            qt_array = QByteArray(python_array)
                            current_bytes = QByteArray(qt_array)
                            item_file_path = FileUtils.temp_file_path() + "/" \
                                             + unicode(self.widget.item(index.row(), NAME_COLUMN).text())

                            new_file = QFile(item_file_path)
                            new_file.open(QIODevice.WriteOnly)
                            new_file.write(current_bytes.data())
                            new_file.close()
                            QDesktopServices.openUrl(QUrl.fromLocalFile(item_file_path))

                    except SQLAlchemyError, e:
                            PluginUtils.show_error(self.parent, self.tr("File Error"), self.tr("Could not execute: {0}").format(e.message))
                            return True

                elif index.column() == DESCRIPTION_COLUMN or index.column() == NAME_COLUMN:
                    return True

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
