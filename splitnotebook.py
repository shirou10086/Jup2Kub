import ast
import nbformat
import os
import subprocess
import sys
import shutil
import glob
'''
This file split the notebook and keep track of the imported modules
'''
def extract_imports_from_code(code):
    tree = ast.parse(code)
    top_level_imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                top_level_imports.add(name.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                top_level_imports.add(node.module.split('.')[0])
    return top_level_imports


def is_standard_library(module_name):
    return module_name in sys.stdlib_module_names

def extract_imports_and_files(notebook):
    imports = set()
    files = set()

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell_imports = extract_imports_from_code(cell.source)
            imports.update(cell_imports)

            for line in cell.source.split('\n'):
                if 'open(' in line or 'read_csv(' in line or 'read_excel(' in line:
                    file_path = line.split('(')[1].split(')')[0].replace("'", "").replace('"', '').strip()
                    if os.path.isfile(file_path):
                        files.add(file_path)

    return imports, files

def filter_non_standard_libraries(imports):
    filtered_imports = {imp for imp in imports if not is_standard_library(imp)}
    return filtered_imports

def save_cells_to_files(notebook, output_directory):
    os.makedirs(output_directory, exist_ok=True)

    # starting cell index from 1
    valid_cell_index = 1
    for cell in notebook.cells:
        if cell.cell_type == 'code' and cell.source.strip():  # make sure the code box is unempty
            cell_file_path = os.path.join(output_directory, f"cell{valid_cell_index}.py")
            with open(cell_file_path, 'w', encoding='utf-8') as cell_file:
                cell_file.write(cell.source)  # write scource code
            valid_cell_index += 1  # update the cellindex

    print(f"{valid_cell_index - 1} non-empty code cells have been saved to separate files in '{output_directory}'.")



def save_requirements(dependencies, output_directory):
    # Ensure these libraries are always included
    additional_packages = {'grpcio', 'grpcio-tools', 'protobuf'}
    dependencies.update(additional_packages)

    requirements_content = '\n'.join(dependencies)
    requirements_path = os.path.join(output_directory, 'requirements.txt')
    with open(requirements_path, 'w', encoding='utf-8') as file:
        file.write(requirements_content)
    print(f"Requirements saved to {requirements_path}")

def copy_resultshub_files(source_directory, target_directory):
    os.makedirs(target_directory, exist_ok=True)
    for file_path in glob.glob(os.path.join(source_directory, '*')):
        target_file_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy2(file_path, target_file_path)
    print(f"All files from {source_directory} have been copied to {target_directory}")

def process_notebook(notebook_path, output_directory):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    dependencies, _ = extract_imports_and_files(nb)
    filtered_dependencies = filter_non_standard_libraries(dependencies)
    save_cells_to_files(nb, output_directory)
    save_requirements(filtered_dependencies, output_directory)
    # Assuming resultshub_python_client directory exists and needs copying
    copy_resultshub_files('./resultshub_python_client', output_directory)
