"""Graphical representation of calculation nodes"""
from PyQt6.QtWidgets import (QGraphicsItem, QGraphicsTextItem,
                             QGraphicsEllipseItem, QGraphicsPathItem)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QPainterPath, QFont
from typing import Dict, List, TYPE_CHECKING
from module_base import ModuleBase

if TYPE_CHECKING:
    from workflow_engine import ModuleInstance

def get_dynamic_node_width(name_text: str) -> int:
    """Calculate dynamic node width based on text length with a minimum of 300."""
    # Approx 8 pixels per character plus padding
    text_width = len(name_text) * 8 + 40
    return int(max(300, text_width))

class PortGraphicsItem(QGraphicsEllipseItem):
    """Visual representation of an input or output port"""

    def __init__(self, parent, is_input: bool, param_name: str, display_name: str, index: int):
        super().__init__(-5, -5, 10, 10, parent)
        self.is_input = is_input
        self.param_name = param_name
        self.display_name = display_name
        self.index = index

        self.setBrush(QBrush(QColor(100, 200, 100)))
        self.setPen(QPen(QColor(50, 100, 50), 2))
        self.setAcceptHoverEvents(True)

        # Store reference to parent node
        self.node = parent

    def hoverEnterEvent(self, event):
        self.setBrush(QBrush(QColor(150, 255, 150)))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setBrush(QBrush(QColor(100, 200, 100)))
        super().hoverLeaveEvent(event)

    def get_center_scene_pos(self) -> QPointF:
        """Get the center position of this port in scene coordinates"""
        return self.mapToScene(self.boundingRect().center())


class NodeGraphicsItem(QGraphicsItem):
    """Visual representation of a calculation module node"""

    def __init__(self, instance: 'ModuleInstance'):
        super().__init__()
        self.instance = instance
        self.width = get_dynamic_node_width(self.instance.instance_name)
        self.height = 200
        self.title_height = 30

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.input_ports: Dict[str, PortGraphicsItem] = {}
        self.output_ports: Dict[str, PortGraphicsItem] = {}

        self._create_ports()
        self._create_labels()

        # Calculate required height based on ports
        self._adjust_height()

    def _adjust_height(self):
        """Adjust node height based on number of ports"""
        max_ports = max(len(self.input_ports), len(self.output_ports))
        min_height = self.title_height + max_ports * 25 + 20
        self.height = max(self.height, min_height)

    def _create_ports(self):
        """Create input and output port graphics"""
        module_class = self.instance.module_class

        # Create input ports
        for i, param in enumerate(module_class.get_input_parameters()):
            port = PortGraphicsItem(self, True, param.name, param.display_name, i)
            y_pos = self.title_height + 20 + i * 25
            port.setPos(0, y_pos)
            self.input_ports[param.name] = port

        # Create output ports
        for i, param in enumerate(module_class.get_output_parameters()):
            port = PortGraphicsItem(self, False, param.name, param.display_name, i)
            y_pos = self.title_height + 20 + i * 25
            port.setPos(self.width, y_pos)
            self.output_ports[param.name] = port

    def _create_labels(self):
        """Create text labels for ports"""
        font = QFont("Arial", 8)

        # Input labels
        for i, (param_name, port) in enumerate(self.input_ports.items()):
            label = QGraphicsTextItem(port.display_name, self)
            label.setFont(font)
            label.setDefaultTextColor(QColor(50, 50, 50))
            label.setPos(15, port.y() - 8)

        # Output labels
        for i, (param_name, port) in enumerate(self.output_ports.items()):
            label = QGraphicsTextItem(port.display_name, self)
            label.setFont(font)
            label.setDefaultTextColor(QColor(50, 50, 50))
            # Right-align output labels
            label.setPos(self.width - 15 - label.boundingRect().width(), port.y() - 8)

    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter: QPainter, option, widget=None):
        # Draw node background
        if self.isSelected():
            painter.setPen(QPen(QColor(255, 165, 0), 3))
        else:
            painter.setPen(QPen(QColor(50, 50, 50), 2))

        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawRoundedRect(0, 0, self.width, self.height, 5, 5)

        # Draw title bar
        painter.setBrush(QBrush(QColor(70, 130, 180)))
        painter.drawRoundedRect(0, 0, self.width, self.title_height, 5, 5)
        painter.drawRect(0, self.title_height - 5, self.width, 5)

        # Draw title text
        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(QRectF(0, 0, self.width, self.title_height),
                         Qt.AlignmentFlag.AlignCenter,
                         self.instance.instance_name)

    def itemChange(self, change, value):
        # Notify connections when node moves
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update any connections
            if hasattr(self.scene(), 'update_connections'):
                self.scene().update_connections(self.instance.instance_id)

        return super().itemChange(change, value)


class ConnectionGraphicsItem(QGraphicsPathItem):
    """Visual representation of a connection between ports"""

    def __init__(self, source_port: PortGraphicsItem, target_port: PortGraphicsItem):
        super().__init__()
        self.source_port = source_port
        self.target_port = target_port

        self.setPen(QPen(QColor(100, 100, 100), 2))
        self.setZValue(-1)  # Draw behind nodes

        self.update_path()

    def update_path(self):
        """Update the connection path based on port positions"""
        path = QPainterPath()

        start = self.source_port.get_center_scene_pos()
        end = self.target_port.get_center_scene_pos()

        path.moveTo(start)

        # Create smooth curve using cubic bezier
        ctrl_offset = abs(end.x() - start.x()) * 0.5
        ctrl1 = QPointF(start.x() + ctrl_offset, start.y())
        ctrl2 = QPointF(end.x() - ctrl_offset, end.y())

        path.cubicTo(ctrl1, ctrl2, end)

        self.setPath(path)