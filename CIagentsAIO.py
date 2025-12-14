import asyncio
import time
import random
from concurrent.futures import ProcessPoolExecutor

NUM_TASKS = 20
N_AGENT = 3
TASK_DURATION_MIN = 0.5
TASK_DURATION_MAX = 1.5

def cpu_intensive_pipeline_step(task_id):
    start_time = time.perf_counter()
    target_range = 1000 + (task_id % 100) * 50
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

def run_cpu_intensive_tasks(task_ids):
    return list(map(cpu_intensive_pipeline_step, task_ids))

async def run_multiprocessing_simulation(tasks):
    task_ids = [task_id for task_id, _ in tasks]
    start_time = time.perf_counter()

    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=N_AGENT) as executor:
        results = await loop.run_in_executor(executor, run_cpu_intensive_tasks, task_ids)

    end_time = time.perf_counter()
    total_time = end_time - start_time
    mp_results = [(task_id, exec_time) for task_id, exec_time in zip(task_ids, results)]
    print(f"Multiprocessing Total Time: {total_time:.2f}s")
    print(f"Multiprocessing Results: {mp_results}")
    return total_time

async def simulate_io_task_async(duration):
    await asyncio.sleep(duration)
    return duration

async def simulate_ci_agent_async(agent_id, task_queue, results, semaphore):
    while True:
        async with semaphore:
            try:
                task_id, duration = task_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        print(f"Async Agent {agent_id} started task {task_id}")
        execution_time = await simulate_io_task_async(duration)
        print(f"Async Agent {agent_id} finished task {task_id} in {execution_time:.2f}s")
        results.append((task_id, execution_time))

    print(f"Async Agent {agent_id} shutting down.")

async def run_asyncio_simulation(tasks):
    task_queue = asyncio.Queue()
    results = []
    semaphore = asyncio.Semaphore(N_AGENT)

    for task_id, duration in tasks:
        task_queue.put_nowait((task_id, duration))

    start_time = time.perf_counter()

    agent_tasks = [
        asyncio.create_task(simulate_ci_agent_async(i, task_queue, results, semaphore))
        for i in range(N_AGENT * 2)
    ]

    await asyncio.gather(*agent_tasks)

    end_time = time.perf_counter()
    total_time = end_time - start_time

    results.sort(key=lambda x: x[0])
    print(f"AsyncIO Total Time: {total_time:.2f}s")
    print(f"AsyncIO Results: {results}")
    return total_time

if __name__ == "__main__":
    tasks = [
        (i, random.uniform(TASK_DURATION_MIN, TASK_DURATION_MAX))
        for i in range(NUM_TASKS)
    ]

    print(f"Simulating {NUM_TASKS} CI tasks with {N_AGENT} max agents...")

    asyncio_time = asyncio.run(run_asyncio_simulation(tasks))
    multiprocessing_time = asyncio.run(run_multiprocessing_simulation(tasks))

    print("\nSummary")
    print(f"AsyncIO Total Time: {asyncio_time:.2f}s")
    print(f"Multiprocessing Total Time: {multiprocessing_time:.2f}s")
