import multiprocessing
import time


N = 200_000_000
NUM_WORKERS = 8


def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def main_multiprocessing():
    step = N // NUM_WORKERS
    ranges = []
    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else N
        ranges.append((start, end))
    
    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=NUM_WORKERS) as pool:
        results = pool.starmap(calculate_sum, ranges)
    elapsed = time.perf_counter() - start_time
    
    total = sum(results)
    return total, elapsed


if __name__ == "__main__":
    multiprocessing.freeze_support()
    total, elapsed = main_multiprocessing()
    expected = N * (N + 1) // 2
    print(f"Multiprocessing ({NUM_WORKERS} процессов)")
    print(f"Сумма: {total:,} (верно: {total == expected})")
    print(f"Время: {elapsed:.2f} сек")
