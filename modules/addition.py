from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class AdditionModule(CalculationModule):
    name = "Addition"
    category = "Basic Math"
    description = "Adds two numbers together"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("val1", "Value 1", float, default_value=0.0),
            InputParameter("val2", "Value 2", float, default_value=0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("sum", "Sum", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        v1 = float(self.inputs.get("val1", 0))
        v2 = float(self.inputs.get("val2", 0))
        return {"sum": v1 + v2}
