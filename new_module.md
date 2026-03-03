How to Add New Modules - Implementation Guide
Current State: The Problem
Right now, adding a new module requires:

Hardcoding it into the ModuleLibrary list
Creating custom logic in WorkflowEngine for each module type
Manually defining properties in PropertiesPanel
No reusable calculation logic
This doesn't scale - adding 50 modules would be a nightmare.

The Solution: Plugin-Based Module System
Architecture Overview
plaintext
┌─────────────────────────────────────────────────┐
│          Module Base Class (Abstract)            │
│  - Defines interface all modules must follow    │
│  - inputs, outputs, calculate(), validate()     │
└─────────────────────────────────────────────────┘
                        ▲
                        │ inherits
         ┌──────────────┼──────────────┐
         │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │ Module  │   │ Module  │   │ Module  │
    │   #1    │   │   #2    │   │   #3    │
    └─────────┘   └─────────┘   └─────────┘
Core Concept: Self-Describing Modules
Each module is a standalone class that describes:

What it does (name, description, category)
What inputs it needs (name, type, units, default value)
What outputs it produces (name, type, units)
How to calculate (the actual computation logic)
How to validate (input checking)
Implementation Steps
Step 1: Create Base Module Class
File: calculation_module.py

Purpose: Abstract base class that all modules inherit from

Key Components:

plaintext
CalculationModule (abstract class)
│
├── Metadata
│   ├── name (str) - "Beam Deflection Calculator"
│   ├── category (str) - "Structural Analysis"
│   ├── description (str) - "Calculates max deflection..."
│   ├── icon (str) - Path to icon file
│   └── version (str) - "1.0.0"
│
├── Input Definition
│   └── inputs (list of InputParameter objects)
│       ├── name - "Load"
│       ├── type - float, int, str, bool
│       ├── units - "kN", "mm", "MPa"
│       ├── default - 10.0
│       ├── min/max - value constraints
│       └── required - True/False
│
├── Output Definition
│   └── outputs (list of OutputParameter objects)
│       ├── name - "Deflection"
│       ├── type - float
│       └── units - "mm"
│
└── Methods
    ├── calculate(inputs) -> outputs
    │   └── The actual calculation logic
    │
    ├── validate(inputs) -> bool, error_message
    │   └── Check if inputs are valid
    │
    └── get_documentation() -> str
        └── Return help text/formula
Why This Works:

Self-contained: Each module knows everything about itself
Auto-discovery: System can read metadata without running calculations
Auto-UI generation: Properties panel builds forms from input definitions
Type safety: Input/output types are explicitly defined
Step 2: Create Input/Output Parameter Classes
Purpose: Structured way to define module inputs and outputs

InputParameter Class:

plaintext
Properties:
- name: str (e.g., "beam_length")
- display_name: str (e.g., "Beam Length")
- type: Python type (float, int, str, bool, Enum)
- units: str (e.g., "m", "kN", "MPa")
- default_value: any
- min_value: numeric (optional)
- max_value: numeric (optional)
- required: bool
- description: str (tooltip text)
- validation_rules: list of custom validators
OutputParameter Class:

plaintext
Properties:
- name: str
- display_name: str
- type: Python type
- units: str
- description: str
Why Separate Classes:

Enables automatic form generation
Provides built-in validation
Makes serialization easier (save/load workflows)
Step 3: Create Example Concrete Modules
Approach: Create actual calculation modules by inheriting from base class

Example Structure (conceptual):

Simple Module: Basic Math Addition
plaintext
Class: AdditionModule
Inherits: CalculationModule

Metadata:
- name = "Addition"
- category = "Basic Math"
- description = "Adds two numbers"

Inputs:
- Input 1: float, default=0, units="", required=True
- Input 2: float, default=0, units="", required=True

Outputs:
- Sum: float, units=""

calculate():
    return input1 + input2

validate():
    (no special validation needed)
Complex Module: Beam Deflection
plaintext
Class: BeamDeflectionModule
Inherits: CalculationModule

Metadata:
- name = "Simply Supported Beam Deflection"
- category = "Structural Analysis"
- description = "EC3 beam deflection for UDL"

Inputs:
- Load (w): float, units="kN/m", min=0, required=True
- Span (L): float, units="m", min=0.1, max=50, required=True
- Young's Modulus (E): float, units="GPa", default=210
- Moment of Inertia (I): float, units="cm⁴", min=0, required=True

Outputs:
- Max Deflection: float, units="mm"
- Max Moment: float, units="kNm"

calculate():
    deflection = (5 * w * L^4) / (384 * E * I)
    moment = (w * L^2) / 8
    return {deflection, moment}

validate():
    if deflection > L/250:
        warning: "Deflection exceeds limit"
Step 4: Module Registry System
Purpose: Central system to manage all available modules

Registry Class:

plaintext
ModuleRegistry
│
├── registered_modules: dict
│   └── {category: [module_class1, module_class2, ...]}
│
├── Methods:
│   ├── register(module_class)
│   │   └── Add module to registry
│   │
│   ├── get_all_modules() -> list
│   │   └── Return all available modules
│   │
│   ├── get_by_category(category) -> list
│   │   └── Filter by category
│   │
│   ├── get_by_name(name) -> module_class
│   │   └── Find specific module
│   │
│   ├── create_instance(name) -> module_instance
│   │   └── Instantiate a module
│   │
│   └── scan_plugins(directory)
│       └── Auto-discover modules from folder
