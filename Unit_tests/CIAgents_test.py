import time
import queue
import random
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Конфигурация
NUM_TASKS = 20
N_AGENT = 3
TASK_DURATION_MIN = 0.5
TASK_DURATION_MAX = 1.5


# I/O задача
def simulate_io_task(duration):
    time.sleep(duration)
    return duration


# CPU задача
def cpu_intensive_pipeline_step(task_id):
    start_time = time.perf_counter()
    target_range = 1000 + (task_id % 100) * 50
    primes = []
    for num in range(2, target_range):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    end_time = time.perf_counter()
    return end_time - start_time


# Агент (threading)
def simulate_ci_agent_thread(agent_id, task_queue, results_queue, semaphore):
    while True:
        with semaphore:
            try:
                task_id, duration = task_queue.get_nowait()
            except queue.Empty:
                break
        execution_time = simulate_io_task(duration)
        results_queue.put((task_id, execution_time))
        task_queue.task_done()


def run_threading_simulation(tasks):
    task_queue = queue.Queue()
    results_queue = queue.Queue()
    semaphore = threading.Semaphore(N_AGENT)
    for t in tasks:
        task_queue.put(t)

    start_time = time.perf_counter()
    with ThreadPoolExecutor(max_workers=N_AGENT * 2) as executor:
        futures = [executor.submit(simulate_ci_agent_thread, i, task_queue, results_queue, semaphore) for i in
                   range(N_AGENT * 2)]
        for f in futures: f.result()

    end_time = time.perf_counter()
    thread_results = sorted([results_queue.get() for _ in range(results_queue.qsize())])
    return end_time - start_time, thread_results


# Multiprocessing
def run_multiprocessing_simulation(tasks):
    task_ids = [task_id for task_id, _ in tasks]
    start_time = time.perf_counter()
    with ProcessPoolExecutor(max_workers=N_AGENT) as executor:
        cpu_times = list(executor.map(cpu_intensive_pipeline_step, task_ids))
    end_time = time.perf_counter()
    mp_results = list(zip(task_ids, cpu_times))
    return end_time - start_time, mp_results


if __name__ == "__main__":
    tasks = [(i, random.uniform(TASK_DURATION_MIN, TASK_DURATION_MAX)) for i in range(NUM_TASKS)]

    threading_time, threading_res = run_threading_simulation(tasks)
    mp_time, mp_res = run_multiprocessing_simulation(tasks)

    print(f"Threading: {threading_time:.2f}s")
    print(f"Multiprocessing: {mp_time:.2f}s")
    # Threading быстрее для I/O. Multiprocessing для CPU.