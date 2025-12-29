#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit, QPushButton
)
import prc


class ActivationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Activation")

        machine_id = prc.get_machine_id()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Send this Machine ID to activate the application:"))

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(machine_id)
        layout.addWidget(text)

        btn = QPushButton("Copy")
        btn.clicked.connect(lambda: text.selectAll())
        layout.addWidget(btn)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    dialog = ActivationDialog()
    dialog.show()
    sys.exit(app.exec_())
