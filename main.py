import sys
import os  # 确保导入 os
import subprocess
from splitnotebook import process_notebook
from py2docker import create_dockerfile, build_docker_image
import py2docker

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
    
    # 正确设置 dockerfiles_path
    dockerfiles_path = os.path.join(output_dir, "docker")
    python_version = py2docker.get_python_version() # 示例 Python 版本, 根据需要调整
    
    # 确保 dockerfiles 目录存在
    os.makedirs(dockerfiles_path, exist_ok=True)

    # Step 2: 遍历 Python 文件并构建 & 推送 Docker 镜像
    for file in os.listdir(output_dir):
        if file.endswith('.py') and file.startswith('cell_'):
            # 创建 Dockerfile 并构建镜像
            dockerfile_path = create_dockerfile(file, 'requirements.txt', dockerfiles_path, python_version)
            image_tag = f"{dockerhub_username}/{dockerhub_repository}:{file.split('.')[0]}"
            build_docker_image(dockerfile_path, image_tag, output_dir)
            # Step 3: 推送到 Docker Hub
            push_to_docker_hub(image_tag)

if __name__ == '__main__':
    notebook_path = sys.argv[1] if len(sys.argv) > 1 else './example/iris.ipynb'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else './example/output'
    dockerhub_username = sys.argv[3] if len(sys.argv) > 3 else "shirou10086"  # Default Docker Hub username
    dockerhub_repository = sys.argv[4] if len(sys.argv) > 4 else "jup2kub"  # Default Docker Hub repository

    main(notebook_path, output_dir, dockerhub_username, dockerhub_repository)
