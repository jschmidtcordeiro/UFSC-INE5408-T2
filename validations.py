from threading import Thread, Semaphore
from SudokuThread import SudokuThread
import numpy
## This is a file with the validation functions

# t = Thread().start()

class Value:
    def __init__(self, val = None):
        self.val = val
        
def validate_game(solutions, process_number, solution_number, n_threads):
    functions_list = [validate_line, validate_column, validate_region]
    threads: list[Thread] = []
    values = []
    n_funcition = 0
    for i in range(len(solutions)):
        print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
        
        while n_funcition != 27:
            for k in range(n_threads):
                if (n_funcition == 27):
                    break
                values.append(Value())
                threads.append(Thread(target=functions_list[n_funcition % 3], args=(n_funcition//3, solutions[i])))
                threads[k].start()
                n_funcition +=1
                
            for index,thread in enumerate(threads):
                thread.join()
                
            
            threads = []

def create_threads(n: int) -> list[SudokuThread]:
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

def validate_game_cereating_threads_once(solutions, process_number, solution_number, n_threads):
    functions_list = [validate_line, validate_column, validate_region]
    threads = create_threads(n_threads)
    for i in range(len(solutions)):
        print(f"Processo {process_number}: resolvendo quebra-cabeças {solution_number+i}")
        results = {}
        n_funcition = 0
        
        while n_funcition != 27:
            #z = 0
            for thread in threads:
                if n_funcition == 27:
                    #print(n_funcition+z); z += 1;
                    # TODO: ACHAR UM JEITO DE NÃO FAZER ISSO. passar a executar próxima outra solução?
                    thread.reset(target=None, args=None) # a thread não executa tal
                    thread.lock.release() # indica que a thread já pode começar a executar a função destinada a ela
                    continue

                thread.reset(target=functions_list[n_funcition % 3], args=(n_funcition//3, solutions[i], ))
                thread.lock.release() # indica que a thread já pode começar a executar a função destinada a ela
                
                n_funcition +=1
        
            for n, thread in enumerate(threads):
                thread.finished_lock.acquire() # espera até que a thread termine de executar a função
                
                if thread.result is None:
                    continue

                if n in results.keys():
                    results[n].add(thread.result)
                else:
                    results[n] = set([thread.result])

        print_results(results, process_number, n_threads)
        
    for thread in threads:
        thread.stop()
    
            

def count_to_nine(list):
    """ Count from 1 to 9 verifing if the list contains 
    one of each number

    Parameters
    ----------
    sound : list
        The list with the comlum, line or region numbers

    Return
    ------
    bool
        If it has an error, return false, if it's ok 
        return true
    """
    for i in range(1,9):
        if i not in list:
            return False

    return True

def validate_line(line_number, matrix):
    """ Define the initial point, final point and the steps to
    create a list of a line and call the count function

    Parameters
    ----------
    line_number : int
        The line number to calculate
    matrix : list
        The matrix

    Return
    ------
        TODO
    """
    input_list = matrix[line_number]
    
    if not count_to_nine(input_list):
        return f"L{line_number+1}"

def validate_column(column_number, matrix):
    """ Define the initial point, final point and the steps to
    create a list of a column and call the count function

    Parameters
    ----------
    column_number : int
        The column number to calculate
    matrix : list
        The matrix

    Return
    ------
        TODO
    """
    input_list = []

    matrix_transpose = numpy.transpose(numpy.array(matrix))
    input_list = matrix_transpose[column_number]

    # print(f"Region number {column_number}")
    # print(f"Initial point Line {initial_point_line}")
    # print(f"Initial point Column {initial_point_column}")
    # print(f"Input_list {input_list}")
    
    if not count_to_nine(input_list):
        return f"C{column_number+1}"

def validate_region(region_number, matrix):
    """ Define the initial point, final point and the steps to
    create a list of a region and call the count function

    Parameters
    ----------
    region_number : int
        The region number to calculate
    matrix : list
        The matrix

    Return
    ------
        TODO
    """
    input_list = []

    initial_point_line = ((region_number) // 3) * 3
    initial_point_column = ((region_number) % 3) * 3
    
    for i in range(initial_point_line, initial_point_line + 3):
        for j in range(initial_point_column, initial_point_column + 3):
            input_list.append(matrix[i][j])
    # print(f"Region number {region_number}")
    # print(f"Initial point Line {initial_point_line}")
    # print(f"Initial point Column {initial_point_column}")
    # print(f"Input_list {input_list}")
    if not count_to_nine(input_list):
        return f"R{region_number+1}"
    
    





