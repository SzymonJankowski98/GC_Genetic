import random
import math
import copy
import time


class Graph:
    def __init__(self):
        self.__graph = None

    def load(self, file):
        FILE = open(file, "r")
        ammount = FILE.readline()
        self.__graph = [[] for i in range(int(ammount))]
        for line in FILE:
            line = line.split(" ")
            self.__graph[int(line[0]) - 1].append(int(line[1]) - 1)
            self.__graph[int(line[1]) - 1].append(int(line[0]) - 1)
        FILE.close()
        return self.__graph

    def generate(self):
        pass


class GC_Greedy:
    def __init__(self, graph):
        self.__graph = graph

    def gc_greedy(self):
        colors = [-1] * len(self.__graph)
        for i in range(len(self.__graph)):
            colors[i] = self.__pick_color(i, colors)
        return colors

    def __pick_color(self, x, colors):
        temp = [0] * len(self.__graph)
        for i in self.__graph[x]:
            if colors[i] > -1:
                temp[colors[i]] = 1
        for j in range(len(temp)):
            if temp[j] == 0:
                return j
        return len(self.__graph) + 1


class WrongMuteRange(Exception):
    """Niewłaściwy zakres: [(a, b)]
       k = ilość wierzchołków
       a = [0 - k]
       b = [0 - k]
       a <= b
    """
    pass


class Instance:
    def __init__(self, graph):
        self.__graph = graph
        self.__inst = self.__generate_instance()
        self.__rank = self.__calculate_rank()

    def __generate_instance(self):
        inst = random.sample(list(range(len(self.__graph))), k=len(self.__graph))
        return inst

    def mutate(self, mut_range: tuple):
        if mut_range[0] > mut_range[1] or mut_range[0] < 0 or mut_range[1] > len(self.__inst):
            raise WrongMuteRange
        numb_of_mut = random.randint(mut_range[0], mut_range[1])
        n = len(self.__inst)
        for i in range(n):
            if random.random() <= numb_of_mut / (n - i):
                self.__inst[i] = self.__pick_color(i)
                numb_of_mut -= 1
        self.__rank = self.__calculate_rank()

    def __pick_color(self, x):
        temp = [0] * len(self.__inst)
        for i in self.__graph[x]:
            temp[self.__inst[i]] = 1
        for j in range(len(temp)):
            if temp[j] == 0:
                return j

    def __calculate_rank(self):
        rank = len(set(self.__inst))
        return rank

    def get_rank(self):
        return self.__rank

    def get_inst(self):
        return self.__inst


class WrongDeleteRange(Exception):
    """Niewłaściwy zakres: [0-1]"""
    pass


class GC_Genetic:
    def __init__(self, graph, numb_of_inst):
        self.__gen_number = 1
        self.__graph = graph
        self.__generation = [Instance(self.__graph) for _ in range(numb_of_inst)]
        self.__sort_generation()

    def gc_genetic(self, numb_of_iter, delete=0.5, mut_range: tuple = (1, 5), range_multiplier=10):
        for i in range(numb_of_iter):
            self.print_generation()
            gen_multi = int((range_multiplier * (numb_of_iter - i + 1) / numb_of_iter))
            self.next_generation(delete, (gen_multi * mut_range[0], gen_multi * mut_range[1]))
        self.print_result()

    def next_generation(self, delete, mut_range):
        if delete < 0 or delete > 1:
            raise WrongDeleteRange
        self.__gen_number += 1
        n = len(self.__generation)
        how_many_to_save = n - math.floor(n * delete)
        self.__generation = self.__generation[:how_many_to_save]
        mod = len(self.__generation)
        for i in range(n - how_many_to_save):
            self.__generation.append(copy.deepcopy(self.__generation[i % mod]))
            self.__generation[i % mod].mutate(mut_range)
        self.__sort_generation()

    def __sort_generation(self):
        self.__generation.sort(key=lambda x: x.get_rank())

    def print_generation(self):
        print("Generation nr " + str(self.__gen_number) + ":")
        for i in self.__generation:
            print([i.get_rank(), i.get_inst()])
        print("_____________________________________________________________________")

    def print_result(self):
        print([self.__generation[0].get_rank(), self.__generation[0].get_inst()])


if __name__ == '__main__':
    x = Graph().load("inst2.txt")
    t = time.time()
    GC = GC_Genetic(x, 50)
    GC.gc_genetic(20, 0.75, (1, 20))
    print(time.time() - t)
    gc = GC_Greedy(x)
    t = time.time()
    print(max(gc.gc_greedy()) + 1)
    print(time.time() - t)