import requests
import os
#this file works for k8s communication stats
def get_cluster_ip(service_name, namespace='default'):
    #finds the clusterip
    cmd = [
        "kubectl", "get", "service", service_name,
        "-n", namespace,
        "-o=jsonpath='{.spec.clusterIP}'"
    ]

    try:
        cluster_ip = subprocess.check_output(cmd, text=True).strip().strip("'")
        return cluster_ip
    except subprocess.CalledProcessError as e:
        print(f"Error 4 ClusterIP: {e}")
        return None
    
def communicate_with_service(cluster_ip, path="/"):
    #connect with the cluster ip
    url = f"http://{cluster_ip}{path}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to communicate at {url}. Error: {e}")
        return None

if __name__ == "__main__":

    service_name = input("Enter the service name: ")
    namespace = input("Enter the namespace (default if empty): ")
    namespace = namespace if namespace else 'default'
    ip = get_cluster_ip(service_name, namespace)
    MY_SERVICE_CLUSTER_IP = ip

    if not MY_SERVICE_CLUSTER_IP:
        print("Please set the MY_SERVICE_CLUSTER_IP environment variable.")
        exit(1)

    response = communicate_with_service(MY_SERVICE_CLUSTER_IP)
    if response:
        print("Response from the service:")
        print(response)
