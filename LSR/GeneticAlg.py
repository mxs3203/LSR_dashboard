import json
import os
import time

import numpy as np
from matplotlib import pyplot as plt
plt.switch_backend('Agg')
from pygad import pygad

from LSR.SpectraWizSaver import save_curve
from LSR.utils import scale_curve, readAndCurateCurve, generate_random

def make_plot(ten_nums, recon_curve, ref_curve, nm):
    plt.plot(nm, recon_curve)
    plt.plot(nm, ref_curve)
    plt.legend(['Recreated by {} gen'.format(10), 'Ref Curve'])
    plt.title("_".join(str(e) for e in ten_nums))
    plt.savefig("tmp/fig.png", transparent=True)


def on_generation(ga_instance):
    print("ON GENERATION")
    with open('tmp/solution_curve.json') as json_file:
        recon_curve = json.load(json_file)
        json_file.close()
    ref_curve, _ = readAndCurateCurve("tmp/ref.IRR")
    # print(recon_curve)
    print("\t\tGeneration : ", ga_instance.generations_completed)
    print("\t\tFitness of the best solution :", ga_instance.best_solution()[1])
    print("\t\tTen Nums:", ga_instance.best_solution()[0])
    solution_json = {"generation": ga_instance.generations_completed,
                     "fitness": ga_instance.best_solution()[1],
                     "solution": ga_instance.best_solution()[0].tolist(),
                     "reconstruced_curve": recon_curve[0],
                     "ref_curve": ref_curve['value'].values.tolist(),
                     "nm": ref_curve['nm'].values.tolist(),
                     "temp": recon_curve[1],
                     "current_process": recon_curve[2],
                     "tec_status": recon_curve[3]
                     }
    solution_json = json.dumps(solution_json)
    with open("tmp/solution.json", "w") as outfile:
        outfile.write(solution_json)
        outfile.close()

    if ga_instance.generations_completed == 10:
        make_plot(ga_instance.best_solution()[0], recon_curve[0], ref_curve['value'].values.tolist(), ref_curve['nm'].values.tolist())


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
                                    fitness_func=fitness_func_online,
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
    sensor_reading = np.random.randint(120, size=161)
    sensor_reading_json = sensor_reading.tolist()
    sensor_reading_json = json.dumps(sensor_reading_json)
    with open("tmp/solution_curve.json", "w") as outfile:
        outfile.write(sensor_reading_json)
        outfile.close()

    desired_output, _ = readAndCurateCurve("tmp/ref.IRR")
    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading))).mean(axis=0)
    print("MSE= ", mse)
    print("Fitness: ", 1.0 / mse)
    return 1.0 / mse

def fitness_func_online(solution, soulution_idx):
    solution = [int(ele) for ele in solution]
    #lsr = LSR_comm("COM3")
    # Start LSR with params
    from main import lsr as lsr
    lsr.set_column_data(1, solution)
    lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
    lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
    lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
    lsr.run()

    lsr.ask_for_status()
    temp = lsr.block_temp
    current_process = lsr.current_process
    tec_status = lsr.tec_status

    # Spectra has to point to example_database folder before starting
    save_curve("{}".format("recreated.IRR"))
    print("Waiting for recreated file to be saved...")

    while not os.path.exists("tmp/{}".format("recreated.IRR")):
        time.sleep(0.2)

    print("\t Reading new HyperOCR data...")
    # Read HYperOCR (Current Curve)
    sensor_reading, _ = readAndCurateCurve("tmp/recreated.IRR")

    #sensor_reading = pd.DataFrame(list(zip(np.random.randint(120, size=161),np.random.randint(120, size=161))), columns=['nm','value'])
    sensor_reading_json = sensor_reading['value'].values.tolist()
    sensor_reading_json = json.dumps([sensor_reading_json, temp, current_process, tec_status])
    with open("tmp/solution_curve.json", "w") as outfile:
        outfile.write(sensor_reading_json)
        outfile.close()

    desired_output, _ = readAndCurateCurve("tmp/ref.IRR")
    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading['value'].values))).mean(axis=0)
    print("MSE= ", mse)
    print("Fitness: ", 1.0 / mse)
    return 1.0 / mse


