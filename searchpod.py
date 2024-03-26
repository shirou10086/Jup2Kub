import subprocess
import re
#a helper function to find pod by matching pod name
def find_pod_by_pattern(pattern):
    try:
        # get all pods listed by kubectl
        result = subprocess.run(["kubectl", "get", "pods"], stdout=subprocess.PIPE, text=True, check=True)
        pods = result.stdout.splitlines()

        # get pod by pattern

        for pod in pods:
            if re.search(pattern, pod):
                # get the first pod
                return pod.split()[0]

    except subprocess.CalledProcessError as e:
        print(f"processError: {e}")
        return None

# a demo of how to use:
pod_name_pattern = "pod-0-.*"
pod_name = find_pod_by_pattern(pod_name_pattern)
if pod_name:
    print(f"foundPod: {pod_name}")
else:
    print("Unable to found Pod")
