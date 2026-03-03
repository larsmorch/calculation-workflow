from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit


class PropertiesPanel(QWidget):
    """Panel for editing node properties"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # Form for properties
        self.form_layout = QFormLayout()
        layout.addLayout(self.form_layout)

        layout.addStretch()

    def show_node_properties(self, node):
        """Display properties for selected node"""
        # Clear existing
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add properties
        self.form_layout.addRow("Module:", QLabel(node.module_type))
        self.form_layout.addRow("Input 1:", QLineEdit())
        self.form_layout.addRow("Input 2:", QLineEdit())