import nbformat
import json
import os
import subprocess

def split_notebook(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as original_nb_file:
        original_nb = nbformat.read(original_nb_file, as_version=4)

    # for each cell, new docker
    for index, cell in enumerate(original_nb.cells):
        if cell.cell_type == 'code':
            new_nb = nbformat.v4.new_notebook()
            new_nb.cells.append(cell)

            new_nb_path = f'split_notebook_{index}.ipynb'
            with open(new_nb_path, 'w', encoding='utf-8') as new_nb_file:
                nbformat.write(new_nb, new_nb_file)


            build_and_run_docker_container(new_nb_path, index)

def build_and_run_docker_container(notebook_path, index):
    docker_image_name = f'notebook_cell_{index}'
    docker_container_name = f'container_for_cell_{index}'

    # DockerImage
    subprocess.run(['docker', 'build', '-t', docker_image_name, '.'], check=True)

    # run Docker for new notebook
    subprocess.run(['docker', 'run', '--name', docker_container_name, '-v', f"{os.getcwd()}:/home/jovyan", docker_image_name, 'start-notebook.sh', f"--NotebookApp.default_url=/notebooks/{notebook_path}"], check=True)


notebook_path = ''
split_notebook(notebook_path)
