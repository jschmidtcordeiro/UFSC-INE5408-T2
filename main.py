from sys import argv
from multiprocessing import Process
from os.path import exists
from concurrent.futures import ProcessPoolExecutor
import validate_game

## This is the main file of the program

def validate_input(argv) -> tuple[str, int, int]:
    """ Validate arguments in argv

    Parameters
    ----------
    argv : list
        list with the arguments to be validated

    Return
    ------
    tuple[str, int, int]
        tuple with the file that will be read and the number of processes and threads.

    """
    
    if len(argv) < 4:
        print("Uso: main.py [arquivo.txt] [número de processos] [número de threads]")
        exit(1)
    
    file = argv[1]
    if not exists(file):
        print("O arquivo indicado não existe")
        exit(1)
    
    try:
        n_process, n_threads = [int(x) for x in argv[2:4]]
    except:
        print("O a quantidade de threads ou processos deve ser um número inteiro!")
        exit(1)
    
    if n_process < 1 or n_threads < 1:
        print("O número de threads e processos deve ser pelo menos 1")
        exit(1)
    
    return file, n_process, n_threads 



def read_file(file: str) -> list[list[list[int]]]:
    """ Read the input file and create a list containing the various solutions on it

    Parameters
    ----------
    file : str
        path to the input file

    Return
    ------
    list[list[list[int]]]
        A list of matrices, where each one represents a solution

    """

    with open(file, "r") as f:
        lines = f.readlines()
    
    curr_line_index = 0
    matrices = []
    while curr_line_index < len(lines):
        # create an empty matrix
        matrix = [[0 for j in range(9)] for i in range(9)]

        for i in range(9):
            curr_line = lines[curr_line_index]
            for j in range(9):
                matrix[i][j] = int(curr_line[j])
        
            curr_line_index += 1

        curr_line_index += 1 # increment the index since theres an empty line between each matrix
        matrices.append(matrix)

                
    return matrices
   

def create_process(solutions: list[list[list[int]]], n_process: int, n_threads: int, validation_func) -> None:
    """ Creates the processes

    Parameters
    ----------
    solutions : list[list[list[int]]]
        The list of all of the solutions
    n_process : int
        The number of processes
    n_threads : int
        The number of threads that the program is using

    Return
    ------
    None
    
    """
    remainder = len(solutions) % n_process
    num_solutions = len(solutions) // n_process
    process: list[Process] = []
    begin = 0
    for i in range(n_process):
        end = begin + num_solutions
        
        if remainder > 0:
            end += 1
            remainder -= 1

        process.append(Process(target=validation_func, args=(solutions[begin:end], begin + 1, n_threads)))
        begin = end

    for proc in process:
        proc.start()

    for proc in process:
        proc.join()



if __name__ == "__main__":
    NUM_VALIDATIONS = 27
    file, n_process, n_threads = validate_input(argv)
    solutions = read_file(file)

    if n_process > len(solutions):
        n_process = len(solutions)

    if n_threads > NUM_VALIDATIONS:
        n_threads = NUM_VALIDATIONS


    validation_func = validate_game.validate_many_games_at_once
    if len(argv) > 4:
        if argv[4] == "validate_game_creating_threads_once":
            validation_func = validate_game.validate_game_creating_threads_once
        elif argv[4] == "validate_game_creating_threads_once_and_using_thread_pool":
            validation_func = validate_game.validate_game_creating_threads_once_and_using_thread_pool
        elif argv[4] == "validate_game_thread_pool_executor":
            validation_func = validate_game.validate_game_thread_pool_executor
        elif argv[4] == "validate_game_sequentially":
            validation_func = validate_game.validate_game_sequentially

    create_process(solutions, n_process, n_threads, validation_func)
