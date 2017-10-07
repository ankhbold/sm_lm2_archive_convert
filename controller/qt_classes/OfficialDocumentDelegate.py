__author__ = 'anna'
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from sqlalchemy.exc import SQLAlchemyError

from ...model.SetOfficialDocument import SetOfficialDocument
from ...utils.FileUtils import FileUtils
from ...utils.PluginUtils import PluginUtils
from ...utils.SessionHandler import SessionHandler

VISIBLE_COLUMN = 0
NAME_COLUMN = 1
DESCRIPTION_COLUMN = 2
OPEN_FILE_COLUMN = 3
VIEW_COLUMN = 4


class OfficialDocumentDelegate(QStyledItemDelegate):

    def __init__(self, widget, parent):

        super(OfficialDocumentDelegate, self).__init__(parent)
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
        elif index.column() == VIEW_COLUMN:
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

                if index.column() == OPEN_FILE_COLUMN:

                    file_dialog = QFileDialog()
                    file_dialog.setModal(True)
                    file_dialog.setFileMode(QFileDialog.ExistingFile)
                    if file_dialog.exec_():

                        selected_file = file_dialog.selectedFiles()[0]
                        file_info = QFileInfo(selected_file)
                        if QFileInfo(file_info).size()/(1024*1024) > 5:
                            PluginUtils.show_error(self.parent, self.tr("File size exceeds limit!"), self.tr("The maximum size of documents to be attached is 5 MB."))
                            return False

                        self.widget.item(index.row(), NAME_COLUMN).setText(file_info.fileName())
                        self.widget.item(index.row(), OPEN_FILE_COLUMN).setData(Qt.UserRole, file_info.filePath())

                elif index.column() == VIEW_COLUMN:

                    try:
                        current_id = self.widget.item(index.row(), NAME_COLUMN).data(Qt.UserRole)
                        if current_id == -1:
                            file_path = self.widget.item(index.row(), OPEN_FILE_COLUMN).data(Qt.UserRole)
                            if file_path is not None:
                                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))

                        else:

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

                elif index.column() == VISIBLE_COLUMN:
                    if index.data(Qt.CheckStateRole) == Qt.Unchecked:
                        item = self.widget.item(index.row(), VISIBLE_COLUMN)
                        item.setCheckState(Qt.Checked)
                    else:
                        item = self.widget.item(index.row(), VISIBLE_COLUMN)
                        item.setCheckState(Qt.Unchecked)

                elif index.column() == DESCRIPTION_COLUMN or index.column() == NAME_COLUMN:
                    return True

                else:
                    index.model().setData(index, 0, Qt.EditRole)
        return False
