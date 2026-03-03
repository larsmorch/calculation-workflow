from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter
from modules.functions.moment_shear_deflection_funtion import beam_centered_udl_numeric_deflection_mm_kN, plot_all_mm_kN
import numpy as np
import matplotlib.pyplot as plt

class MomentShearDeflection(CalculationModule):
    name = "Moment Shear Deflection"
    category = "Structural"
    description = "Simply supported beam with centered partial UDL"
    version = "1.0.0"
    
    latex_formula = r"$\mathbf{y''} = \frac{M}{EI}, \quad \quad \mathbf{V}(x) = \Sigma F$"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("w", "Load intensity (w)", float, units="kN/m", default_value=10.0, min_value=0.0),
            InputParameter("a", "Loaded length (a)", float, units="mm", default_value=4000.0, min_value=0.1),
            InputParameter("L", "Beam Length (L)", float, units="mm", default_value=10000.0, min_value=1.0),
            InputParameter("E", "Youngs Modulus (E)", float, units="Pa", default_value=210e9, min_value=1.0),
            InputParameter("I", "Moment of Inertia (I)", float, units="mm^4", default_value=5.517e8, min_value=1.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("max_M", "Max Moment", float, units="kN·m"),
            OutputParameter("max_V", "Max Shear", float, units="kN"),
            OutputParameter("mid_deflect", "Midspan Deflection", float, units="mm"),
            OutputParameter("RA", "Reaction A", float, units="kN"),
            OutputParameter("RB", "Reaction B", float, units="kN")
        ]

    def calculate(self) -> Dict[str, Any]:
        w = float(self.inputs.get("w", 10.0))
        a = float(self.inputs.get("a", 4000.0))
        L = float(self.inputs.get("L", 10000.0))
        E = float(self.inputs.get("E", 210e9))
        I = float(self.inputs.get("I", 5.517e8))
        
        # Guard limits
        if a > L:
            a = L

        x, V_kN, M_kNm, y_mm, (RA, RB, x1, x2) = beam_centered_udl_numeric_deflection_mm_kN(w, a, L, E, I)
        
        # Avoid creating ghost plots memory leaking over time via matplotlib context
        plt.close(self.figure) if self.figure else None
        
        self.figure = plot_all_mm_kN(x, V_kN, M_kNm, y_mm, L, x1, x2, w, RA, RB)
        
        # Maxes
        max_M = float(np.max(np.abs(M_kNm)))
        max_V = float(np.max(np.abs(V_kN)))
        mid_deflect = float(np.interp(L/2.0, x, y_mm))
        
        return {
            "max_M": max_M,
            "max_V": max_V,
            "mid_deflect": mid_deflect,
            "RA": float(RA),
            "RB": float(RB)
        }
