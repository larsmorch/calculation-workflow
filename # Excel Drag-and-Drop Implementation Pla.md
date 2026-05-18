# Excel Drag-and-Drop Implementation Plan

## Objective
Enable users to drag and drop `.xlsx` files directly onto the main application window to automatically generate and place calculation nodes. These nodes will dynamically derive their inputs and outputs using the existing logic in `extract_variables.py`.

## Key Files & Context
*   **`src/main_window.py`**: Needs updates to enable drag-and-drop events and instantiate the nodes onto the canvas.
*   **`src/extract_variables.py`**: Requires a minor refactor to return the extracted inputs and outputs as data structures instead of just printing them to the console.
*   **`src/calculation_module.py`**: Provides the base class that the newly generated Excel modules will inherit from.

## Proposed Solution
We will utilize **Dynamic Class Generation** to create unique `CalculationModule` classes for each dropped Excel file. This approach seamlessly integrates with the existing class-based `module_registry` and `@classmethod` parameters without requiring a major refactor of the application's core architecture.

## Implementation Steps

### 1. Refactor `extract_variables.py`
*   Modify the `extract_variables` function to return a tuple `(inputs, outputs)` containing the parsed lists of dictionaries.
*   Ensure backward compatibility for command-line usage by maintaining the print statements under the `__main__` block.

### 2. Implement Drag-and-Drop in `MainWindow`
*   In `src/main_window.py`, set `self.setAcceptDrops(True)` during initialization.
*   Override `dragEnterEvent` to accept events that contain `.xlsx` file URLs.
*   Override `dropEvent` to capture the file path, map the screen drop position to the canvas scene coordinates, and initiate the node creation process.

### 3. Dynamic Node Creation & Registration
*   Create a helper method in `MainWindow` (e.g., `_create_excel_node(file_path, position)`).
*   Call `extract_variables(file_path)` to get the inputs and outputs.
*   Dynamically construct a new Python class inheriting from `CalculationModule` using Python's `type()` function or a class factory.
*   Map the extracted data dictionaries to `InputParameter` and `OutputParameter` objects within the dynamic class's `@classmethod`s.
*   Implement a placeholder `calculate()` method inside this dynamic class that simply mirrors or leaves the outputs empty for now (since actual Excel evaluation logic isn't fully scoped yet).
*   Register this new class with `registry.register()` and use `self.node_canvas.add_node()` to place it at the drop coordinates.

## Verification & Testing
1.  **Manual Drag & Drop:** Start the application, drag `test.xlsx` onto the canvas, and verify that a new node appears exactly at the cursor location.
2.  **Property Validation:** Select the new node and verify that the extracted parameters are correctly populated in the Properties Panel.
3.  **Port Generation:** Verify that the correct number of input (green) and output (blue) ports are generated visually on the node based on the Excel file's data.