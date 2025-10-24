# gui/windows/group_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QWidget, QMessageBox
)
from PySide6.QtCore import Qt


class GroupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create or Join Group")
        self.setModal(True)
        self.resize(400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #2D3748;
            }
            QLineEdit {
                border: 1px solid #CBD5E0;
                border-radius: 6px;
                padding: 6px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3182CE;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #2B6CB0;
            }
        """)

        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        self.create_tab = self._create_group_tab()
        self.join_tab = self._join_group_tab()

        self.tabs.addTab(self.create_tab, "Create Group")
        self.tabs.addTab(self.join_tab, "Join Group")

        layout.addWidget(self.tabs)

        self.result_data = None

    def _create_group_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        name_label = QLabel("Group Name:")
        self.group_name_input = QLineEdit()
        create_btn = QPushButton("Create")
        create_btn.clicked.connect(self.create_group)

        layout.addWidget(name_label)
        layout.addWidget(self.group_name_input)
        layout.addWidget(create_btn)
        layout.addStretch(1)
        return widget

    def _join_group_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        code_label = QLabel("Group Code:")
        self.group_code_input = QLineEdit()
        join_btn = QPushButton("Join")
        join_btn.clicked.connect(self.join_group)

        layout.addWidget(code_label)
        layout.addWidget(self.group_code_input)
        layout.addWidget(join_btn)
        layout.addStretch(1)
        return widget

    def create_group(self):
        name = self.group_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Warning", "Please enter a group name.")
            return

        self.result_data = {
            "mode": "create",
            "group_name": name,
        }
        self.accept()

    def join_group(self):
        code = self.group_code_input.text().strip()
        if not code:
            QMessageBox.warning(self, "Warning", "Please enter a group name or code.")
            return

        self.result_data = {
            "mode": "join",
            "group_name": code,
        }
        self.accept()

    def get_result(self):
        return self.result_data
