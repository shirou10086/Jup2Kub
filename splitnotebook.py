import ast
import nbformat
import os
import subprocess
import sys
import shutil
import glob

def is_standard_library(module_name):
    import sys
    return module_name in sys.stdlib_module_names

def extract_imports_from_code_python(code):
    tree = ast.parse(code)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update([name.name.split('.')[0] for name in node.names])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def extract_imports_from_code_r(code):
    imports = set()
    lines = code.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('library('):
            imports.add(line.split('library(')[1].split(')')[0].strip().replace("'", "").replace('"', ''))
        elif line.startswith('require('):
            imports.add(line.split('require(')[1].split(')')[0].strip().replace("'", "").replace('"', ''))
    return imports


def save_requirements(dependencies, output_directory):
    # Ensure these libraries are always included
    additional_packages = {'grpcio', 'grpcio-tools', 'protobuf'}
    dependencies.update(additional_packages)

    requirements_content = '\n'.join(dependencies)
    requirements_path = os.path.join(output_directory, 'requirements.txt')
    with open(requirements_path, 'w', encoding='utf-8') as file:
        file.write(requirements_content)
    print(f"Requirements saved to {requirements_path}")

def save_r_packages(packages, output_directory, filename='install_packages.R'):
    requiredpackages = []

    # this is a list of required packages for reticulate
    for pkg in requiredpackages:
        packages.add(pkg)

    path = os.path.join(output_directory, filename)
    with open(path, 'w', encoding='utf-8') as file:
        for pkg in packages:
            file.write(f'install.packages("{pkg}", repos="http://cran.rstudio.com/")\n')
        file.write('''
# set python path
library(reticulate)
use_virtualenv("/root/.virtualenvs/r-reticulate", required = TRUE)
''')
    print(f"Saved R packages installation script to {path}")
def copy_resultshub_files(source_directory, target_directory):
    os.makedirs(target_directory, exist_ok=True)
    for file_path in glob.glob(os.path.join(source_directory, '*')):
        target_file_path = os.path.join(target_directory, os.path.basename(file_path))
        shutil.copy2(file_path, target_file_path)
    print(f"All files from {source_directory} have been copied to {target_directory}")
def process_notebook(notebook_path, output_directory):
    with open(notebook_path, 'r', encoding='utf-8') as file:
        notebook = nbformat.read(file, as_version=4)

    os.makedirs(output_directory, exist_ok=True)

    python_imports = set()
    r_packages = set()
    cell_index = 1

    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and cell['source'].strip():
            is_r_cell = cell['source'].strip().split('\n')[0].startswith('#R')
            file_extension = '.R' if is_r_cell else '.py'
            filename = f"cell{cell_index}{file_extension}"
            cell_path = os.path.join(output_directory, filename)

            with open(cell_path, 'w', encoding='utf-8') as cell_file:
                cell_file.write(cell['source'])

            if is_r_cell:
                r_packages.update(extract_imports_from_code_r(cell['source']))

            else:
                python_imports.update(extract_imports_from_code_python(cell['source']))

            print(f"Saved {filename}")
            cell_index += 1

    save_requirements(python_imports, output_directory)
    save_r_packages(r_packages, output_directory)
    copy_resultshub_files('./resultshub_python_client', output_directory)



# Example usage
notebook_path = './example/Rexample.ipynb'
output_directory = 'execution'
process_notebook(notebook_path, output_directory)
