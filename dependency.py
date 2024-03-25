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
    # 匹配只遵循 "cell_<number>.py" 命名约定的文件
    if not re.match(r'cell-\d+\.py$', os.path.basename(filepath)):
        return

    with open(filepath, 'r') as file:
        file_content = file.read()

    tree = ast.parse(file_content)
    tracker = VariableTracker()
    tracker.visit(tree)
    cell_number = int(re.search(r'cell-(\d+)\.py$', os.path.basename(filepath)).group(1))

    # 准备提交代码
    submit_code = "\n# SUBMIT CODE START\n"
    submit_code += f"submission = rh.ResultsHubSubmission(cell_number={cell_number}, host='results-hub-service.default.svc.cluster.local')\n"
    for var in tracker.defined_vars:
        if var == 'submission':
            continue
        submit_code += f"submission.addVar('{var}', locals().get('{var}', None))\n"
    submit_code += "submission.submit()\n"
    submit_code += f"print('Submission Success for cell {cell_number}.')\n"
    submit_code += "# SUBMIT CODE END\n"

    # 读取变量跟踪列表
    if os.path.exists(track_list_path):
        with open(track_list_path, 'r') as file:
            variable_track_list = json.load(file)
    else:
        variable_track_list = {}

    # 准备获取代码
    fetch_code = "# FETCH CODE START\n"
    fetch_code +="import ResultsHub as rh"
    for var, update_cell in variable_track_list.items():
        if update_cell < cell_number:
            fetch_code += f"{var} = rh.fetchVarResult('{var}', varAncestorCell={update_cell}, host='results-hub-service.default.svc.cluster.local')\n"
    fetch_code += "# FETCH CODE END\n"

    # 更新变量跟踪列表
    for var in tracker.defined_vars:
        variable_track_list[var] = cell_number

    with open(track_list_path, 'w') as file:
        json.dump(variable_track_list, file, indent=4)

    # 将更新后的内容写回文件
    # 查找并替换或添加提交和获取代码段
    pattern_submit = re.compile(r"# SUBMIT CODE START.*?# SUBMIT CODE END", re.DOTALL)
    pattern_fetch = re.compile(r"# FETCH CODE START.*?# FETCH CODE END", re.DOTALL)
    if pattern_submit.search(file_content) and pattern_fetch.search(file_content):
        updated_content = pattern_submit.sub(submit_code, file_content)
        updated_content = pattern_fetch.sub(fetch_code, updated_content)
    else:
        updated_content = fetch_code + "\n" + file_content + "\n" + submit_code

    with open(filepath, 'w') as file:
        file.write(updated_content)


def add_code_to_all_files(directory, track_list_path):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        process_file(filepath, track_list_path)
