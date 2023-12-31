from kubernetes import client, config

def delete_statefulset_resources(name, count):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    for i in range(count + 1):
        # 构建资源名称
        resource_name = f"{name}-{i}"

        # 删除 StatefulSet
        try:
            apps_v1.delete_namespaced_stateful_set(name=resource_name, namespace="default")
            print(f"StatefulSet {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting StatefulSet {resource_name}: {e}")

        # 删除 PersistentVolumeClaim
        try:
            v1.delete_namespaced_persistent_volume_claim(name=resource_name, namespace="default")
            print(f"PersistentVolumeClaim {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting PersistentVolumeClaim {resource_name}: {e}")

        # 删除服务
        try:
            v1.delete_namespaced_service(name=resource_name, namespace="default")
            print(f"Service {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting Service {resource_name}: {e}")

        # 删除 PersistentVolume
        try:
            v1.delete_persistent_volume(name=resource_name)
            print(f"PersistentVolume {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting PersistentVolume {resource_name}: {e}")

def main():
    name = "cell"  # StatefulSet 的基本名称
    count = int(input("Enter the number x to delete cells from 0 to x: "))
    delete_statefulset_resources(name, count)
if __name__ == "__main__":
    main()