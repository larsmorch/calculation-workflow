import sys
from PyQt6.QtWidgets import QApplication
import os
import sys

# add src to path
sys.path.append(os.path.abspath('src'))

from main_window import MainWindow

app = QApplication(sys.argv)
window = MainWindow()

# create excel node
window._create_excel_node(os.path.abspath('test.xlsx'), window.node_canvas.mapToScene(100, 100))
node = window.workflow_engine.nodes[0]

print("BEFORE CALC Outputs:")
for k, port in node.output_ports.items():
    print(k, port.value_display.toPlainText())

# Run calc
window.workflow_engine.execute()

print("AFTER CALC Outputs:")
for k, port in node.output_ports.items():
    print(k, port.value_display.toPlainText())
