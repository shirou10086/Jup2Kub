import ast
import os
import json
import re

# This file contains the functions for Variable Dependency Analysis and Codegen into Cells
def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)
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

def gen_code_to_cell(filepath, track_list_path, all_relations_path, ancestor_track_path, waitForList):
    if not re.match(r'cell\d+\.py$', os.path.basename(filepath)):
        return

    with open(filepath, 'r') as file:
        lines = file.readlines()

    lines.insert(0, "import ResultsHub as rh\n")

    # Fetching variable code
    tree = ast.parse(''.join(lines))
    tracker = VariableTracker()
    tracker.visit(tree)

    cell_number = int(re.search(r'cell(\d+)\.py$', os.path.basename(filepath)).group(1))

    # Read and update variable track list
    if os.path.exists(track_list_path):
        with open(track_list_path, 'r') as file:
            variable_track_list = json.load(file)
    else:
        variable_track_list = {}

    # Read and update all-relation data (currently used for stream processing scheduling)
    if os.path.exists(all_relations_path):
        with open(all_relations_path, 'r') as file:
            all_relations = json.load(file)
    else:
        all_relations = {}

    if os.path.exists(ancestor_track_path):
        with open(ancestor_track_path, 'r') as file:
            ancestor_track = json.load(file)
    else:
        ancestor_track = {}
    current_cell_ancstors = []

    # Prepare all-rel update for current cell
    current_cell_allrel = all_relations.get(str(cell_number), {})

    fetch_and_wait_statements = []
    for var, used_line in tracker.used_vars.items():
        if var in variable_track_list and variable_track_list[var] < cell_number:
            defined_line = tracker.global_vars.get(var, float('inf'))
            if used_line < defined_line:
                fetch_code = f"{var} = rh.fetchVarResult('{var}', varAncestorCell={variable_track_list[var]}, host='results-hub-service.default.svc.cluster.local')"
                fetch_and_wait_statements.append(fetch_code)
                # Update all-rel data for variable usage across cells
                all_relations[str(variable_track_list[var])][var].append(str(cell_number))
                current_cell_ancstors.append(variable_track_list[var])

    # Update all-rel for current cell's variables
    for var in tracker.global_vars:
        if var in current_cell_allrel:
            current_cell_allrel[var].append(str(cell_number))
        else:
            current_cell_allrel[var] = [str(cell_number)]
    all_relations[str(cell_number)] = current_cell_allrel

    # Add waiting for cell code according to the waitForList
    for waitFor in waitForList:
        fetch_and_wait_statements.append(f"rh.waitForCell(waitFor={waitFor}, host='results-hub-service.default.svc.cluster.local')")

    # Insert fetch & wait code at the beginning of the file
    import_index = next((i for i, line in enumerate(lines) if "import ResultsHub as rh" in line), 0)
    lines.insert(import_index + 1, "\n".join(fetch_and_wait_statements) + "\n")

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

    # Save the updated variable track list
    for var, line_no in tracker.global_vars.items():
        variable_track_list[var] = cell_number

    with open(track_list_path, 'w') as file:
        json.dump(variable_track_list, file, indent=4)

    # Save the updated all-rel data
    with open(all_relations_path, 'w') as file:
        json.dump(all_relations, file, indent=4)
    
    ancestor_track[str(cell_number)] = current_cell_ancstors
    with open(ancestor_track_path, 'w') as file:
        json.dump(ancestor_track, file, indent=4)

def gen_code_to_all_cells(directory, track_list_path, conflict_list_path, all_relations_path, ancestor_track_path):
    # read the conflict list file
    with open(os.path.join(conflict_list_path)) as f:
        all_conflicts = json.load(f)
    
    j2k_config = load_config('J2K_CONFIG.json')
    # SPECIAL HANDLING FOR STREAM PROCESSING
    skip_cell1 = False
    if 'streamProcessing' in j2k_config:
        recursive_vars = j2k_config['streamProcessing']['recursiveVars']
        initial_track_list = {var: 1 for var in recursive_vars}
        with open(track_list_path, 'w') as f:
            json.dump(initial_track_list, f, indent=4)
        inital_all_rels = {"1": {var: [] for var in recursive_vars}}
        with open(all_relations_path, 'w') as f:
            json.dump(inital_all_rels, f, indent=4)
        skip_cell1 = True

    for filename in os.listdir(directory):
        if filename.startswith('cell'):
            cell_num = int(filename[len('cell'):].split('.')[0])
            if skip_cell1 and cell_num == 1:
                continue
            filepath = os.path.join(directory, filename)
            gen_code_to_cell(filepath, track_list_path, all_relations_path, ancestor_track_path, all_conflicts[f"{cell_num}"])

# if __name__ == "__main__":
#     directory = '/path/to/your/cells'
#     track_list_path = '/path/to/your/track/list.json'
#     all_relations_path = '/path/to/your/byproduct.json'
#     gen_code_to_all_cells(directory, track_list_path, all_relations_path)
