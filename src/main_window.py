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
            self.workflow_engine = WorkflowEngine()
            self.statusBar().showMessage("New workflow created")

    def open_workflow(self):
        """Open an existing workflow"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Workflow",
            "",
            "Workflow Files (*.wf);;All Files (*)"
        )

        if filename:
            # TODO: Implement workflow loading
            self.statusBar().showMessage(f"Opening {filename}")

    def save_workflow(self):
        """Save current workflow"""
        # TODO: Implement workflow saving
        self.statusBar().showMessage("Workflow saved")

    def save_workflow_as(self):
        """Save workflow with new name"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Workflow As",
            "",
            "Workflow Files (*.wf);;All Files (*)"
        )

        if filename:
            # TODO: Implement workflow saving
            self.statusBar().showMessage(f"Saved as {filename}")

    def delete_selected(self):
        """Delete selected nodes"""
        # TODO: Implement node deletion
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