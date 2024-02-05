import nbformat
import subprocess

def get_notebook_kernel(notebook_path):
    with open(notebook_path, 'r', encoding='utf-8') as notebook_file:
        nb = nbformat.read(notebook_file, as_version=4)
    kernel_name = nb.metadata.kernelspec.name
    return kernel_name

def generate_dockerfile(kernel_name):
    dockerfile_lines = [
        "FROM jupyter/datascience-notebook\n",
        "USER root\n"
    ]

    if kernel_name == 'python3':
        dockerfile_lines.append("# Python kernel is already included in the base image\n")
    elif kernel_name == 'ir':
        dockerfile_lines.extend([
            "RUN conda install --quiet --yes 'r-base' 'r-irkernel' && \\\n",
            "    conda clean --all -f -y && \\\n",
            "    fix-permissions $CONDA_DIR && \\\n",
            "    fix-permissions /home/$NB_USER\n"
        ])
    elif kernel_name == 'julia-1.5':
        dockerfile_lines.extend([
            "RUN conda install --quiet --yes 'julia' && \\\n",
            "    echo 'Pkg.add(\"IJulia\")' | julia && \\\n",
            "    fix-permissions $JULIA_PKGDIR && \\\n",
            "    fix-permissions /home/$NB_USER\n"
        ])
    else:
        raise ValueError(f"Unsupported kernel: {kernel_name}")

    with open('Dockerfile', 'w') as dockerfile:
        dockerfile.writelines(dockerfile_lines)

def build_docker_image(image_name):
    subprocess.run(['docker', 'build', '-t', image_name, '.'], check=True)

def process_notebook(notebook_path, image_name):
    kernel_name = get_notebook_kernel(notebook_path)
    print(f"Detected kernel: {kernel_name}")
    generate_dockerfile(kernel_name)
    build_docker_image(image_name)
    print(f"Docker image '{image_name}' built successfully.")

# Example usage
notebook_path = 'path_to_your_notebook.ipynb'
image_name = 'custom_jupyter_image'
process_notebook(notebook_path, image_name)
