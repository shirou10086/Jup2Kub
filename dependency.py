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

def process_file(filepath, track_list_path):
    # Match only files that follow the naming convention "cell_<number>.py"
    if not re.match(r'cell_\d+\.py$', os.path.basename(filepath)):
        return
    
    with open(filepath, 'r') as file:
        file_content = file.read()
    
    tree = ast.parse(file_content)
    tracker = VariableTracker()
    tracker.visit(tree)

    cell_number = int(re.search(r'cell_(\d+)\.py$', os.path.basename(filepath)).group(1))

    # Prepare the submission code
    submit_code = "\n# Upload tracked variables to ResultsHub\n"
    submit_code += "import ResultsHub as rh\n"
    submit_code += f"submission = rh.ResultsHubSubmission(cell_number={cell_number}, host='results-hub-service.default.svc.cluster.local')\n"

    for var in tracker.defined_vars:
        if var == 'submission':
            continue 
        submit_code += f"submission.addVar('{var}', locals().get('{var}', None))\n"
    
    submit_code += "submission.submit()\n"
    submit_code += "print(f'Submission Success for cell {cell_number}.')\n"
    
    # Read the variable tracking list
    if os.path.exists(track_list_path):
        with open(track_list_path, 'r') as file:
            variable_track_list = json.load(file)
    else:
        variable_track_list = {}
    
    for var in tracker.defined_vars:
        variable_track_list[var] = cell_number
    
    with open(track_list_path, 'w') as file:
        json.dump(variable_track_list, file)

    # Prepare the fetch code
    fetch_code = ""
    for var, update_cell in variable_track_list.items():
        if update_cell < cell_number:
            fetch_code += f"{var} = rh.fetchVarResult('{var}', varAncestorCell={update_cell}, host='results-hub-service.default.svc.cluster.local')\n"
    
    # Write the updated content back to the file
    updated_content = fetch_code + file_content + submit_code
    with open(filepath, 'w') as file:
        file.write(updated_content)

def add_code_to_all_files(directory, track_list_path):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        process_file(filepath, track_list_path)

directory_path = './example/output'  # Update to your directory path
track_list_path = './variable_track_list.txt'  # Path for variable tracking list
add_code_to_all_files(directory_path, track_list_path)
