import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from PyQt6.QtWidgets import QApplication
from main_window import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())