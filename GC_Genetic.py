import random
import math
import copy
import time
import numpy as np


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

    def mutate(self, mut_chance, mut_range: tuple):
        if mut_range[0] > mut_range[1] or mut_range[0] < 0 or mut_range[1] > len(self.__inst):
            raise WrongMuteRange
        rand = random.random()
        if rand < mut_chance:
            numb_of_mut = random.randint(mut_range[0], mut_range[1])
            n = len(self.__inst)
            for i in range(n):
                if random.random() <= numb_of_mut / (n - i):
                    self.__inst[i] = self.__pick_color(i)
                    numb_of_mut -= 1
            self.__rank = self.__calculate_rank()

    def repair(self, start=0, stop=-1):
        if stop == -1:
            stop = len(self.__inst)
        for i in range(start, stop):
            if self.__is_conflict(self.__inst[i], i):
                self.__pick_color2(i)

    def __is_conflict(self, color, index):
        for i in self.__graph[index]:
            if i == color:
                return True
        return False

    def __pick_color(self, x):
        temp = [0] * len(self.__inst)
        for i in self.__graph[x]:
            temp[self.__inst[i]] = 1
        for j in range(len(temp)):
            if temp[j] == 0:
                return j

    def __pick_color2(self, x):
        temp = [0] * len(self.__inst)
        for i in self.__graph[x]:
            temp[self.__inst[i]] = 1
        rand = random.randint(0, len(self.__inst))
        while rand + 1 % len(self.__inst) == 0:
            if temp[rand % len(self.__inst)] == 0:
                return rand

    def __calculate_rank(self):
        rank = len(set(self.__inst))
        return rank

    def get_rank(self):
        return self.__rank

    def get_inst(self):
        return self.__inst

    def set_inst(self, inst):
        self.__inst = inst


class WrongDeleteRange(Exception):
    """Niewłaściwy zakres: [0-1]"""
    pass


class GC_Genetic:
    def __init__(self, graph, numb_of_inst, numb_of_iter, delete=0.5, mut_chance=0.05, mut_range: tuple = (1, 3), mut_range_multiplier=2):
        self.__gen_number = 1
        self.__graph = graph
        self.__generation = [Instance(self.__graph) for _ in range(numb_of_inst)]
        self.__chances_to_merge = self.__calculate_chances_to_merge(delete)
        self.__sort_generation()

        for i in range(numb_of_iter):
            self.print_generation()
            gen_multi = int((mut_range_multiplier * (numb_of_iter - i + 1) / numb_of_iter))
            self.__next_generation(delete, mut_chance, (gen_multi * mut_range[0], gen_multi * mut_range[1]))
        self.print_result()

    def __next_generation(self, delete, mut_chance, mut_range):
        if delete < 0 or delete > 1:
            raise WrongDeleteRange
        self.__gen_number += 1
        n = len(self.__generation)
        how_many_to_save = n - math.floor(n * delete)
        self.__generation = self.__generation[:how_many_to_save]
        for i in range(n - how_many_to_save):
            #pick instances to merge
            to_marge = np.random.choice(how_many_to_save, 2, p=self.__chances_to_merge, replace=False)
            self.__generation.append(copy.deepcopy(self.__generation[to_marge[0]]))
            self.__merge_instances(self.__generation[-1], self.__generation[to_marge[1]])
            self.__generation[-1].mutate(mut_chance, mut_range)
        self.__sort_generation()

    def __merge_instances(self, inst1: Instance, inst2: Instance, proportions=0.5):
        rand = random.random()
        l = len(inst1.get_inst())
        ammount = math.floor(l * proportions)
        if rand > 0.5:
            inst1.set_inst(inst1.get_inst()[:ammount] + inst2.get_inst()[ammount:])
            inst1.repair(ammount)
        else:
            inst1.set_inst(inst2.get_inst()[:ammount] + inst1.get_inst()[ammount:])
            inst1.repair(0, ammount)

    def __calculate_chances_to_merge(self, delete):
        n = len(self.__generation)
        l = n - math.floor(n * delete)
        result = []
        for i in range(1, l * 2, 2):
            result.append(1/l)
        return result

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
    GC = GC_Genetic(x, 500, 200, 0.5, 0.5, (1, 2), 5)
    print(time.time() - t)
    gc = GC_Greedy(x)
    t = time.time()
    print(max(gc.gc_greedy()) + 1)
    print(time.time() - t)