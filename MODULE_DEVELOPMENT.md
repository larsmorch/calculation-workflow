# How to Create a New Calculation Module

Creating new logic blocks for the **Calculation Workflow** application is incredibly straightforward. The application features a dynamic registry system that automatically discovers and loads any valid python object placed inside the `modules/` folder.

This step-by-step guide will show you everything you need to know, from a basic calculation to advanced mathematical rendering and external API integrations.

---

## 1. The Basic Module Structure

A calculation module is simply a Python class that inherits from `CalculationModule`. 
Create a new `.py` file inside the `modules/` directory (e.g., `modules/my_module.py`). 

Here is the most basic template:

```python
from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class MyBasicModule(CalculationModule):
    # Metadata used by the GUI
    name = "My Custom Adder"
    category = "Math"
    description = "Adds two numbers together"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        # Define what inputs this block receives
        return [
            InputParameter("val_a", "Value A", float, default_value=0.0),
            InputParameter("val_b", "Value B", float, default_value=0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        # Define what this block outputs
        return [
            OutputParameter("sum_result", "Addition Result", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        # Core logic: pull inputs, compute, return outputs
        a = float(self.inputs.get("val_a", 0.0))
        b = float(self.inputs.get("val_b", 0.0))
        
        return {
            "sum_result": a + b
        }
```

Once this file is saved, the GUI will automatically discover it on boot and place it into the "Math" category!

---

## 2. Advanced Parameter Configurations

`InputParameter` and `OutputParameter` take several arguments allowing you strict control over their GUI behavior:

### Setting Units & Decimal Precision
You can define explicit metrics utilizing `units="kN"` and precision explicitly using `decimals=X`. (By default, decimals fall back to `1` across the entire application).

```python
InputParameter("length", "Beam Length", float, units="mm", default_value=1200.0, min_value=1.0, decimals=3)
```

In the canvas, this output will be explicitly truncated to `1200.000` because `decimals=3` was provided.

**Available Parameter Configurations:**
* `name`: Internal codename mapped into `self.inputs` dictionary.
* `display_name`: Visual label string users see on the canvas.
* `type`: Variable restriction (e.g., `float`, `int`, `str`).
* `units`: Appends a "[unit]" string to the block labels natively (e.g. `kN/m`).
* `default_value`: Starting injection value.
* `min_value` / `max_value`: Enforces safety boundaries on the GUI typable boxes.
* `decimals`: Number of places behind the comma (defaults to 1).

---

## 3. LaTeX Mathematical Formulas

If your module represents a complex mathematical equation, you can declare a `latex_formula` string globally at the top of your class.

When a user selects your module, the canvas will utilize the `matplotlib` rendering engine to draw a pixel-perfect image of your formula dynamically at the top of the Properties Panel!

```python
class CircleArea(CalculationModule):
    name = "Area of Circle"
    category = "Geometry"
    description = "Calculates circle area"
    version = "1.0.0"
    
    # Renders the exact mathematical text securely in the GUI
    latex_formula = r"$\mathbf{A} = \pi r^2$"
```

---

## 4. Using External Heavy Functions (Wrapper Pattern)

When calculating intense logic (like Structural Beam Shears or FEA matrices), you shouldn't put all the raw math directly inside the `calculate` method. The canvas logic should strictly act as a **Wrapper**.

Store your heavy raw math logic freely in external script files (e.g., `modules/functions/my_heavy_math.py`) that know absolutely nothing about the Canvas GUI framework. 

Then, simply import them into your module wrapper:

```python
import numpy as np
from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

# Import our raw physics script from an external file
from modules.functions.moment_shear_deflection_funtion import beam_centered_udl_numeric_deflection_mm_kN

class MomentShearDeflection(CalculationModule):
    name = "Moment Shear Deflection"
    category = "Structural"
    # ... setup inputs/outputs here ...

    def calculate(self) -> Dict[str, Any]:
        # 1. Pull GUI Inputs
        w = float(self.inputs.get("w", 10.0))
        L = float(self.inputs.get("L", 10000.0))

        # 2. Feed them to external mathematical script
        x, V_kN, M_kNm, y_mm = beam_centered_udl_numeric_deflection_mm_kN(w, L)

        # 3. Translate external script output back into GUI output dictionary
        return {
            "max_M": float(np.max(np.abs(M_kNm))),
            "max_V": float(np.max(np.abs(V_kN)))
        }
```

---

## 5. Exposing Matplotlib Figures natively into the GUI

If your external functions use `matplotlib` to generate logic charts (like bending moment diagrams), you can inject those charts directly into the Workflow Canvas!

Inside your `calculate()` function, assign a generated `matplotlib.figure.Figure` object onto `self.figure`. The application will automatically construct it as a dynamic widget.

```python
    def calculate(self) -> Dict[str, Any]:
        # ... fetch inputs ...

        # Make sure to close previous ghost figures to save RAM
        import matplotlib.pyplot as plt
        if self.figure:
            plt.close(self.figure)
            
        # Call an external graphing script that returns a `fig` object!
        # Do not use `plt.show()` inside the external script! Just `return fig`
        self.figure = external_script.generate_plot(...)
        
        return {
           # return scalar metrics mapped to outputs
        }
```
*Note: Make sure your external plotting function calls `plt.close(fig)` **never** happens before returning the fig! The Qt layout relies on the figure staying alive in memory!*
