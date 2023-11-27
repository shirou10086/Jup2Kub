import nbformat
import os
import subprocess
import sys
import re

def get_installed_packages():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""
def extract_imports_and_files(notebook):
    imports = set()
    files = set()

    for cell in notebook.cells:
        if cell.cell_type == 'code':
            for line in cell.source.split('\n'):
                if line.startswith('import ') or line.startswith('from '):
                    imports.add(line.strip())
                if 'open(' in line or 'read_csv(' in line or 'read_excel(' in line:
                    file_path = line.split('(')[1].split(')')[0].replace("'", "").replace('"', '').strip()
                    if os.path.isfile(file_path):
                        files.add(file_path)

    return imports, files

def save_cells_to_files(notebook, output_directory, dependencies):
    os.makedirs(output_directory, exist_ok=True)
    dependencies_block = '\n'.join(dependencies) + '\n\n'

    valid_cell_index = 0
    for cell in notebook.cells:
        if cell.cell_type == 'code' and cell.source.strip():
            cell_file_path = os.path.join(output_directory, f"cell_{valid_cell_index}.py")
            with open(cell_file_path, 'w', encoding='utf-8') as cell_file:
                cell_file.write(dependencies_block + cell.source)
            valid_cell_index += 1

    print(f"{valid_cell_index} non-empty cells have been saved to separate files in {output_directory}, with dependencies included.")

def get_environment_info():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else "Error capturing environment info"
def map_dependencies_to_versions(dependencies, installed_packages):
    # 创建一个映射，将子模块映射到顶级包
    submodule_to_package = {
        'matplotlib.pyplot': 'matplotlib',
        # 这里可以添加更多映射
    }

    versioned_dependencies = set()
    for dep in dependencies:
        # 从依赖中提取包名
        package_name = dep.split()[1] if 'import ' in dep else dep.split()[2]
        package_name = submodule_to_package.get(package_name, package_name)
        # 寻找匹配的版本
        regex = re.compile(rf"{package_name}==[\d\.]+", re.IGNORECASE)
        matches = regex.findall(installed_packages)
        if matches:
            versioned_dependencies.add(matches[0])
        else:
            print(f"Warning: Version for '{package_name}' not found.")

    return versioned_dependencies
def save_requirements(dependencies, output_directory):
    requirements_content = '\n'.join(dependencies)
    requirements_path = os.path.join(output_directory, 'requirements.txt')
    with open(requirements_path, 'w', encoding='utf-8') as file:
        file.write(requirements_content)
    print(f"Requirements saved to {requirements_path}")

def process_notebook(notebook_path, output_directory):
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    dependencies, file_paths = extract_imports_and_files(nb)
    installed_packages = get_installed_packages()
    versioned_dependencies = map_dependencies_to_versions(dependencies, installed_packages)

    save_cells_to_files(nb, output_directory, dependencies)
    save_requirements(versioned_dependencies, output_directory)

# Example usage
notebook_path = './example/jup2kub_iris.ipynb'
output_directory = './example/output'
process_notebook(notebook_path, output_directory)
