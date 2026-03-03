from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit


class ResultsPanel(QWidget):
    """Panel for displaying calculation results"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Results")
        title.setStyleSheet("font-weight: bold; font-size: 12pt;")
        layout.addWidget(title)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        layout.addWidget(self.results_text)

    def show_results(self, results):
        """Display calculation results"""
        self.results_text.setPlainText(str(results))