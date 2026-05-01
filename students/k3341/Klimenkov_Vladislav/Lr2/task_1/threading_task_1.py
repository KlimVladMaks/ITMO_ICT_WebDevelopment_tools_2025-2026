import threading
import time


N = 200_000_000
NUM_WORKERS = 8


def calculate_sum(start, end, results, idx):
    total = 0
    for i in range(start, end + 1):
        total += i
    results[idx] = total


def main_threading():
    step = N // NUM_WORKERS
    ranges = []
    for i in range(NUM_WORKERS):
        start = i * step + 1
        end = (i + 1) * step if i != NUM_WORKERS - 1 else N
        ranges.append((start, end))
    
    results = [0] * NUM_WORKERS
    threads = []
    start_time = time.perf_counter()
    
    for idx, (s, e) in enumerate(ranges):
        t = threading.Thread(target=calculate_sum, args=(s, e, results, idx))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.perf_counter() - start_time
    total = sum(results)
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = main_threading()
    expected = N * (N + 1) // 2
    print(f"Threading ({NUM_WORKERS} потоков)")
    print(f"Сумма: {total:,} (верно: {total == expected})")
    print(f"Время: {elapsed:.2f} сек")
