# workflow_engine.py
"""
Workflow Engine - Manages execution of module instances in dependency order
"""

from typing import Dict, List, Any, Optional, Tuple
from collections import deque
import uuid


class WorkflowEngine:
    """
    Manages the workflow graph, validates dependencies, and executes modules
    in the correct topological order.
    """

    def __init__(self):
        self.instances = {}  # {instance_id: instance_data}
        self.connections = []  # List of connection dictionaries
        self.results = {}  # {instance_id: {output_name: value}}
        self.execution_order = []  # Calculated topological order

    def add_instance(self, module_type, module_class, position=(0, 0), name=None):
        """
        Add a new module instance to the workflow.

        Args:
            module_type: String identifier for module type (e.g., "Friksjonskrefter")
            module_class: The actual module class to instantiate
            position: (x, y) position on canvas
            name: Display name for instance (auto-generated if None)

        Returns:
            instance_id: Unique identifier for this instance
        """
        instance_id = str(uuid.uuid4())

        # Create instance of the module
        module_instance = module_class()

        # Count existing instances of this type for naming
        if name is None:
            count = sum(1 for inst in self.instances.values()
                        if inst['type'] == module_type)
            name = f"{module_type} #{count + 1}"

        self.instances[instance_id] = {
            'id': instance_id,
            'type': module_type,
            'name': name,
            'module': module_instance,
            'position': position,
            'input_values': {},  # Manual input values
            'input_connections': {}  # {input_name: (source_instance_id, source_output_name)}
        }

        return instance_id

    def remove_instance(self, instance_id):
        """
        Remove a module instance and all its connections.
        """
        if instance_id not in self.instances:
            return False

        # Remove all connections involving this instance
        self.connections = [
            conn for conn in self.connections
            if conn['from_instance'] != instance_id and
               conn['to_instance'] != instance_id
        ]

        # Remove from instances
        del self.instances[instance_id]

        # Clear results
        if instance_id in self.results:
            del self.results[instance_id]

        return True

    def rename_instance(self, instance_id, new_name):
        """
        Rename a module instance.
        """
        if instance_id in self.instances:
            self.instances[instance_id]['name'] = new_name
            return True
        return False

    def add_connection(self, from_instance, from_output, to_instance, to_input):
        """
        Add a connection between two module instances.

        Args:
            from_instance: Source instance ID
            from_output: Name of output parameter
            to_instance: Target instance ID
            to_input: Name of input parameter

        Returns:
            True if connection added, False if invalid
        """
        # Validate instances exist
        if from_instance not in self.instances or to_instance not in self.instances:
            return False

        # Validate output exists in source module
        source_module = self.instances[from_instance]['module']
        if from_output not in [out['name'] for out in source_module.get_outputs()]:
            return False

        # Validate input exists in target module
        target_module = self.instances[to_instance]['module']
        if to_input not in [inp['name'] for inp in target_module.get_inputs()]:
            return False

        # Check if this input already has a connection (only one source per input)
        for conn in self.connections:
            if conn['to_instance'] == to_instance and conn['to_input'] == to_input:
                # Remove old connection
                self.connections.remove(conn)
                break

        # Add connection
        connection = {
            'from_instance': from_instance,
            'from_output': from_output,
            'to_instance': to_instance,
            'to_input': to_input
        }
        self.connections.append(connection)

        # Update input connections mapping
        self.instances[to_instance]['input_connections'][to_input] = (from_instance, from_output)

        return True

    def remove_connection(self, from_instance, from_output, to_instance, to_input):
        """
        Remove a specific connection.
        """
        connection = {
            'from_instance': from_instance,
            'from_output': from_output,
            'to_instance': to_instance,
            'to_input': to_input
        }

        if connection in self.connections:
            self.connections.remove(connection)

            # Update input connections mapping
            if to_input in self.instances[to_instance]['input_connections']:
                del self.instances[to_instance]['input_connections'][to_input]

            return True
        return False

    def set_manual_input(self, instance_id, input_name, value):
        """
        Set a manual input value for an instance.
        """
        if instance_id not in self.instances:
            return False

        self.instances[instance_id]['input_values'][input_name] = value
        return True

    def get_manual_input(self, instance_id, input_name):
        """
        Get a manual input value for an instance.
        """
        if instance_id not in self.instances:
            return None

        return self.instances[instance_id]['input_values'].get(input_name)

    def validate_workflow(self):
        """
        Validate the workflow for:
        - Circular dependencies
        - Missing inputs

        Returns:
            (is_valid, error_messages)
        """
        errors = []

        # Check for circular dependencies using topological sort
        try:
            self._calculate_execution_order()
        except ValueError as e:
            errors.append(f"Circular dependency detected: {str(e)}")
            return False, errors

        # Check that all inputs are satisfied (either connected or have manual value)
        for instance_id, instance_data in self.instances.items():
            module = instance_data['module']

            for input_def in module.get_inputs():
                input_name = input_def['name']

                # Check if input is connected or has manual value
                is_connected = input_name in instance_data['input_connections']
                has_manual_value = input_name in instance_data['input_values']
                has_default = 'default' in input_def and input_def['default'] is not None

                if not (is_connected or has_manual_value or has_default):
                    errors.append(
                        f"Instance '{instance_data['name']}': "
                        f"Input '{input_name}' has no value or connection"
                    )

        is_valid = len(errors) == 0
        return is_valid, errors

    def _calculate_execution_order(self):
        """
        Calculate topological order for execution using Kahn's algorithm.

        Returns:
            List of instance_ids in execution order

        Raises:
            ValueError if circular dependency detected
        """
        # Build adjacency list and in-degree count
        graph = {instance_id: [] for instance_id in self.instances}
        in_degree = {instance_id: 0 for instance_id in self.instances}

        for conn in self.connections:
            from_id = conn['from_instance']
            to_id = conn['to_instance']
            graph[from_id].append(to_id)
            in_degree[to_id] += 1

        # Kahn's algorithm
        queue = deque([node for node, degree in in_degree.items() if degree == 0])
        execution_order = []

        while queue:
            current = queue.popleft()
            execution_order.append(current)

            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if all nodes were processed (if not, there's a cycle)
        if len(execution_order) != len(self.instances):
            raise ValueError("Circular dependency detected in workflow")

        self.execution_order = execution_order
        return execution_order

    def execute_workflow(self):
        """
        Execute all modules in the workflow in dependency order.

        Returns:
            (success, results_dict, error_messages)
        """
        # Validate workflow first
        is_valid, errors = self.validate_workflow()
        if not is_valid:
            return False, {}, errors

        # Clear previous results
        self.results = {}
        errors = []

        # Execute in topological order
        for instance_id in self.execution_order:
            instance_data = self.instances[instance_id]
            module = instance_data['module']

            try:
                # Gather inputs for this module
                input_values = {}

                for input_def in module.get_inputs():
                    input_name = input_def['name']

                    # Check if connected
                    if input_name in instance_data['input_connections']:
                        source_id, source_output = instance_data['input_connections'][input_name]

                        # Get value from source module's results
                        if source_id in self.results and source_output in self.results[source_id]:
                            input_values[input_name] = self.results[source_id][source_output]
                        else:
                            raise ValueError(
                                f"Source module output '{source_output}' not available"
                            )

                    # Check if manual value set
                    elif input_name in instance_data['input_values']:
                        input_values[input_name] = instance_data['input_values'][input_name]

                    # Use default value
                    elif 'default' in input_def and input_def['default'] is not None:
                        input_values[input_name] = input_def['default']

                    else:
                        raise ValueError(f"No value for required input '{input_name}'")

                # Execute module calculation
                outputs = module.calculate(input_values)

                # Store results
                self.results[instance_id] = outputs

            except Exception as e:
                error_msg = f"Error in '{instance_data['name']}': {str(e)}"
                errors.append(error_msg)
                return False, self.results, errors

        return True, self.results, []

    def get_instance_data(self, instance_id):
        """
        Get all data for a specific instance.
        """
        return self.instances.get(instance_id)

    def get_instance_result(self, instance_id):
        """
        Get calculation results for a specific instance.
        """
        return self.results.get(instance_id, {})

    def get_all_instances(self):
        """
        Get all instances in the workflow.
        """
        return self.instances

    def get_all_connections(self):
        """
        Get all connections in the workflow.
        """
        return self.connections

    def clear_workflow(self):
        """
        Clear all instances and connections.
        """
        self.instances = {}
        self.connections = []
        self.results = {}
        self.execution_order = []

    def get_connections_for_instance(self, instance_id):
        """
        Get all connections (incoming and outgoing) for an instance.

        Returns:
            (incoming_connections, outgoing_connections)
        """
        incoming = [conn for conn in self.connections
                    if conn['to_instance'] == instance_id]
        outgoing = [conn for conn in self.connections
                    if conn['from_instance'] == instance_id]

        return incoming, outgoing

    def to_dict(self):
        """
        Serialize workflow to dictionary for saving.
        """
        instances_data = {}
        for inst_id, inst_data in self.instances.items():
            instances_data[inst_id] = {
                'type': inst_data['type'],
                'name': inst_data['name'],
                'position': inst_data['position'],
                'input_values': inst_data['input_values']
            }

        return {
            'instances': instances_data,
            'connections': self.connections
        }

    def from_dict(self, data, module_registry):
        """
        Load workflow from dictionary.

        Args:
            data: Dictionary containing workflow data
            module_registry: Dictionary mapping module types to module classes
        """
        self.clear_workflow()

        # Recreate instances
        for inst_id, inst_data in data['instances'].items():
            module_type = inst_data['type']

            if module_type not in module_registry:
                raise ValueError(f"Unknown module type: {module_type}")

            module_class = module_registry[module_type]
            module_instance = module_class()

            self.instances[inst_id] = {
                'id': inst_id,
                'type': module_type,
                'name': inst_data['name'],
                'module': module_instance,
                'position': tuple(inst_data['position']),
                'input_values': inst_data['input_values'],
                'input_connections': {}
            }

        # Recreate connections
        for conn in data['connections']:
            self.add_connection(
                conn['from_instance'],
                conn['from_output'],
                conn['to_instance'],
                conn['to_input']
            )


class ExecutionLogger:
    """
    Optional: Logger to track execution flow for debugging.
    """

    def __init__(self):
        self.log = []

    def add_entry(self, instance_name, status, message=""):
        """
        Add a log entry.
        """
        entry = {
            'instance': instance_name,
            'status': status,  # 'started', 'completed', 'error'
            'message': message
        }
        self.log.append(entry)

    def get_log(self):
        """
        Get full execution log.
        """
        return self.log

    def clear(self):
        """
        Clear the log.
        """
        self.log = []

    def print_log(self):
        """
        Print log to console.
        """
        for entry in self.log:
            print(f"[{entry['status'].upper()}] {entry['instance']}: {entry['message']}")