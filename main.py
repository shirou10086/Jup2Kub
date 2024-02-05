# main.py
import sys
from split_notebook_python import process_notebook,get_python_version
from py2docker import create_dockerfile, build_docker_image
from statefulset import PodManager, DynamicPodDeployer
import os
import delete
import time

def count_cell_files(output_dir):
    files = os.listdir(output_dir)
    cell_files = [file for file in files if file.startswith('cell') and file.endswith('.py')]
    return len(cell_files)

def main(notebook_path, output_dir):
    # step1: split the notebook
    process_notebook(notebook_path, output_dir) 
    cellnum= count_cell_files(output_dir)-1
    # step2: dockerlize python files
    python_version = get_python_version()
    requirements_path = os.path.join(output_dir, 'requirements.txt')
    dockerfiles_path = os.path.join(output_dir, 'dockerfiles')
    os.makedirs(dockerfiles_path, exist_ok=True)
    for file in os.listdir(output_dir):
        if file.endswith('.py'):
            dockerfile_path = create_dockerfile(file, 'requirements.txt', dockerfiles_path, python_version)
            build_docker_image(dockerfile_path, f"{file.split('.')[0]}", output_dir)

    # step3: deploy to kubernetes
    pod_manager = PodManager()
    pod_manager.generate_pods(cellnum)
    deployer = DynamicPodDeployer(pod_manager)
    deployer.deploy_all_pods('latest')  #use latest as

if __name__ == '__main__':
    notebook_path = sys.argv[1] if len(sys.argv) > 1 else input("Enter the path to the notebook: ")
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './example/output'
    main(notebook_path, output_dir)
