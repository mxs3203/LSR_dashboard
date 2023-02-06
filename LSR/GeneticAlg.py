import json
import os
import time

import numpy as np
from pygad import pygad

from LSR.LSR_comm import LSR_comm
from LSR.SpectraWizSaver import save_curve
#from LSR.LSR_comm import LSR_comm
#from LSR.SpectraWizSaver import save_curve
from LSR.utils import scale_curve, readAndCurateCurve, generate_random

def on_generation(ga_instance):
    print("\t\tGeneration : ", ga_instance.generations_completed)
    print("\t\tFitness of the best solution :", ga_instance.best_solution()[1])
    print("\t\tTen Nums:", ga_instance.best_solution()[0])
    solution_json = {"generation": ga_instance.generations_completed,
                     "fitness": ga_instance.best_solution()[1],
                     "solution": ga_instance.best_solution()[0].tolist()
                     }
    solution_json = json.dumps(solution_json)
    print(solution_json)
    with open("tmp/solution.json", "w") as outfile:
        outfile.write(solution_json)

    time.sleep(3)


class GeneticAlg:

    def __init__(self, init_range_low, init_range_high, gene_space):
        self.num_generations = 10
        self.num_parents_mating = 4
        self.sol_per_pop = 8
        self.num_genes = 10
        self.parent_selection_type = "sss"
        self.keep_parents = 2
        self.crossover_type = "scattered"
        self.mutation_type = "random"
        self.mutation_percent_genes = 20
        self.init_range_low = init_range_low
        self.init_range_high = init_range_high
        self.gene_space = gene_space
        self.function_inputs = generate_random(int(init_range_high))
        self.ga_instance = pygad.GA(num_generations=self.num_generations,
                                    num_parents_mating=self.num_parents_mating,
                                    fitness_func=fitness_func_offline,
                                    sol_per_pop=self.sol_per_pop,
                                    num_genes=self.num_genes,
                                    gene_type=int,
                                    gene_space=None,
                                    init_range_low=self.init_range_low,
                                    init_range_high=self.init_range_high,
                                    parent_selection_type=self.parent_selection_type,
                                    keep_parents=self.keep_parents,
                                    crossover_type=self.crossover_type,
                                    mutation_type=self.mutation_type,
                                    mutation_percent_genes=self.mutation_percent_genes,
                                    keep_elitism=1,
                                    save_best_solutions=True,
                                    on_generation=on_generation)


    def run(self):
        self.ga_instance.run()
        print(self.ga_instance.best_solutions)
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        print("Parameters of the best solution : {solution}".format(solution=solution))
        print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))

        prediction = np.sum(np.array(self.function_inputs) * solution)
        print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))


def fitness_func_offline(solution, soulution_idx):
    sensor_reading = np.random.randint(500, size=161)
    desired_output, _ = readAndCurateCurve("tmp/ref.IRR")
    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading))).mean(axis=0)
    print("MSE= ", mse)
    print("Fitness: ", 1.0 / mse)
    return 1.0 / mse

def fitness_func_online(solution, soulution_idx):
    solution = [int(ele) for ele in solution]
    lsr = LSR_comm("COM3")
    # Start LSR with params
    lsr.set_column_data(1, solution)
    lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
    lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
    lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
    lsr.run()

    # Spectra has to point to example_database folder before starting
    save_curve("{}".format("tmp/recreated.ssm"))
    print("Waiting for recreated file to be saved...")
    time.sleep(0.5)
    while not os.path.exists("tmp/{}".format("recreated.ssm")):
        time.sleep(1)

    print("\t Reading new HyperOCR data...")
    # Read HYperOCR (Current Curve)
    sensor_reading, _ = readAndCurateCurve("tmp/recreated.ssm")

    desired_output, _ = readAndCurateCurve("tmp/ref.IRR")
    # sensor_reading = np.random.randint(65000, size=201)

    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading['value'].values))).mean(axis=0)
    print("MSE= ", mse)
    print("Fitness: ", 1.0 / mse)
    return 1.0 / mse



