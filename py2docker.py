import os
import subprocess
import sys
#build docker images based on splited python files
def get_python_version():
    # get current version
    version = sys.version_info
    return f"{version.major}.{version.minor}"


def create_dockerfile(file_name, requirements_path, dockerfiles_path, python_version):
    dockerfile_content = f'''
    FROM python:{python_version}
    WORKDIR /app
    COPY {file_name} /app
    COPY ResultsHub.py /app
    COPY J2kResultsHub_pb2.py /app
    COPY J2kResultsHub_pb2_grpc.py /app
    COPY {requirements_path} /app
    RUN apt-get update && pip install --ignore-installed -r requirements.txt
    CMD ["python", "/app/{os.path.basename(file_name)}"]
    '''

    dockerfile_path = os.path.join(dockerfiles_path, f"Dockerfile_{file_name.split('.')[0]}")
    with open(dockerfile_path, 'w') as file:
        file.write(dockerfile_content)
    return dockerfile_path

def build_docker_image(dockerfile_path, image_tag, context_path):
    print('creating docker')
    try:
        subprocess.run(["docker", "build", "-f", dockerfile_path, "-t", image_tag, context_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"An standard libray been included in requirements.txt while building the Docker image: {e}")

'''
# an example of use local python version create docker images
#use this by : "python py2docker.py" then type the cell count number
output_dir = './example/output'
requirements_path = os.path.join(output_dir, 'requirements.txt')
dockerfiles_path = os.path.join(output_dir, 'docker')
python_version = get_python_version()

os.makedirs(dockerfiles_path, exist_ok=True)

for file in os.listdir(output_dir):
    if file.endswith('.py') and file.startswith('cell'):
        dockerfile_path = create_dockerfile(file, 'requirements.txt', dockerfiles_path, python_version)
        build_docker_image(dockerfile_path, f"{file.split('.')[0]}", output_dir)
'''
