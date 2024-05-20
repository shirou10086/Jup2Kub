import os
import subprocess
import sys
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_version_r(default_version='4.4.0'):
    """
    Retrieve the R version using the Rscript command. If unable to retrieve, return the default version.
    Make sure to add R in system PATH!
    """
    try:
        result = subprocess.run(['Rscript', '--version'], capture_output=True, text=True)
        version_line = result.stdout.split('\n')[0]
        # get version using re
        match = re.search(r"\b\d+\.\d+\.\d+\b", version_line)
        if match:
            print("Matching"+match.group(0)+"!")
            return match.group(0)
        print("UnMatching"+match.group(0))
    except FileNotFoundError as e:
        print(f"Error: Rscript not found. Ensure R is installed and in your PATH. Using default version {default_version}. Error: {e}")
    except Exception as e:
        print(f"Error retrieving R version, using default version {default_version}. Error: {e}")

    return default_version



def create_dockerfile_r(file_name, requirements_path_r, requirements_path_py, dockerfiles_path):
    dockerfile_content = f'''
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies and gnupg for managing GPG keys
RUN apt-get update && apt-get install -y --no-install-recommends \
    gnupg \
    build-essential \
    libpq-dev \
    python3.8 \
    python3-pip \
    python3-setuptools \
    python3-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libpng-dev \
    virtualenv \
    software-properties-common

# Add the CRAN repository
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 51716619E084DAB9 && \
    add-apt-repository 'deb [arch=amd64,i386] https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'

# Install R
RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base

# Upgrade pip
RUN pip3 install --upgrade pip

# Create the virtual environment
RUN virtualenv --python=python3.8 /root/.virtualenvs/r-reticulate

ENV PYTHONPATH "$PYTHONPATH:/app"
WORKDIR /app

# Copy all necessary files
COPY {file_name} /app
COPY ResultsHub.py /app
COPY ResultsHubForR.py /app
COPY J2kResultsHub_pb2.py /app
COPY J2kResultsHub_pb2_grpc.py /app
COPY {requirements_path_py} /app
COPY install_packages.R /app

# Install Python libraries
RUN pip3 install -r requirements.txt

# Install R libraries and check for reticulate installation
RUN Rscript -e "install.packages(c('reticulate', 'virtualenv'), repos='http://cran.rstudio.com/')"

# Install remaining R libraries
RUN Rscript install_packages.R

# Set the command to run the R script
CMD ["Rscript", "/app/{os.path.basename(file_name)}"]
'''

    dockerfile_path = os.path.join(dockerfiles_path, f"Dockerfile_{file_name.split('.')[0]}")
    with open(dockerfile_path, 'w', encoding='utf-8') as file:
        file.write(dockerfile_content)
    return dockerfile_path

def build_docker_image_r(dockerfile_path, image_tag, context_path):
    print('Creating docker image...')
    try:
        subprocess.run(["docker", "build", "-f", dockerfile_path, "-t", image_tag, context_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during Docker image build: {e}")

# Example usage
output_dir = './execution'
requirements_path_r = os.path.join(output_dir, 'install_packages.R')
requirements_path_py = 'requirements.txt'
dockerfiles_path = os.path.join(output_dir, 'docker')
r_version = get_version_r()

os.makedirs(dockerfiles_path, exist_ok=True)

r_file_names = [file for file in os.listdir(output_dir) if file.endswith('.R') and file.startswith('cell')]

with ThreadPoolExecutor(max_workers=4) as executor:
    futures = []
    for file_name in r_file_names:
        dockerfile_path = create_dockerfile_r(file_name, requirements_path_r, requirements_path_py, dockerfiles_path)
        image_tag = f"{file_name.split('.')[0]}"
        futures.append(executor.submit(build_docker_image_r, dockerfile_path, image_tag, output_dir))

    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"An error occurred: {e}")

print("All Docker images built successfully.")
