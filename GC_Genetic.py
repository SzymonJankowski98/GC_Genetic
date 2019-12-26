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
    def __init__(self, graph, ammount_of_colors):
        self.__graph = graph
        self.__ammount_of_colors = ammount_of_colors
        self.__inst = []
        self.__generate_instance()
        self.__rank = self.__calculate_rank()

    def __generate_instance(self):
        for i in range(len(self.__graph)):
            avail = self.__bit_vect_to_array(self.__available_colors(i))
            if avail == []:
                self.__inst.append(self.__ammount_of_colors)
                self.__ammount_of_colors += 1
            else:
                pick = int(np.random.choice(avail, 1))
                self.__inst.append(pick)

    def mutate(self, mut_chance, mut_range: tuple):
        if mut_range[0] > mut_range[1] or mut_range[0] < 0 or mut_range[1] > len(self.__inst):
            raise WrongMuteRange
        rand = random.random()
        if rand < mut_chance:
            numb_of_mut = random.randint(mut_range[0], mut_range[1])
            n = len(self.__inst)
            for i in range(n):
                if random.random() <= numb_of_mut / (n - i):
                    self.__inst[i] = self.__pick_color2(i)
                    numb_of_mut -= 1
            self.__rank = self.__calculate_rank()

    def repair(self, start=0, stop=-1):
        if stop == -1:
            stop = len(self.__inst)
        for i in range(start, stop):
            if self.__is_conflict(self.__inst[i], i):
                self.__inst[i] = self.__pick_color2(i)
        self.__rank = self.__calculate_rank()

    def __is_conflict(self, color, index):
        for i in self.__graph[index]:
            if self.__inst[i] == color:
                return True
        return False

    def __available_colors(self, vert):
        col = [0] * self.__ammount_of_colors
        for i in self.__graph[vert]:
            try:
                if self.__inst[i]:
                    col[self.__inst[i]] = 1
            except IndexError:
                #break
                pass
        return col

    def __bit_vect_to_array(self, vec):
        result = []
        for i in range(len(vec)):
            if vec[i] == 0:
                result.append(i)
        return result

    def __pick_color(self, x):
        temp = self.__available_colors(x)
        for j in range(len(temp)):
            if temp[j] == 0:
                return j

    def __pick_color2(self, x):
        temp = self.__available_colors(x)
        rand = random.randint(0, self.__ammount_of_colors)
        for i in range(rand, rand + self.__ammount_of_colors):
            if temp[i % self.__ammount_of_colors] == 0:
                return i % self.__ammount_of_colors

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
        greedy = GC_Greedy(graph)
        self.__generation = [Instance(self.__graph, max(greedy.gc_greedy()) + 1) for _ in range(numb_of_inst)]
        self.__sort_generation()
        self.__chances_to_merge = self.__calculate_chances_to_merge(delete)

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
            self.__merge_instances(self.__generation[-1], self.__generation[to_marge[1]], 0.5)
            self.__generation[-1].mutate(mut_chance, mut_range)
        self.__sort_generation()

    def __merge_instances(self, inst1: Instance, inst2: Instance, proportions=random.random()):
        l = len(inst1.get_inst())
        #ammount = math.floor(l * proportions)
        new_inst = []
        for i in range(len(l)):
            f
        #inst1.set_inst(inst1.get_inst()[:ammount] + inst2.get_inst()[ammount:])
        #inst1.repair(ammount)

    def __calculate_chances_to_merge(self, delete):
        result = []
        n = len(self.__generation)
        how_many = n - math.floor(n * delete)
        for i in range(1, how_many * 2, 2):
            result.append((how_many * 2 - i) / how_many ** 2)
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
    x = Graph().load("queen6.txt")
    t = time.time()
    GC = GC_Genetic(x, 300, 100, 0.75, 1, (1, 30), 1)
    print(time.time() - t)
    gc = GC_Greedy(x)
    t = time.time()
    print(max(gc.gc_greedy()) + 1)
    print(time.time() - t)