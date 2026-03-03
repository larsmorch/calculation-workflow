from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPen, QColor, QPainter


class NodeCanvas(QGraphicsView):
    """Canvas for displaying and connecting calculation nodes"""

    node_selected = pyqtSignal(object)  # Emits selected node
    connection_created = pyqtSignal(object, object)  # Emits (from_node, to_node)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Setup view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # Grid background
        self.setBackgroundBrush(QColor(240, 240, 240))

        self.nodes = []
        self.connections = []
        self.temp_connection = None

    def add_node(self, module_type, position=None):
        """Add a new calculation node to the canvas"""
        if position is None:
            position = QPointF(100, 100)

        node = CalculationNode(module_type, position)
        self.nodes.append(node)
        self.scene.addItem(node)
        return node

    def remove_node(self, node):
        """Remove a node and its connections"""
        if node in self.nodes:
            self.nodes.remove(node)
            self.scene.removeItem(node)

    def clear_canvas(self):
        """Remove all nodes and connections"""
        self.scene.clear()
        self.nodes.clear()
        self.connections.clear()


class CalculationNode(QGraphicsItem):
    """Visual representation of a calculation module"""

    def __init__(self, module_type, position):
        super().__init__()
        self.module_type = module_type
        self.setPos(position)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.width = 150
        self.height = 80

    def boundingRect(self):
        from PyQt6.QtCore import QRectF
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget):
        from PyQt6.QtGui import QBrush

        # Draw node box
        if self.isSelected():
            painter.setPen(QPen(QColor(0, 120, 215), 2))
        else:
            painter.setPen(QPen(Qt.GlobalColor.black, 1))

        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

        # Draw module name
        painter.drawText(10, 25, self.module_type)