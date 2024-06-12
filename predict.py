from sympy import symbols
import numpy

def gauss(arr, brr):
    for k in range(arr.shape[0] - 1):
        #поиск строки с максимальным элементом
        max_elem = 0
        str = 0
        for i in range (k, arr.shape[0]):
            if abs(arr[i,k]) > abs(max_elem):
                max_elem = arr[i,k]
                str = i
        #меняем местами строки квадратной матрицы
        change = numpy.repeat(arr[k], 1)
        arr[k], arr[str] = arr[str], change
        #меняем местами элементы вектора-столбца
        change = numpy.repeat(brr[k], 1)
        brr[k], brr[str] = brr[str], change
        #делим полученную строку на max_elem
        arr[k] = arr[k] / max_elem
        brr[k] = brr[k] / max_elem
        #домножаем строку на коэффициенты и вычитаем ее из остальных строк
        for i in range (k + 1, arr.shape[0]):
            factor = arr[i,k]
            arr[i] = arr[i] - arr[k] * factor
            brr[i] = brr[i] - brr[k] * factor
    #находим неизвестные
    arg = [brr[brr.shape[0] - 1] / (arr[arr.shape[0] - 1, arr.shape[0] - 1])]
    for i in range(arr.shape[0] - 2, -1, -1):
        n = brr[i]
        for j in range(len(arg)):
            n = n - arg[j] * arr[i, arr.shape[0] - 1 - j]
        arg.append(n)
    #переворачиваем значения в списке
    X = []
    for i in reversed(arg): X.append(i)
    return X


def MNK(xi, yi, K):
    x = symbols('x')
    # поиск констант
    A = numpy.zeros([K + 1, K + 1])
    for i in range(K + 1):
        for j in range(K + 1):
            for t in xi: A[i, j] += t ** (2 * K - i - j)
    B = numpy.zeros([K + 1])
    for i in range(K + 1):
        for j in range(len(xi)): B[i] += yi[j] * xi[j] ** (K - i)
    X = []
    for j in gauss(A, B): X.append(float(j))
    # составление уравнения
    f = 0
    for i in range(len(X)):
        f += X[i] * x ** (len(X) - 1 - i)
    return f