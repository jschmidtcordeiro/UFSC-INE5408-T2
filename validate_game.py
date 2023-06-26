import multiprocessing

from queue import Queue
from threading import Thread
from validations import validate_column, validate_line, validate_region
from concurrent.futures import ThreadPoolExecutor, Future
from SudokuThread import SudokuThread, Semaphore
from typing import Callable

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


def print_results(results: dict[int, list[str]], process_number: int, n_threads: int = None) -> None:
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

    for thread_num in results.keys():
        n_erros += len(results[thread_num])
        error = f"T{thread_num+1}: "
        lines = []
        columns = []
        regions = []
        results[thread_num] = sorted(results[thread_num])
        for res in results[thread_num]:
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



def handle_results(queue: Queue, n_solutions: int, process_number: int) -> None:
    """
    - Recebe um Future enviado pela `queue` representando o resultado de uma validação de uma solução
    - Uma solução validada é printada qunado o seu número de validações for igual a 27 e 
      todos as soluções anteriores a ela já terem sido printadas
    """
    
    # cada dicionário da lista representa uma solução validada pelo processo
    # As chaves do dicionários são os identificadores das threads que realizaram a validação.
    # O svalores são os erros encontrados pelas threads
    validated_solutions: list[dict[int, list[str] | None]] = [dict() for _ in range(n_solutions)]

    # Lista com contadores indicando a quantidade de validações concluídas de cada resultado.
    # Uma solução validada só é printada qunado o seu número de validações for igual a 27 e todos as soluções anteriores a ela já terem sido printadas
    validation_counters: list[int] = [0 for _ in range(n_solutions)]

    # Indica o número da solução que será printada a seguir
    solution_to_print = 0


    """
        - Enquanto ainda haver soluções a serem printadas, recebe uma validação de alguma solução e atualiza os dados referentes a ela.
        - Caso todas as validações da solução atual tenham sido realizadas, printa os erros encontrados
    """
    while solution_to_print < n_solutions:
        # - A queue inicialmente retorna um future. Quando o resultado de tal future for obtido, ele retornaŕa uma tupla contendo tais elementos:
        #   - número da solução validada
        #   - outra tupla contendo: O erro encontrado durante a validação e athread que encontrou tal erro. 
        #     Caso nenhum erro seja encontrado, esse elemento será None


        future: Future = queue.get()
        
        # Cada resultado retorna uma lista contendo uma tupla que representa uma validação específica.
        # Cada valiadção é composta pelo número da solução a qual ela está relacionada e outra tupla contento
        # o erro encontrado e a thread que o encontrou. Caso nenhum erro tenha sido encontrado, a última tupla será None
        results: list[tuple[int, tuple[str, int] | None]] = future.result()
        for solution_number, error_info in results:
            validation_counters[solution_number] += 1

            # se algum erro foi encontrado
            if error_info is not None:
                error_msg, thread_number = error_info

                if  thread_number in validated_solutions[solution_number].keys():
                    validated_solutions[solution_number][thread_number].append(error_msg)
                else:
                    validated_solutions[solution_number][thread_number] = [error_msg]
            

            # se a validação da solução atual já pode ser printada
            if validation_counters[solution_to_print] == 27:
                print_results(validated_solutions[solution_number], process_number)
                solution_to_print +=1


def execute_validations(validations_to_execute: list[Callable[[], tuple[int, tuple[str, int]]]]) -> None:
    results = []
    for validation in validations_to_execute:
        results.append(validation())
    return results


def validate_many_games_at_once(solutions: list[list[list[int]]], solution_number: int, n_threads: int) -> None:
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
    with ThreadPoolExecutor(max_workers=n_threads, thread_name_prefix="Thread") as pool:
        process_number = multiprocessing.current_process().name[8:]
        functions_list = [validate_line, validate_column, validate_region]
        queue = Queue()

        result_handler = Thread(target=handle_results, args=(queue, len(solutions), process_number))
        result_handler.start()

        validation_batch = [] # lista contendo validações que serão realizadas por uma única thread
        for i,solution in enumerate(solutions):
            print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
            for j in range(27):
                def validation(
                        solution_number = i,
                        func = functions_list[j % 3],
                        index = j//3,
                        solution = solution
                ):
                    return solution_number, func(index, solution)


                validation_batch.append(validation)

                if len(validation_batch) == 10 or (i == len(solutions) - 1 and j == 26):
                    future = pool.submit(execute_validations, validation_batch)
                    validation_batch = []

                    queue.put(future)

        result_handler.join()
