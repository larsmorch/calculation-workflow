from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal


class ModuleLibrary(QWidget):
    """Panel showing available calculation modules"""

    module_selected = pyqtSignal(str)  # Emits module name

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Available Modules")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # Module list
        self.module_list = QListWidget()
        self.module_list.addItems([
            "Basic Math",
            "Structural Analysis",
            "Material Properties",
            "Load Calculator",
            "Section Properties"
        ])
        self.module_list.itemDoubleClicked.connect(self.on_module_double_clicked)
        layout.addWidget(self.module_list)

        # Add button
        add_btn = QPushButton("Add to Canvas")
        add_btn.clicked.connect(self.on_add_clicked)
        layout.addWidget(add_btn)

    def on_module_double_clicked(self, item):
        self.module_selected.emit(item.text())

    def on_add_clicked(self):
        current_item = self.module_list.currentItem()
        if current_item:
            self.module_selected.emit(current_item.text())