from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsPathItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsProxyWidget, QDoubleSpinBox, QSpinBox, QLineEdit
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPen, QColor, QPainter, QPainterPath, QBrush

from module_registry import registry
from node_graphics import get_dynamic_node_width, get_dynamic_node_height

class NodeCanvas(QGraphicsView):
    """Canvas for displaying and connecting calculation nodes"""

    node_selected = pyqtSignal(object)  # Emits selected node
    connection_created = pyqtSignal(object, object)  # Emits (from_node, to_node)
    node_deleted = pyqtSignal(object) # Flow deletion sync
    connection_deleted = pyqtSignal(object) 
    calculation_requested = pyqtSignal()  # Live auto calc trigger

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # Setup view properties
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)

        # Grid background
        self.setBackgroundBrush(QColor(240, 240, 240))

        self.nodes = []
        self.connections = []
        self.temp_connection = None

    def add_node(self, type_id, position=None):
        """Add a new calculation node to the canvas using a module type ID"""
        if position is None:
            position = QPointF(100, 100)
            
        try:
            # Instantiate the actual calculation module class
            module_instance = registry.create_instance(type_id)
        except KeyError:
            print(f"Error: Module type {type_id} not found in registry")
            return None

        node = CalculationNode(module_instance, position)
        self.nodes.append(node)
        self.scene.addItem(node)
        return node

    def remove_node(self, node):
        """Remove a node and its connections"""
        if node in self.nodes:
            for port in list(node.input_ports.values()) + list(node.output_ports.values()):
                for conn in list(port.connections):
                    self.remove_connection(conn)
            self.nodes.remove(node)
            self.scene.removeItem(node)
            self.node_deleted.emit(node)
            self.calculation_requested.emit()

    def clear_canvas(self):
        """Remove all nodes and connections"""
        self.scene.clear()
        self.nodes.clear()
        self.connections.clear()
        self.temp_connection = None

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            items = list(self.scene.selectedItems())
            for item in items:
                if isinstance(item, CalculationNode):
                    self.remove_node(item)
                elif isinstance(item, NodeConnection):
                    self.remove_connection(item)
        super().keyPressEvent(event)
        
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            scale_factor = 1.15
        else:
            scale_factor = 1.0 / 1.15
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.scale(scale_factor, scale_factor)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.last_pan_pos = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return

        item = self.itemAt(event.pos())
        if event.button() == Qt.MouseButton.LeftButton:
            if isinstance(item, NodePort):
                # Start drawing a connection
                self.temp_connection = NodeConnection(start_port=item)
                self.scene.addItem(self.temp_connection)
                self.temp_connection.update_path()
                return # Don't pass to super to prevent dragging node
            elif isinstance(item, CalculationNode):
                self.node_selected.emit(item)
        elif event.button() == Qt.MouseButton.RightButton:
            if isinstance(item, NodeConnection):
                self.remove_connection(item)
                return
                
        super().mousePressEvent(event)
        
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.MiddleButton:
            if hasattr(self, 'last_pan_pos'):
                delta = event.pos() - self.last_pan_pos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
                self.last_pan_pos = event.pos()
            return

        if self.temp_connection:
            # Update the end position of the temporary bezier curve
            pos = self.mapToScene(event.pos())
            self.temp_connection.current_end_pos = pos
            self.temp_connection.update_path()
        else:
            super().mouseMoveEvent(event)
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
            if hasattr(self, 'last_pan_pos'):
                del self.last_pan_pos
            return

        if self.temp_connection:
            item = self.itemAt(event.pos())
            if isinstance(item, NodePort) and self.is_valid_connection(self.temp_connection.start_port, item):
                # Finalize connection
                self.temp_connection.end_port = item
                self.temp_connection.update_path()
                
                # Register connection on both ports
                self.temp_connection.start_port.add_connection(self.temp_connection)
                item.add_connection(self.temp_connection)
                
                self.connections.append(self.temp_connection)
                self.connection_created.emit(self.temp_connection.start_port, item)
            else:
                # Cancel connection
                self.scene.removeItem(self.temp_connection)
                
            self.temp_connection = None
        else:
            super().mouseReleaseEvent(event)
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.resetTransform()
            if self.nodes:
                self.centerOn(self.nodes[0])
            return
        super().mouseDoubleClickEvent(event)
            
    def is_valid_connection(self, start_port, end_port):
        """Check if ports can be connected"""
        if start_port == end_port or start_port.parent_node == end_port.parent_node:
            return False
            
        # Must connect output to input, or input to output
        if start_port.is_input == end_port.is_input:
            return False
            
        # Multiple incoming connections to the same input are allowed for summing
        return True
        
    def remove_connection(self, connection):
        if connection in self.connections:
            connection.start_port.remove_connection(connection)
            if connection.end_port:
                connection.end_port.remove_connection(connection)
            self.scene.removeItem(connection)
            self.connections.remove(connection)
            self.connection_deleted.emit(connection)
            self.calculation_requested.emit()


