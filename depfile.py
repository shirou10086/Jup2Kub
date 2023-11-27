import os
import nbformat
import shutil
import split_notebook_python
def check_python_file_for_imports(file_path):
    installed_packages = split_notebook_python.get_installed_packages()
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line_number, line in enumerate(lines, start=1):
        if line.strip().startswith('from ') or line.strip().startswith('import '):
            print(f"Found 'from' or 'import' statement in {file_path} at line {line_number}:")
            print(line.strip())

def extract_imported_module_names(notebook):
    imported_modules = set()

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            for line in cell.source.split('\n'):
                if line.startswith('import ') or line.startswith('from '):
                    # Extract module name from import statement
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        module_name = parts[1]
                        imported_modules.add(module_name)

    return imported_modules

def copy_python_modules(imported_modules, source_directory, output_directory):
    current_num = 0  # 用于编号文件
    for module_name in imported_modules:
        python_module_path = os.path.join(source_directory, f"{module_name}.py")
        if os.path.isfile(python_module_path):
            target_file_name = f"cell_{current_num}.py"
            target_file_path = os.path.join(output_directory, target_file_name)
            shutil.copy(python_module_path, target_file_path)
            current_num += 1


# Example usage
notebook_path = './example/jup2kub_iris_withpy.ipynb'
output_directory = './example/output'
os.makedirs(output_directory, exist_ok=True)
source_directory = './example'  # Update this to the appropriate source directory
with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = nbformat.read(f, as_version=4)

imported_modules = extract_imported_module_names(nb)
copy_python_modules(imported_modules, source_directory, output_directory)
