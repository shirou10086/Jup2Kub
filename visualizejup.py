import psutil
import matplotlib.pyplot as plt
import time
import threading
import sys
#a helper function to monitor the current running jupyter notebook
pid = 184130
  # 替换为您要监控的进程的PID
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

# 创建并启动监控线程
monitor_thread = threading.Thread(target=monitor_process)
monitor_thread.start()

# 创建并启动监听输入的线程
exit_thread = threading.Thread(target=listen_for_exit_command)
exit_thread.start()

# 等待监控线程完成
monitor_thread.join()

# 绘图
plt.figure(figsize=(10, 5))

# 绘制CPU时间图
plt.subplot(1, 2, 1)
plt.plot(cpu_times, color='blue')
plt.title('CPU Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('CPU Usage (%)')

# 绘制内存使用图
plt.subplot(1, 2, 2)
plt.plot(memory_usage, color='red')
plt.title('Memory Usage Over Time')
plt.xlabel('Time (seconds)')
plt.ylabel('Memory Usage (MB)')

# 显示图表
plt.tight_layout()
plt.show()
