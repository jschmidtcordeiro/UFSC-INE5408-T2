from threading import Thread, Semaphore, current_thread
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from SudokuThread import SudokuThread
import numpy
## This is a file with the validations functions

def count_to_nine(list: list[int]) -> bool:
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
    for i in range(1,10):
        if i not in list:
            return False

    return True

def validate_line(line_number: int, matrix: list[int]) -> tuple[str, int]:
    from threading import current_thread
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
    str
        The information of an error, if there was an error
    int
        The number of the thread 
    """
    input_list = matrix[line_number]

    thread_name = current_thread().name
    thread_num = 1 if thread_name == "MainThread" else int(thread_name[7:])
    if not count_to_nine(input_list):
        return f"L{line_number+1}", thread_num

def validate_column(column_number: int, matrix: list[int]) -> tuple[str, int]:
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
    str
        The information of an error, if there was an error
    int
        The number of the thread 
    """
    input_list = []

    matrix_transpose = numpy.transpose(numpy.array(matrix))
    input_list = matrix_transpose[column_number]
    
    thread_name = current_thread().name
    thread_num = 1 if thread_name == "MainThread" else int(thread_name[7:])
    if not count_to_nine(input_list):
        return f"C{column_number+1}", thread_num

def validate_region(region_number: int, matrix: list[int]) -> tuple[str, int]:
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
    str
        The information of an error, if there was an error
    int
        The number of the thread 
    """
    input_list = []

    initial_point_line = ((region_number) // 3) * 3
    initial_point_column = ((region_number) % 3) * 3
    
    for i in range(initial_point_line, initial_point_line + 3):
        for j in range(initial_point_column, initial_point_column + 3):
            input_list.append(matrix[i][j])

    thread_name = current_thread().name
    thread_num = 1 if thread_name == "MainThread" else int(thread_name[7:])
    if not count_to_nine(input_list):
        return f"R{region_number+1}", thread_num
    
    





