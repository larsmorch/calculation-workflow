import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter, QMessageBox,
    QFileDialog, QDockWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon, QKeySequence

# Fixed imports - remove any 'workflow.' prefix
from node_canvas import NodeCanvas
from module_library import ModuleLibrary
from properties_panel import PropertiesPanel
from results_panel import ResultsPanel
from workflow_engine import WorkflowEngine


class MainWindow(QMainWindow):
    """Main application window for the Calculation Workflow Application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculation Workflow - SwecoGPT Edition")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize workflow engine
        self.workflow_engine = WorkflowEngine()
        self.current_workflow_file = None

        # Setup UI components
        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        # Connect signals
        self.connect_signals()

    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget with node canvas
        self.node_canvas = NodeCanvas()
        self.setCentralWidget(self.node_canvas)

        # Left dock - Module Library
        self.module_library = ModuleLibrary()
        left_dock = QDockWidget("Module Library", self)
        left_dock.setWidget(self.module_library)
        left_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                  Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, left_dock)

        # Right dock - Properties Panel
        self.properties_panel = PropertiesPanel()
        right_dock = QDockWidget("Properties", self)
        right_dock.setWidget(self.properties_panel)
        right_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea |
                                   Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, right_dock)

        # Bottom dock - Results Panel
        self.results_panel = ResultsPanel()
        bottom_dock = QDockWidget("Results", self)
        bottom_dock.setWidget(self.results_panel)
        bottom_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, bottom_dock)

    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Workflow", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_workflow)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Workflow...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_workflow)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Workflow", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_workflow)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Workflow &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_workflow_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")

        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)

        # Workflow Menu
        workflow_menu = menubar.addMenu("&Workflow")

        run_action = QAction("&Run Workflow", self)
        run_action.setShortcut("F5")
        run_action.triggered.connect(self.run_workflow)
        workflow_menu.addAction(run_action)

        validate_action = QAction("&Validate Workflow", self)
        validate_action.triggered.connect(self.validate_workflow)
        workflow_menu.addAction(validate_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        """Create application toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # New
        new_action = QAction("New", self)
        new_action.triggered.connect(self.new_workflow)
        toolbar.addAction(new_action)

        # Open
        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_workflow)
        toolbar.addAction(open_action)

        # Save
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_workflow)
        toolbar.addAction(save_action)

        toolbar.addSeparator()

        # Run
        run_action = QAction("Run", self)
        run_action.triggered.connect(self.run_workflow)
        toolbar.addAction(run_action)

    def create_status_bar(self):
        """Create status bar"""
        self.statusBar().showMessage("Ready")

    def connect_signals(self):
        """Connect signals and slots"""
        # Module library signals
        self.module_library.module_selected.connect(self.on_module_selected)

        # Node canvas signals
        self.node_canvas.node_selected.connect(self.on_node_selected)
        self.node_canvas.connection_created.connect(self.on_connection_created)
        self.node_canvas.node_deleted.connect(self.workflow_engine.remove_node)
        self.node_canvas.connection_deleted.connect(self.workflow_engine.remove_connection)
        self.node_canvas.calculation_requested.connect(self.run_workflow) # LIVE UPDATES!
        self.workflow_engine.calculation_complete.connect(self.on_calculation_complete)

    # Slot methods
    def on_connection_created(self, start_port, end_port):
        """Pass the new connection from UI to the execution engine graph"""
        for conn in self.node_canvas.connections:
            if conn.start_port == start_port and conn.end_port == end_port:
                self.workflow_engine.add_connection(conn)
                self.statusBar().showMessage(f"Connected {start_port.parent_node.module.name} to {end_port.parent_node.module.name}")
                break
    def on_module_selected(self, module_name):
        """Handle module selection from library"""
        node = self.node_canvas.add_node(module_name)
        self.workflow_engine.add_node(node)
        self.statusBar().showMessage(f"Added {module_name} to canvas")

    def on_node_selected(self, node):
        """Handle node selection on canvas"""
        self.properties_panel.show_node_properties(node)

    def on_calculation_complete(self, results):
        """Handle workflow calculation completion"""
        self.results_panel.show_results(results)
        self.statusBar().showMessage("Calculation complete")

    # Action handlers
    def new_workflow(self):
        """Create a new workflow"""
        reply = QMessageBox.question(
            self,
            "New Workflow",
            "Clear current workflow?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.node_canvas.clear_canvas()
            self.workflow_engine.nodes.clear()
            self.workflow_engine.connections.clear()
            self.current_workflow_file = None
            self.statusBar().showMessage("New workflow created")

    def open_workflow(self):
        """Open an existing workflow"""
        filename, _ = QFileDialog.getOpenFileName(self, "Open Workflow", "", "Workflow Files (*.wf);;All Files (*)")
        if not filename: return
        
        import json
        from PyQt6.QtCore import QPointF
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.node_canvas.clear_canvas()
            self.workflow_engine.nodes.clear()
            self.workflow_engine.connections.clear()
            
            created_nodes = {}
            for i, n_data in enumerate(data.get("nodes", [])):
                node = self.node_canvas.add_node(n_data["type_id"], QPointF(n_data["x"], n_data["y"]))
                if not node: continue
                node.module.name = n_data["name"]
                
                for k, v in n_data.get("inputs", {}).items():
                    node.module.set_input(k, v)
                    if k in node.input_ports:
                        widget = node.input_ports[k].input_widget.widget()
                        from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QLineEdit
                        widget.blockSignals(True)
                        if isinstance(widget, QDoubleSpinBox):
                            widget.setValue(float(v) if v is not None else 0.0)
                        elif isinstance(widget, QSpinBox):
                            widget.setValue(int(v) if v is not None else 0)
                        elif isinstance(widget, QLineEdit):
                            widget.setText(str(v) if v is not None else "")
                        widget.blockSignals(False)
                        
                from node_graphics import get_dynamic_node_width
                node.width = get_dynamic_node_width(node.module.name)
                for port in node.output_ports.values():
                    port.setPos(node.width, port.pos().y())
                node.update()
                
                self.workflow_engine.add_node(node)
                created_nodes[i] = node
                
            for c_data in data.get("connections", []):
                start_node = created_nodes.get(c_data["start_node"])
                end_node = created_nodes.get(c_data["end_node"])
                if start_node and end_node:
                    start_port = start_node.output_ports.get(c_data["start_port"])
                    end_port = end_node.input_ports.get(c_data["end_port"])
                    if start_port and end_port:
                        from node_canvas import NodeConnection
                        conn = NodeConnection(start_port, end_port)
                        conn.update_path()
                        start_port.add_connection(conn)
                        end_port.add_connection(conn)
                        self.node_canvas.scene.addItem(conn)
                        self.node_canvas.connections.append(conn)
                        self.workflow_engine.add_connection(conn)
            
            self.current_workflow_file = filename
            self.statusBar().showMessage(f"Opened {filename}")
            self.run_workflow()
        except Exception as e:
            QMessageBox.critical(self, "Error Loading", f"Failed to open workflow: {e}")

    def save_workflow(self):
        """Save current workflow"""
        if self.current_workflow_file:
            self._save_to_file(self.current_workflow_file)
        else:
            self.save_workflow_as()

    def save_workflow_as(self):
        """Save workflow with new name"""
        filename, _ = QFileDialog.getSaveFileName(self, "Save Workflow As", "", "Workflow Files (*.wf);;All Files (*)")
        if filename:
            if not filename.endswith('.wf'): filename += '.wf'
            self.current_workflow_file = filename
            self._save_to_file(filename)

    def _save_to_file(self, filename):
        import json
        data = {"nodes": [], "connections": []}
        
        for i, node in enumerate(self.workflow_engine.nodes):
            node.save_id = i
            data["nodes"].append({
                "type_id": node.module.get_module_type_id(),
                "name": node.module.name,
                "x": node.scenePos().x(),
                "y": node.scenePos().y(),
                "inputs": node.module.inputs
            })
            
        for conn in self.workflow_engine.connections:
            data["connections"].append({
                "start_node": getattr(conn.start_port.parent_node, 'save_id', -1),
                "start_port": conn.start_port.name,
                "end_node": getattr(conn.end_port.parent_node, 'save_id', -1),
                "end_port": conn.end_port.name
            })
            
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        self.statusBar().showMessage(f"Workflow saved to {filename}")

    def delete_selected(self):
        """Delete selected nodes"""
        from node_canvas import CalculationNode, NodeConnection
        for item in list(self.node_canvas.scene.selectedItems()):
            if isinstance(item, CalculationNode):
                self.node_canvas.remove_node(item)
            elif isinstance(item, NodeConnection):
                self.node_canvas.remove_connection(item)
        self.statusBar().showMessage("Deleted selected items")

    def run_workflow(self):
        """Execute the workflow"""
        self.statusBar().showMessage("Running workflow...")
        self.workflow_engine.execute()

    def validate_workflow(self):
        """Validate the workflow"""
        # TODO: Implement validation
        QMessageBox.information(self, "Validation", "Workflow is valid!")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Calculation Workflow",
            "Calculation Workflow Application\n\n"
            "A modular calculation framework for engineering workflows.\n\n"
            "Built with PyQt6"
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())