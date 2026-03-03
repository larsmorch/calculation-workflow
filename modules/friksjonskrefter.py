from typing import Dict, Any, List
from calculation_module import CalculationModule, InputParameter, OutputParameter

class FriksjonskrefterModule(CalculationModule):
    name = "Friksjonskrefter"
    category = "Mechanical"
    description = "Friction force and torque calculation"
    version = "1.0.0"

    @classmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        return [
            InputParameter("diameter", "Diameter", float, "mm", default_value=10.0),
            InputParameter("normal_force", "Normal Force", float, "N", default_value=100.0),
            InputParameter("friction_coef", "Friction Coefficient", float, "", default_value=0.15)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        return [
            OutputParameter("friction_force", "Friction Force", float, "N"),
            OutputParameter("torque", "Torque", float, "Nm")
        ]

    def calculate(self) -> Dict[str, Any]:
        diameter = float(self.inputs.get("diameter", 0))
        normal_force = float(self.inputs.get("normal_force", 0))
        friction_coef = float(self.inputs.get("friction_coef", 0))

        friction_force = normal_force * friction_coef
        torque = friction_force * (diameter / 2.0) / 1000.0  # Convert mm to m

        return {
            "friction_force": friction_force,
            "torque": torque
        }
