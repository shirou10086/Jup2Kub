# [Jup2Kub: Convert Jupyter Notebooks to Kubernetes Deployments](https://arxiv.org/pdf/2311.12308.pdf)

## Abstract
Jup2Kub is an innovative tool designed to transform Jupyter notebooks into scalable and fault-tolerant workflows within a Kubernetes environment. It addresses common issues faced when dealing with large datasets in scientific computing, such as scalability, fault tolerance, and dependency management. Jup2Kub facilitates the translation of scientific workflows from a Jupyter notebook format to a distributed, high-performance Kubernetes setting.

## Features
- **Workflow Translation**: Converts Jupyter notebook workflows for execution in Kubernetes.
- **Scalability and Fault Tolerance**: Ensures robust workflow execution even with large datasets.
- **Dependency Management**: Utilizes Reprozip and Docker to capture and manage software dependencies.

## Getting Started

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop) with Kubernetes enabled
- Python 3.x
- Jupyter Notebook wanted to transform(only supporting python under current version)
- macOS/Ubuntu (donot work in windows,example case in Ubuntu23.1)

### Installation
1. Clone the Jup2Kub repository:
   ```
   git clone https://github.com/shirou10086/Jup2Kub.git
   cd Jup2Kub
   ```
2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

### Usage
1. Ensure Docker Desktop is running with Kubernetes enabled.
2. Execute the `main.py` script with the path to your Jupyter notebook:
   ```
   python main.py path/to/your-notebook.ipynb
   ```
   This will:
   - Split the notebook into separate Python files.
   - Dockerize these files and create Docker images.
   - Deploy the images to Kubernetes.
3. To clean up the previous deployment and related files, use the `delete.py` script:
   ```
   python delete.py
   ```


## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
Special thanks to all users of this project.

---
For more information and support, please refer to the project documentation or contact the project maintainers.
