"""Registry for managing available calculation modules"""

import os
import sys
import importlib.util
from typing import Dict, List, Type
from calculation_module import CalculationModule


class ModuleRegistry:
    """Central registry system to manage all available modules."""

    def __init__(self):
        # Maps module identifying type strings to their classes
        self._registry: Dict[str, Type[CalculationModule]] = {}

    def register(self, module_class: Type[CalculationModule]):
        """Registers a module class."""
        if not issubclass(module_class, CalculationModule):
            raise TypeError("Module must inherit from CalculationModule")
        type_id = module_class.get_module_type_id()
        self._registry[type_id] = module_class

    def get_all_modules(self) -> List[Type[CalculationModule]]:
        """Returns all registered module classes."""
        return list(self._registry.values())
        
    def get_modules_by_category(self) -> Dict[str, List[Type[CalculationModule]]]:
        """Returns modules grouped by their category string."""
        categories = {}
        for mod_class in self._registry.values():
            cat = mod_class.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(mod_class)
        return categories

    def get_by_type_id(self, type_id: str) -> Type[CalculationModule]:
        """Returns a specific module class by its type ID."""
        if type_id not in self._registry:
            raise KeyError(f"Module '{type_id}' is not registered.")
        return self._registry[type_id]

    def create_instance(self, type_id: str) -> CalculationModule:
        """Instantiates and returns a module by its type ID."""
        module_class = self.get_by_type_id(type_id)
        return module_class()

    def discover_builtins(self):
        """Discovers and registers all modules defined in the 'modules' directory."""
        # Find the path to the modules directory relative to this file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        modules_dir = os.path.join(base_dir, "..", "modules")
        
        if not os.path.exists(modules_dir):
            return
            
        # Add root dir to sys.path so modules can import from calculation_module
        if base_dir not in sys.path:
            sys.path.insert(0, base_dir)

        # Iterate through .py files
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                file_path = os.path.join(modules_dir, filename)
                
                # Dynamically load the module
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    mod = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(mod)
                        
                        # Find classes that inherit from CalculationModule
                        for name in dir(mod):
                            obj = getattr(mod, name)
                            if isinstance(obj, type) and issubclass(obj, CalculationModule) and obj is not CalculationModule:
                                self.register(obj)
                    except Exception as e:
                        print(f"Failed to load plugin module {filename}: {e}")

# Create a global default registry instance for the application to share
registry = ModuleRegistry()
registry.discover_builtins()
