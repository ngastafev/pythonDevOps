# tests/test_ci_agents_async.py
import asyncio
import time
import pytest
from unittest.mock import patch
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

        execution_time = await simulate_io_task_async(duration)
        results.append((task_id, execution_time))

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
    return total_time

# --- Тесты ---

@pytest.mark.asyncio
async def test_run_asyncio_simulation_basic():
    tasks = [(0, 0.1), (1, 0.1)]
    time_taken = await run_asyncio_simulation(tasks)
    assert time_taken >= 0.0

@pytest.mark.asyncio
async def test_run_multiprocessing_simulation_basic():
    tasks = [(0, 0.0), (1, 0.0)]
    time_taken = await run_multiprocessing_simulation(tasks)
    assert time_taken >= 0.0

@pytest.mark.asyncio
async def test_asyncio_semaphore_limited_concurrent_agents():
    active_agents = []
    max_active = 0

    async def tracked_io_task(duration):
        active_agents.append("agent")
        nonlocal max_active
        max_active = max(max_active, len(active_agents))
        await asyncio.sleep(duration)
        active_agents.remove("agent")
        return duration

    with patch('__main__.simulate_io_task_async', side_effect=tracked_io_task):
        tasks = [(i, 0.01) for i in range(5)]
        await run_asyncio_simulation(tasks)

    assert max_active <= N_AGENT

@pytest.mark.asyncio
async def test_asyncio_results_sorted():
    tasks = [(2, 0.1), (0, 0.1), (1, 0.1)]
    with patch('__main__.simulate_io_task_async', side_effect=lambda d: d):
        task_queue = asyncio.Queue()
        results = []
        semaphore = asyncio.Semaphore(N_AGENT)
        for t in tasks:
            task_queue.put_nowait(t)

        agent_tasks = [
            asyncio.create_task(simulate_ci_agent_async(i, task_queue, results, semaphore))
            for i in range(N_AGENT * 2)
        ]
        await asyncio.gather(*agent_tasks)
        sorted_results = sorted(results, key=lambda x: x[0])
        assert results == sorted_results

def test_cpu_intensive_pipeline_step():
    time_taken = cpu_intensive_pipeline_step(1)
    assert isinstance(time_taken, float)
    assert time_taken >= 0
