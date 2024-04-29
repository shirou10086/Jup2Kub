from kubernetes import client, config
from kubernetes.client.rest import ApiException
import json
import os
import shutil
import time

def delete_all_resources():
    # Load J2K_CONFIG
    with open("./J2K_CONFIG.json", 'r') as file:
        j2k_config = json.load(file)
    namespace = j2k_config['results-hub']['namespace']
    # Load kubeconfig
    config.load_kube_config()
    
    # Initialize API clients
    v1 = client.CoreV1Api()
    batch_v1 = client.BatchV1Api()
    apps_v1 = client.AppsV1Api()
    
    try:
        # Delete all Services
        v1.delete_collection_namespaced_service(namespace=namespace)
        print(f"All services deleted in namespace {namespace}.")
    except ApiException as e:
        print(f"Failed to delete services: {e}")

    try:
        # Delete all Jobs
        batch_v1.delete_collection_namespaced_job(namespace=namespace)
        print(f"All jobs deleted in namespace {namespace}.")
    except ApiException as e:
        print(f"Failed to delete jobs: {e}")

    try:
        # Delete all Pods
        v1.delete_collection_namespaced_pod(namespace=namespace)
        print(f"All pods deleted in namespace {namespace}.")
    except ApiException as e:
        print(f"Failed to delete pods: {e}")

    try:
        # Delete all StatefulSets
        apps_v1.delete_collection_namespaced_stateful_set(namespace=namespace)
        print(f"All statefulsets deleted in namespace {namespace}.")
    except ApiException as e:
        print(f"Failed to delete statefulsets: {e}")

    try:
        # Delete all PVCs
        v1.delete_collection_namespaced_persistent_volume_claim(namespace=namespace)
        print(f"All PVCs deleted in namespace {namespace}.")
    except ApiException as e:
        print(f"Failed to delete PVCs: {e}")

    try:
        # Delete all PVs
        v1.delete_collection_persistent_volume()
        print("All PVs deleted in the cluster.")
    except ApiException as e:
        print(f"Failed to delete PVs: {e}")

def create_reset_results_log():
    # Load J2K_CONFIG
    with open("./J2K_CONFIG.json", 'r') as file:
        j2k_config = json.load(file)
    rh_log_path = j2k_config['results-hub']['local-pv-path']

    # Check if the directory exists
    if os.path.exists(rh_log_path):
        # If the directory exists, remove all its contents
        for filename in os.listdir(rh_log_path):
            file_path = os.path.join(rh_log_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory and all its contents
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        # If the directory does not exist, create it
        try:
            os.makedirs(rh_log_path)
            print(f'Directory created: {rh_log_path}')
        except OSError as e:
            print(f'Failed to create directory {rh_log_path}. Reason: {e}')

def wait_for_jobs():
    # Load J2K_CONFIG
    with open("./J2K_CONFIG.json", 'r') as file:
        j2k_config = json.load(file)
    namespace = j2k_config['results-hub']['namespace']

    # Load the kubeconfig file to connect to the Kubernetes cluster
    config.load_kube_config()
    
    # Initialize the Kubernetes client for the BatchV1 API
    batch_v1 = client.BatchV1Api()
    
    while True:
        # Get the list of all jobs in the specified namespace
        jobs = batch_v1.list_namespaced_job(namespace)
        
        all_finished = True
        any_failed = False
        
        for job in jobs.items:
            # Check the status conditions for each job
            conditions = job.status.conditions
            if conditions:
                for condition in conditions:
                    if condition.type == 'Failed':
                        any_failed = True
                        break
            # Determine if the job is still active
            if job.status.active:
                all_finished = False
        
        # Exit loop if all jobs have finished
        if all_finished:
            break
        
        # Sleep for 1 second before the next check
        time.sleep(1)
    
    # Output the final status of the jobs
    if any_failed:
        print("Some jobs have failed, stop waiting!")
    else:
        print("All jobs have completed successfully.")

def clear_codegen_outputs():
    # Load J2K_CONFIG
    with open("./J2K_CONFIG.json", 'r') as file:
        j2k_config = json.load(file)
    output_dir = j2k_config['execution']['output-directory']

    # Check if the directory exists
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        try:
            # Recursively remove the directory and all its contents
            shutil.rmtree(output_dir)
            print(f"Successfully removed directory: {output_dir}")
        except Exception as e:
            print(f"Failed to remove directory: {output_dir}. Reason: {e}")
    else:
        print(f"The specified directory does not exist: {output_dir}")

def main():
    print("\nChoose a tool from the following:")
    print("1. Delete all resources in a specific namespace")
    print("2. Reset ResultsHub's logs")
    print("3. Wait for all jobs finish")
    print("4. Clear all codegen outputs")
    print("5. Exit")
    
    # Get user input
    choice = input("Enter your choice (1-5): ")
    
    # Process the choice
    if choice == '1':
        delete_all_resources()
    elif choice == '2':
        create_reset_results_log()
    elif choice == '3':
        wait_for_jobs()
    elif choice == '4':
        clear_codegen_outputs()
    elif choice == '5':
        print("Exiting toolbox.")
    else:
        print("Invalid input!")

if __name__ == "__main__":
    main()



