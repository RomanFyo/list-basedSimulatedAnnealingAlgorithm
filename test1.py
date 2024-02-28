import os
import time

import instance
import solution

benchmark_names = os.listdir(os.path.dirname(__file__) + "\\benchmarks")
print(benchmark_names)

optimal_solutions = {}
with open("optimalSolutions.txt", "r") as optimals:
    for string in optimals.readlines():
        name, answer = map(lambda s: s.strip(), string.split(":"))
        if name + ".tsp" in benchmark_names:
            optimal_solutions[name] = answer

print(optimal_solutions)

with open("test1_results" + str(int(time.time())) + ".txt", "w") as file:
    for name in benchmark_names:
        file.write(f"Проблема - {name[:-4]}. Оптимальное решение - {optimal_solutions[name[:-4]]}\n\n\n")
        print(name)
        for temp_amount in range(100, 311, 100):
            for p0 in (0.3, 0.6):
                for _ in range(10):
                    time0 = time.time()
                    problem = instance.TSP_INSTANCE(f"benchmarks\\{name}")
                    sol = solution.Solution(temp_amount, p0, 2500, problem.d)
                    result_time = time.time() - time0
                    file.write(f"Кол-во температур = {temp_amount}, "
                               f"p0 = {p0}, "
                               f"ответ: {sol.answer}. "
                               f"Время: {result_time}\n"
                               )
                    file.write(f"Список лучших решений в промежуточных итерациях - {sol.best_by_iterations}\n")
                    print(f"Кол-во температур = {temp_amount}, "
                               f"p0 = {p0}, "
                               f"ответ: {sol.answer}. "
                               f"Время: {result_time}")
                file.write("\n")
        file.write("\n\n\n")