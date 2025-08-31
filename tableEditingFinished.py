from PyQt5 import QtWidgets, QtCore


class MyTable(QtWidgets.QTableWidget):
    editingFinished = QtCore.pyqtSignal(int, int, str)  # row, col, new_text

    def closeEditor(self, editor, hint):
        super().closeEditor(editor, hint)
        index = self.currentIndex()
        if index.isValid():
            item = self.item(index.row(), index.column())
            if item:
                self.editingFinished.emit(index.row(), index.column(), item.text())
