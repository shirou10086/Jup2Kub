import sys
import os
import subprocess
from splitnotebook import process_notebook
from dependency import add_code_to_all_files
from py2docker import create_dockerfile, build_docker_image
from deploymentUtils import *
import py2docker
import importlib.util
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


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

def main(notebook_path, output_dir, dockerhub_username, dockerhub_repository, image_list_path):

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

        # STEP 3: Dockerize the Python files
        dockerfiles_path = os.path.join(output_dir, "docker")
        python_version = py2docker.get_python_version()
        os.makedirs(dockerfiles_path, exist_ok=True)

        with ThreadPoolExecutor(max_workers=4) as executor:  # max_worker default set to 4
            futures = [executor.submit(dockerize_and_push, filename, dockerfiles_path, python_version, output_dir, dockerhub_username, dockerhub_repository)
                       for filename in os.listdir(output_dir)
                       if filename.endswith('.py') and filename.startswith('cell-')]

            for future in futures:
                image_tag = future.result()
                job_info_list.append(image_tag)

    # # STEP 4: Makesure cleanup_info.json exists
    # cleanup_info_filename = "cleanup_info.txt"
    # try:
    #     cleanup_info = open(cleanup_info_filename, 'x')
    # except FileExistsError:
    #     # If the file already exists, open it in 'a' mode to append without truncating it.
    #     cleanup_info = open(cleanup_info_filename, 'a')

    # STEP 5: Deploy J2K's control plane: PV, PVC, and ResultsHub
    # create pv
    node_name = "node0.net-test.rdma-prefetch-pg0.wisc.cloudlab.us" # NOTE: REPLACE NODE_NAME EVERYTIME CHANGE THE MACHINE!
    local_path = "/data/my-pv"
    pv_name = "local-pv"
    storage_size = "1Gi" # Adjust the size as needed
    pvc_name = "local-pvc-for-rh"
    namespace = "default" # for ResultsHub and jobs

    create_local_pv(node_name, local_path, pv_name, storage_size)

    # create pvc
    create_pvc(pvc_name, storage_size, namespace)

    # deploy ResultsHub
    deploy_resultsHub_to_statefulset(pvc_name, namespace)
    time.sleep(3) # short sleep waiting results hub to be running

    # STEP 6: Deploy the cell jobs
    for image_tag in job_info_list:
        deploy_stateless_job(image_name=image_tag[0], tag=image_tag[1], namespace=namespace)


if __name__ == '__main__':
    skip_dockerization = True if len(sys.argv) > 1 and sys.argv[1] == "skip" else False
    notebook_path = sys.argv[2] if len(sys.argv) > 2 else './example/iris.ipynb'
    output_dir = sys.argv[3] if len(sys.argv) > 3 else './execution'
    dockerhub_username = sys.argv[4] if len(sys.argv) > 4 else "shirou10086"  # Default Docker Hub username
    dockerhub_repository = sys.argv[5] if len(sys.argv) > 5 else "jup2kub"  # Default Docker Hub repository

    main(notebook_path, output_dir, dockerhub_username, dockerhub_repository, os.path.join(output_dir, "image_list.txt"))