class NodePort(QGraphicsEllipseItem):
    """Visual representation of a connection port"""
    
    def __init__(self, parent_node, param, is_input, index, total_ports):
        # Port geometry
        self.radius = 6
        super().__init__(-self.radius, -self.radius, self.radius*2, self.radius*2, parent=parent_node)
        
        self.parent_node = parent_node
        self.param = param
        self.name = param.name
        self.is_input = is_input
        self.connections = []
        
        # Calculate vertical position based on index to distribute evenly
        y_step = parent_node.height / (total_ports + 1)
        y_pos = y_step * (index + 1)
        
        self.input_widget = None
        self.value_display = None
        
        # UI init pushed here from construct to allow format_value binding
        
        if self.is_input:
            self.setPos(0, y_pos)
            self.setBrush(QBrush(QColor(100, 200, 100))) # Green for input
            
            # Label
            label_text = self.name
            if hasattr(self.param, 'units') and self.param.units:
                label_text += f" [{self.param.units}]"
            label = QGraphicsTextItem(label_text, self)
            label.setPos(self.radius + 2, -10)
            
            # Calculate dynamic offset based on label length constraints
            label_width = label.boundingRect().width()
            widget_offset = self.radius + 4 + label_width
            
            # Inline Input Widget
            self.input_widget = QGraphicsProxyWidget(self)
            
            # Determine correct widget type
            if param.type is float:
                widget = QDoubleSpinBox()
                widget.setRange(param.min_value if param.min_value is not None else -1e9, 
                                param.max_value if param.max_value is not None else 1e9)
                widget.setDecimals(param.decimals)
                widget.setValue(float(param.default_value) if param.default_value is not None else 0.0)
                widget.valueChanged.connect(self._on_input_changed)
                self.parent_node.module.set_input(self.name, widget.value())
            elif param.type is int:
                widget = QSpinBox()
                widget.setRange(int(param.min_value) if param.min_value is not None else -1000000, 
                                int(param.max_value) if param.max_value is not None else 1000000)
                widget.setValue(int(param.default_value) if param.default_value is not None else 0)
                widget.valueChanged.connect(self._on_input_changed)
                self.parent_node.module.set_input(self.name, widget.value())
            else:
                widget = QLineEdit()
                widget.setText(str(param.default_value) if param.default_value is not None else "")
                widget.textChanged.connect(self._on_input_changed)
                self.parent_node.module.set_input(self.name, widget.text())
            
            widget.setFixedWidth(50)
            widget.setStyleSheet("font-size: 9px; padding: 0px;")
            self.input_widget.setWidget(widget)
            
            # Position the inline input box next to label dynamically
            self.input_widget.setPos(widget_offset, -10)
            
            # Value display for when widget is hidden (due to being wired)
            self.value_display = QGraphicsTextItem(self.format_value("--"), self)
            self.value_display.setDefaultTextColor(QColor(50, 50, 50))
            self.value_display.setPos(widget_offset, -10)
            self.value_display.hide()
            
        else:
            self.setPos(parent_node.width, y_pos)
            self.setBrush(QBrush(QColor(100, 100, 200))) # Blue for output
            
            # Label
            label = QGraphicsTextItem(self.name, self)
            label_width = label.boundingRect().width()
            label.setPos(-label_width - self.radius - 2, -10)
            
            # Value display (will be placed to the left of the label based on final length)
            self.value_display = QGraphicsTextItem(self.format_value("--"), self)
            self.value_display.setDefaultTextColor(QColor(50, 50, 50))
            self.value_display.setPos(-label_width - self.radius - 40, -10)
            
        self.setPen(QPen(Qt.GlobalColor.black, 1))
        # Important to catch mouse events for dragging
        self.setAcceptHoverEvents(True)
        
    def format_value(self, val):
        """Standardizes graphical string representations of parameter values, appending its custom unit string if it exists."""
        unit_str = f" {self.param.units}" if hasattr(self.param, 'units') and self.param.units else ""
        if val is None or val == "--":
            return f"= --{unit_str}"
        if isinstance(val, (int, float)):
            decimals = getattr(self.param, 'decimals', 1)
            return f"= {val:.{decimals}f}{unit_str}"
        return f"= {val}{unit_str}"
        
    def add_connection(self, connection):
        self.connections.append(connection)
        if self.is_input:
            if self.input_widget:
                self.input_widget.hide() # Hide manual entry if wired
            if self.value_display:
                self.value_display.show()
                
    def _on_input_changed(self, value):
        """Helper to inject new typed values down into logic engine and fire live redraw queue!"""
        self.parent_node.module.set_input(self.name, value)
        if self.scene() and self.scene().views():
            # Force auto run workflow by emitting to canvas!
            self.scene().views()[0].calculation_requested.emit()
        
    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)
        if self.is_input and not self.connections:
            if self.input_widget:
                self.input_widget.show() # Show manual entry if un-wired
            if self.value_display:
                self.value_display.hide()

    def get_global_pos(self):
        """Return absolute position of port center in scene coordinates"""
        return self.scenePos()


