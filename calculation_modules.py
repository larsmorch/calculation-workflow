"""Specific calculation modules for the application"""
from module_base import ModuleBase, Parameter
from typing import Dict, Any, List
import math


class InputModule(ModuleBase):
    """Simple input module for entering values"""

    @classmethod
    def get_module_name(cls) -> str:
        return "Input"

    @classmethod
    def get_input_parameters(cls) -> List[Parameter]:
        return [
            Parameter("value", "Value", "", "Input value", float, 0.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[Parameter]:
        return [
            Parameter("output", "Output", "", "Output value", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        return {"output": self.inputs["value"]}


class FriksjonskrefterModule(ModuleBase):
    """Friction force calculation module"""

    @classmethod
    def get_module_name(cls) -> str:
        return "Friksjonskrefter"

    @classmethod
    def get_input_parameters(cls) -> List[Parameter]:
        return [
            Parameter("diameter", "Diameter", "mm", "Bolt diameter", float, 10.0),
            Parameter("normal_force", "Normal Force", "N", "Normal force", float, 100.0),
            Parameter("friction_coef", "Friction Coefficient", "", "Coefficient of friction", float, 0.15)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[Parameter]:
        return [
            Parameter("friction_force", "Friction Force", "N", "Total friction force", float),
            Parameter("torque", "Torque", "Nm", "Friction torque", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        diameter = self.inputs["diameter"]
        normal_force = self.inputs["normal_force"]
        friction_coef = self.inputs["friction_coef"]

        friction_force = normal_force * friction_coef
        torque = friction_force * (diameter / 2.0) / 1000.0  # Convert mm to m

        return {
            "friction_force": friction_force,
            "torque": torque
        }


class PakningsklemModule(ModuleBase):
    """Gasket clamping force calculation"""

    @classmethod
    def get_module_name(cls) -> str:
        return "Pakningsklem"

    @classmethod
    def get_input_parameters(cls) -> List[Parameter]:
        return [
            Parameter("bolt_force", "Bolt Force", "N", "Force from bolt", float, 1000.0),
            Parameter("gasket_area", "Gasket Area", "mm²", "Effective gasket area", float, 100.0),
            Parameter("num_bolts", "Number of Bolts", "", "Number of bolts", int, 4)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[Parameter]:
        return [
            Parameter("total_clamping", "Total Clamping Force", "N", "Total clamping force", float),
            Parameter("gasket_pressure", "Gasket Pressure", "MPa", "Pressure on gasket", float)
        ]

    def calculate(self) -> Dict[str, Any]:
        bolt_force = self.inputs["bolt_force"]
        gasket_area = self.inputs["gasket_area"]
        num_bolts = self.inputs["num_bolts"]

        total_clamping = bolt_force * num_bolts
        gasket_pressure = total_clamping / gasket_area  # N/mm² = MPa

        return {
            "total_clamping": total_clamping,
            "gasket_pressure": gasket_pressure
        }


class KnekkingModule(ModuleBase):
    """Buckling calculation for tension rod"""

    @classmethod
    def get_module_name(cls) -> str:
        return "Knekking av Opptrekkstang"

    @classmethod
    def get_input_parameters(cls) -> List[Parameter]:
        return [
            Parameter("length", "Length", "mm", "Rod length", float, 1000.0),
            Parameter("diameter", "Diameter", "mm", "Rod diameter", float, 20.0),
            Parameter("elastic_modulus", "E-modulus", "GPa", "Elastic modulus", float, 200.0),
            Parameter("applied_force", "Applied Force", "N", "Applied compressive force", float, 500.0)
        ]

    @classmethod
    def get_output_parameters(cls) -> List[Parameter]:
        return [
            Parameter("critical_load", "Critical Load", "N", "Euler buckling load", float),
            Parameter("safety_factor", "Safety Factor", "", "Safety factor against buckling", float),
            Parameter("status", "Status", "", "Pass/Fail status", str)
        ]

    def calculate(self) -> Dict[str, Any]:
        length = self.inputs["length"]  # mm
        diameter = self.inputs["diameter"]  # mm
        E = self.inputs["elastic_modulus"] * 1000  # Convert GPa to MPa
        applied_force = self.inputs["applied_force"]  # N

        # Calculate moment of inertia (mm^4)
        I = math.pi * (diameter ** 4) / 64

        # Euler buckling load for pinned-pinned column (N)
        # P_cr = π²EI / L²
        critical_load = (math.pi ** 2) * E * I / (length ** 2)

        # Safety factor
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


# Registry of all available modules
AVAILABLE_MODULES = [
    InputModule,
    FriksjonskrefterModule,
    PakningsklemModule,
    KnekkingModule
]