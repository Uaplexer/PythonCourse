import random


def is_local_minimum(matrix, row, col):
    current_value = matrix[row][col]
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    neighbors = [matrix[i][j] for i in range(max(0, row - 1), min(row + 2, num_rows))
                 for j in range(max(0, col - 1), min(col + 2, num_cols)) if (i, j) != (row, col)]
    return all(current_value < neighbor for neighbor in neighbors)



def find_local_minimums(matrix):
    return sum(1 for row in range(len(matrix)) for col in range(len(matrix[0])) if is_local_minimum(matrix, row, col))


def matrix_output(cols, rows):
    return [[random.randint(-8, 20) for _ in range(cols)] for _ in range(rows)]


def sum_of_upper_numbers(matrix):
    return sum(matrix[i][j] for j in range(len(matrix[0])) for i in range(len(matrix)) if j > i)


def print_matrix(matrix):
    for row in matrix:
        print(row)


cols = int(input('Enter number of columns: '))
rows = int(input('Enter number of rows: '))

matrix = matrix_output(cols, rows)
print_matrix(matrix)
print(f'Number of local minimums: {find_local_minimums(matrix)}')
print(f'Sum of numbers above the main diagonal: {sum_of_upper_numbers(matrix)}')
