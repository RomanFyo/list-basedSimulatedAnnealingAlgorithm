import random

import pytest

from tools import *


def test_inverse_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert inverse_op(lst, i, j) == [6, 5, 4, 3, 2, 1, 0]


def test_insert_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert insert_op(lst, i, j) == [6, 0, 1, 2, 3, 4, 5]


def test_swap_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert swap_op(lst, i, j) == [6, 1, 2, 3, 4, 5, 0]


def test_f():
    d = [[2, 3, 4], [100, 120, 153], [1253, 1351, 1235]]
    perm = [0, 2, 1]
    assert f(perm, d) == 1455


def test_f_inverse():
    # Создание симметричной матрицы расстояний
    size = 50
    d_sim = [
        [random.randrange(1000) if i >= j else 0 for i in range(size)]
        for j in range(size)
    ]
    for i in range(size):
        for j in range(i):
            d_sim[i][j] = d_sim[j][i]

    # Генерация матрицы расстояний (несимметричная)
    d_asim = [[random.randrange(10000) for _ in range(size)] for __ in range(size)]

    # Генерация изначальной перестановки x
    old_perm = list(range(size))
    random.shuffle(old_perm)

    # Непосредственно проверки
    for i, j in ((0, size - 1), (5, 7), (2, 30)):
        new_perm = inverse_op(old_perm, i, j)
        assert f_inverse(old_perm, f(old_perm, d_sim), new_perm, i, j, d_sim) == f(
            new_perm, d_sim
        )
        assert f_inverse(
            old_perm, f(old_perm, d_asim), new_perm, i, j, d_asim, mod="asymmetric"
        ) == f(new_perm, d_asim)


def test_f_insert():
    # Генерация матрицы расстояний (несимметричная)
    size = 50
    d = [[random.randrange(10000) for _ in range(size)] for __ in range(size)]

    # Генерация изначальной перестановки x
    old_perm = list(range(size))
    random.shuffle(old_perm)

    # Непосредственно проверки
    for i, j in ((2, 7), (0, 49), (13, 46)):
        new_perm = insert_op(old_perm, i, j)
        assert f_insert(old_perm, f(old_perm, d), new_perm, i, j, d) == f(new_perm, d)


def test_f_swap():
    # Генерация матрицы расстояний (несимметричная)
    size = 50
    d = [[random.randrange(10000) for _ in range(size)] for __ in range(size)]

    # Генерация изначальной перестановки x
    old_perm = list(range(size))
    random.shuffle(old_perm)

    # Непосредственно проверки
    for i, j in ((2, 7), (0, 49), (13, 46)):
        new_perm = swap_op(old_perm, i, j)
        assert f_swap(old_perm, f(old_perm, d), new_perm, i, j, d) == f(new_perm, d)


if __name__ == "__main__":
    random.seed(4)
    pytest.main()
