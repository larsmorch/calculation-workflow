from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class Subtraksjon(CalculationModule):
    name = "Subtraksjon"
    category = "Matte"
    description = "Trekker et tall fra et annet"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("val1", "Value 1", float, units="kN", default_value=0.0),
            InputParameter("val2", "Value 2", float, units="kN", default_value=0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("sum", "Sum", float, units="kN")
        ]

    def calculate(self) -> Dict[str, Any]:
        v1 = float(self.inputs.get("val1", 0))
        v2 = float(self.inputs.get("val2", 0))
        return {"sum": v1 - v2}
