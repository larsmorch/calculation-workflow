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
            InputParameter("prop_value", "Placeholder Property", float, default_value=0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("prop_value_out", "Placeholder Property Out", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        """Dynamically mirrors every present input directly to equivalent outputs."""
        results = {}
        for key, value in self.inputs.items():
            results[f"{key}_out"] = value
        return results
