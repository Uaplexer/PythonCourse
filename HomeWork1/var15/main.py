import random


def matrix_output(cols, rows):
    return [[random.randint(-8, 20) for _ in range(cols)] for _ in range(rows)]


def first_col_with_zero(matrix):
    for row in matrix:
        for col_i, col in enumerate(row, start=1):
            if not col:
                return col_i
    return None


def find_sums_of_negative_even_rows(matrix):
    return [sum(elem for elem in row if elem < 0 and elem % 2 == 0) for row in matrix]


def sort_matrix_by_neg_even_sum(matrix, sum_list):
    return sorted(matrix, key=lambda row: sum_list[matrix.index(row)], reverse=True)


def print_matrix(matrix):
    for row in matrix:
        print(row)
    print('\n')


cols = int(input('Enter number of columns: '))
rows = int(input('Enter number of rows: '))

matrix = matrix_output(cols, rows)
print('Matrix: ')
print_matrix(matrix)
sums = find_sums_of_negative_even_rows(matrix)
print('Sorted matrix: ')
print_matrix(sort_matrix_by_neg_even_sum(matrix, sums))

print(f'First column with zero in matrix: {first_col_with_zero(matrix)}')
