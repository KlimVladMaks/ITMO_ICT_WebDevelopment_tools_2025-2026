import asyncio
import time


N = 200_000_000
NUM_WORKERS = 8


def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


async def calculate_sum_async(start, end):
    return await asyncio.to_thread(calculate_sum, start, end)


async def main_async():
    step = N // NUM_WORKERS
    ranges = []
    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else N
        ranges.append((start, end))
    
    tasks = [calculate_sum_async(s, e) for s, e in ranges]
    results = await asyncio.gather(*tasks)
    return sum(results)


def run_async():
    start_time = time.perf_counter()
    total = asyncio.run(main_async())
    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = run_async()
    expected = N * (N + 1) // 2
    print(f"Asyncio + to_thread ({NUM_WORKERS} потоков)")
    print(f"Сумма: {total:,} (верно: {total == expected})")
    print(f"Время: {elapsed:.2f} сек")
