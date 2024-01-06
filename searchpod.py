import subprocess
import re

def find_pod_by_pattern(pattern):
    try:
        # 运行 kubectl 命令以获取所有 Pods
        result = subprocess.run(["kubectl", "get", "pods"], stdout=subprocess.PIPE, text=True, check=True)
        pods = result.stdout.splitlines()

        # 搜索符合模式的 Pod
        for pod in pods:
            if re.search(pattern, pod):
                # 返回找到的第一个符合模式的 Pod 名称
                return pod.split()[0]

    except subprocess.CalledProcessError as e:
        print(f"执行命令出错: {e}")
        return None

# 示例用法
pod_name_pattern = "pod-0-.*"
pod_name = find_pod_by_pattern(pod_name_pattern)
if pod_name:
    print(f"找到的 Pod 名称: {pod_name}")
else:
    print("未找到符合模式的 Pod")
