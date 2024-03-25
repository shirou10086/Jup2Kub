from kubernetes import client, config
from kubernetes.client.rest import ApiException

'''
This file contains the functions for cleanup files & k8s cluster deployments
'''

def delete_job(job_name, namespace):
    config.load_kube_config()
    batch_v1 = client.BatchV1Api()
    try:
        response = batch_v1.delete_namespaced_job(
            name=job_name,
            namespace=namespace,
            body=client.V1DeleteOptions(
                propagation_policy='Foreground',
            ),
        )
        print(f"Job '{job_name}' in namespace '{namespace}' deleted. Status: {response.status}")
    except ApiException as e:
        if e.status == 404:
            print(f"Job '{job_name}' in namespace '{namespace}' not found.")
        else:
            print(f"Error deleting job '{job_name}' in namespace '{namespace}': {e}")

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

