import sys
import numpy as np
import time

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

if __name__ == "__main__":
    n_iteration = int(sys.argv[2])
    results = []
    for i in range(n_iteration):
        arr = np.random.randint(1, 10000, 10000)
        start_time = time.time()
        bubble_sort(arr)
        end_time = time.time()
        results.append(end_time - start_time)
    
    avg_time = sum(results) / n_iteration
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    output = f"Function run time: {avg_time} seconds\nCurrent time: {current_time}"
    print(output)
