import nbformat
import os
import subprocess
import sys
import re
import pkgutil
from isort import place_module
import shutil
import yaml
import tarfile


def get_python_version():
    # Getting the current Python version
    version = sys.version_info
    return f"{version.major}.{version.minor}.{version.micro}"
def get_installed_packages():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else ""

def is_standard_library_module(module_name):
    if sys.version_info >= (3, 10):
        return module_name in sys.stdlib_module_names
    else:
        return place_module(module_name)=='STDLIB'

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

def map_dependencies_to_versions(dependencies, installed_packages):
    versioned_dependencies = set()

    for dep in dependencies:
        # Extract the package name before the first dot (if present)
        split_dep = dep.split()
        if len(split_dep) >= 2:
            package_name = split_dep[1] if 'import ' in dep else split_dep[2]
            package_name = package_name.split('.')[0]  # Get the part before the first dot

            # Check if the package is a standard library module
            if not is_standard_library_module(package_name):
                # Search for a matching version in installed packages
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


def extract_reprozip_package(rpz_path, extract_to):
    """unpack reprozip"""
    with tarfile.open(rpz_path, "r") as tar:
        tar.extractall(path=extract_to)

def extract_dependencies(config_path):
    """get dependencies from reprozip"""
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)

    dependencies = []
    # ReproZip config.yml
    packages = config.get('packages', [])
    for pkg in packages:
        dependencies.append(pkg.get('name'))

    files = config.get('other_files', [])
    for file in files:
        dependencies.append(file.get('path'))

    return dependencies

def generate_dependencies_file(dependencies, output_path):
    """save dependencies"""
    with open(output_path, 'w') as file:
        for dep in dependencies:
            file.write(f"# Dependency: {dep}\n")