class NodeConnection(QGraphicsPathItem):
    """Bezier curve connecting two ports"""
    
    def __init__(self, start_port, end_port=None):
        super().__init__()
        self.start_port = start_port
        self.end_port = end_port
        
        self.setPen(QPen(QColor(150, 150, 150), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        self.setZValue(-1) # Draw behind nodes
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        
        self.current_end_pos = start_port.get_global_pos() if start_port else QPointF()

    def paint(self, painter, option, widget=None):
        if self.isSelected():
            self.setPen(QPen(QColor(255, 0, 0), 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        else:
            self.setPen(QPen(QColor(150, 150, 150), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        super().paint(painter, option, widget)
        
    def update_path(self):
        """Redraws the bezier curve based on current port positions"""
        if not self.start_port:
            return
            
        start_pos = self.start_port.get_global_pos()
        end_pos = self.end_port.get_global_pos() if self.end_port else self.current_end_pos
        
        # Calculate control points for smooth bezier (extend outward horizontally)
        dist = abs(end_pos.x() - start_pos.x()) * 0.5
        c1 = QPointF(start_pos.x() + dist, start_pos.y())
        c2 = QPointF(end_pos.x() - dist, end_pos.y())
        
        path = QPainterPath(start_pos)
        path.cubicTo(c1, c2, end_pos)
        self.setPath(path)


class CalculationNode(QGraphicsItem):
    """Visual representation of a calculation module"""

    def __init__(self, module_instance, position):
        super().__init__()
        # Store the actual computation instance
        self.module = module_instance
        self.setPos(position)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        # Dynamic sizing based on ports/name
        inputs = self.module.get_input_parameters()
        outputs = self.module.get_output_parameters()
        
        self.width = get_dynamic_node_width(self.module.name)
        self.height = get_dynamic_node_height(len(inputs), len(outputs))
        
        # Visual Ports dicts
        self.input_ports = {}
        self.output_ports = {}
        
        self._create_ports(inputs, outputs)
        
    def _create_ports(self, inputs, outputs):
        # Create input ports
        for i, param in enumerate(inputs):
            port = NodePort(self, param, is_input=True, index=i, total_ports=len(inputs))
            self.input_ports[param.name] = port
            
        # Create output ports
        for i, param in enumerate(outputs):
            port = NodePort(self, param, is_input=False, index=i, total_ports=len(outputs))
            self.output_ports[param.name] = port
            
    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
            # Update all connected paths when node moves
            for port in list(self.input_ports.values()) + list(self.output_ports.values()):
                for conn in port.connections:
                    conn.update_path()
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedHasChanged:
            if value and self.scene() and self.scene().views():
                self.scene().views()[0].node_selected.emit(self)
        return super().itemChange(change, value)

    def update_outputs_display(self, outputs_dict):
        """Updates the visual strings next to output ports after calculation"""
        for param_name, port in self.output_ports.items():
            if param_name in outputs_dict and port.value_display:
                val = outputs_dict[param_name]
                port.value_display.setPlainText(port.format_value(val))
                
                # Re-align dynamically so text pushes left perfectly from label
                label_width = QGraphicsTextItem(port.name).boundingRect().width()
                val_width = port.value_display.boundingRect().width()
                port.value_display.setPos(-label_width - port.radius - 4 - val_width, -10)
                port.value_display.show() # Failsafe force explicit visualization
        
        # Flush Qt redraw cache natively out to GUI
        self.update()

    def update_inputs_display(self):
        """Updates the visual strings next to input ports after variable injection"""
        for param_name, port in self.input_ports.items():
            if port.value_display:
                # Get exact injected value from inner application
                val = self.module.inputs.get(param_name)
                port.value_display.setPlainText(port.format_value(val))

    def boundingRect(self):
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
        painter.drawText(10, 25, self.module.name)
        
    def mouseDoubleClickEvent(self, event):
        """Allow user to rename the module by double clicking the node background"""
        from PyQt6.QtWidgets import QInputDialog, QLineEdit
        from node_graphics import get_dynamic_node_width
        
        new_name, ok = QInputDialog.getText(None, "Rename Node", "New Node Name:", QLineEdit.EchoMode.Normal, self.module.name)
        if ok and new_name.strip():
            self.prepareGeometryChange()
            self.module.name = new_name.strip()
            
            # Recalculate node width
            self.width = get_dynamic_node_width(self.module.name)
            
            # Shift all output ports to match new width border
            for port in self.output_ports.values():
                port.setPos(self.width, port.pos().y())
                
            # Trigger connection line updates
            for port in list(self.input_ports.values()) + list(self.output_ports.values()):
                for conn in port.connections:
                    conn.update_path()
                    
            # Refresh visuals
            self.update()
            
        super().mouseDoubleClickEvent(event)