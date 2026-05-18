# Calculation Workflow Application

## Project Overview
Calculation Workflow is a visual, node-based engineering calculation application built with Python and PyQt6. It provides a graphical interface for creating, connecting, and executing modular calculation workflows, designed specifically for engineering tasks at Sweco. The application follows a Model-View-Controller (MVC) architecture with dockable panels including a node canvas, module library, properties panel, and results panel.

## Building and Running
1. **Install Dependencies:** Ensure you have Python installed and run:
   ```bash
   pip install -r requirements.txt
   ```
   *(Currently, the main dependencies are PyQt6, and matplotlib/numpy are expected as enhancements).*
   
2. **Run the Application:**
   Execute the main entry point from the project root:
   ```bash
   python main.py
   ```

## Development Conventions & Architecture
*   **Application Entry Point:** `main.py` bootstraps the application and loads `src/main_window.py`.
*   **Modular Architecture:** The system uses a dynamic registry system that automatically discovers and loads valid python objects placed inside the `modules/` folder.
*   **Creating Modules:**
    *   New calculation modules should inherit from `CalculationModule`.
    *   They must implement `get_input_parameters()`, `get_output_parameters()`, and `calculate()`.
    *   Place new module files directly in the `modules/` directory.
*   **Wrapper Pattern for Heavy Calculations:**
    *   Intensive logic (e.g., Structural Beam Shears, FEA matrices) should **not** be placed directly inside the `calculate` method.
    *   Instead, place raw mathematical logic in external files (e.g., `modules/functions/my_heavy_math.py`) and import them. The module class should merely act as a wrapper to interact with the GUI.
*   **UI Capabilities in Modules:**
    *   You can declare a `latex_formula` (raw string) at the top of a module class, which will be securely rendered in the GUI using matplotlib.
    *   Matplotlib figure objects can be injected natively into the Workflow Canvas by assigning them to `self.figure` within the `calculate()` method. Always ensure you close previous figures (`plt.close(self.figure)`) to prevent memory leaks.
*   **Testing:** `pytest` is the recommended testing framework (e.g., tests located in the `tests/` directory). Ensure unit tests are added for individual modules.