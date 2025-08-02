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
    # Благодаря этому достигается возможность организации максимальной двоичной кучи встроенными средствами python
    def __lt__(self, other):
        return self.value > other.value

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return str(self.value)


def inverse_op(perm: list, i: int, j: int) -> list:
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


def insert_op(perm: list, i: int, j: int) -> list:
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


def swap_op(perm: list, i: int, j: int) -> list:
    """Меняет местами города на позиции i и на позиции j

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


def f(perm: list, d: list) -> int:
    """Вычисление длины гамильтонового цикла

    Args:
        perm (list): Перестановка x
        d (list): Матрица расстояний

    Returns:
        Значение целевой функции f
    """
    total = 0
    for i in range(len(perm)):
        total += d[perm[i]][perm[(i + 1) % len(perm)]]

    return total


def f_inverse(
    old_perm: list, f: float, new_perm: list, i: int, j: int, d: list, mod="symmetric"
) -> int:
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора инверсии

    Args:
        old_perm (list): Перестановка x
        f (float): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора инверсии
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний
        mod (string): Тип задачи (symmetric | asymmetric). По умолчанию symmetric

    Returns:
        Измененное значение целевой функции f
    """
    if mod == "symmetric":
        for k in (i - 1, j):
            # Проверка случая, когда происходит инверсия всего списка
            if k == -1 and j == len(old_perm) - 1:
                continue
            f -= d[old_perm[k]][old_perm[(k + 1) % len(old_perm)]]
            f += d[new_perm[k]][new_perm[(k + 1) % len(new_perm)]]
    else:
        for k in range(i - 1, j + 1):
            if k == -1 and j == len(old_perm) - 1:
                continue
            f -= d[old_perm[k]][old_perm[(k + 1) % len(old_perm)]]
            f += d[new_perm[k]][new_perm[(k + 1) % len(new_perm)]]

    return f


def f_insert(old_perm: list, f: float, new_perm: list, i: int, j: int, d: list) -> int:
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора вставки

    Args:
        old_perm (list): Перестановка x
        f (float): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора вставки
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний

    Returns:
        Новое значение целевой функции f
    """
    # Проверка случая, когда самый последний город вставляется в начало списка
    if i == 0 and j == len(old_perm) - 1:
        return f

    # Вычитание длин дорог между городами, которые теперь не будут являться соседними
    for k in (i - 1, j - 1, j):
        f -= d[old_perm[k]][old_perm[(k + 1) % len(old_perm)]]

    # Прибавление длин между городами, которые теперь являются соседями
    for k in (i - 1, i, j):
        f += d[new_perm[k]][new_perm[(k + 1) % len(new_perm)]]

    return f


def f_swap(old_perm: list, f: float, new_perm: list, i: int, j: int, d: list) -> int:
    """Вычисление длины гамильтонового цикла для соседнего решения, полученного применением оператора замены

    Args:
        old_perm (list): Перестановка x
        f (float): Значение целевой функции для x
        new_perm (list): Перестановка, полученная из x путем применения оператора замены
        i (int): Индекс
        j (int): Индекс
        d (list): Матрица расстояний

    Returns:
        Новое значение целевой функции f
    """
    for k in (i - 1, i, j - 1, j):
        # В случае i, стоящего на первом месте, и j, стоящего на последнем,
        # длина дороги между первым и последним пунктом будет пересчитываться 2 раза
        if k == -1 and j == len(old_perm) - 1:
            continue
        f -= d[old_perm[k]][old_perm[(k + 1) % len(old_perm)]]
        f += d[new_perm[k]][new_perm[(k + 1) % len(new_perm)]]

    return f
