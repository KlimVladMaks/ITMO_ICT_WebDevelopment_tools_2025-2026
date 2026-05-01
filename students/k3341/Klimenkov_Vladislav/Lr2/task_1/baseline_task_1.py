import time


N = 200_000_000


def calculate_sum(start, end):
    total = 0
    for i in range(start, end + 1):
        total += i
    return total


def single_thread():
    start_time = time.perf_counter()
    total = calculate_sum(1, N)
    elapsed = time.perf_counter() - start_time
    return total, elapsed


if __name__ == "__main__":
    total, elapsed = single_thread()
    expected = N * (N + 1) // 2
    print(f"Однопоточный режим")
    print(f"Сумма: {total:,} (совпадает: {total == expected})")
    print(f"Время: {elapsed:.2f} сек")
