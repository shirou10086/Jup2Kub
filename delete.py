from kubernetes import client, config
#this function deletes all the related pods/images/files and other resources
def delete_statefulset_resources(name, count):
    config.load_kube_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    for i in range(count + 1):
        resource_name = f"{name}-{i}"

        # delete StatefulSet
        try:
            apps_v1.delete_namespaced_stateful_set(name=resource_name, namespace="default")
            print(f"StatefulSet {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting StatefulSet {resource_name}: {e}")

        # delete PersistentVolumeClaim
        try:
            v1.delete_namespaced_persistent_volume_claim(name=resource_name, namespace="default")
            print(f"PersistentVolumeClaim {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting PersistentVolumeClaim {resource_name}: {e}")

        # delete services
        try:
            v1.delete_namespaced_service(name=resource_name, namespace="default")
            print(f"Service {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting Service {resource_name}: {e}")

        # delete PersistentVolume
        try:
            v1.delete_persistent_volume(name=resource_name)
            print(f"PersistentVolume {resource_name} deleted.")
        except client.rest.ApiException as e:
            print(f"Error deleting PersistentVolume {resource_name}: {e}")
import os
import subprocess

def get_docker_images():
    try:
        # get all Docker images
        result = subprocess.run(['docker', 'images', '--format', '{{.Repository}}:{{.Tag}}'], capture_output=True, text=True, check=True)
        return result.stdout.strip().split('\n')
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while fetching Docker images: {e}")
        return []

def delete_docker_image(image_tag):
    try:
        # delete   Docker image by tag
        subprocess.run(['docker', 'rmi', image_tag], check=True)
        print(f"Deleted Docker image: {image_tag}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while deleting Docker image '{image_tag}': {e}")

import os
import shutil

def delete_directory(path):
    # check if direct exist
    if os.path.exists(path):
        # use shutil.rmtree delete files under direct
        shutil.rmtree(path)
        print(f"Directory '{path}' has been deleted.")
    else:
        print(f"Directory '{path}' does not exist.")

def main():
    name = "cell"  # StatefulSet basic name
    count = int(input("Enter the number x to delete cells from 0 to x: "))
    delete_statefulset_resources(name, count)
    output_dir = './example/output'
    docker_images = get_docker_images()

    for file in os.listdir(output_dir):
        if file.endswith('.py'):
            image_tag = file.split('.')[0]
            full_image_tag = next((img for img in docker_images if img.startswith(image_tag + ':')), None)
            if full_image_tag:
                delete_docker_image(full_image_tag)
    directory_path = output_dir
    delete_directory(directory_path)

if __name__ == "__main__":
    main()
