import psutil
import matplotlib.pyplot as plt
import time
import threading
import sys

import subprocess
#a helper function to monitor the current running k8s programs

def find_first_process(name):
    try:
        # use pgrep -f  search process
        result = subprocess.run(['pgrep', '-f', name], check=True, stdout=subprocess.PIPE, text=True)
        pids = result.stdout.strip().split('\n')  # 获取输出并分割为PID列表
        return int(pids[0]) if pids[0] else None  # 返回第一个PID，如果有的话
    except subprocess.CalledProcessError:
        # pgrep unable to find process
        return None

# seach for  statefulset.py's Python file first PID
pid = find_first_process('main.py')

if pid:
    print(f"Found process with PID: {pid}")
else:
    print("No process found.")

process = psutil.Process(pid)

cpu_times = []
memory_usage = []
monitoring = True

def monitor_process():
    global monitoring
    while monitoring:
        cpu_times.append(process.cpu_percent(interval=1))
        memory_usage.append(process.memory_info().rss / 1024 / 1024)  # 将字节转换为MB

def listen_for_exit_command():
    global monitoring
    while True:
        if input().lower() == 'exit':
            monitoring = False
            break

#start monitor
monitor_thread = threading.Thread(target=monitor_process)
monitor_thread.start()

exit_thread = threading.Thread(target=listen_for_exit_command)
exit_thread.start()

monitor_thread.join()

# draw plot
plt.figure(figsize=(10, 5))

# draw cpu time plot
plt.subplot(1, 2, 1)
plt.plot(cpu_times, color='blue')
plt.title('CPU Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('CPU Usage (%)')

# draw memory use
plt.subplot(1, 2, 2)
plt.plot(memory_usage, color='red')
plt.title('Memory Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Memory Usage (MB)')

# show plot
plt.tight_layout()
plt.show()
