import os
import subprocess

def create_dockerfile(file_name, requirements_path, dockerfiles_path):
    dockerfile_content = f'''
    FROM python:3.8
    WORKDIR /app
    COPY {file_name} /app
    COPY {requirements_path} /app
    RUN pip install -r requirements.txt
    CMD ["python", "/app/{file_name}"]
    '''
    dockerfile_path = os.path.join(dockerfiles_path, f"Dockerfile_{file_name.split('.')[0]}")
    with open(dockerfile_path, 'w') as file:
        file.write(dockerfile_content)
    return dockerfile_path

def build_docker_image(dockerfile_path, image_tag):
    subprocess.run(["docker", "build", "-f", dockerfile_path, "-t", image_tag, "."], check=True)

output_dir = './example/output'
requirements_path = os.path.join(output_dir, 'requirements.txt')
dockerfiles_path = os.path.join(output_dir, 'docker')

os.makedirs(dockerfiles_path, exist_ok=True)

for file in os.listdir(output_dir):
    if file.endswith('.py'):
        dockerfile_path = create_dockerfile(file, requirements_path, dockerfiles_path)
        build_docker_image(dockerfile_path, f"cell_{file.split('.')[0]}")
