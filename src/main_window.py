import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QMenu, QToolBar, QStatusBar, QSplitter, QMessageBox,
    QFileDialog, QDockWidget, QInputDialog
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
        self.setWindowTitle("Calculation Workflow")
        self.setGeometry(100, 100, 1400, 900)

        # Initialize persistent Excel app manager
        self.excel_app = None

        # Initialize workflow engine
        self.workflow_engine = WorkflowEngine()
        self.current_workflow_file = None
        self.project_number = None

        # Setup UI components
        self.setup_ui()
        self.create_menus()
        self.create_toolbar()
        self.create_status_bar()

        # Connect signals
        self.connect_signals()
        
        # Enable drag and drop
        self.setAcceptDrops(True)

    def closeEvent(self, event):
        """Handle application close to clean up background processes"""
        if self.excel_app:
            try:
                import pythoncom
                pythoncom.CoInitialize()
                self.excel_app.quit()
                self.excel_app = None
            except Exception as e:
                print(f"Error closing Excel app: {e}")
            finally:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass
        super().closeEvent(event)

    def _get_excel_app(self):
        """Get or create the persistent Excel application"""
        if self.excel_app is None:
            import xlwings as xw
            import pythoncom
            pythoncom.CoInitialize()
            self.excel_app = xw.App(visible=False)
            self.excel_app.display_alerts = False
        return self.excel_app

    def _get_or_create_excel_class(self, file_path):
        import os
        import re
        from extract_variables import extract_variables
        from calculation_module import CalculationModule, InputParameter, OutputParameter
        from module_registry import registry
        
        filename = os.path.basename(file_path)
        module_name = os.path.splitext(filename)[0]
        
        # Robust class name generation supporting Norwegian characters (Unicode is valid in Python 3 identifiers)
        # We title() the name, then filter for alphanumeric characters only.
        # Python 3 supports ÆØÅ in identifiers, but for maximum compatibility with dynamic type creation,
        # we'll keep them but ensure it's a valid identifier.
        clean_name = "".join(c for c in module_name.title() if c.isalnum() or c == '_')
        if not clean_name or clean_name[0].isdigit():
            clean_name = "Excel_" + clean_name
        class_name = clean_name + "ExcelModule"
        
        if registry.has_type(class_name):
            return class_name
            
        inputs, outputs = extract_variables(file_path)
        if not inputs and not outputs:
            return None

        input_params = []
        for item in inputs:
            py_type = float if isinstance(item['value'], (int, float)) else str
            input_params.append(
                InputParameter(name=item['name'], display_name=item['name'], type=py_type, units=item['unit'] or "", default_value=item['value'])
            )
            
        output_params = []
        for item in outputs:
            py_type = float if isinstance(item['value'], (int, float)) else str
            output_params.append(
                OutputParameter(name=item['name'], display_name=item['name'], type=py_type, units=item['unit'] or "", initial_value=item['value'])
            )
            
        def get_input_parameters(cls):
            return input_params

        def get_output_parameters(cls):
            return output_params

        # Store main window reference locally for dynamic class
        main_window_ref = self

        def calculate(self):
            import pythoncom
            
            pythoncom.CoInitialize()
            try:
                # Use persistent app and cache workbook
                app = main_window_ref._get_excel_app()
                
                if not hasattr(self, '_wb'):
                    # Open workbook if not already open for this node
                    self._wb = app.books.open(file_path)
                
                wb = self._wb
                
                # Write inputs ONLY if they are connected
                connected_inputs = getattr(self, 'connected_inputs', [])
                for param_name, val in self.inputs.items():
                    if param_name in connected_inputs and val is not None:
                        try:
                            wb.names[param_name].refers_to_range.value = val
                        except Exception:
                            try:
                                sheet_name, cell = param_name.split('!')
                                wb.sheets[sheet_name].range(cell).value = val
                            except Exception as e2:
                                print(f"Error writing input {param_name}: {e2}")
                                
                # Calculate
                app.calculate()
                
                # Sync back unconnected inputs from Excel
                for param in self.get_input_parameters():
                    if param.name not in connected_inputs:
                        try:
                            val = wb.names[param.name].refers_to_range.value
                            self.inputs[param.name] = val
                        except Exception:
                            try:
                                sheet_name, cell = param.name.split('!')
                                val = wb.sheets[sheet_name].range(cell).value
                                self.inputs[param.name] = val
                            except Exception:
                                pass

                # Read outputs
                results = {}
                for param in self.get_output_parameters():
                    try:
                        val = wb.names[param.name].refers_to_range.value
                        results[param.name] = val
                    except Exception:
                        try:
                            sheet_name, cell = param.name.split('!')
                            val = wb.sheets[sheet_name].range(cell).value
                            results[param.name] = val
                        except Exception as e2:
                            print(f"Error reading output {param.name}: {e2}")
                            results[param.name] = None
                            
                return results
                
            except Exception as e:
                print(f"Excel Execution Error: {e}")
                return {"Error": str(e)}
            finally:
                try:
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

        dynamic_class = type(str(class_name), (CalculationModule,), {
            "name": module_name,
            "category": "Excel",
            "description": f"Generated from {filename}",
            "version": "1.0.0",
            "get_input_parameters": classmethod(get_input_parameters),
            "get_output_parameters": classmethod(get_output_parameters),
            "calculate": calculate,
            "excel_path": file_path
        })
        
        registry.register(dynamic_class)
        return class_name

    def _create_excel_node(self, file_path, position):
        import os
        from module_registry import registry
        
        class_name = self._get_or_create_excel_class(file_path)
        if not class_name:
            QMessageBox.warning(self, "Excel Import", f"No inputs or outputs found in {os.path.basename(file_path)}.")
            return

        node = self.node_canvas.add_node(class_name, position)
        if node:
            # Ensure excel_path is set on the instance as well
            node.module.excel_path = file_path
            self.workflow_engine.add_node(node)
            self.statusBar().showMessage(f"Added Excel module {os.path.basename(file_path)} to canvas")

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

        new_project_action = QAction("&New Project...", self)
        new_project_action.triggered.connect(self.create_new_project)
        file_menu.addAction(new_project_action)

        file_menu.addSeparator()

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

        # New Project
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self.create_new_project)
        toolbar.addAction(new_project_action)

        toolbar.addSeparator()

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
        self.node_canvas.file_dropped.connect(self._create_excel_node)
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
        if filename:
            self._load_from_file(filename)

    def _load_from_file(self, filename):
        import json
        from PyQt6.QtCore import QPointF
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            self.node_canvas.clear_canvas()
            self.workflow_engine.nodes.clear()
            self.workflow_engine.connections.clear()
            
            # Load project number
            self.project_number = data.get("project_number")
            self._update_window_title()

            created_nodes = {}
            for i, n_data in enumerate(data.get("nodes", [])):
                type_id = n_data["type_id"]
                excel_path = n_data.get("excel_path")
                
                if excel_path:
                    # Recreate dynamic excel module class if needed
                    self._get_or_create_excel_class(excel_path)
                
                node = self.node_canvas.add_node(type_id, QPointF(n_data["x"], n_data["y"]))
                if not node: continue
                
                if excel_path:
                    node.module.excel_path = excel_path
                    
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
                node.width = get_dynamic_node_width(node.module.name, node.module.get_input_parameters(), node.module.get_output_parameters())
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
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error Loading", f"Failed to open workflow: {e}")

    def _update_window_title(self):
        title = "Calculation Workflow"
        if self.project_number:
            title += f" - Project: {self.project_number}"
        self.setWindowTitle(title)

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
        data = {"project_number": self.project_number, "nodes": [], "connections": []}
        
        for i, node in enumerate(self.workflow_engine.nodes):
            node.save_id = i
            node_data = {
                "type_id": node.module.get_module_type_id(),
                "name": node.module.name,
                "x": node.scenePos().x(),
                "y": node.scenePos().y(),
                "inputs": node.module.inputs
            }
            if hasattr(node.module, 'excel_path') and node.module.excel_path:
                node_data["excel_path"] = node.module.excel_path
                
            data["nodes"].append(node_data)
            
        for conn in self.workflow_engine.connections:
            data["connections"].append({
                "start_node": getattr(conn.start_port.parent_node, 'save_id', -1),
                "start_port": conn.start_port.name,
                "end_node": getattr(conn.end_port.parent_node, 'save_id', -1),
                "end_port": conn.end_port.name
            })
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
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

    def create_new_project(self):
        """Create a new project by duplicating Excel files and saving a new workflow"""
        import os
        import shutil
        import json

        # Check if we have Excel nodes
        excel_nodes = [node for node in self.workflow_engine.nodes if hasattr(node.module, 'excel_path') and node.module.excel_path]
        if not excel_nodes:
            QMessageBox.warning(self, "New Project", "No Excel-based modules found in the current workflow.")
            return

        # Prompt for project number
        project_number, ok = QInputDialog.getText(self, "New Project", "Enter Project Number:")
        if not ok or not project_number:
            return

        # Prompt for target directory
        target_dir = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if not target_dir:
            return

        try:
            # 0. Close all managed workbooks to release file locks
            if self.excel_app:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                    for book in list(self.excel_app.books):
                        try:
                            book.close()
                        except Exception:
                            pass
                    # Also clear the cached references on the modules
                    for node in excel_nodes:
                        if hasattr(node.module, '_wb'):
                            delattr(node.module, '_wb')
                except Exception as e_excel:
                    print(f"Warning: Could not close all workbooks: {e_excel}")
                finally:
                    try:
                        pythoncom.CoUninitialize()
                    except Exception:
                        pass

            # 1. Map unique Excel files to their new paths
            unique_files = {}
            for node in excel_nodes:
                src_path = node.module.excel_path
                if src_path not in unique_files:
                    filename = os.path.basename(src_path)
                    new_filename = f"{project_number}_{filename}"
                    dest_path = os.path.join(target_dir, new_filename)
                    unique_files[src_path] = dest_path

            # 2. Copy files
            for src, dest in unique_files.items():
                try:
                    shutil.copy2(src, dest)
                except PermissionError:
                    QMessageBox.critical(
                        self, 
                        "Permission Error", 
                        f"Could not copy '{os.path.basename(src)}'.\n\n"
                        "Please ensure the file is not open in Excel or another application and try again."
                    )
                    return

            # 3. Create JSON payload for the new workflow
            data = {"project_number": project_number, "nodes": [], "connections": []}
            
            for i, node in enumerate(self.workflow_engine.nodes):
                node.save_id = i
                
                # Default type_id
                type_id = node.module.get_module_type_id()
                
                # If it's an Excel node, the type_id will change because the filename changed
                excel_path = getattr(node.module, 'excel_path', None)
                new_excel_path = None
                
                if excel_path:
                    new_excel_path = unique_files.get(excel_path)
                    if new_excel_path:
                        # Calculate the new class name/type_id exactly as _get_or_create_excel_class does
                        new_filename = os.path.basename(new_excel_path)
                        new_module_name = os.path.splitext(new_filename)[0]
                        clean_name = "".join(c for c in new_module_name.title() if c.isalnum() or c == '_')
                        if not clean_name or clean_name[0].isdigit():
                            clean_name = "Excel_" + clean_name
                        type_id = clean_name + "ExcelModule"

                node_data = {
                    "type_id": type_id,
                    "name": node.module.name,
                    "x": node.scenePos().x(),
                    "y": node.scenePos().y(),
                    "inputs": node.module.inputs
                }
                if new_excel_path:
                    node_data["excel_path"] = new_excel_path
                    
                data["nodes"].append(node_data)
                
            for conn in self.workflow_engine.connections:
                data["connections"].append({
                    "start_node": getattr(conn.start_port.parent_node, 'save_id', -1),
                    "start_port": conn.start_port.name,
                    "end_node": getattr(conn.end_port.parent_node, 'save_id', -1),
                    "end_port": conn.end_port.name
                })

            # 4. Save the new workflow file
            wf_filename = f"{project_number}_calculation workflow.wf"
            wf_path = os.path.join(target_dir, wf_filename)
            with open(wf_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            # 5. Prompt to load
            reply = QMessageBox.question(
                self,
                "New Project Created",
                f"Project {project_number} created successfully.\nLoad the new workflow now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self._load_from_file(wf_path)
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to create new project: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
