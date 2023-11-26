import nbformat
import os
import subprocess
#把所有的dependency全部列出来
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
#切割然后保存
def save_cells_to_files(notebook, output_directory, dependencies):
    os.makedirs(output_directory, exist_ok=True)
    dependencies_block = '\n'.join(dependencies) + '\n\n'

    valid_cell_index = 0  # 用于跟踪有效单元格的编号
    for cell in notebook.cells:
        if cell.cell_type == 'code' and cell.source.strip():
            cell_file_path = os.path.join(output_directory, f"cell_{valid_cell_index}.py")
            with open(cell_file_path, 'w', encoding='utf-8') as cell_file:
                cell_file.write(dependencies_block + cell.source)
            valid_cell_index += 1  # 仅在保存有效单元格后递增

    print(f"{valid_cell_index} non-empty cells have been saved to separate files in {output_directory}, with dependencies included.")

def get_environment_info():
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    return result.stdout if result.returncode == 0 else "Error capturing environment info"

def save_requirements(output_directory):
    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)
    if result.returncode == 0:
        requirements_path = os.path.join(output_directory, 'requirements.txt')
        with open(requirements_path, 'w', encoding='utf-8') as file:
            file.write(result.stdout)
        print(f"Requirements saved to {requirements_path}")
    else:
        print("Error capturing environment info")

def process_notebook(notebook_path, output_directory):
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    # Extract imports and file paths
    dependencies, file_paths = extract_imports_and_files(nb)
    print("Dependencies found in the notebook:")
    for dep in dependencies:
        print(dep)

    print("\nFile paths found in the notebook:")
    for path in file_paths:
        print(path)

    # Save each cell to a separate file with dependencies
    save_cells_to_files(nb, output_directory, dependencies)
    print(f"Non-empty cells have been saved to separate files in {output_directory}, with dependencies included.")

    # Print environment info
    env_info = get_environment_info()
    print("\nEnvironment information:")
    print(env_info)

    save_requirements(output_directory)

# Example usage
notebook_path = './example/jup2kub_iris.ipynb'  # Replace with your notebook path
output_directory = './example/output'  # Replace with your desired output directory
process_notebook(notebook_path, output_directory)
