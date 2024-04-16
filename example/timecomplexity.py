import numpy as np
import time
import os
output_file_dir = './data'
n_iteration = 1

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

start_time = time.time()
for i in range(n_iteration):
    random_numbers = np.random.randint(1, 10000, 10000)
    sorted_numbers = quick_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

with open(os.path.join(output_file_dir, "quick_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)

def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

start_time = time.time()
for i in range(n_iteration):
    random_numbers = np.random.randint(1, 10000, 10000)
    bubble_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

with open(os.path.join(output_file_dir, "bubble_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)


def fibonacci(n):
    if n <= 1:
        return n
    else:
        return(fibonacci(n-1) + fibonacci(n-2))

start_time = time.time()
for i in range(n_iteration):  
    fibonacci_numbers = [fibonacci(i) for i in range(40)]
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
with open(os.path.join(output_file_dir, "fibonacci_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)

def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i-1
        while j >=0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

start_time = time.time()
for i in range(n_iteration):
    random_numbers = np.random.randint(1, 10000, 10000)
    insertion_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
with open(os.path.join(output_file_dir, "insertion_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)

def selection_sort(arr):
    for i in range(len(arr)):
        min_idx = i
        for j in range(i+1, len(arr)):
            if arr[min_idx] > arr[j]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]

start_time = time.time()
for i in range(3):  # Repeat the sort 3 times to find the average time
    random_numbers = np.random.randint(1, 10000, 10000)
    selection_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
with open(os.path.join(output_file_dir, "selection_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)



def merge_sort(arr):
    if len(arr) > 1:
        mid = len(arr) // 2
        L = arr[:mid]
        R = arr[mid:]

        merge_sort(L)
        merge_sort(R)

        i = j = k = 0

        while i < len(L) and j < len(R):
            if L[i] < R[j]:
                arr[k] = L[i]
                i += 1
            else:
                arr[k] = R[j]
                j += 1
            k += 1

        while i < len(L):
            arr[k] = L[i]
            i += 1
            k += 1

        while j < len(R):
            arr[k] = R[j]
            j += 1
            k += 1

start_time = time.time()
for i in range(3):  # Repeat the sort 3 times to find the average time
    random_numbers = np.random.randint(1, 10000, 10000)
    merge_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
with open(os.path.join(output_file_dir, "merge_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)


def heapify(arr, n, i):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and arr[l] > arr[largest]:
        largest = l

    if r < n and arr[r] > arr[largest]:
        largest = r

    if largest != i:
        arr[i], arr[largest] = arr[largest], arr[i]
        heapify(arr, n, largest)

def heap_sort(arr):
    n = len(arr)

    # Build a maxheap.
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)

    # One by one extract elements
    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]  # swap
        heapify(arr, i, 0)

start_time = time.time()
for i in range(3):  # Repeat the sort 3 times to find the average time
    random_numbers = np.random.randint(1, 10000, 10000)
    heap_sort(random_numbers)
end_time = time.time()

res = f"Function run time: {(end_time - start_time) / n_iteration} seconds"
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
with open(os.path.join(output_file_dir, "heap_sort_times.txt"), "w") as file:
    file.write(res)
    file.write(current_time)
