from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox
from functools import partial


class PropertiesPanel(QWidget):
    """Panel for editing node properties"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Allow panel scaling for large graphs
        self.layout_main = QVBoxLayout(self)
        
        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        self.layout_main.addWidget(title)

        # Form for properties wrapped in scroll area
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        self.form_layout = QFormLayout(container)
        scroll.setWidget(container)
        
        self.layout_main.addWidget(scroll)

    def show_node_properties(self, node):
        """Display properties for selected node"""
        # Clear existing
        while self.form_layout.count():
            item = self.form_layout.takeAt(0)
            if item.widget():
                if "FigureCanvas" in type(item.widget()).__name__:
                    item.widget().setParent(None)
                else:
                    item.widget().deleteLater()

        if not node:
            return

        module = node.module

        # Add LaTeX Formula if exists
        latex_formula = getattr(module, 'latex_formula', "")
        if latex_formula:
            try:
                from matplotlib.figure import Figure
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
                fig_latex = Figure(figsize=(3, 0.8), dpi=100)
                ax_latex = fig_latex.add_subplot(111)
                ax_latex.text(0.5, 0.5, latex_formula, size=14, ha='center', va='center')
                ax_latex.axis("off")
                fig_latex.tight_layout()
                canvas_latex = FigureCanvasQTAgg(fig_latex)
                
                # Make background transparent if possible, or color matched
                fig_latex.patch.set_facecolor('#f0f0f0') 
                self.form_layout.addRow(canvas_latex)
            except Exception as e:
                print(f"LaTeX Render Error: {e}")

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
                widget.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.NoButtons)
                widget.setRange(
                    param.min_value if param.min_value is not None else -1e9,
                    param.max_value if param.max_value is not None else 1e9
                )
                widget.setDecimals(param.decimals)
                # Set current value
                current = module.inputs.get(param.name)
                if current is not None:
                    widget.setValue(float(current))
                    
                # Bind changes to module state
                widget.valueChanged.connect(partial(self.on_value_changed, module, param.name))
                self.form_layout.addRow(label_text + ":", widget)
                
            elif param.type is int:
                widget = QSpinBox()
                widget.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
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

        # Render custom module figure plot if exists natively!
        if hasattr(module, 'figure') and module.figure is not None:
            try:
                from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
                if getattr(module.figure, 'canvas', None):
                    canvas = module.figure.canvas
                    canvas.setParent(None) # Reparent safely
                else:
                    canvas = FigureCanvasQTAgg(module.figure)
                canvas.setMinimumHeight(400)
                self.form_layout.addRow(canvas)
            except Exception as e:
                print(f"Figure render error: {e}")

    def on_value_changed(self, module, param_name, new_value):
        """Update the module's internal state when a UI field changes"""
        module.set_input(param_name, new_value)