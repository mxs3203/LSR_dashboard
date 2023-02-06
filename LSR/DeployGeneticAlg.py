import os
import time

import numpy as np
import pygad

from LSR.utils import readAndCurateCurve, scale_curve, findLSRTenNumberRange, computeRange, generate_random
#import admin
from LSR_comm import LSR_comm
from SpectraWizSaver import save_curve
import matplotlib.pyplot as plt


#if not admin.isUserAdmin():
#    admin.runAsAdmin()


input_curve_file = r"C:\Users\Korisnik\Desktop\MLJET10_2022\2110_1418oblacno_uW.IRR"
file_name = input_curve_file.split("\\")[-1]
desired_output_all, desired_log10_curve = readAndCurateCurve(input_curve_file)
desired_output = desired_output_all['value'].values


def fitness_func(solution, soulution_idx):

    solution = [int(ele) for ele in solution]
    lsr = LSR_comm("COM3")
    # Start LSR with params
    lsr.set_column_data(1, solution)
    lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
    lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
    lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
    lsr.run()

    # Spectra has to point to example_database folder before starting
    save_curve("{}".format("recreated.ssm"))
    print("Waiting for recreated file to be saved...")
    time.sleep(0.5)
    while not os.path.exists("example_database/{}".format("recreated.ssm")):
        time.sleep(1)

    print("\t Reading new HyperOCR data...")
    # Read HYperOCR (Current Curve)
    sensor_reading,_ = readAndCurateCurve("example_database/recreated.ssm")

    #sensor_reading = np.random.randint(65000, size=201)

    mse = (np.abs(scale_curve(desired_output) - scale_curve(sensor_reading['value'].values))).mean(axis=0)
    print("MSE= ",mse)
    print("Fitness: ", 1.0/mse)
    return 1.0/mse


fitness_function = fitness_func

num_generations = 10
num_parents_mating = 4

sol_per_pop = 8
num_genes = 10

parent_selection_type = "sss"
keep_parents = 2

crossover_type = "scattered"

mutation_type = "random"
mutation_percent_genes = 20

simulated_range = findLSRTenNumberRange(desired_log10_curve)

print("1",simulated_range)
ten_num_range, init_range_low, init_range_high = computeRange(simulated_range)
print("2", ten_num_range)
print("3",init_range_low)
print("4",init_range_high)
function_inputs = generate_random(int(init_range_high))
print("5",function_inputs)

ga_instance = pygad.GA(num_generations=num_generations,
                       num_parents_mating=num_parents_mating,
                       fitness_func=fitness_function,
                       sol_per_pop=sol_per_pop,
                       num_genes=num_genes,
                       gene_type=int,
                       gene_space=None,
                       init_range_low=init_range_low,
                       init_range_high=init_range_high,
                       parent_selection_type=parent_selection_type,
                       keep_parents=keep_parents,
                       crossover_type=crossover_type,
                       mutation_type=mutation_type,
                       mutation_percent_genes=mutation_percent_genes,
                       keep_elitism=1,
                       save_best_solutions=True)

ga_instance.run()
print(ga_instance.best_solutions)
solution, solution_fitness, solution_idx = ga_instance.best_solution()
print("Parameters of the best solution : {solution}".format(solution=solution))
print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=solution_fitness))

prediction = np.sum(np.array(function_inputs)*solution)
print("Predicted output based on the best solution : {prediction}".format(prediction=prediction))

lsr = LSR_comm("COM3")
time.sleep(0.5)
# Start LSR with params
lsr.set_column_data(1, solution)
lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
lsr.run()

save_curve("{}".format("recreated.IRR"))
print("Waiting for recreated file to be saved...")
time.sleep(0.5)
while not os.path.exists("example_database/{}".format("recreated.IRR")):
    time.sleep(1)

print("\t Reading new HyperOCR data...")
# Read HYperOCR (Current Curve)
sensor_reading, _ = readAndCurateCurve("example_database/recreated.IRR")
# Compare the two curves
plt.plot(sensor_reading['nm'].values, sensor_reading['value'].values)
plt.plot(desired_output_all['nm'].values, desired_output_all['value'].values)
plt.legend(['Recreated by {} gen'.format(num_generations), file_name])
plt.title("The best solution(MSE)")
plt.show()



# Go through top 3 solutions
cnt = 1
for s in ga_instance.best_solutions:
    lsr.set_column_data(1, s)
    lsr.set_column_data(2, lsr.compute_column_based_on_first(0.7))
    lsr.set_column_data(3, lsr.compute_column_based_on_first(0.5))
    lsr.set_column_data(4, lsr.compute_column_based_on_first(0.3))
    lsr.run()

    save_curve("{}".format("recreated.IRR"))
    print("Waiting for recreated file to be saved...")
    time.sleep(0.5)
    while not os.path.exists("example_database/{}".format("recreated.IRR")):
        time.sleep(1)

    print("\t Reading new HyperOCR data...")
    # Read HYperOCR (Curreynt Curve)
    sensor_reading, _ = readAndCurateCurve("example_database/recreated.IRR")
    # Compare the two curves
    plt.plot(sensor_reading['nm'].values, sensor_reading['value'].values)
    plt.plot(desired_output_all['nm'].values, desired_output_all['value'].values)
    plt.legend(['Recreated by {} gen'.format(num_generations), file_name])
    plt.title("Alternative Solution {}".format(cnt))
    plt.show()
    cnt = cnt + 1
    if cnt > 3:
        break






# wait for 100 sec
time.sleep(10000)