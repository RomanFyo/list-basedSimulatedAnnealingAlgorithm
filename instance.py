import math
import re
import sys
import time

import solution
import tools


class TSP_INSTANCE:
    def __init__(self, file_name):
        self.instance = open(file_name, "r")

        # Чтение шапки файла
        self.ATTRIBUTES = {}

        string = self.instance.readline().strip()
        while not re.match(".*SECTION", string):
            key, value = map(lambda s: s.strip(), string.split(": "))
            self.ATTRIBUTES[key] = value
            string = self.instance.readline().strip()


        # Чтение информации об узлах
        if self.ATTRIBUTES["TYPE"] == "TSP":
            self.node_list = self.read_tsp_file()
            self.d = self.create_distance_matrix(self.node_list)
        else:
            raise AttributeError("Алгоритм не может обработать данный тип файла!")

        # Закрытие файла
        self.instance.close()

    def read_tsp_file(self):
        node_list = []
        for node in self.instance.readlines():
            if node.strip() == "EOF":
                break
            x, y = node.split()[1:]
            try:
                node_list.append([int(x), int(y)])
            except ValueError:
                node_list.append([float(x), float(y)])

        return node_list

    def create_distance_matrix(self, nodes: list) -> list:
        n = int(self.ATTRIBUTES["DIMENSION"])
        # Заполнение нулями матрицы для хранения расстояний
        distance_matrix = [[0] * n for _ in range(n)]
        # Запись расстояний в матрицу
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue  # Расстояние от узла до самого себя всегда 0
                distance_matrix[i][j] = round(distance(nodes[i], nodes[j]))

        return distance_matrix

    def __str__(self):
        string = ""
        for key, value in self.ATTRIBUTES.items():
            string += f"{key}: {value}\n"

        return string


def distance(node1, node2):
    """
    Вычисление расстояния от одного узла до другого
    """
    return math.sqrt((node1[0]-node2[0])**2 + (node1[1]-node2[1])**2)


if __name__ == "__main__":
    problem1 = TSP_INSTANCE("benchmarks/u724.tsp")
    solution1 = solution.Solution(1500, 0.1, 20000, problem1.d).run()
    print(solution1.answer)
    for _ in range(1, 25):
        time1 = time.time()
        problem2 = TSP_INSTANCE("benchmarks/u724.tsp")
        solution2 = solution.Solution(1500, 0.04*_, 20000, problem2.d).run()
        print(solution2.answer)
        print(solution2.best)
        print(time.time() - time1)
