import subprocess
from kubernetes import client, config
from time import sleep
import os

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(e.stderr)
class PodManager:
    def __init__(self):
        self.pods = {}

    def add_pod(self, name, depends_on=None, is_producer=False, is_consumer=False, topic=None):
        self.pods[name] = {
            'depends_on': depends_on,
            'is_producer': is_producer,
            'is_consumer': is_consumer,
            'topic': topic
        }

    def generate_pods(self, x):
        for i in range(x + 1):
            pod_name = f"cell_{i}"
            depends_on = f"cell_{i - 1}" if i > 0 else None

            is_producer = False
            is_consumer = i > 0  # Every pod except the first one is a consumer

            # The previous pod is a producer if it exists
            if depends_on:
                self.pods[depends_on]['is_producer'] = True

            self.add_pod(pod_name, depends_on, is_producer, is_consumer)

class DynamicPodDeployer:
    def __init__(self, pod_manager):
        self.pod_manager = pod_manager
        config.load_kube_config()
        self.v1 = client.CoreV1Api()
    def create_output_directory(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
    def deploy_all_pods(self, tag):
        for pod_name, pod_info in self.pod_manager.pods.items():
            image_name = pod_name  # Set image name based on pod name
            if pod_info['depends_on']!=None:
                # Check if the dependent pod is ready
                self.wait_for_pod_ready(pod_info['depends_on'])
            self.deploy_to_kubernetes(image_name, tag, pod_name, pod_info)

    def deploy_to_kubernetes(self, image_name, tag, pod_name, pod_info):
        sanitized_pod_name = pod_name.replace("_", "-")  # Replace underscores with dashes
        env_content = ""
        if pod_info['is_producer']:
            env_content += f"""
            - name: PRODUCER_TOPIC
            value: "{pod_info['topic']}"
            """
        if pod_info['is_consumer']:
            env_content += f"""
            - name: CONSUMER_TOPIC
            value: "{pod_info['topic']}"
            """

        pv, pvc = self.create_efs_pv_pvc(f"{sanitized_pod_name}-efs", "default", "fs-0af813165c0ebd42b.efs.us-east-1.amazonaws.com")

        deployment_content = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {sanitized_pod_name}-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {sanitized_pod_name}
  template:
    metadata:
      labels:
        app: {sanitized_pod_name}
    spec:
      containers:
      - name: {sanitized_pod_name}-container
        image: {image_name}:{tag}
        env:
        - name: KAFKA_BROKER
          value: "0.0:9092"
        {env_content.strip()}
        volumeMounts:
        - name: efs-volume
          mountPath: /mnt/efs
      volumes:
      - name: efs-volume
        persistentVolumeClaim:
          claimName: {sanitized_pod_name}-efs-pvc
    """

        output_dir = "./example/output/k8s"
        self.create_output_directory(output_dir)

        pv_file_path = os.path.join(output_dir, f"{sanitized_pod_name}-efs-pv.yaml")
        pvc_file_path = os.path.join(output_dir, f"{sanitized_pod_name}-efs-pvc.yaml")
        deployment_file_path = os.path.join(output_dir, f"{sanitized_pod_name}-deployment.yaml")

        with open(pv_file_path, "w") as file:
            file.write(pv)

        with open(pvc_file_path, "w") as file:
            file.write(pvc)

        run_command(["kubectl", "apply", "-f", pv_file_path])
        run_command(["kubectl", "apply", "-f", pvc_file_path])

        with open(deployment_file_path, "w") as file:
            file.write(deployment_content)

        run_command(["kubectl", "apply", "-f", deployment_file_path])



        def wait_for_pod_ready(self, pod_name):
            print(f"Waiting for {pod_name} to be ready...")
            ready = False
            while not ready:
                pod_status = self.v1.read_namespaced_pod_status(pod_name, "default")
                if pod_status.status.conditions:
                    for condition in pod_status.status.conditions:
                        if condition.type == "Ready" and condition.status == "True":
                            ready = True
                            break
                if not ready:
                    sleep(10)
            print(f"{pod_name} is ready.")
    def wait_for_pod_ready(self, pod_name):
        print(f"Waiting for {pod_name} to be ready...")
        ready = False
        while not ready:
            pod_status = self.v1.read_namespaced_pod_status(pod_name, "default")
            if pod_status.status.conditions:
                for condition in pod_status.status.conditions:
                    if condition.type == "Ready" and condition.status == "True":
                        ready = True
                        break
            if not ready:
                sleep(10)
        print(f"{pod_name} is ready.")

    def create_efs_pv_pvc(self, name, namespace, efs_dns_name):
        sanitized_name = name.replace("_", "-")  # 确保名称符合规范
        pv = f"""apiVersion: v1
kind: PersistentVolume
metadata:
  name: {sanitized_name}
spec:
  capacity:
    storage: 5Gi
  accessModes:
    - ReadWriteMany
  persistentVolumeReclaimPolicy: Retain
  storageClassName: efs
  csi:
    driver: efs.csi.aws.com
    volumeHandle: {efs_dns_name}
"""

        pvc = f"""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {sanitized_name}
  namespace: {namespace}
spec:
  accessModes:
    - ReadWriteMany
  storageClassName: efs
  resources:
    requests:
      storage: 5Gi
"""

        return pv, pvc



# existing run_command function

def main():
    x = int(input("Enter the number x to deploy cells from 0 to x: "))
    tag = "latest"

    pod_manager = PodManager()
    pod_manager.generate_pods(x)

    deployer = DynamicPodDeployer(pod_manager)
    deployer.deploy_all_pods(tag)

if __name__ == "__main__":
    main()
