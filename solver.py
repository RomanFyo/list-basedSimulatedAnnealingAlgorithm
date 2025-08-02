import heapq
import math
import random
from multiprocessing.connection import Connection
from typing import List, Optional

import tools


class TSPSolver:
    """Класс для решения задачи о коммивояжере

    Данный солвер основан на алгоритме, приведенном в статье Shi-hua Zhan, Juan Lin, Ze-jun Zhang, Yi-wen Zhong -
    List-Based Simulated Annealing Algorithm for Traveling Salesman Problem

    Typical usage example:
        solver = TSPSolver(number_of_temperatures, initial_p, outer_limit, distance_matrix)
        answer = solver.run()

    Attributes:
        d (List[List[float]]): матрица расстояний между городами
        outer_limit (int): количество итераций внешнего цикла
        inner_limit (int): количество итераций внутреннего цикла
        input_pipe (Optional[Connection]): труба для передачи данных в другой процесс
        x (List[int]): текущая перестановка (решение задачи)
        f_x (float): значение целевой функции для перестановки x
        temperature_list (List[tools.Temperature]): список температур
        best (float): лучшее из встречавшихся решений
        best_by_iterations (Dict[int, float]): словарь лучших решений по итерациям
    """
    def __init__(
            self,
            temp_len: int,
            p0: float,
            outer_limit: int,
            d: List[List[float]],
            input_pipe: Optional[Connection] = None
    ):
        """Инициализация солвера для задачи о коммивояжере

        Args:
            temp_len (int): Длина списка температур
            p0 (float): изначальная вероятность (чем выше, тем выше начальные температуры)
            outer_limit (int): количество итераций для внешнего цикла
            d (List[List[float]]): матрица расстояний между городами
            input_pipe (Optional[Connection]): труба для передачи данных. По умолчанию None
        """
        self.d = d
        self.outer_limit = outer_limit
        self.inner_limit = temp_len
        self.input_pipe = input_pipe
        self.x = [x for x in range(len(self.d))]
        random.shuffle(self.x)
        self.f_x = tools.f(self.x, self.d)
        self.temperature_list = self.__generate_temperature_list(temp_len, p0)
        self.best = tools.f(self.x, self.d)
        self.best_by_iterations = {}

    def run(self) -> float:
        self.__outer_loop()
        return self.f_x

    def __get_best_from_neighboring_solutions(self):
        """Генерирует соседние решения и возвращает лучшее из них.

        Генерируется 2 индекса, а затем при помощи операторов инверсии, вставки и замены (из модуля tools)
        генерируются соседние решения. Затем вычисляются значения целевой функции и возвращается перестановка с
        наименьшим значением.

        Returns:
            Кортеж из 2 элементов:
                - List[int]: лучшая соседняя перестановка;
                - float: значение целевой функции для данной перестановки
        """
        # Генерация 2 случайных индексов
        indices = set()
        while len(indices) < 2:
            indices.add(random.randrange(len(self.d)))
        i, j = sorted(list(indices))  # i < j

        # Генерация соседних решений
        y1 = tools.inverse_op(self.x, i, j)
        y2 = tools.insert_op(self.x, i, j)
        y3 = tools.swap_op(self.x, i, j)

        # Вычисление целевых функций для соседних решений
        f_y1 = tools.f_inverse(self.x, self.f_x, y1, i, j, self.d)
        f_y2 = tools.f_insert(self.x, self.f_x, y2, i, j, self.d)
        f_y3 = tools.f_swap(self.x, self.f_x, y3, i, j, self.d)

        # Жадный выбор оптимального из 3 соседей (возвращается соседнее решение с наименьшей целевой функцией f)
        return sorted([(y1, f_y1), (y2, f_y2), (y3, f_y3)], key = lambda item: item[1])[0]

    def __generate_temperature_list(self, temp_len: int, p0: float) -> List[tools.Temperature]:
        """Генерирует изначальные температуры

        Создается двоичная куча. После этого ищутся соседние решения и в кучу добавляется температура, рассчитанная
        по формуле, учитывающей целевое значение изначальной перестановки и лучшей полученной соседней перестановки

        Args:
            temp_len (int): длина списка температур
            p0 (float): изначальная вероятность

        Returns:
            Список температур, полученных по формуле -abs(f_for_neighboring_solution - f_current) / math.log(p0)
        """
        temperature_list = []
        heapq.heapify(temperature_list)

        while len(temperature_list) < temp_len:
            y, f_y = self.__get_best_from_neighboring_solutions()
            heapq.heappush(temperature_list, tools.Temperature(-abs(f_y - self.f_x) / math.log(p0)))
            # Если решение лучше текущего, то происходит замена текущего решения на лучшее
            if f_y < self.f_x:
                self.x, self.f_x = y, f_y

        return temperature_list

    def __outer_loop(self):
        """Выполняет внешний цикл алгоритма имитации отжига.

        В каждой итерации генерируется новая температура при помощи исполнения внутреннего цикла. Если
        температура сгенерирована успешно, то она заменяет одну из температур в списке температур
        """
        outer_cntr = 0
        while outer_cntr < self.outer_limit:
            # Запись лучшего решения на определенном количестве итераций
            if outer_cntr % 100 == 0 and outer_cntr != 0:
                self.best_by_iterations[outer_cntr] = self.best

            new_temperature = self.__inner_loop()
            if new_temperature is not None:
                heapq.heappop(self.temperature_list)
                heapq.heappush(self.temperature_list, tools.Temperature(new_temperature))

            outer_cntr += 1

            if self.input_pipe and outer_cntr % 500 == 0:  # передача данных по трубе
                self.input_pipe.send((self.x, outer_cntr, self.best))

    def __inner_loop(self) -> Optional[float]:
        """Выполняет один внутренний цикл алгоритма имитации отжига.

        В каждой итерации выбирается лучшее соседнее решение. Если оно лучше текущего — принимается.
        Если хуже — может быть принято с вероятностью, зависящей от текущей температуры.
        Для всех принятых (ухудшающих) решений рассчитываются температуры,
        на основе которых будет вычислена новая средняя температура.

        Returns:
            float | None: Новое значение температуры, если хотя бы одно ухудшающее решение было принято.
                          None в противном случае
        """
        total_t = 0     # сумма температур, вычисленных для каждого принятого соседнего решения
        number_of_t = 0    # количество температур
        inner_cntr = 0
        temperature = self.temperature_list[0].value

        while inner_cntr < self.inner_limit:
            y, f_y = self.__get_best_from_neighboring_solutions()
            if f_y <= self.f_x:
                self.x, self.f_x = y, f_y
            else:
                p = math.exp(-(f_y - self.f_x) / temperature)  # вероятность принятия соседнего решения
                r = 1
                while r == 1:  # r == 1 -> math.log(r) == 0 -> error (ZeroDivisionError)
                    r = random.random()
                # Симуляция принятия соседнего решения
                if r < p:
                    self.best = min(f_y, self.f_x, self.best)
                    total_t -= (f_y - self.f_x) / math.log(r)
                    self.x, self.f_x = y, f_y
                    number_of_t += 1

            inner_cntr += 1

        if number_of_t == 0:
            return None
        else:
            return total_t / number_of_t
