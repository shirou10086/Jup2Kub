import ast
import nbformat
import os
import subprocess
import sys
import shutil
import glob
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


def is_standard_library(module_name):
    return module_name in sys.stdlib_module_names

def filter_non_standard_libraries(imports):
    filtered_imports = {imp for imp in imports if not is_standard_library(imp)}
    return filtered_imports

def save_cells_to_files(notebook, output_directory, all_python_imports, all_r_libraries):
    #This function checks both library and imports from R and python and added in the files
    os.makedirs(output_directory, exist_ok=True)

    valid_cell_index = 1
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code' and cell['source'].strip():
            is_r_cell = cell['source'].strip().split('\n')[0].startswith('#R')
            file_extension = '.R' if is_r_cell else '.py'
            cell_file_path = os.path.join(output_directory, f"cell{valid_cell_index}{file_extension}")

            # Prepare the cell content
            cell_content = cell['source']
            if is_r_cell:
                # Add missing R libraries
                existing_libraries = {line.split('library(')[1].split(')')[0].strip().replace("'", "").replace('"', '')
                                      for line in cell['source'].split('\n') if line.startswith('library(')}
                libraries_to_add = [lib for lib in all_r_libraries if lib not in existing_libraries]
                if libraries_to_add:
                    # Prepend the missing libraries to the cell content
                    cell_content = '\n'.join(f'library({lib})' for lib in libraries_to_add) + '\n\n' + cell_content
            else:
                # Add missing Python imports
                imports_to_add = [imp for imp in all_python_imports if imp not in cell['source']]
                if imports_to_add:
                    cell_content = '\n'.join(imports_to_add) + '\n\n' + cell_content

            with open(cell_file_path, 'w', encoding='utf-8') as cell_file:
                cell_file.write(cell_content)

            valid_cell_index += 1
            print(f"Saved {cell_file_path}")


def extract_full_import_statements_python(code):
    """
    Extracts and returns a set of full import statements from a given piece of code.
    """
    tree = ast.parse(code)
    import_statements = set()

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            # Convert the node back to a string of code
            import_statements.add(ast.unparse(node))

    return import_statements

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



def save_r_packages(packages, output_directory, filename='install_packages.R'):
    requiredpackages = []

    # this is a list of required packages for reticulate
    for pkg in requiredpackages:
        packages.add(pkg)

    path = os.path.join(output_directory, filename)
    with open(path, 'w', encoding='utf-8') as file:
        for pkg in packages:
            file.write(f'install.packages("{pkg}", repos="http://cran.rstudio.com/")\n')
    print(f"Saved R packages installation script to {path}")


def process_notebook(notebook_path, output_directory):
    with open(notebook_path, 'r', encoding='utf-8') as file:
        notebook = nbformat.read(file, as_version=4)

    os.makedirs(output_directory, exist_ok=True)

    r_packages = set()
    cell_index = 1
    imports_statements_py = set()
    imports_names_py = set()

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
                cell_imports_statements = extract_full_import_statements_python(cell.source)
                imports_statements_py.update(cell_imports_statements)

                cell_imports_names = extract_imports_from_code_python(cell.source)
                imports_names_py.update(cell_imports_names)

            print(f"Saved {filename}")
            cell_index += 1

#process R files:
    save_r_packages(r_packages, output_directory)
#process py files:
    dependencies = filter_non_standard_libraries(imports_names_py)
    if 'ResultsHub' in dependencies:
        dependencies.remove('ResultsHub')
    save_requirements(dependencies, output_directory)
#adding the imports for both R and py
    save_cells_to_files(notebook, output_directory, imports_statements_py,r_packages)
#add r and py resulthub client:
    copy_resultshub_files('./resultshub_client', output_directory)

'''
# Example usage
notebook_path = './example/Rexample.ipynb'
output_directory = 'execution'
process_notebook(notebook_path, output_directory)
'''
