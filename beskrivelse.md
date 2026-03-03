Calculation Workflow Application - Project Documentation
Project Overview
Calculation Workflow is a visual, node-based engineering calculation application built with PyQt6. It provides a graphical interface for creating, connecting, and executing modular calculation workflows, designed specifically for engineering tasks at Sweco.

Current State (Version 0.1 - Initial Release)
Architecture
The application follows a modular, object-oriented design with clear separation of concerns:

plaintext
calculation-workflow/
├── main.py                 # Application entry point
├── main_window.py          # Main application window and orchestration
├── node_canvas.py          # Visual canvas for node placement and interaction
├── module_library.py       # Panel displaying available calculation modules
├── properties_panel.py     # Panel for editing node properties
├── results_panel.py        # Panel for displaying calculation results
└── workflow_engine.py      # Calculation execution engine
Implemented Features
1. Main Window (main_window.py) - ~450 lines
Layout: Dockable panel interface with resizable sections
Menu System:
File: New, Open, Save, Save As, Exit
Edit: Undo, Redo, Delete
Workflow: Run, Validate
Help: About
Toolbar: Quick access to common actions (New, Open, Save, Run)
Status Bar: Real-time feedback on application state
Signal/Slot Architecture: Event-driven communication between components
2. Node Canvas (node_canvas.py)
Graphics View: QGraphicsView-based rendering with antialiasing
Node Management: Add, remove, and clear nodes
Visual Nodes:
Movable and selectable calculation blocks (150x80px)
Visual selection feedback with highlight borders
Module type labeling
Grid Background: Light gray workspace for better visibility
Interaction Modes: Rubber band selection support
3. Module Library (module_library.py)
Available Modules:
Basic Math
Structural Analysis
Material Properties
Load Calculator
Section Properties
Interaction: Double-click or button to add modules to canvas
Signal Emission: Communicates module selection to main window
4. Properties Panel (properties_panel.py)
Dynamic Form: Displays properties for selected nodes
Fields: Module type, Input 1, Input 2 (placeholder inputs)
Auto-clear: Refreshes when different nodes are selected
5. Results Panel (results_panel.py)
Read-only Display: Shows calculation outputs
Text Area: Formatted results display
Update Mechanism: Receives results from workflow engine
6. Workflow Engine (workflow_engine.py)
Node Registry: Tracks all nodes in the workflow
Execution: Basic calculation execution framework
Signal Emission: Notifies when calculations complete
Results Dictionary: Structured output format
Technical Stack
Framework: PyQt6 (latest Qt6 bindings for Python)
Language: Python 3.x
GUI Components:
QMainWindow (application frame)
QGraphicsView/QGraphicsScene (canvas rendering)
QDockWidget (panel management)
QMenuBar, QToolBar (navigation)
Architecture Pattern: Model-View-Controller (MVC)
Current Capabilities
✅ Application launches successfully
✅ Modular, dockable interface
✅ Add calculation nodes to canvas
✅ Move and select nodes visually
✅ View node properties
✅ Basic workflow execution framework
✅ Menu and toolbar navigation
✅ Status feedback system

Known Limitations
❌ No actual calculations implemented (placeholder logic only)
❌ No node connections/data flow visualization
❌ No save/load functionality
❌ No undo/redo implementation
❌ No input validation
❌ No error handling for calculations
❌ No custom icons for toolbar
❌ No workflow validation logic
❌ Limited module types
❌ No user documentation

Next Steps to Enhance the Application
Phase 1: Core Functionality (Priority: High)
1.1 Implement Node Connections
Goal: Visual representation of data flow between nodes

Connection Lines: Draw bezier curves or straight lines between nodes
Port System:
Input ports (left side of nodes)
Output ports (right side of nodes)
Color-coded by data type
Connection Logic:
Click and drag from output to input port
Validate compatible connections
Delete connections on right-click
Data Flow: Automatically determine execution order based on connections
Estimated Effort: 3-4 days

1.2 Real Calculation Modules
Goal: Implement actual engineering calculations

Module Base Class: Create abstract CalculationModule class with:

inputs property
outputs property
calculate() method
validate() method
Initial Modules:

Basic Math: Add, subtract, multiply, divide, power, square root
Unit Converter: Length, force, stress, pressure conversions
Beam Calculator: Simple supported beam deflection and moment
Section Properties: Area, I, W for standard sections
Material Database: Steel, concrete properties lookup
Estimated Effort: 5-7 days

1.3 Save/Load Workflows
Goal: Persist workflows to disk

JSON Serialization:

Node positions and types
Connection mappings
Input values
Metadata (author, date, version)
File Format: .wf or .json extension

Features:

Auto-save functionality
Recent files menu
File association (double-click to open)
Estimated Effort: 2-3 days

Phase 2: User Experience (Priority: Medium)
2.1 Undo/Redo System
QUndoStack Implementation: Track all user actions
Commands: Add node, delete node, move node, create connection
UI Integration: Menu items, keyboard shortcuts (Ctrl+Z, Ctrl+Y)
Estimated Effort: 3 days

2.2 Enhanced Properties Panel
Dynamic Field Types:

