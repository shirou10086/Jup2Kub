import sys
import os  # 确保导入 os
import subprocess
from splitnotebook import process_notebook
from py2docker import create_dockerfile, build_docker_image

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

def main(notebook_path, output_dir, dockerhub_username, dockerhub_repository):
    # Step 1: Process the notebook
    process_notebook(notebook_path, output_dir)
    
    # Assume dockerfiles_path and python_version are determined here
    dockerfiles_path = "./example/output/dockerfiles"
    python_version = "3.8"  # Example Python version, adjust as needed

    # Step 2: Iterate through Python files and build & push Docker images
    for file in os.listdir(output_dir):
        if file.endswith('.py') and file.startswith('cell_'):
            dockerfile_path = create_dockerfile(file, 'requirements.txt', dockerfiles_path, python_version)
            image_tag = f"{dockerhub_username}/{dockerhub_repository}:{file.split('.')[0]}"
            build_docker_image(dockerfile_path, image_tag, output_dir)
            # Step 3: Push to Docker Hub
            push_to_docker_hub(image_tag)

if __name__ == '__main__':
    notebook_path = sys.argv[1] if len(sys.argv) > 1 else './example/iris.ipynb'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './example/output'
    dockerhub_username = sys.argv[3] if len(sys.argv) > 3 else "shirou10086"  # Default Docker Hub username
    dockerhub_repository = sys.argv[4] if len(sys.argv) > 4 else "jup2kub"  # Default Docker Hub repository

    main(notebook_path, output_dir, dockerhub_username, dockerhub_repository)
