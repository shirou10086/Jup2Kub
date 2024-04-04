import ast
import os
import json
import re

class VariableTracker(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.defined_vars = set()

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.defined_vars.add(node.target.id)
        self.generic_visit(node)

    def visit_For(self, node):
        if isinstance(node.target, ast.Name):
            self.defined_vars.add(node.target.id)
        self.generic_visit(node)

class VariableUsageFinder(ast.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.used_vars = {}  # Changed to dictionary to track line numbers

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):  # Only consider variables that are being loaded (used)
            if node.id not in self.used_vars:
                self.used_vars[node.id] = node.lineno
        self.generic_visit(node)


def process_file(filepath, track_list_path):
    if not re.match(r'cell\d+\.py$', os.path.basename(filepath)):
        return

    with open(filepath, 'r') as file:
        lines = file.readlines()

    tree = ast.parse(''.join(lines))
    tracker = VariableTracker()
    tracker.visit(tree)
    usage_finder = VariableUsageFinder()
    usage_finder.visit(tree)
    if not any("import ResultsHub as rh" in line for line in lines):
        lines.insert(0, "import ResultsHub as rh\n")
    cell_number = int(re.search(r'cell(\d+)\.py$', os.path.basename(filepath)).group(1))

    if os.path.exists(track_list_path):
        with open(track_list_path, 'r') as file:
            variable_track_list = json.load(file)
    else:
        variable_track_list = {}

    # Preparing to insert fetch code directly before the line where the variable is first used
    insertions = []
    for var, line_no in usage_finder.used_vars.items():
        if var in variable_track_list and variable_track_list[var] < cell_number:
            fetch_code = f"{var} = rh.fetchVarResult('{var}', varAncestorCell={variable_track_list[var]}, host='results-hub-service.default.svc.cluster.local')"
            # Adjusting line number to Python's 0-based indexing
            insertions.append((line_no - 1, fetch_code))

    # Insert fetch codes in reverse order to not mess up the line numbers
    for line_no, fetch_code in sorted(insertions, reverse=True):
        lines.insert(line_no, fetch_code + "\n")

    updated_content = "".join(lines)

    submit_code = "\n# SUBMIT CODE START\n"
    submit_code += f"submission = rh.ResultsHubSubmission(cell_number={cell_number}, host='results-hub-service.default.svc.cluster.local')\n"
    for var in tracker.defined_vars:
        submit_code += f"submission.addVar('{var}', locals().get('{var}', None))\n"
    submit_code += "submission.submit()\n"
    submit_code += f"print('Submission Success for cell {cell_number}.')\n"
    submit_code += "# SUBMIT CODE END\n"

    updated_content += submit_code

    with open(filepath, 'w') as file:
        file.write(updated_content)

    # Update the variable track list only for defined variables
    for var in tracker.defined_vars:
        variable_track_list[var] = cell_number

    with open(track_list_path, 'w') as file:
        json.dump(variable_track_list, file, indent=4)

def add_code_to_all_files(directory, track_list_path):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        process_file(filepath, track_list_path)
