import yaml
import subprocess
from kubernetes import client, config
from time import sleep

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(e.stderr)

class JobManager:
    def __init__(self):
        self.jobs = {}

    def add_job(self, name, depends_on=None, is_producer=False, is_consumer=False, topic=None):
        self.jobs[name] = {
            'depends_on': depends_on,
            'is_producer': is_producer,
            'is_consumer': is_consumer,
            'topic': topic
        }

    def generate_jobs(self, x):
        for i in range(x + 1):
            job_name = f"cell-{i}"
            depends_on = f"cell-{i - 1}" if i > 0 else None

            is_producer = False
            is_consumer = i > 0

            if depends_on:
                self.jobs[depends_on]['is_producer'] = True

            self.add_job(job_name, depends_on, is_producer, is_consumer)

class DynamicJobDeployer:
    def __init__(self, job_manager):
        self.job_manager = job_manager
        config.load_kube_config()
        self.batch_v1 = client.BatchV1Api()

    def deploy_all_jobs(self, tag):
        for job_name, job_info in self.job_manager.jobs.items():
            image_name = f"{job_name}:{tag}"  # Modify this to match your image name
            if job_info['depends_on']:
                self.wait_for_job_ready(job_info['depends_on'])
            self.deploy_to_kubernetes(job_name, image_name, job_info)

    def deploy_to_kubernetes(self, job_name, image_name, job_info):
        with open('job_template.yaml', 'r') as file:
            job_yaml = yaml.safe_load(file)
            job_yaml['metadata']['name'] = job_name
            job_yaml['spec']['template']['spec']['containers'][0]['name'] = job_name + "-container"
            job_yaml['spec']['template']['spec']['containers'][0]['image'] = image_name

            # Set environment variables
            env_vars = job_yaml['spec']['template']['spec']['containers'][0]['env']
            for env_var in env_vars:
                if env_var['name'] == 'PRODUCER_TOPIC' and job_info['is_producer']:
                    env_var['value'] = job_info['topic']
                elif env_var['name'] == 'CONSUMER_TOPIC' and job_info['is_consumer']:
                    env_var['value'] = job_info['topic']

            self.batch_v1.create_namespaced_job(body=job_yaml, namespace="default")

    def wait_for_job_ready(self, job_name, namespace='default'):
        while True:
            job_status = self.batch_v1.read_namespaced_job_status(job_name, namespace)
            if job_status.status.succeeded == 1:
                break
            sleep(10)
        print(f"Job '{job_name}' completed.")

def main():
    x = int(input("Enter the number x to deploy cells from 0 to x: "))
    tag = "latest"

    job_manager = JobManager()
    job_manager.generate_jobs(x)

    deployer = DynamicJobDeployer(job_manager)
    deployer.deploy_all_jobs(tag)

if __name__ == "__main__":
    main()
