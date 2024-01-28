import sys
import tools
import solution
import time
import math


class TSP_INSTANCE:
    def __init__(self, file_name):
        self.instance = open(file_name, "r")

        # Чтение шапки файла
        self.NAME = self.instance.readline().strip().split()[1]  # Имя файла
        self.FILE_TYPE = self.instance.readline().strip().split()[1]  # Тип файла
        self.COMMENT = self.instance.readline().strip()  # Комментарий
        self.COMMENT = self.COMMENT[self.COMMENT.find(":") + 1:].lstrip()
        self.DIMENSION = int(self.instance.readline().strip().split()[1])  # Размер (количество узлов)
        self.EDGE_WEIGHT_TYPE = self.instance.readline().strip().split()[1]  # Тип хранения узлов
        self.instance.readline()

        # Чтение информации об узлах
        if self.FILE_TYPE == "TSP":
            node_list = self.read_tsp_file()
            self.d = self.create_distance_matrix(node_list)
        else:
            raise AttributeError("Алгоритм не может обработать данный тип файла!")

        # print(*self.d, sep="\n")

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
        # Заполнение нулями матрицы для хранения расстояний
        distance_matrix = [[0] * self.DIMENSION for _ in range(self.DIMENSION)]
        # Запись расстояний в матрицу
        for i in range(self.DIMENSION):
            for j in range(self.DIMENSION):
                if i == j:
                    continue  # Расстояние от узла до самого себя всегда 0
                distance_matrix[i][j] = round(distance(nodes[i], nodes[j]))

        return distance_matrix

    def solve(self):
        pass


    def __str__(self):
        return (f"Name: {self.NAME}\n"
                f"File type: {self.FILE_TYPE}\n"
                f"comment: {self.COMMENT}\n"
                f"Dimension: {self.DIMENSION}\n"
                f"Edge weight type: {self.EDGE_WEIGHT_TYPE}")


def distance(node1, node2):
    """
    Вычисление расстояния от одного узла до другого
    """
    return math.sqrt((node1[0]-node2[0])**2 + (node1[1]-node2[1])**2)


if __name__ == "__main__":
    problem1 = TSP_INSTANCE("benchmarks/berlin52.tsp")
    solution1 = solution.Solution(100, 0.1, 30000, problem1.d)
    print(solution1.answer)
    # right answer1 = 7542
    # best algorithm answer = 7544.365901904087
    for _ in range(1, 25):
        time1 = time.time()
        problem2 = TSP_INSTANCE("benchmarks/a280.tsp")
        solution2 = solution.Solution(200, 0.04*_, 80000, problem2.d)
        print(solution2.answer)
        print(solution2.best)
        print(time.time() - time1)
    # right answer = 2579
    # best algorithm answer = 2649
