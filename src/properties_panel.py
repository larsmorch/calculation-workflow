from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox
from functools import partial


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

        if not node:
            return

        module = node.module

        # Add generic properties
        self.form_layout.addRow("Module:", QLabel(module.name))
        
        # Add dynamic inputs based on parameter specifications
        for param in module.get_input_parameters():
            label_text = param.display_name
            if param.units:
                label_text += f" ({param.units})"
            
            # Use appropriate widget based on parameter type
            if param.type is float:
                widget = QDoubleSpinBox()
                widget.setRange(
                    param.min_value if param.min_value is not None else -1e9,
                    param.max_value if param.max_value is not None else 1e9
                )
                widget.setDecimals(4)
                # Set current value
                current = module.inputs.get(param.name)
                if current is not None:
                    widget.setValue(float(current))
                    
                # Bind changes to module state
                widget.valueChanged.connect(partial(self.on_value_changed, module, param.name))
                self.form_layout.addRow(label_text + ":", widget)
                
            elif param.type is int:
                widget = QSpinBox()
                widget.setRange(
                    int(param.min_value) if param.min_value is not None else -1000000000,
                    int(param.max_value) if param.max_value is not None else 1000000000
                )
                # Set current value
                current = module.inputs.get(param.name)
                if current is not None:
                    widget.setValue(int(current))
                    
                # Bind changes to module state
                widget.valueChanged.connect(partial(self.on_value_changed, module, param.name))
                self.form_layout.addRow(label_text + ":", widget)
                
            else:
                # Fallback string input
                widget = QLineEdit()
                current = module.inputs.get(param.name)
                if current is not None:
                    widget.setText(str(current))
                    
                widget.textChanged.connect(partial(self.on_value_changed, module, param.name))
                self.form_layout.addRow(label_text + ":", widget)

    def on_value_changed(self, module, param_name, new_value):
        """Update the module's internal state when a UI field changes"""
        module.set_input(param_name, new_value)