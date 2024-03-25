from kubernetes import client, config
from kubernetes.client.rest import ApiException

def delete_local_pv(pv_name):
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    try:
        api_instance.delete_persistent_volume(name=pv_name)
        print(f"PersistentVolume '{pv_name}' deleted.")
    except ApiException as e:
        print(f"Exception when deleting PersistentVolume: {e}")

def delete_pvc(pvc_name, namespace):
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    try:
        api_instance.delete_namespaced_persistent_volume_claim(name=pvc_name, namespace=namespace)
        print(f"PersistentVolumeClaim '{pvc_name}' deleted from namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when deleting PersistentVolumeClaim: {e}")

def delete_statefulset(statefulset_name, namespace):
    config.load_kube_config()
    api_instance = client.AppsV1Api()
    try:
        api_instance.delete_namespaced_stateful_set(name=statefulset_name, namespace=namespace)
        print(f"StatefulSet '{statefulset_name}' deleted from namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when deleting StatefulSet: {e}")

def delete_service(service_name, namespace):
    config.load_kube_config()
    api_instance = client.CoreV1Api()
    try:
        api_instance.delete_namespaced_service(name=service_name, namespace=namespace)
        print(f"Service '{service_name}' deleted from namespace '{namespace}'.")
    except ApiException as e:
        print(f"Exception when deleting Service: {e}")

if __name__ == "__main__":
    # Names and namespace used during creation
    pv_name = "local-pv"
    pvc_name = "local-pvc-for-rh"
    statefulset_name = "results-hub"
    service_name = "results-hub-service"
    namespace = "default"

    # DELETE RESOURCES
    # Note: Order of deletion matters. Delete dependents first.
    delete_service(service_name, namespace)
    delete_statefulset(statefulset_name, namespace)
    delete_pvc(pvc_name, namespace)
    delete_local_pv(pv_name)

    print("Cleanup completed.")
