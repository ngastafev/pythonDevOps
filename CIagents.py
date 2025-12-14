import time
import queue
import random
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

# Конфигурация симуляции
NUM_TASKS = 20  #Кол-во задач
N_AGENT = 3   #Кол-во агентов
TASK_DURATION_MIN = 0.5 #Минимальное время на выполнение задачи
TASK_DURATION_MAX = 1.5 #Максимальное время на выполнение задачи

#I/O
def simulate_io_task(duration):
    time.sleep(duration)
    return duration

#Симуляция тяжелой задачи на проц
def cpu_intensive_pipeline_step(task_id):
    start_time = time.perf_counter()
    target_range = 1000 + (task_id % 100) * 50 # Изменяем размер задачи в зависимости от ID
    primes = []
    for num in range(2, target_range):
        is_prime = True
        for i in range(2, int(num**0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    return elapsed


def simulate_ci_agent_thread(agent_id, task_queue, results_queue, semaphore):
    while True:
        with semaphore:
            try:
                task_id, duration = task_queue.get_nowait()
            except queue.Empty:
                break

        print(f"Thread Agent {agent_id} started task {task_id}")
        execution_time = simulate_io_task(duration)
        print(f"Thread Agent {agent_id} finished task {task_id} in {execution_time:.2f}s")
        results_queue.put((task_id, execution_time))
        task_queue.task_done()

    print(f"Thread Agent {agent_id} shutting down.")


def run_threading_simulation(tasks):
    print("\nThreading Simulation ")
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    semaphore = threading.Semaphore(N_AGENT)

    for task_id, duration in tasks:
        task_queue.put((task_id, duration))

    start_time = time.perf_counter()

    with ThreadPoolExecutor(max_workers=N_AGENT * 2) as executor:
        futures = [
            executor.submit(simulate_ci_agent_thread, i, task_queue, results_queue, semaphore)
            for i in range(N_AGENT * 2) # Запускаем N_AGENT * 2 потоков
        ]
        for future in futures:
            future.result()

    end_time = time.perf_counter()
    total_time = end_time - start_time

    thread_results = []
    while not results_queue.empty():
        thread_results.append(results_queue.get())
    thread_results.sort(key=lambda x: x[0])

    print(f"Threading Total Time: {total_time:.2f}s")
    print(f"Threading Results: {thread_results}")
    return total_time


def run_multiprocessing_simulation(tasks):
    print("\nMultiprocessing Simulation ")
    task_ids = [task_id for task_id, _ in tasks]

    start_time = time.perf_counter()

    with ProcessPoolExecutor(max_workers=N_AGENT) as executor:
        results = list(executor.map(cpu_intensive_pipeline_step, task_ids))

    end_time = time.perf_counter()
    total_time = end_time - start_time

    mp_results = [(task_id, exec_time) for task_id, exec_time in zip(task_ids, results)]
    print(f"Multiprocessing Total Time: {total_time:.2f}s")
    print(f"Multiprocessing Results: {mp_results}")
    return total_time


if __name__ == "__main__":
    tasks = [
        (i, random.uniform(TASK_DURATION_MIN, TASK_DURATION_MAX))
        for i in range(NUM_TASKS)
    ]

    print(f"Simulating {NUM_TASKS} CI tasks with {N_AGENT} max agents...")

    threading_time = run_threading_simulation(tasks)
    multiprocessing_time = run_multiprocessing_simulation(tasks)

    print("\n Summary")
    print(f"Threading Total Time: {threading_time:.2f}s")
    print(f"Multiprocessing Total Time: {multiprocessing_time:.2f}s")
