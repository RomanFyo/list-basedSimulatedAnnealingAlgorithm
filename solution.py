import heapq
import math
import random
import time

import tools


class Solution:
    def __init__(self, temp_len, p0, outer_limit, d, input_pipe=None):
        # Необходимые переменные
        self.d = d                                # матрица расстояний
        self.outer_limit = outer_limit            # количество внешних циклов
        self.inner_limit = temp_len               # количество внутренних циклов (равно длине списка температур)
        self.input_pipe = input_pipe              # вход для трубы, связывающей процессы
        self.x = [x for x in range(len(self.d))]  # генерация случайного решения
        random.shuffle(self.x)
        self.f_x = tools.f(self.x, self.d)        # значение целевой функции для решения x
        self.temperature_list = self.generate_temperature_list(temp_len, p0)  # получение списка температур
        self.best = tools.f(self.x, self.d)                       # лучшее из встречавшихся решений
        self.best_by_iterations = {}                              # словарь лучших решений по итерациям

        self.time = time.time()  # todo: удалить
        self.outer_loop()
        self.answer = tools.f(self.x, self.d)  # todo: удалить, answer уже вычислен и лежит в f_x

    def get_best_from_random_neighbours(self):
        # Генерация 2 случайных индексов
        indices = set()
        while len(indices) < 2:
            indices.add(random.randrange(len(self.d)))
        i, j = sorted(list(indices))  # i < j

        # Генерация соседних решений
        y1 = tools.inverse_op(self.x, i, j)  # соседнее решение, полученное применением inverse оператора
        y2 = tools.insert_op(self.x, i, j)   # соседнее решение, полученное применением insert оператора
        y3 = tools.swap_op(self.x, i, j)     # соседнее решение, полученное применением swap оператора

        # Вычисление целевых функций для соседних решений
        f_y1 = tools.f_inverse(self.x, self.f_x, y1, i, j, self.d)
        f_y2 = tools.f_insert(self.x, self.f_x, y2, i, j, self.d)
        f_y3 = tools.f_swap(self.x, self.f_x, y3, i, j, self.d)

        # Жадный выбор оптимального из 3 соседей (возвращается соседнее решение с наименьшей целевой функцией f)
        return sorted([(y1, f_y1), (y2, f_y2), (y3, f_y3)], key = lambda item: item[1])[0]

    def generate_temperature_list(self, temp_len, p0):
        # Генерация списка температур (в виде двоичной кучи)
        temperature_list = []
        heapq.heapify(temperature_list)

        # Заполнение списка температур
        while len(temperature_list) < temp_len:
            # Получение лучшего из 3 случайных соседних решений
            y, f_y = self.get_best_from_random_neighbours()
            # Вычисление общего пройденного расстояния для 2 решений
            # вычисление температуры и добавление ее в список температур
            heapq.heappush(temperature_list, tools.Temperature(-abs(f_y - self.f_x) / math.log(p0)))
            # Если решение лучше текущего, то происходит замена текущего решения на лучшее
            if f_y < self.f_x:
                self.x, self.f_x = y, f_y

        return temperature_list

    def outer_loop(self):
        flag = False # todo: delete
        outer_cntr = 0  # счетчик внешних итераций
        while outer_cntr < self.outer_limit:
            # Запись лучшего решения на определенном количестве итераций 
            if outer_cntr % 100 == 0 and outer_cntr != 0:
                self.best_by_iterations[outer_cntr] = self.best
            
            # Запуск внутреннего цикла, получение новой температуры
            new_temperature = self.inner_loop()

            # Если новую температуру удалось посчитать, то она заменяет предыдущую температуру
            if new_temperature is not None:
                heapq.heappop(self.temperature_list)
                heapq.heappush(self.temperature_list, tools.Temperature(new_temperature))

            outer_cntr += 1

            # Если была передана труба, то нужно возвращать данные в другой процесс
            if self.input_pipe and outer_cntr % 500 == 0:
                self.input_pipe.send((self.x, outer_cntr, self.best))

    def inner_loop(self):
        total_t = 0     # сумма температур, вычисленных для каждого принятого соседнего решения
        amount_t = 0    # количество температур
        inner_cntr = 0  # счетчик внутренних итераций
        temperature = self.temperature_list[0].value  # температура в текущем внутреннем цикле

        # Непосредственно внутренний цикл
        while inner_cntr < self.inner_limit:
            # Получение лучшего из 3 случайных соседних решений
            y, f_y = self.get_best_from_random_neighbours()
            # Если соседнее решение лучше текущего или оно принимается с какой-то вероятностью, то x = y
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
                    amount_t += 1

            inner_cntr += 1

        # Вычисление новой температуры
        if amount_t == 0:
            return None  # не получилось посчитать среднее значение, так как не было принятых решений
        else:
            return total_t / amount_t  # возврат среднего значения температур принятых решений
