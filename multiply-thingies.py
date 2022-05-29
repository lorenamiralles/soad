from random import random, randint

def genMatrix(rows, columns):
    matrix = []
    for i in range(rows):
        matrix.append([])
        for j in range(columns):
            matrix[i].append(random())
    return matrix

def genIdentityMatrix(rows):
    matrix = []
    for i in range(rows):
        matrix.append([])
        for j in range(rows):
            if i == j:
                matrix[i].append(1)
            else:
                matrix[i].append(0)
    return matrix

def multiplyMatixes(matrix1, matrix2):
    matrix = []
    for i in range(len(matrix1)):
        matrix.append([])
        for j in range(len(matrix2[0])):
            matrix[i].append(0)
            for k in range(len(matrix2)):
                matrix[i][j] += matrix1[i][k] * matrix2[k][j]
    return matrix

def writeMatrix(matrix):
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            print(matrix[i][j], end = " ")
        print()

def writeMatrixFile(matrix, filename):
    with open(filename, "w") as file:
        for i in range(len(matrix)):
            for j in range(len(matrix[0])):
                file.write(str(matrix[i][j]) + " ")
            file.write("\n")


if __name__ == "__main__":
    rows_a = randint(3, 10)
    columns_a = randint(3, 10)
    rows_b = columns_a
    columns_b = randint(3, 10)
    matrix_a = genMatrix(rows_a, columns_a)
    matrix_b = genMatrix(rows_b, columns_b)
    matrix_c = multiplyMatixes(matrix_a, matrix_b)

    writeMatrixFile(matrix_a, "matrix_a.txt")
    writeMatrixFile(matrix_b, "matrix_b.txt")
    writeMatrixFile(matrix_c, "matrix_c.txt")