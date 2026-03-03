import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest
from PyQt6.QtWidgets import QApplication

# Setup QApp for UI testing contexts if needed
# app = QApplication(sys.argv)

from module_registry import registry
from main_window import MainWindow

def test_registry_populated():
    assert len(registry.get_all_modules()) >= 4
    cat = registry.get_modules_by_category()
    assert "Basic Math" in cat

def test_addition_module_calculation():
    addition_class = None
    for m in registry.get_all_modules():
        if m.name == "Addition":
            addition_class = m
            break
            
    assert addition_class is not None
    instance = addition_class()
    instance.set_input("val1", 5.5)
    instance.set_input("val2", 4.5)
    
    assert instance.execute() is True
    assert instance.get_output("sum") == 10.0

if __name__ == "__main__":
    test_registry_populated()
    test_addition_module_calculation()
    print("Core logic tests passed!")
