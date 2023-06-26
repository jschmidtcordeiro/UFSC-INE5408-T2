import multiprocessing

from validations import validate_column, validate_line, validate_region
from concurrent.futures import ThreadPoolExecutor
from SudokuThread import SudokuThread, Semaphore

"""
This is a file with multiple Game validations functions,
create threads and print results functions.

"""


def create_threads(n: int) -> list[SudokuThread]:
    """ Creates the threads

    Parameters
    ----------
    n : int
        The number of threads to be created

    Return
    ------
    list[SudokuThread]
        The list of threads created (SudokuThread's elements)
    
    """
    
    threads = []
    for _ in range(n):        
        finished_lock = Semaphore(0)
        main_thread_lock = Semaphore(0)

        thread = SudokuThread(
            lock=main_thread_lock,
            finished_lock=finished_lock,
            id=_
        )

        thread.start()
        threads.append(thread)
    
    return threads


def print_results(results: dict[int, str], process_number: int, n_threads: int) -> None:
    """ Print the results of the validation of a puzzle

    Parameters
    ----------
    results : dict
        The dictionary containing one result string for each validated puzzle
    process_number : int
        The number of the process that is being executed
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None
    
    """
    if len(results.keys()) == 0:
        print(f"Processo {process_number}: 0 erros encontrados")
        return
    
    errors = []
    n_erros = 0

    for i in range(n_threads):
        if i in results:
            n_erros += len(results[i])
            error = f"T{i+1}: "
            lines = []
            columns = []
            regions = []
            results[i] = sorted(results[i])
            for res in results[i]:
                if "L" in res:
                    lines.append(res)
                elif "C" in res:
                    columns.append(res)
                else:
                    regions.append(res)
            
            error += ', '.join(lines + columns + regions)
            errors.append(error)
    
    errors = '; '.join(errors)
    print(f"Processo {process_number}: {n_erros} erros encontrados ({errors})")


def validate_game_creating_threads_once(solutions: list[list[list[int]]], solution_number, n_threads) -> None:
    """ Validates the game creating threads once and dividing
    the validations for the number of threads in each process

    Parameters
    ----------
    solution : list[list[list[int]]]
        The solution that one process is going to validate
    solution_number : int
        The number of the puzzle that is being validated
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None
    
    """
    process_number = multiprocessing.current_process().name[8:]
    functions_list = [validate_line, validate_column, validate_region]
    threads = create_threads(n_threads)
    for i in range(len(solutions)):
        print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
        results = {}
        n_funcition = 0
        
        while n_funcition != 27:
            for thread in threads:
                if n_funcition == 27:
                    thread.reset(target=None, args=None) # a thread não executa em tal iteração
                    thread.lock.release()
                    continue

                thread.reset(target=functions_list[n_funcition % 3], args=(n_funcition//3, solutions[i], ))
                thread.lock.release() # indica que a thread já pode começar a executar a função destinada a ela
                
                n_funcition +=1
        
            for thread in threads:
                thread.finished_lock.acquire() # espera até que a thread termine de executar a função
                
                if thread.result is None:
                    continue

                result, thread_num = thread.result
                if thread_num in results.keys():
                    results[thread_num].add(result)
                else:
                    results[thread_num] = set([result])

        print_results(results, process_number, n_threads)
        
    for thread in threads:
        thread.stop()

def validate_game_creating_threads_once_and_using_thread_pool(solutions: list[list[list[int]]], solution_number: int, n_threads: int) -> None:
    """ Validates the game using the creating threads once
    and thread pool executor method

    Parameters
    ----------
    solution : list[list[list[int]]]
        The solutions that one process is going to validate
    solution_number : int
        The number of the puzzle that is being validated
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None

    """
    process_number = multiprocessing.current_process().name[8:]
    with ThreadPoolExecutor(max_workers=n_threads, thread_name_prefix="Thread") as pool:
        functions_list = [validate_line, validate_column, validate_region]

        for i,solution in enumerate(solutions):
            print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
            results = {}
            
            futures = []
            for j in range(27):
                futures.append(pool.submit(functions_list[j % 3], j//3, solution))

            
        
            for future in futures:
                result = future.result()
                
                if result is None:
                    continue

                error, thread_num = result
                if thread_num in results.keys():
                    results[thread_num].add(error)
                else:
                    results[thread_num] = set([error])

            print_results(results, process_number, n_threads)

def validate_game_thread_pool_executor(solutions: list[list[list[int]]], solution_number: int, n_threads: int) -> None:
    """ Validates the game using the thread pool executor
    method

    Parameters
    ----------
    solution : list[list[list[int]]]
        The solutions that one process is going to validate
    solution_number : int
        The number of the puzzle that is being validated
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None

    """
    process_number = multiprocessing.current_process().name[8:]

    for i, solution in enumerate(solutions):
        with ThreadPoolExecutor(max_workers=n_threads, thread_name_prefix="Thread") as pool:
            functions_list = [validate_line, validate_column, validate_region]
        
            print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
            results = {}
            
            futures = []
            for j in range(27):
                futures.append(pool.submit(functions_list[j % 3], j//3, solution))

            
        
            for future in futures:
                result = future.result()
                
                if result is None:
                    continue

                error, thread_num = result
                if thread_num in results.keys():
                    results[thread_num].add(error)
                else:
                    results[thread_num] = set([error])

            print_results(results, process_number, n_threads)


def validate_game_sequentially(solutions: list[list[list[int]]], solution_number: int, n_threads: int) -> None:
    """ Validates the game sequentially

    Parameters
    ----------
    solution : list[list[list[int]]]
        The solutions that one process is going to validate
    solution_number : int
        The number of the puzzle that is being validated
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None

    """
    process_number = multiprocessing.current_process().name[8:]

    for i, solution in enumerate(solutions):
        functions_list = [validate_line, validate_column, validate_region]
    
        print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
        
        results = {}
        for j in range(27):
            func = functions_list[j % 3]
            result = func(j//3, solution)

            if result is None:
                continue

            error, thread_num = result
            if thread_num in results.keys():
                results[thread_num].add(error)
            else:
                results[thread_num] = set([error])

        print_results(results, process_number, n_threads)
