import random

cols = int(input('Enter number of columns: '))
rows = int(input('Enter number of rows: '))

matrix = [[random.randint(-8, 20) for _ in range(cols)] for _ in range(rows)]


def find_local_minimum(matrix):
    def is_local_minimum(row, col):
        current_element = matrix[row][col]
        top_neighbor = matrix[row - 1][col] if row > 0 else float('inf')
        bottom_neighbor = matrix[row + 1][col] if row < len(matrix) - 1 else float('inf')
        left_neighbor = matrix[row][col - 1] if col > 0 else float('inf')
        right_neighbor = matrix[row][col + 1] if col < len(matrix[0]) - 1 else float('inf')

        return current_element <= top_neighbor and current_element <= bottom_neighbor and \
            current_element <= left_neighbor and current_element <= right_neighbor

    counter = 0
    for row in range(len(matrix)):
        for col in range(len(matrix[0])):
            if is_local_minimum(row, col):
                counter += 1

    return counter


def print_matrix(matrix):
    for row in matrix:
        print(row)


def sum_of_upper_numbers(matrix):
    sum = 0
    rows = len(matrix)
    cols = len(matrix[0])

    for i in range(rows):
        for j in range(cols):
            if j > i:
                sum += matrix[i][j]
    return sum

print_matrix(matrix)

print(f'Number of local minimums: {find_local_minimum(matrix)}')
print(f'Sum of numbers above the main diagonal: {sum_of_upper_numbers(matrix)}')
