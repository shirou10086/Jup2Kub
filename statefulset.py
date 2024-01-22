import subprocess
from kubernetes import client, config
from time import sleep
import os
import textwrap

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
        self.apps_v1 = client.AppsV1Api()

    def apply_yaml(self, yaml_content):
        # 创建一个临时文件来保存 YAML 内容
        temp_filename = "temp.yaml"
        with open(temp_filename, "w") as file:
            file.write(yaml_content)

        # 使用 kubectl 命令应用 YAML 文件
        run_command(["kubectl", "apply", "-f", temp_filename])

        # 删除临时文件
        os.remove(temp_filename)

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

    def deploy_all_pods(self, tag):
        for pod_name, pod_info in self.pod_manager.pods.items():
            image_name = pod_name  # Set image name based on pod name
            self.deploy_statefulset(image_name, tag, pod_name, pod_info)

    def deploy_to_kubernetes(self, image_name, tag, pod_name, pod_info):
      sanitized_pod_name = pod_name.replace("_", "-")

      # Initialize the environment content string
      env_content = ""

      # Add environment variables based on pod_info
      if pod_info['is_producer']:
        env_content += f"        - name: PRODUCER_TOPIC\n          value: \"{pod_info['topic']}\"\n"
      if pod_info['is_consumer']:
        env_content += f"        - name: CONSUMER_TOPIC\n          value: \"{pod_info['topic']}\"\n"

      # 使用本地存储的 PV 和 PVC
      pv, pvc = self.create_local_pv_pvc(f"{sanitized_pod_name}-local", "default", "/Documents/Jup2Kub/example/output")

      # 使用环境内容在部署 YAML 中
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
        imagePullPolicy: IfNotPresent  # 修改此处
        env:
{env_content}
        volumeMounts:
        - name: local-volume
          mountPath: /mnt/local
      volumes:
      - name: local-volume
        persistentVolumeClaim:
          claimName: {sanitized_pod_name}-local
"""

      output_dir = "./example/output/k8s"
      self.create_output_directory(output_dir)

      pv_file_path = os.path.join(output_dir, f"{sanitized_pod_name}-local-pv.yaml")
      pvc_file_path = os.path.join(output_dir, f"{sanitized_pod_name}-local-pvc.yaml")
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




    def wait_for_pod_ready(self, deployment_name, namespace='default'):
        ready = False
        while not ready:
            pods = self.v1.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}")
            if not pods.items:
                print(f"No pods found for deployment '{deployment_name}'. Waiting...")
                sleep(10)
                continue

            ready = all(pod.status.phase == "Running" for pod in pods.items)
            if not ready:
                print(f"Waiting for pods of deployment '{deployment_name}' to be ready...")
                sleep(10)

        print(f"All pods for deployment '{deployment_name}' are ready.")


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

    def create_local_pv_pvc(self, name, namespace, storage_path):
        sanitized_name = name.replace("_", "-")
        pv = f"""apiVersion: v1
kind: PersistentVolume
metadata:
  name: {sanitized_name}
spec:
  capacity:
    storage: 5Gi
  volumeMode: Filesystem
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: local-storage
  hostPath:
    path: {storage_path}
    type: DirectoryOrCreate
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - "docker-desktop"
"""

        pvc = f"""apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: {sanitized_name}
  namespace: {namespace}
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: local-storage
  resources:
    requests:
      storage: 5Gi
"""

        return pv, pvc

    def create_headless_service(self, name, namespace):
        body = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1ServiceSpec(
                cluster_ip="None",  # Headless Service
                selector={"app": name}
            )
        )
        self.v1.create_namespaced_service(namespace=namespace, body=body)
    def deploy_statefulset(self, image_name, tag, pod_name, pod_info, replicas=1):
        sanitized_pod_name = pod_name.replace("_", "-")
        self.create_headless_service(sanitized_pod_name, "default")

        # 准备环境变量
        env_vars = []
        if pod_info['is_producer']:
            env_vars.append(client.V1EnvVar(name="PRODUCER_TOPIC", value=pod_info['topic']))
        if pod_info['is_consumer']:
            env_vars.append(client.V1EnvVar(name="CONSUMER_TOPIC", value=pod_info['topic']))

        # 为 StatefulSet 的每个 Pod 创建 PV 和 PVC
        pv, pvc = self.create_local_pv_pvc(sanitized_pod_name, "default", "/mnt/data")

        # 应用 PV 和 PVC
        self.apply_yaml(pv)
        self.apply_yaml(pvc)
        # 定义 StatefulSet
        stateful_set_body = client.V1StatefulSet(
            api_version="apps/v1",
            kind="StatefulSet",
            metadata=client.V1ObjectMeta(name=sanitized_pod_name),
            spec=client.V1StatefulSetSpec(
                service_name=sanitized_pod_name,
                replicas=replicas,
                selector=client.V1LabelSelector(
                    match_labels={"app": sanitized_pod_name}
                ),
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": sanitized_pod_name}),
                    spec=client.V1PodSpec(
                        containers=[
                            client.V1Container(
                                name=sanitized_pod_name + "-container",
                                image=f"{image_name}:{tag}",
                                env=env_vars,
                                volume_mounts=[  # 定义卷挂载点
                                    client.V1VolumeMount(
                                        name=sanitized_pod_name,
                                        mount_path="/mnt/local"
                                    )
                                ]
                            )
                        ],
                        volumes=[  # 定义卷
                            client.V1Volume(
                                name=sanitized_pod_name,
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name=sanitized_pod_name
                                )
                            )
                        ]
                    )
                )
            )
        )

        # 部署 StatefulSet
        try:
            self.apps_v1.create_namespaced_stateful_set(
                namespace="default",  # 指定命名空间
                body=stateful_set_body
            )
            print(f"StatefulSet {sanitized_pod_name} deployed successfully.")
        except client.rest.ApiException as e:
            print(f"Exception when deploying StatefulSet: {e}")
'''
# existing run_command function

def main():
    x = int(input("Enter the number x to deploy cells from 0 to x: "))
    tag = "latest"

    pod_manager = PodManager()
    pod_manager.generate_pods(x)

    deployer = DynamicPodDeployer(pod_manager)
    deployer.deploy_all_pods(tag)

if __name__ == "__main__":
    main()'''
