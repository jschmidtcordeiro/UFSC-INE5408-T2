import subprocess
from time import perf_counter


def test_function(function_name, sequential_time):
    run_and_print_time(1, 2, function_name, sequential_time)
    run_and_print_time(2, 1, function_name, sequential_time)
    run_and_print_time(4, 4, function_name, sequential_time)
    run_and_print_time(4, 16, function_name, sequential_time)
    run_and_print_time(6, 16, function_name, sequential_time)

def run_and_print_time(n_process, n_threads, function_name, sequential_time = None):
    begin = perf_counter()
    args = [
        "python3",
        "main.py",
        "input-big.txt",
        str(n_process),
        str(n_threads),
        function_name
    ]
    subprocess.run(args, stdout=subprocess.DEVNULL)
    end = perf_counter()

    result = f"{function_name}: {n_process} {n_threads} = {end - begin:.3f} segundos!"
    if sequential_time is not None:
        result += f" --> speedup = {(end - begin)/sequential_time}"
    print(result)

    return end - begin

def print_function_name(function_name):
    print(10*"=" + ' ' + function_name + ' ' + 10*'=')

print("Funçao testada: [n processos] [n threads] [tempo em segundos]")

print_function_name("validate_game_sequentially")
sequential_time = run_and_print_time(1, 1, "validate_game_sequentially")

print_function_name("validate_game_creating_threads_once")
test_function("validate_game_creating_threads_once", sequential_time)

print_function_name("validate_game_creating_threads_once_and_using_thread_pool")
test_function("validate_game_creating_threads_once_and_using_thread_pool", sequential_time)

print_function_name("validate_game_thread_pool_executor")
test_function("validate_game_thread_pool_executor", sequential_time)

print_function_name("validate_many_games_at_once")
test_function("validate_many_games_at_once", sequential_time)
