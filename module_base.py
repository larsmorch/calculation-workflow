"""Base classes for calculation modules"""
from dataclasses import dataclass
from typing import Any, Dict, List
from abc import ABC, abstractmethod


@dataclass
class Parameter:
    """Defines an input or output parameter"""
    name: str
    display_name: str
    unit: str = ""
    description: str = ""
    param_type: type = float
    default_value: Any = None


class ModuleBase(ABC):
    """Base class for all calculation modules"""

    def __init__(self):
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Set default values for inputs"""
        for param in self.get_input_parameters():
            if param.default_value is not None:
                self.inputs[param.name] = param.default_value

    @classmethod
    @abstractmethod
    def get_module_name(cls) -> str:
        """Return the display name of this module"""
        pass

    @classmethod
    @abstractmethod
    def get_input_parameters(cls) -> List[Parameter]:
        """Return list of input parameters"""
        pass

    @classmethod
    @abstractmethod
    def get_output_parameters(cls) -> List[Parameter]:
        """Return list of output parameters"""
        pass

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Perform the calculation using self.inputs
        Returns dictionary of outputs
        """
        pass

    def execute(self) -> bool:
        """
        Execute the module calculation
        Returns True if successful, False otherwise
        """
        try:
            # Validate all required inputs are present
            for param in self.get_input_parameters():
                if param.name not in self.inputs:
                    raise ValueError(f"Missing required input: {param.display_name}")

            # Perform calculation
            self.outputs = self.calculate()
            return True
        except Exception as e:
            print(f"Error executing {self.get_module_name()}: {str(e)}")
            return False

    def set_input(self, name: str, value: Any):
        """Set an input value"""
        self.inputs[name] = value

    def get_output(self, name: str) -> Any:
        """Get an output value"""
        return self.outputs.get(name)