import subprocess
import sys


scripts = [
    "baseline_task_1.py",
    "threading_task_1.py",
    "multiprocessing_task_1.py",
    "asyncio_task_1.py"
]


def run_script(script_name):
    print(f"\n--- Запуск {script_name} ---")
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            check=False,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr, file=sys.stderr)
        if result.returncode != 0:
            print(f"⚠️  {script_name} завершился с кодом {result.returncode}")
        else:
            print(f"✅ {script_name} выполнен успешно")
        return result.returncode
    except FileNotFoundError:
        print(f"❌ Файл {script_name} не найден!", file=sys.stderr)
        return 1


def main():
    exit_codes = []
    for script in scripts:
        code = run_script(script)
        exit_codes.append(code)
    
    print("\n=== Итоговые коды возврата ===")
    for script, code in zip(scripts, exit_codes):
        print(f"{script}: {code}")
    
    if any(exit_codes):
        sys.exit(1)


if __name__ == "__main__":
    main()
