import random

cols = int(input('Enter number of columns: '))
rows = int(input('Enter number of rows: '))

matrix = [[random.randint(-20, 9) for _ in range(cols)] for _ in range(rows)]


def first_col_with_zero(matrix):
    num_cols = max(len(row) for row in matrix)
    for col in range(num_cols):
        for row in range(len(matrix)):
            if col < len(matrix[row]) and matrix[row][col] == 0:
                return col + 1
    return None

def find_sum_of_negative_even_rows(matrix):
    sum_list = []
    for row in matrix:
        negative_even_sum = 0
        for elem in row:
            if elem < 0 and elem % 2 == 0:
                negative_even_sum += elem
        sum_list.append(negative_even_sum)
    return sum_list


def sort_matrix_by_neg_even_sum(matrix, sum_list):
    sorted_matrix = sorted(matrix, key=lambda row: sum_list[matrix.index(row)], reverse=True)
    return sorted_matrix


def print_matrix(matrix):
    for row in matrix:
        print(row)
    print('\n')


print('Matrix: ')
print_matrix(matrix)
sums = find_sum_of_negative_even_rows(matrix)
print('Sorted matrix: ')
print_matrix(sort_matrix_by_neg_even_sum(matrix, sums))

print(f'First column with zero in matrix: {first_col_with_zero(matrix)}')