Number inputs with units (spinboxes)
Dropdowns for selections
Material/section browsers
Color pickers for visualization
Live Updates: Changes immediately affect calculations

Validation: Red borders for invalid inputs, error messages

Estimated Effort: 2-3 days

2.3 Results Visualization
Tabular Display: Formatted tables with headers

Charts/Graphs: matplotlib integration for:

Shear/moment diagrams
Load distributions
Stress plots
Export: Copy to clipboard, save as CSV, PDF reports

Estimated Effort: 4-5 days

2.4 Visual Improvements
Custom Icons: Professional toolbar/menu icons

Node Appearance:

Color-coded by category
Icons representing module type
Connection port indicators
Execution status (pending, running, complete, error)
Canvas Features:

Grid snapping
Zoom in/out (mouse wheel)
Mini-map for large workflows
Background grid lines
Estimated Effort: 3-4 days

Phase 3: Advanced Features (Priority: Low)
3.1 Workflow Validation
Circular Dependency Detection: Prevent infinite loops
Type Checking: Ensure compatible connections
Missing Input Detection: Warn about unconnected required inputs
Visual Feedback: Highlight errors in red
Estimated Effort: 2-3 days

3.2 Execution Control
Step-by-Step Mode: Execute one node at a time
Breakpoints: Pause execution at specific nodes
Watch Values: Monitor intermediate results
Execution History: Timeline of calculations
Estimated Effort: 4 days

3.3 Module Plugin System
Plugin Architecture: Load external Python modules
Plugin Manager: Browse, install, update modules
Custom Modules: Users create their own calculations
Module Marketplace: Share modules with team
Estimated Effort: 7-10 days

3.4 Collaboration Features
Version Control Integration: Git integration for workflows
Comments/Annotations: Add notes to nodes and canvas
Shared Libraries: Team-wide module repositories
Export Formats: Share as standalone Python script
Estimated Effort: 5-7 days

3.5 Code Generation
Export to Python: Generate standalone calculation script
Export to Excel: VBA or Python-Excel integration
Documentation: Auto-generate calculation report
Standards Compliance: Include code references (Eurocode, etc.)
Estimated Effort: 6-8 days

Phase 4: Production Readiness (Priority: Medium-High)
4.1 Error Handling
Try-Catch Blocks: Graceful handling of calculation errors
User-Friendly Messages: Clear error descriptions
Error Logging: Save errors to log file
Recovery: Prevent application crashes
Estimated Effort: 2 days

4.2 Testing
Unit Tests: pytest for individual modules
Integration Tests: Test workflow execution
UI Tests: Automated GUI testing
Test Coverage: Aim for 80%+ coverage
Estimated Effort: 5-7 days

4.3 Documentation
User Manual: Step-by-step guides with screenshots
Developer Documentation: API reference, architecture diagrams
Tutorial Workflows: Example calculations to learn from
Video Tutorials: Screen recordings of common tasks
Estimated Effort: 4-5 days

4.4 Packaging & Distribution
Installer: PyInstaller or cx_Freeze for standalone executable
Cross-Platform: Windows, macOS, Linux builds
Auto-Update: Check for new versions on startup
Installation Guide: IT department deployment instructions
Estimated Effort: 3-4 days

Recommended Implementation Roadmap
Sprint 1 (2-3 weeks): Foundation
Node connections (visual + logic)
Basic calculation modules (math, units)
Save/load workflows
Basic error handling
Deliverable: Functional workflow creation and execution

Sprint 2 (2 weeks): Usability
Undo/redo
Enhanced properties panel
Visual improvements (icons, colors)
Input validation
Deliverable: Polished user experience

Sprint 3 (2 weeks): Results & Validation
Results visualization (tables, charts)
Workflow validation
Export results
More calculation modules
Deliverable: Production-ready calculation tool

Sprint 4 (1-2 weeks): Production
Comprehensive testing
Documentation
Packaging for distribution
User training
Deliverable: Deployed application

Success Metrics
Usability: Engineers can create a basic workflow in < 5 minutes
Reliability: 99%+ uptime, no data loss
Performance: Workflows with 100+ nodes execute in < 5 seconds
Adoption: 80% of calculation team using within 3 months
Efficiency: 50% reduction in repetitive calculation time
Technology Considerations
Potential Upgrades
Database: SQLite for storing module library and templates
Web Version: PyQt WebEngine or Django-based web app
Cloud Sync: Save workflows to cloud storage
AI Integration: Suggest optimal workflow configurations
Mobile Companion: View results on tablets/phones
Dependencies to Add
plaintext
matplotlib      # Charting
numpy           # Numerical calculations
pandas          # Data manipulation
openpyxl        # Excel export
reportlab       # PDF generation
pytest          # Testing
Conclusion
The Calculation Workflow Application is currently at a functional prototype stage with a solid architectural foundation. The modular design allows for incremental enhancement without major refactoring.

Immediate priority should be Phase 1 features (connections, real calculations, save/load) to make the application genuinely useful for daily engineering work. Once core functionality is solid, UX improvements will drive adoption, followed by advanced features for power users.

Estimated Time to Production-Ready v1.0: 8-12 weeks with dedicated development effort.
