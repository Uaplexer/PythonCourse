import random

cols = int(input('Enter number of columns: '))
rows = int(input('Enter number of rows: '))

matrix = [[random.randint(-8, 20) for _ in range(cols)] for _ in range(rows)]


def multiplication_of_positive_rows(matrix):
    row_positive = []
    for row in matrix:
        if all(elem >= 0 for elem in row):
            row_result = 1
            for elem in row:
                row_result *= elem
            row_positive.append(row_result)
    return row_positive


def sum_of_parallel_diagonal(matrix):
    size = len(matrix)
    diagonals = []

    for i in range(1, size - 1):
        diagonals.append([matrix[j][j + i] for j in range(size - i)])

    for i in range(1, size - 1):
        diagonals.append([matrix[j + i][j] for j in range(size - i)])

    return max(sum(diagonal) for diagonal in diagonals)


def print_matrix(matrix):
    for row in matrix:
        print(row)


print_matrix(matrix)

print(f'Multiplication of positive rows: {multiplication_of_positive_rows(matrix)}')
print(f'Max sum of parallel diagonals: {sum_of_parallel_diagonal(matrix)}')
