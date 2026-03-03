import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import pytest

from module_registry import registry
from workflow_engine import WorkflowEngine
from node_canvas import CalculationNode
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF

# Only initialize QApplication once for all tests
app = QApplication(sys.argv)

def test_workflow_topological_execution():
    engine = WorkflowEngine()
    
    # 1. Create two identical addition modules in graph
    modA = registry.create_instance("AdditionModule")
    nodeA = CalculationNode(modA, QPointF(0,0))
    nodeA.module.set_input("val1", 10.0)
    nodeA.module.set_input("val2", 5.0) # -> Sum A should be 15.0
    
    modB = registry.create_instance("AdditionModule")
    nodeB = CalculationNode(modB, QPointF(200,0))
    # We will pipe nodeA's output to nodeB's val1
    nodeB.module.set_input("val2", 5.0) # -> Sum B should be 20.0
    
    engine.add_node(nodeA)
    engine.add_node(nodeB)
    
    # Simulate a canvas connection 
    # Create mock connection object
    class MockPort:
        def __init__(self, node, name):
            self.parent_node = node
            self.name = name
            
    class MockConn:
        def __init__(self, nA, portA, nB, portB):
            self.start_port = MockPort(nA, portA)
            self.end_port = MockPort(nB, portB)
            
    # Connect output 'sum' of nodeA to input 'val1' of nodeB
    conn = MockConn(nodeA, "sum", nodeB, "val1")
    engine.add_connection(conn)
    
    # Execute workflow
    results = engine.execute()
    
    # Verify node A executed first and node B received the data
    assert "Addition (1)" in results
    assert "Addition (2)" in results
    
    # node A outputs
    assert results["Addition (1)"]["sum"] == 15.0
    # node B outputs
    assert results["Addition (2)"]["sum"] == 20.0

if __name__ == "__main__":
    test_workflow_topological_execution()
    print("Graph traversal and connection injection logic passes!")
