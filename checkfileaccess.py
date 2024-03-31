import ast
import os
from typing import Set

def collect_called_functions_from_file(filename: str) -> Set[str]:
    """
    Parses a Python file and collects names of all functions called within it.
    """
    class FunctionCallCollector(ast.NodeVisitor):
        def __init__(self):
            super().__init__()
            self.called_functions = set()

        def visit_Call(self, node: ast.Call):
            if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                self.called_functions.add(f"{node.func.value.id}.{node.func.attr}")
            elif isinstance(node.func, ast.Attribute):
                self.called_functions.add(node.func.attr)
            elif isinstance(node.func, ast.Name):
                self.called_functions.add(node.func.id)
            self.generic_visit(node)

    with open(filename, 'r', encoding='utf-8') as file:
        source_code = file.read()

    parsed_ast = ast.parse(source_code)
    collector = FunctionCallCollector()
    collector.visit(parsed_ast)
    return collector.called_functions

def checks_file_access(called_functions: Set[str]) -> bool:
    """
    Checks if any of the called functions are related to file access operations.
    """
    file_operations = {
        'open', 'read', 'write', 'readline', 'readlines',
        'os.remove', 'os.unlink', 'os.rename', 'os.renames', 'os.mkdir', 'os.makedirs', 'os.rmdir', 'os.removedirs',
        'shutil.copy', 'shutil.copy2', 'shutil.copyfile', 'shutil.copytree', 'shutil.move', 'shutil.rmtree',
        'pandas.read_csv', 'pandas.to_csv', 'pandas.read_excel', 'pandas.to_excel',
        'numpy.load', 'numpy.save', 'numpy.savetxt', 'json.load', 'json.dump',
        'csv.reader', 'csv.writer', 'pickle.load', 'pickle.dump', 'yaml.load', 'yaml.dump',
        'xml.etree.ElementTree.parse', 'xml.etree.ElementTree.ElementTree.write',
    }

    return any(func in called_functions for func in file_operations)

def check_file_for_access(file_path: str) -> bool:
    """
    Checks the specified Python file to see if it performs any file access operations.
    Returns True if file access is detected, else False.
    """
    if os.path.exists(file_path):
        called_functions = collect_called_functions_from_file(file_path)
        if checks_file_access(called_functions):
            return True  # File access detected, return True

    return False  # No file access detected, return False
