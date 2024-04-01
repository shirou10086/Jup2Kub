# Standard packages
import json
import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


# J2K packages
from dependency import add_code_to_all_files
import py2docker
from py2docker import build_docker_image, create_dockerfile
from deploymentUtils import *
from splitnotebook import process_notebook
from checkfileaccess import generate_file_access_report

'''
This file provide a unified user interface
'''
def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def push_to_docker_hub(image_tag):
    """
    Pushes a Docker image to Docker Hub.
    Assumes Docker CLI is installed and user is logged in.
    """
    try:
        subprocess.run(["docker", "push", image_tag], check=True)
        print(f"Successfully pushed {image_tag} to Docker Hub.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to push {image_tag} to Docker Hub: {e}")

def dockerize_and_push(filename, dockerfiles_path, python_version, output_dir, dockerhub_username, dockerhub_repository):
    """
    packs the functions for create Dockerfile, build image, and push to Docker Hub.
    one function in one thread.
    """
    dockerfile_path = create_dockerfile(filename, 'requirements.txt', dockerfiles_path, python_version)
    image_name_tag = f"{dockerhub_username}/{dockerhub_repository}:{filename.split('.')[0]}"
    build_docker_image(dockerfile_path, image_name_tag, output_dir)
    push_to_docker_hub(image_name_tag)
    return (f"{dockerhub_username}/{dockerhub_repository}", filename.split('.')[0])



def main(skip_dockerization, notebook_path, output_dir, dockerhub_username, dockerhub_repository, image_list_path, n_docker_worker):

    # STEP 0: Check if we can skip the codegen & dockerization phase
    # also prepare the list of image:tag to be deployed
    job_info_list = []
    if skip_dockerization and os.path.exists(output_dir) and os.path.exists(image_list_path):
        with open(image_list_path, 'r') as file:
            for line in file:
                # strip the newline character from the end of the line
                line = line.strip()
                # split the line by the first occurrence of ":"
                parts = line.split(':', 1)
                if len(parts) == 2:
                    job_info_list.append((parts[0], parts[1]))
    else:
        # NOT SKIPPING DOCKERIZATION

        # STEP 1: Split and Process the notebook
        process_notebook(notebook_path, output_dir)

        # STEP 2: Run dependency analysis
        track_list_path = os.path.join(output_dir, 'variable_track_list.txt')
        add_code_to_all_files(output_dir, track_list_path)
        #STEP2.1: run file check analysis
        generate_file_access_report()


        # STEP 3: Dockerize the Python files
        dockerfiles_path = os.path.join(output_dir, "docker")
        python_version = py2docker.get_python_version()
        os.makedirs(dockerfiles_path, exist_ok=True)

        with ThreadPoolExecutor(max_workers=int(n_docker_worker)) as executor:
            futures = [executor.submit(dockerize_and_push, filename, dockerfiles_path, python_version, output_dir, dockerhub_username, dockerhub_repository)
                       for filename in os.listdir(output_dir)
                       if re.match(r'cell\d+\.py$', filename)]  # match files here

            for future in as_completed(futures):
                image_tag = future.result()
                job_info_list.append(image_tag)
        print("+++++++++++++++++++++++++++++++++++++++")
        for item in job_info_list:
            print(item)


    # # STEP 4: Makesure cleanup_info.json exists
    # cleanup_info_filename = "cleanup_info.txt"
    # try:
    #     cleanup_info = open(cleanup_info_filename, 'x')
    # except FileExistsError:
    #     # If the file already exists, open it in 'a' mode to append without truncating it.
    #     cleanup_info = open(cleanup_info_filename, 'a')

    # STEP 5: Deploy J2K's control plane: PV, PVC, and ResultsHub
    j2k_config = load_config('J2K_CONFIG.json')
    node_name = j2k_config['results-hub']['master-node-name']
    local_path = j2k_config['results-hub']['local-pv-path']
    pv_name = j2k_config['results-hub']['pv-name']
    pv_storage_size = j2k_config['results-hub']['pv-storage-size']
    pvc_storage_size = j2k_config['results-hub']['pvc-storage-size']
    pvc_name = j2k_config['results-hub']['pvc-name']
    namespace = j2k_config['results-hub']['namespace']

    # create pv
    create_local_pv(node_name, local_path, pv_name, pv_storage_size)

    # create pvc
    create_pvc(pvc_name, pvc_storage_size, namespace)

    # deploy ResultsHub
    deploy_resultsHub_to_statefulset(pvc_name, namespace)
    time.sleep(3) # short sleep waiting results hub to be running

    # STEP 6: Deploy the cell jobs
    for image_tag in job_info_list:
        deploy_stateless_job(image_name=image_tag[0], tag=image_tag[1], namespace=namespace)



if __name__ == '__main__':
    skip_dockerization = True if len(sys.argv) > 1 and sys.argv[1] == "skip" else False
    notebook_path = sys.argv[2] if len(sys.argv) > 2 else './example/readexample.ipynb'

    # Parse the configuration file
    j2k_config = load_config('J2K_CONFIG.json')
    output_dir = j2k_config['execution']['output-directory']
    dockerhub_username = j2k_config['execution']['dockerhub-username']
    dockerhub_repository = j2k_config['execution']['dockerhub-repo-name']
    image_list_filename = j2k_config['execution']['image-list-filename']
    n_docker_worker = j2k_config['execution']['n-docker-worker']

    main(skip_dockerization, notebook_path, output_dir, dockerhub_username, dockerhub_repository, os.path.join(output_dir, image_list_filename), n_docker_worker)
