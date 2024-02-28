import functools
import random

import pytest


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
    # Благодаря этому достигается возможность организации максимальной двоичной кучи встроенными средствами python
    def __lt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)


def inverse_op(perm, i, j):
    """Разворачивает обход городов в решении с города i по город j (i < j)

    new_perm[i] = perm[j],
    new_perm[i+1] = perm[j-1],
    ...
    new_perm[j] = perm[i]

    Args:
        perm (list): Перестановка x
        i (int): индекс
        j (int): индекс

    Returns:
        Новая перестановка, полученная путем применения оператора инверсии к x
    """
    j = j + 1
    new_perm = perm[:]
    new_perm[i:j] = new_perm[i:j][::-1]
    return new_perm


def test_inverse_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert inverse_op(lst, i, j) == [6, 5, 4, 3, 2, 1, 0]


def insert_op(perm, i, j):
    """Перемещает город с позиции j на позицию i, i < j

    new_perm[i] = perm[j],
    new_perm[i+1] = perm[i],
    ...
    new_perm[j] = perm[j-1]

    Args:
        perm (list): Перестановка x
        i (int): индекс
        j (int): индекс

    Returns:
        Новая перестановка, полученная путем применения оператора вставки к x
    """
    new_perm = perm[:]
    temp = new_perm[j]
    del new_perm[j]
    new_perm.insert(i, temp)
    return new_perm


def test_insert_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert insert_op(lst, i, j) == [6, 0, 1, 2, 3, 4, 5]


def swap_op(perm, i, j):
    """    Меняет местами города на позиции i и на позиции j

    new_perm[i] = perm[j],
    new_perm[j] = perm[i]

    Args:
        perm (list): Перестановка x
        i (int): индекс
        j (int): индекс

    Returns:
        Новая перестановка, полученная путем применения оператора замены к x
    """
    new_perm = perm[:]
    new_perm[i], new_perm[j] = new_perm[j], new_perm[i]
    return new_perm


def test_swap_op():
    lst = [0, 1, 2, 3, 4, 5, 6]
    i, j = 0, 6
    assert swap_op(lst, i, j) == [6, 1, 2, 3, 4, 5, 0]


def f(perm, d):
    """Вычисление длины гамильтонового цикла

    Args:
        perm (list): Перестановка x
        d (list): Матрица расстояний

    Returns:
        Значение целевой функции f
    """
    total = 0
    for i in range(len(perm)):
        total += d[perm[i]][perm[(i+1) % len(perm)]]

    return total


def test_f():
    d = [[2, 3, 4], [100, 120, 153], [1253, 1351, 1235]]
    perm = [0, 2, 1]
    assert f(perm, d) == 1455


def f_inverse(old_perm, f, new_perm, i, j, d, mod="symmetric"):
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора инверсии

    Args:
        old_perm (list): Перестановка x
        f (int): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора инверсии
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний
        mod (string): Тип задачи (symmetric | asymmetric). По умолчанию symmetric

    Returns:
        Измененное значение целевой функции f
    """
    if mod == "symmetric":
        for k in (i-1, j):
            # Проверка случая, когда происходит инверсия всего списка
            if k == -1 and j == len(old_perm)-1:
                continue
            f -= d[old_perm[k]][old_perm[(k+1) % len(old_perm)]]
            f += d[new_perm[k]][new_perm[(k+1) % len(new_perm)]]
    else:
        for k in range(i-1, j+1):
            if k == -1 and j == len(old_perm)-1:
                continue
            f -= d[old_perm[k]][old_perm[(k+1) % len(old_perm)]]
            f += d[new_perm[k]][new_perm[(k+1) % len(new_perm)]]

    return f


def test_f_inverse():
    random.seed(5)

    # Создание симметричной матрицы расстояний
    size = 50
    d_sim = [[random.randrange(1000) if i >= j else 0 for i in range(size)] for j in range(size)]
    for i in range(size):
        for j in range(i):
            d_sim[i][j] = d_sim[j][i]

    # Генерация матрицы расстояний (несимметричная)
    d_asim = [[random.randrange(10000) for _ in range(size)] for __ in range(size)]

    # Генерация изначальной перестановки x
    old_perm = list(range(size))
    random.shuffle(old_perm)

    # Непосредственно проверки
    for i, j in ((0, size-1), (5, 7), (2, 30)):
        new_perm = inverse_op(old_perm, i, j)
        assert f_inverse(old_perm, f(old_perm, d_sim), new_perm, i, j, d_sim) == f(new_perm, d_sim)
        assert f_inverse(old_perm, f(old_perm, d_asim), new_perm, i, j, d_asim, mod="asymmetric") == f(new_perm, d_asim)


def f_insert(old_perm, f, new_perm, i, j, d):
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора вставки

    Args:
        old_perm (list): Перестановка x
        f (int): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора вставки
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний

    Returns:
        Новое значение целевой функции f
    """
    # Проверка случая, когда самый последний город вставляется в начало списка
    if i == 0 and j == len(old_perm)-1:
        return f

    # Вычитание длин дорог между городами, которые теперь не будут являться соседними
    for k in (i-1, j-1, j):
        f -= d[old_perm[k]][old_perm[(k+1) % len(old_perm)]]

    # Прибавление длин между городами, которые теперь являются соседями
    for k in (i-1, i, j):
        f += d[new_perm[k]][new_perm[(k+1) % len(new_perm)]]

    return f


def test_f_insert():
    random.seed(4)

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


def f_swap(old_perm, f, new_perm, i, j, d):
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора замены

    Args:
        old_perm (list): Перестановка x
        f (int): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора замены
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний

    Returns:
        Новое значение целевой функции f
    """
    for k in (i-1, i, j-1, j):
        # В случае i, стоящего на первом месте, и j, стоящего на последнем,
        # длина дороги между первым и последним пунктом будет пересчитываться 2 раза
        if k == -1 and j == len(old_perm) - 1:
            continue
        f -= d[old_perm[k]][old_perm[(k+1) % len(old_perm)]]
        f += d[new_perm[k]][new_perm[(k+1) % len(new_perm)]]

    return f


def test_f_swap():
    random.seed(4)

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
    pytest.main()
