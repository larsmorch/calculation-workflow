from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class ProjectProperties(CalculationModule):
    name = "Project Properties"
    category = "General"
    description = "Copies all input values securely directly into parallel logic outputs."
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("hrv", "HRV", float, units="kote", default_value=0.0),
            InputParameter("luketerskel", "LUKETERSKEL", float, units="kote", default_value=0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("hrv_out", "HRV Out", float, units="kote"),
            OutputParameter("luketerskel_out", "LUKETERSKEL Out", float, units="kote")
        ]

    def calculate(self) -> Dict[str, Any]:
        """Dynamically mirrors every present input directly to equivalent outputs."""
        results = {}
        for key, value in self.inputs.items():
            results[f"{key}_out"] = value
        return results
