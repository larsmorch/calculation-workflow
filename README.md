# Calculation Workflow Application

A visual, node-based engineering calculation platform built with Python and PyQt6. This application allows engineers to create complex calculation chains by connecting modular calculation blocks, with a heavy focus on seamless Excel integration.

## Key Features

- **Visual Workflow Canvas:** Drag and drop modules to create calculation chains.
- **Deep Excel Integration:**
    - **Drag & Drop Import:** Drag any `.xlsx` or `.xlsm` (macro-enabled) file directly onto the canvas.
    - **Single Source of Truth:** Input values are read directly from Excel. The GUI properties panel is read-only to ensure your spreadsheets remain the master data source.
    - **Intelligent Synchronization:** The app only writes values to Excel that are driven by upstream workflow connections. Manual edits in your Excel files are automatically synced back to the GUI.
- **Project Management:**
    - **New Project Workflow:** Instantly scaffold a new project folder. The app duplicates your active spreadsheets, renames them with a project prefix, and updates all workflow links automatically.
    - **Norwegian Support:** Full support for Norwegian characters (Æ, Ø, Å) in filenames, paths, and internal module generation.
- **Dynamic Module System:** Automatically discovers and registers Python-based calculation modules.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Microsoft Excel (required for Excel-based modules)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/larsmorch/calculation-workflow.git
   cd calculation-workflow
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

Execute the main entry point:
```bash
python main.py
```

## How to Use

### 1. Creating a Workflow
- Use the **Module Library** on the left to find built-in calculation modules.
- **Import Excel files** by dragging them from your file explorer directly onto the main canvas.
- Connect modules by dragging wires between **Output ports** (Blue) and **Input ports** (Green).

### 2. Running Calculations
- The workflow automatically runs whenever a connection is made or a value changes.
- You can manually trigger a run using **F5** or the **Run** button in the toolbar.
- View detailed results in the **Results Panel** at the bottom.

### 3. Creating a New Project
- Click the **New Project** button in the toolbar.
- Enter your **Project Number**.
- Select a destination folder.
- The application will automatically:
    - Close managed Excel files.
    - Copy all active spreadsheets to the new folder with the project number as a prefix.
    - Create a new project-specific workflow file.
    - Prompt you to load the new project.

## Development

- **Adding Modules:** Place new Python classes inheriting from `CalculationModule` into the `modules/` directory.
- **Excel Logic:** Ensure your Excel files use **Defined Names** (Name Manager) for inputs and outputs. The app uses these names to map data to node ports.
