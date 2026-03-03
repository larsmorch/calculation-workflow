from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class BeamDeflectionModule(CalculationModule):
    name = "Simply Supported Beam Deflection"
    category = "Structural Analysis"
    description = "Calculates max deflection and moment for a simple supported beam with UDL"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("w", "Load (w)", float, "kN/m", min_value=0.0, default_value=10.0),
            InputParameter("L", "Span (L)", float, "m", min_value=0.1, max_value=50.0, default_value=5.0),
            InputParameter("E", "Young's Modulus (E)", float, "GPa", default_value=210.0),
            InputParameter("I", "Moment of Inertia (I)", float, "cm⁴", min_value=0.0, default_value=1000.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("deflection", "Max Deflection", float, "mm"),
            OutputParameter("moment", "Max Moment", float, "kNm")
        ]

    def calculate(self) -> Dict[str, Any]:
        w = float(self.inputs.get("w", 0))
        L = float(self.inputs.get("L", 0))
        E = float(self.inputs.get("E", 1)) * 1e9  # Convert GPa to N/m^2
        I = float(self.inputs.get("I", 1)) * 1e-8 # Convert cm^4 to m^4

        # Convert w from kN/m to N/m
        w_n = w * 1000

        # Max deflection = 5wL^4 / 384EI (in meters)
        deflection_m = (5 * w_n * (L ** 4)) / (384 * E * I)
        deflection_mm = deflection_m * 1000

        # Max moment = wL^2 / 8 (in kNm)
        moment = (w * (L ** 2)) / 8
        
        return {
            "deflection": deflection_mm,
            "moment": moment
        }
