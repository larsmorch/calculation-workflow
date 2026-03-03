from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class PakningsklemModule(CalculationModule):
    name = "Pakningsklem"
    category = "Mechanical"
    description = "Gasket clamping force calculation"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("bolt_force", "Bolt Force", float, "N", default_value=1000.0),
            InputParameter("gasket_area", "Gasket Area", float, "mm²", default_value=100.0),
            InputParameter("num_bolts", "Number of Bolts", int, "", default_value=4)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("total_clamping", "Total Clamping Force", float, "N"),
            OutputParameter("gasket_pressure", "Gasket Pressure", float, "MPa")
        ]

    def calculate(self) -> Dict[str, Any]:
        bolt_force = float(self.inputs.get("bolt_force", 0))
        gasket_area = float(self.inputs.get("gasket_area", 1))
        num_bolts = int(self.inputs.get("num_bolts", 1))

        total_clamping = bolt_force * num_bolts
        gasket_pressure = total_clamping / gasket_area  # N/mm² = MPa

        return {
            "total_clamping": total_clamping,
            "gasket_pressure": gasket_pressure
        }
