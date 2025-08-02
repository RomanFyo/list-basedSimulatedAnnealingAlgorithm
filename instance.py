import math
import re


class TSP_INSTANCE:
    """Класс, создающий объект условий для задачи о коммивояжере.

    Данный класс может обработать только задачи типа TSP (формат условия - TSP)

    Attributes:
        file (TextIO): файл
        attributes (Dict[str, str]): атрибуты (параметры) файла
        node_list (List[List[float]]): список координат узлов (городов)
        d (List[List[float]]): матрица расстояний между городами
    """
    def __init__(self, file_name: str):
        """Инициализация объекта с уловиями для задачи о коммивожере

        Args:
            file_name (str): название файла с условием задачи о коммивояжере
        """
        self.file = open(file_name, "r")
        self.attributes = self.__read_file_header()
        self.node_list = self.__read_file()
        self.d = self.__create_distance_matrix()

        # Закрытие файла
        self.file.close()

    def __read_file_header(self) -> dict:
        """Читает файл и выделяет из него атрибуты (параметры)

        Returns:
            атрибуты файла
        """
        attributes = {}
        string = self.file.readline().strip()
        while not re.match(".*SECTION", string):
            key, value = map(lambda s: s.strip(), string.split(": "))
            attributes[key] = value
            string = self.file.readline().strip()

        return attributes

    def __read_file(self) -> list:
        """Читает файл и выделяет из него информацию о городах

        Returns:
            Список координат городов

        Raises:
            AttributeError: ошибка из-за подачи файла типа, который не может быть обработан
        """
        if self.attributes["TYPE"] == "TSP":
            node_list = []
            for node in self.file.readlines():
                if node.strip() == "EOF":
                    break
                x, y = node.split()[1:]
                node_list.append([float(x), float(y)])

            return node_list
        else:
            raise AttributeError("Алгоритм не может обработать данный тип файла!")

    def __create_distance_matrix(self) -> list:
        """Вычисляет матрицу расстояний между городами"""
        n = int(self.attributes["DIMENSION"])
        distance_matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue  # расстояние от узла до самого себя всегда 0
                distance_matrix[i][j] = round(
                    self.__get_distance(self.node_list[i], self.node_list[j])
                )

        return distance_matrix

    @staticmethod
    def __get_distance(node1: list, node2: list) -> float:
        """Вычисление расстояния от одного узла до другого"""
        return math.sqrt((node1[0] - node2[0]) ** 2 + (node1[1] - node2[1]) ** 2)

    def __str__(self):
        string = ""
        for key, value in self.attributes.items():
            string += f"{key}: {value}\n"

        return string


if __name__ == "__main__":
    problem1 = TSP_INSTANCE("data/benchmarks/u724.tsp")
    print(problem1.d, problem1.attributes, problem1.node_list, sep="\n")
    # solution1 = solver.TSPSolver(1500, 0.1, 20000, problem1.d).run()
    # print(solution1.answer)
    # for _ in range(1, 25):
    #     time1 = time.time()
    #     problem2 = TSP_INSTANCE("benchmarks/u724.tsp")
    #     solution2 = solver.TSPSolver(1500, 0.04*_, 20000, problem2.d).run()
    #     print(solution2.answer)
    #     print(solution2.best)
    #     print(time.time() - time1)
