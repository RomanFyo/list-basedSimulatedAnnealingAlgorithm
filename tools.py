import math
import pytest
import functools

@functools.total_ordering
class Temperature:
    """
    По умолчанию в python нет максимальной двоичной кучи, поэтому можно организовать минимальную двоичную кучу над
    элементами, для которых все операции сравнения выдают противоположный их изначальному значению результат.
    Элементы класса Temperature будут составлять максимальную двоичную кучу.
    """
    def __init__(self, value):
        self.value = value

    # __lt__() для данного класса похож на __rt__() стандартных классов
    # (функции операторов сравнений поменяны местами)
    def __lt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)

def inverse_op(perm, i, j):
    """
    Разворачивает обход городов в решении с города i по город j (i < j)

    new_perm[i] = perm[j],
    new_perm[i+1] = perm[j-1],
    ...
    new_perm[j] = perm[i],
    """
    j = j + 1
    new_perm = perm[:]
    new_perm[i:j] = new_perm[i:j][::-1]
    return new_perm

def test_inverse_op():
    list = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert inverse_op(list, i, j) == [6, 5, 4, 3, 2, 1, 0]

def insert_op(perm, i, j):
    """
    Перемещает город с позиции j на позицию i, i < j

    new_perm[i] = perm[j],
    new_perm[i+1] = perm[i],
    ...
    new_perm[j] = perm[j-1]
    """
    new_perm = perm[:]
    temp = new_perm[j]
    del new_perm[j]
    new_perm.insert(i, temp)
    return new_perm

def test_insert_op():
    list = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert insert_op(list, i, j) == [6, 0, 1, 2, 3, 4, 5]

def swap_op(perm, i, j):
    """
    Меняет местами города на позиции i и на позиции j

    new_perm[i] = perm[j],
    new_perm[j] = perm[i]
    """
    new_perm = perm[:]
    new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
    return new_perm

def test_swap_op():
    list = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert swap_op(list, i, j) == [6, 1, 2, 3, 4, 5, 0]

def f(perm, d):
    """
    Вычисление длины гамильтонового цикла
    """
    total = 0
    for i in range(len(perm)):
        total += d[perm[i]][perm[(i+1)%len(perm)]]

    return total

def test_f():
    d = [[2,3,4],[100,120,153],[1253,1351,1235]]
    perm = [0,2,1]
    assert f(perm, d) == 1455


if __name__ == "__main__":
    pytest.main()