from PyQt6.QtCore import QObject, pyqtSignal


class WorkflowEngine(QObject):
    """Engine for executing calculation workflows"""

    calculation_complete = pyqtSignal(dict)  # Emits results

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.connections = []

    def add_node(self, node):
        """Add node to workflow"""
        self.nodes.append(node)
        
    def add_connection(self, connection):
        self.connections.append(connection)

    def remove_connection(self, connection):
        if connection in self.connections:
            self.connections.remove(connection)

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)

    def get_execution_order(self):
        """Topological sort based on connections"""
        # Graph adjacency list: node -> list of nodes depending on it
        graph = {node: [] for node in self.nodes}
        # In-degree count: node -> number of dependencies
        in_degree = {node: 0 for node in self.nodes}
        
        for conn in self.connections:
            # start_port is output from upstream, end_port is input to downstream
            upstream_node = conn.start_port.parent_node
            downstream_node = conn.end_port.parent_node
            
            # Ensure both are in our list
            if upstream_node in graph and downstream_node in graph:
                graph[upstream_node].append(downstream_node)
                in_degree[downstream_node] += 1
                
        # Topo sort (Kahn's algorithm)
        queue = [node for node in self.nodes if in_degree[node] == 0]
        sorted_nodes = []
        
        while queue:
            node = queue.pop(0)
            sorted_nodes.append(node)
            for dependent in graph[node]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
                    
        # If lengths don't match, we have a cycle, but we'll execute what we can
        return sorted_nodes

    def execute(self):
        """Execute the workflow resolving data flows per node"""
        results = {}
        
        # Determine strict order
        execution_order = self.get_execution_order()
        
        for i, node in enumerate(execution_order):
            # First, resolve variable injection for this node based on upstream wires
            injections = {}
            for conn in self.connections:
                if conn.end_port.parent_node == node:
                    upstream_node = conn.start_port.parent_node
                    output_name = conn.start_port.name
                    input_name = conn.end_port.name
                    
                    # Fetch calculated output from upstream module
                    val = upstream_node.module.get_output(output_name)
                    if val is not None:
                        if input_name not in injections:
                            injections[input_name] = []
                        injections[input_name].append(val)
            
            # Sum up connections combining into single inputs
            for input_name, values in injections.items():
                if len(values) == 1:
                    node.module.set_input(input_name, values[0])
                else:
                    try:
                        node.module.set_input(input_name, sum(values))
                    except Exception as e:
                        print(f"Failed to sum combined inputs for {input_name}: {e}")
                        node.module.set_input(input_name, values[0])

            # Natively instruct visual nodes to update their front-end labels
            if hasattr(node, 'update_inputs_display'):
                node.update_inputs_display()

            # Execute the attached calculation module natively
            success = node.module.execute()
            
            node_id = f"{node.module.name} ({i+1})"
            if success:
                results[node_id] = node.module.outputs
                node.update_outputs_display(results[node_id])
            else:
                results[node_id] = {"Error": "Calculation failed (check required inputs/validation)."}

        # Send a formatted dictionary straight back to the MainWindow logger
        self.calculation_complete.emit(results)
        return results