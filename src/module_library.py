from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal
from module_registry import registry


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

        # Module list via QTreeWidget to support categories
        self.module_tree = QTreeWidget()
        self.module_tree.setHeaderHidden(True)
        self.populate_modules()
        self.module_tree.itemDoubleClicked.connect(self.on_module_double_clicked)
        layout.addWidget(self.module_tree)

        # Add button
        add_btn = QPushButton("Add to Canvas")
        add_btn.clicked.connect(self.on_add_clicked)
        layout.addWidget(add_btn)

    def populate_modules(self):
        self.module_tree.clear()
        categories = registry.get_modules_by_category()
        for cat, modules in categories.items():
            cat_item = QTreeWidgetItem([cat])
            # Default expand if there are modules
            cat_item.setExpanded(True)
            self.module_tree.addTopLevelItem(cat_item)
            
            for mod_class in modules:
                mod_item = QTreeWidgetItem([mod_class.name])
                # Store the type ID to instantiate it later
                mod_item.setData(0, 100, mod_class.get_module_type_id())
                cat_item.addChild(mod_item)

    def on_module_double_clicked(self, item, column):
        type_id = item.data(0, 100)
        # Double clicking a category has no type_id
        if type_id:
            self.module_selected.emit(type_id)

    def on_add_clicked(self):
        current_item = self.module_tree.currentItem()
        if current_item:
            type_id = current_item.data(0, 100)
            if type_id:
                self.module_selected.emit(type_id)