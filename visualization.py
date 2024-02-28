import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import multiprocessing
import threading
import os

import instance
import solution


class Interface(tk.Tk):
    def __init__(self):
        super().__init__()

        # Установка названия окна
        self.title("Решение задачи коммивояжера")
        # Установка размера окна
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = screen_width // 2 + screen_width // 4  # ширина главного окна
        window_height = screen_height // 2 + screen_height // 4  # высота главного окна
        self.geometry(
            f"{window_width}x{window_height}+"
            f"{(screen_width - window_width) // 2}+"
            f"{(screen_height - window_height - 100) // 2}"
        )

        # переменные
        self.output_pipe, self.input_pipe = None, None  # выход и вход трубы для общения между процессами
        self.process = None  # объявление второго процесса (нужен для запуска решения)
        self.node_list = None  # объявление списка, содержащего координаты вершин для решения
        self.lines = []  # список, содержащий все линии решения (ребра между узлами)

        # Виджеты
        self.menu = tk.Frame(self, bg="orange", bd=2, relief="groove")  # фрейм, на котором распложены все настройки
        self.files = ttk.Combobox(self.menu)  # выпадающий список с выбором файла для запуска
        self.amount_of_loops_label = ttk.Label(self.menu, text="Количество итераций:")
        self.amount_of_loops_entry = ttk.Entry(self.menu)  # поле ввода количества итераций
        self.labels_frame = tk.Frame(self.menu, bg="orange")
        self.outer_cntr_label = ttk.Label(self.labels_frame, text="Количество итераций:")
        self.best_solution_label = ttk.Label(self.labels_frame, text="Найденное решение:")
        self.optimum_label = ttk.Label(self.labels_frame, text="Оптимальное решение:")
        self.outer_cntr_value = ttk.Label(self.labels_frame, text="0")  # количество пройденных итераций
        self.best_solution_value = ttk.Label(self.labels_frame, text="None")  # значение лучшего решения
        self.optimum_value = ttk.Label(self.labels_frame, text="None")  # значение лучшего известного решения

        self.launch = ttk.Button(self.menu, text="Запуск", command=self.get_process)  # кнопка запуска
        self.canvas = tk.Canvas(bg="white")  # холст, на котором будет отрисовываться визуализация

        # Расположение виджетов на экране
        self.set_widgets()

    def set_widgets(self):
        # Установка значения по умолчанию
        self.amount_of_loops_entry.insert(tk.END, "20000")
        options = os.listdir(os.path.dirname(__file__) + r"/benchmarks/")
        self.files.configure(values=options)
        self.files.insert(tk.END, options[0])

        # Упаковка
        self.menu.pack(fill=tk.Y, side=tk.LEFT)
        self.files.pack()
        self.amount_of_loops_label.pack()
        self.amount_of_loops_entry.pack()

        self.labels_frame.pack()
        self.outer_cntr_label.grid(row=0, column=0, sticky=tk.W)
        self.best_solution_label.grid(row=1, column=0, sticky=tk.W)
        self.optimum_label.grid(row=2, column=0, sticky=tk.W)
        self.outer_cntr_value.grid(row=0, column=1, sticky=tk.E)
        self.best_solution_value.grid(row=1, column=1, sticky=tk.E)
        self.optimum_value.grid(row=2, column=1, sticky=tk.E)

        self.launch.pack(side=tk.BOTTOM)

        self.canvas.pack(fill=tk.BOTH, side=tk.RIGHT, expand=1)

    def get_process(self):
        try:
            # Создание трубы для общения между процессом с отрисовкой визуализации и процессом с решением задачи
            self.output_pipe, self.input_pipe = multiprocessing.Pipe()

            # Получение информации о текущей задаче
            problem = instance.TSP_INSTANCE(f"benchmarks/{self.files.get()}")
            self.node_list = problem.node_list  # координаты узлов

            # Получение значения оптимума для текущей задачи
            with open("optimalSolutions.txt", "r") as optimums:
                for string in optimums.readlines():
                    cur_name, answer = map(lambda s: s.strip(), string.split(":"))
                    if f"{cur_name}.tsp" == self.files.get():
                        self.optimum_value.configure(text=answer)

            # Запуск потока, который будет обновлять информацию в окне
            thread = threading.Thread(target=self.draw_current_solution, daemon=True)
            thread.start()

            # Запуск процесса, который будет заниматься решением задачи
            solution_process = multiprocessing.Process(target=get_solution,
                                                       args=(1500,
                                                             0.1,
                                                             int(self.amount_of_loops_entry.get()),
                                                             problem.d,
                                                             self.input_pipe
                                                             )
                                                       )
            solution_process.start()
        except ValueError:
            messagebox.showerror("Ошибка!", "Количество итераций должно быть целым числом!")

    def draw_current_solution(self):
        self.canvas.delete(tk.ALL)
        # Вычисление коэффициентов - отношений между размером холста и требуемым размером для отображения координат
        # (Будут использоваться для вычисления относительных координат точек на холсте)
        min_x = min(self.node_list, key=lambda item: item[0])[0]
        min_y = min(self.node_list, key=lambda item: item[1])[1]
        max_x = max(self.node_list, key=lambda item: item[0])[0]
        max_y = max(self.node_list, key=lambda item: item[1])[1]
        canvas_width = self.canvas.winfo_width() - 6  # ширина холста
        canvas_height = self.canvas.winfo_height() - 6  # высота холста
        indent = 3  # отступ, чтобы точки не рисовались на границе холста
        # Непосредственно вычисление коэффициентов
        coefficient_x = (max_x - min_x) / (canvas_width - 2*indent)
        coefficient_y = (max_y - min_y) / (canvas_height - 2*indent)
        coefficient = max(coefficient_x, coefficient_y)  # нахождение наибольшего коэффициента
        # Вычисление относительных координат
        self.node_list = [((node[0]-min_x) / coefficient + indent,
                           (node[1]-min_y) / coefficient + indent)
                          for node in self.node_list
                          ]
        # Рисование точек на холсте
        for x, y in self.node_list:
            self.canvas.create_oval(x-2, y-2, x+2, y+2, fill="black")

        while True:
            print("поток работает")
            try:
                x, outer_cntr, best = self.output_pipe.recv()
                self.outer_cntr_value.configure(text=str(outer_cntr))
                self.best_solution_value.configure(text=str(best))
                print(x)
                for line in self.lines:
                    self.canvas.delete(line)
                for ind in range(len(x)):
                    self.lines.append(self.canvas.create_line(*self.node_list[x[ind]],
                                                              *self.node_list[x[(ind+1) % len(x)]])
                                      )
            except Exception:
                break

        print("ПОТОК ОТРАБОТАЛ")


def get_solution(temp_len, p0, outer_limit, d, input_pipe):
    solution.Solution(temp_len, p0, outer_limit, d, input_pipe=input_pipe)


if __name__ == "__main__":
    window = Interface()
    window.mainloop()
