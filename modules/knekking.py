import math
from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class KnekkingModule(CalculationModule):
    name = "Knekking av Opptrekkstang"
    category = "Structural Analysis"
    description = "Buckling calculation for tension rod"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("length", "Length", float, "mm", default_value=1000.0),
            InputParameter("diameter", "Diameter", float, "mm", default_value=20.0),
            InputParameter("elastic_modulus", "E-modulus", float, "GPa", default_value=200.0),
            InputParameter("applied_force", "Applied Force", float, "N", default_value=500.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("critical_load", "Critical Load", float, "N"),
            OutputParameter("safety_factor", "Safety Factor", float, ""),
            OutputParameter("status", "Status", str, "")
        ]

    def calculate(self) -> Dict[str, Any]:
        length = float(self.inputs.get("length", 1))  # mm
        diameter = float(self.inputs.get("diameter", 1))  # mm
        E = float(self.inputs.get("elastic_modulus", 1)) * 1000  # Convert GPa to MPa
        applied_force = float(self.inputs.get("applied_force", 0))  # N

        # Calculate moment of inertia (mm^4)
        I = math.pi * (diameter ** 4) / 64

        # Euler buckling load for pinned-pinned column (N)
        critical_load = (math.pi ** 2) * E * I / (length ** 2)

        if applied_force > 0:
            safety_factor = critical_load / applied_force
        else:
            safety_factor = float('inf')

        status = "PASS" if safety_factor > 2.0 else "FAIL"

        return {
            "critical_load": critical_load,
            "safety_factor": safety_factor,
            "status": status
        }
