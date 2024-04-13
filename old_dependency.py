import ast
import os
import json
import re

class VariableTracker(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.global_vars = {}  # Track global variables with their line numbers
        self.local_vars = {}  # Track local variables within functions and loops
        self.used_vars = {}  # Track first use line numbers of all variables
        self.current_scope = self.global_vars  # Start in the global scope

    def visit_FunctionDef(self, node):
        # When entering a function, switch scope to a new local variable dictionary
        previous_scope = self.current_scope
        self.current_scope = {}
        self.generic_visit(node)
        # Update local variables and revert to the previous scope
        self.local_vars.update(self.current_scope)
        self.current_scope = previous_scope

    def visit_For(self, node):
        # Specifically handle the case where variables are defined in for loops
        previous_scope = self.current_scope
        self.current_scope = {}
        # Record the loop variable as a local variable
        if isinstance(node.target, ast.Name):
            self.current_scope[node.target.id] = node.lineno
        self.generic_visit(node)
        # Update local variables and revert to the previous scope
        self.local_vars.update(self.current_scope)
        self.current_scope = previous_scope

    def visit_While(self, node):
        previous_scope = self.current_scope
        self.current_scope = {}
        self.generic_visit(node)
        self.local_vars.update(self.current_scope)
        self.current_scope = previous_scope

    def visit_With(self, node):
        previous_scope = self.current_scope
        self.current_scope = {}
        self.generic_visit(node)
        self.local_vars.update(self.current_scope)
        self.current_scope = previous_scope

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.current_scope[target.id] = node.lineno
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.current_scope[node.target.id] = node.lineno
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load) and node.id not in self.used_vars:
            self.used_vars[node.id] = node.lineno
        self.generic_visit(node)

    def generic_visit(self, node):
        """The generic visit method will ensure any child nodes are visited."""
        ast.NodeVisitor.generic_visit(self, node)

def process_file(filepath, track_list_path):
    if not re.match(r'cell\d+\.py$', os.path.basename(filepath)):
        return

    with open(filepath, 'r') as file:
        lines = file.readlines()

    tree = ast.parse(''.join(lines))
    tracker = VariableTracker()
    tracker.visit(tree)

    cell_number = int(re.search(r'cell(\d+)\.py$', os.path.basename(filepath)).group(1))

    if os.path.exists(track_list_path):
        with open(track_list_path, 'r') as file:
            variable_track_list = json.load(file)
    else:
        variable_track_list = {}

    fetch_statements = []
    for var, used_line in tracker.used_vars.items():
        if var in variable_track_list and variable_track_list[var] < cell_number:
            defined_line = tracker.global_vars.get(var, float('inf'))
            if used_line < defined_line:
                fetch_code = f"{var} = rh.fetchVarResult('{var}', varAncestorCell={variable_track_list[var]}, host='results-hub-service.default.svc.cluster.local')"
                fetch_statements.append(fetch_code)

    # Insert fetch codes at the beginning of the file
    lines.insert(0, "\n".join(fetch_statements) + "\n")

    updated_content = "".join(lines)

    # Generate and append the submission code
    submit_code = "\n# SUBMIT CODE START\n"
    submit_code += f"submission = rh.ResultsHubSubmission(cell_number={cell_number}, host='results-hub-service.default.svc.cluster.local')\n"
    for var in tracker.global_vars:
        submit_code += f"submission.addVar('{var}', locals().get('{var}', None))\n"
    submit_code += "submission.submit()\n"
    submit_code += f"print('Submission Success for cell {cell_number}.')\n"
    submit_code += "# SUBMIT CODE END\n"

    updated_content += submit_code

    with open(filepath, 'w') as file:
        file.write(updated_content)

    # Update the track list for global variables
    for var, line_no in tracker.global_vars.items():
        variable_track_list[var] = cell_number

    with open(track_list_path, 'w') as file:
        json.dump(variable_track_list, file, indent=4)

def add_code_to_all_files(directory, track_list_path):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        process_file(filepath, track_list_path)

if __name__ == "__main__":
    directory = '/path/to/your/cells'
    track_list_path = '/path/to/your/track/list.json'
    add_code_to_all_files(directory, track_list_path)
