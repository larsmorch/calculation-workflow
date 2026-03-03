"""Core definitions for the Calculation Workflow module system"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Type
from abc import ABC, abstractmethod


@dataclass
class InputParameter:
    """Defines an input parameter for a calculation module."""
    name: str
    display_name: str
    type: Type
    units: str = ""
    default_value: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    required: bool = True
    description: str = ""
    decimals: int = 1
    
    def validate(self, value: Any) -> Tuple[bool, str]:
        """Validates a given value against the parameter's constraints."""
        if value is None:
            if self.required:
                return False, f"{self.display_name} is required."
            return True, ""
            
        try:
            # Type casting validation
            val = self.type(value)
        except (ValueError, TypeError):
            return False, f"Invalid type for {self.display_name}. Expected {self.type.__name__}."
            
        if self.type in (int, float):
            if self.min_value is not None and val < self.min_value:
                return False, f"{self.display_name} must be >= {self.min_value}."
            if self.max_value is not None and val > self.max_value:
                return False, f"{self.display_name} must be <= {self.max_value}."
                
        return True, ""


@dataclass
class OutputParameter:
    """Defines an output parameter for a calculation module."""
    name: str
    display_name: str
    type: Type
    units: str = ""
    description: str = ""
    decimals: int = 1


class CalculationModule(ABC):
    """
    Abstract base class for all calculation modules.
    Instances of this class represent a single node in a workflow.
    """
    
    # Metadata properties all subclasses should define
    name: str = "Base Module"
    category: str = "General"
    description: str = "Base calculation module."
    version: str = "1.0.0"
    latex_formula: str = ""

    def __init__(self):
        self.inputs: Dict[str, Any] = {}
        self.outputs: Dict[str, Any] = {}
        self.figure = None
        self._initialize_defaults()

    def _initialize_defaults(self):
        """Sets default values for inputs based on their parameter definitions."""
        for param in self.get_input_parameters():
            if param.default_value is not None:
                self.inputs[param.name] = param.default_value
            else:
                 # Initialize to None to ensure key exists
                self.inputs[param.name] = None
                
    @classmethod
    @abstractmethod
    def get_input_parameters(cls) -> List[InputParameter]:
        """Returns the list of input parameters this module requires."""
        pass

    @classmethod
    @abstractmethod
    def get_output_parameters(cls) -> List[OutputParameter]:
        """Returns the list of output parameters this module produces."""
        pass

    @abstractmethod
    def calculate(self) -> Dict[str, Any]:
        """
        Performs the core calculation using self.inputs.
        Returns a dictionary mapping output parameter names to their computed values.
        """
        pass

    def validate(self) -> Tuple[bool, List[str]]:
        """
        Validates the current input state.
        Can be overridden in subclasses for multi-variable dependent validation.
        """
        errors = []
        for param in self.get_input_parameters():
            is_valid, err_msg = param.validate(self.inputs.get(param.name))
            if not is_valid:
                errors.append(err_msg)
                
        return len(errors) == 0, errors

    def execute(self) -> bool:
        """
        Executes the calculation. Runs validation first.
        Returns True if successful, False otherwise.
        """
        is_valid, errors = self.validate()
        if not is_valid:
            print(f"Validation Error in {self.name}:")
            for err in errors:
                print(f" - {err}")
            return False
            
        try:
            output_results = self.calculate()
            self.outputs = output_results
            return True
        except Exception as e:
            print(f"Execution Error in {self.name}: {str(e)}")
            return False

    def set_input(self, name: str, value: Any):
        """Sets an input value safely."""
        self.inputs[name] = value

    def get_output(self, name: str) -> Any:
        """Gets a calculated output value."""
        return self.outputs.get(name)

    @classmethod
    def get_module_type_id(cls) -> str:
        """Returns a unique identifier string for the class type."""
        return cls.__name__
