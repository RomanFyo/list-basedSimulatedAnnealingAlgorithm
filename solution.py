import math
import heapq
import random
import tools


class Solution:
    def __init__(self, temp_len, p0, outer_limit, d):
        # Необходимые переменные
        self.temp_len = temp_len                  # длина списка температур (длина списка температур)
        self.p0 = p0                              # изначальная возможность принятия решений
        self.d = d                                # матрица расстояний
        self.outer_limit = outer_limit            # количество внешних циклов
        self.inner_limit = temp_len               # количество внутренних циклов (равно длине списка температур)
        self.x = [x for x in range(len(self.d))]  # генерация случайного решения
        random.shuffle(self.x)
        self.temperature_list = self.generate_temperature_list()  # получение списка температур
        self.best = tools.f(self.x, self.d)                       # лучшее из встречавшихся решений
        self.best_by_iterations = {}                              # словарь лучших решений по итерациям
        
        # Решение
        self.outer_loop()
        self.answer = tools.f(self.x, self.d)

    def get_best_from_random_neighbours(self):
        # Генерация 2 случайных индексов
        indices = set()
        while len(indices) < 2:
            indices.add(random.randrange(len(self.d)))
        i, j = sorted(list(indices))  # i < j

        # Генерация соседних решений
        y1 = tools.inverse_op(self.x, i, j)  # соседнее решение, полученное применением inverse оператора
        y2 = tools.insert_op(self.x, i, j)  # соседнее решение, полученное применением insert оператора
        y3 = tools.swap_op(self.x, i, j)  # соседнее решение, полученное применением swap оператора

        # Жадный выбор оптимального из 3 соседей
        return min([y1, y2, y3], key=lambda perm: tools.f(perm, self.d))

    def generate_temperature_list(self):
        # Генерация списка температур (в виде двоичной кучи)
        temperature_list = []
        heapq.heapify(temperature_list)

        # Заполнение списка температур
        while len(temperature_list) < self.temp_len:
            # Получение лучшего из 3 случайных соседних решений
            y = self.get_best_from_random_neighbours()
            # Вычисление общего пройденного расстояния для 2 решений
            f_y = tools.f(y, self.d)
            f_x = tools.f(self.x, self.d)
            # вычисление температуры и добавление ее в список температур
            heapq.heappush(temperature_list, tools.Temperature(-abs(f_y - f_x) / math.log(self.p0)))
            # Если решение лучше текущего, то происходит замена текущего решения на лучшее
            if f_y < f_x:
                self.x = y

        return temperature_list

    def outer_loop(self):
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

    def inner_loop(self):
        total_t = 0     # сумма температур, вычисленных для каждого принятого соседнего решения
        amount_t = 0    # количество температур
        inner_cntr = 0  # счетчик внутренних итераций
        temperature = self.temperature_list[0].value  # температура в текущем внутреннем цикле

        # Непосредственно внутренний цикл
        while inner_cntr < self.inner_limit:
            # Получение лучшего из 3 случайных соседних решений
            y = self.get_best_from_random_neighbours()

            # Вычисление общего пройденного расстояния для 2 решений
            f_y = tools.f(y, self.d)
            f_x = tools.f(self.x, self.d)

            # Если соседнее решение лучше текущего или оно принимается с какой-то вероятностью, то x = y
            if f_y <= f_x:
                self.x = y
            else:
                p = math.exp(-(f_y - f_x) / temperature)  # вероятность принятия соседнего решения
                r = 1
                while r == 1:  # r == 1 -> math.log(r) == 0 -> error (строка 103)
                    r = random.random()
                # Симуляция принятия соседнего решения
                if r < p:
                    self.best = min(f_y, f_x, self.best)
                    self.x = y
                    total_t -= (f_y - f_x) / math.log(r)
                    amount_t += 1

            inner_cntr += 1

        # Вычисление новой температуры
        if amount_t == 0:
            return None  # не получилось посчитать среднее значение, так как не было принятых решений
        else:
            return total_t / amount_t  # возврат среднего значения температур принятых решений
