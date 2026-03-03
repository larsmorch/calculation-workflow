from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class SingleInput(CalculationModule):
    name = "Single Input"
    category = "General"
    description = "Single Input"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("input1", "Input", float, default_value=0.0, decimals=3),
            
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("input1_out", "Input Out", float, decimals=3),
            
        ]

    def calculate(self) -> Dict[str, Any]:
        """Dynamically mirrors every present input directly to equivalent outputs."""
        results = {}
        for key, value in self.inputs.items():
            results[f"{key}_out"] = value
        return results
