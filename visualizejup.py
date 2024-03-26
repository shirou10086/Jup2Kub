import psutil
import matplotlib.pyplot as plt
import time
import threading
import sys
#a helper function to monitor the current running jupyter notebook
pid = 184130
  # replace the PID to your pid of the process wanted to monitor
process = psutil.Process(pid)

cpu_times = []
memory_usage = []
monitoring = True

def monitor_process():
    global monitoring
    while monitoring:
        cpu_times.append(process.cpu_percent(interval=1))
        memory_usage.append(process.memory_info().rss / 1024 / 1024)

def listen_for_exit_command():
    global monitoring
    while True:
        if input().lower() == 'exit':
            monitoring = False
            break

# create and monitor the thread
monitor_thread = threading.Thread(target=monitor_process)
monitor_thread.start()

exit_thread = threading.Thread(target=listen_for_exit_command)
exit_thread.start()

# wait till stop
monitor_thread.join()

# draw figure
plt.figure(figsize=(10, 5))

# draw time plot here
plt.subplot(1, 2, 1)
plt.plot(cpu_times, color='blue')
plt.title('CPU Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('CPU Usage (%)')

# draw memory use plot
plt.subplot(1, 2, 2)
plt.plot(memory_usage, color='red')
plt.title('Memory Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Memory Usage (MB)')

# show plot
plt.tight_layout()
plt.show()
