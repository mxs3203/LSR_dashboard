import json
import os
import shutil
import time

import numpy as np
import pygad
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import sqlite3

from matplotlib import pyplot as plt
from numpy import trapz

import admin


from LSR.LSR_comm import LSR_comm
from LSR.SpectraWizSaver import save_curve
from LSR.utils import readAndCurateCurve, findLSRTenNumberRange, computeRange, generate_random, scale_curve

if not admin.isUserAdmin():
    admin.runAsAdmin()

device_port = "COM3"
app = Flask(__name__)
lsr = LSR_comm(device_port)
lsr.stop()


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
    ref_curve, log10_curve, lsr_peaks = readAndCurateCurve("tmp/ref.IRR")
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

def fitness_func_offline(solution, soulution_idx):
    sensor_reading = np.random.randint(120, size=161)
    sensor_reading_json = sensor_reading.tolist()
    sensor_reading_json = json.dumps(sensor_reading_json)
    with open("tmp/solution_curve.json", "w") as outfile:
        outfile.write(sensor_reading_json)
        outfile.close()


    desired_output, log10_curve,lsr_peaks = readAndCurateCurve("tmp/ref.IRR")
    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading))).mean(axis=0)
    print("MSE= ", mse)
    auc_ref = trapz(scale_curve(desired_output['value'].values), dx=5)
    auc_recon = trapz(scale_curve(sensor_reading), dx=5)
    print("Area Ref: ",auc_ref, " Area Recon: ", auc_recon)
    print ("Diff in Area: ", np.abs(auc_ref-auc_recon))
    fitness = (1.0/mse) + (1.0/np.abs(auc_ref-auc_recon))
    print("Fitness: ", fitness)
    return fitness

def fitness_func_online(solution, soulution_idx):
    solution = [int(ele) for ele in solution]
    #lsr = LSR_comm("COM3")
    # Start LSR with params
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
    sensor_reading, log10_curve, lsr_peaks = readAndCurateCurve("tmp/recreated.IRR")

    #sensor_reading = pd.DataFrame(list(zip(np.random.randint(120, size=161),np.random.randint(120, size=161))), columns=['nm','value'])
    sensor_reading_json = sensor_reading['value'].values.tolist()
    sensor_reading_json = json.dumps([sensor_reading_json, temp, current_process, tec_status])
    with open("tmp/solution_curve.json", "w") as outfile:
        outfile.write(sensor_reading_json)
        outfile.close()

    desired_output, log10_curve, lsr_peaks = readAndCurateCurve("tmp/ref.IRR")
    mse = (np.abs(scale_curve(desired_output['value'].values) - scale_curve(sensor_reading['value'].values))).mean(axis=0)
    print("MSE= ", mse)
    auc_ref = trapz(scale_curve(desired_output['value'].values), dx=1)
    auc_recon = trapz(scale_curve(sensor_reading['value'].values), dx=1)
    print("Area Ref: ", auc_ref, " Area Recon: ", auc_recon)
    print("Diff in Area: ", np.abs(auc_ref - auc_recon))
    fitness = (1.0 / mse) + (1.0 / np.abs(auc_ref - auc_recon))
    print("Fitness: ", fitness)
    return 1.0 / mse

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
        self.mutation_percent_genes = 30
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


###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################
###############################################################


@app.route('/')
def dashboard():
    conn = get_db_connection()
    lsr_data = conn.execute('SELECT * FROM lsr_data ORDER BY created DESC').fetchmany(5)
    conn.close()
    return render_template('index.html', lsr_data=lsr_data)

@app.route('/tables')
def tables():
    conn = get_db_connection()
    lsr_data = conn.execute('SELECT * FROM lsr_data ORDER BY created DESC').fetchall()
    conn.close()
    return render_template('tables.html', lsr_data=lsr_data)

@app.route('/figure')
def figure():
    if request.method == 'GET':
        figurePath = request.args.get('figure')
        return render_template('figure.html', figurePath=figurePath)
    else:
        return "{}", 404

@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':
        name = request.form['name']
        temp = request.form['current_temp']
        ref_curve = request.form['ref_curve']
        lsr_params = request.form['lsr_params']
        f = open('tmp/solution.json')
        data = json.load(f)
        f.close()
        fitness = data['fitness']
        mse = 1.0/fitness
        new_figure_name = "static/Figures/{}.png".format(checkNameForFigure())
        shutil.move("tmp/fig.png", new_figure_name)
        conn = get_db_connection()
        conn.execute("INSERT INTO lsr_data (name, temp, input_curve,lsr_params,mse,figure_path) VALUES (?, ?, ?, ?, ?, ?)",
                (name,temp, ref_curve, lsr_params, mse, new_figure_name)
                     )
        conn.commit()
        conn.close()
        clearTmp()
        return redirect('/')
    else:

        return redirect('/')

def checkNameForFigure():
    figures = os.listdir("static/Figures")
    #print(figures)
    if len(figures) == 0:
        return 1
    else:
        return extract_number(figures)
def extract_number(figures):
    return max([int(f.split(".")[0]) for f in figures]) + 1


def clearTmp():
    if os.path.isfile("tmp/solution.json"):
        os.remove("tmp/solution.json")
    if os.path.isfile("tmp/solution_curve.json"):
        os.remove("tmp/solution_curve.json")
    if os.path.isfile("tmp/ref.IRR"):
        os.remove("tmp/ref.IRR")
    if os.path.isfile("tmp/fig.png"):
        os.remove("tmp/fig.png")
    if os.path.isfile("tmp/recreated.IRR"):
        os.remove("tmp/recreated.IRR")

@app.route('/abort_lsr')
def abort_lsr():
    if request.method == 'GET':

        lsr.stop()

        return "{}", 200
    else:
        return "{}", 205

@app.route('/findCurve',methods=['POST'])
def findCurve():
    if request.method == 'POST':

        f = request.files['file']
        f.save("tmp/ref.IRR")
        curve, log10curve, lsr_peaks = readAndCurateCurve("tmp/ref.IRR")
        ref_auc = trapz(scale_curve(curve['value'].values), dx=1)
        simulated_range = findLSRTenNumberRange(lsr_peaks, ref_auc)
        ten_num_range, init_range_low, init_range_high = computeRange(simulated_range)
        print(ten_num_range, init_range_low, init_range_high)
        print(ref_auc)
        ga = GeneticAlg(init_range_low, init_range_high, ten_num_range)
        ga.run()

        return "{}", 200
    else:
        return "", 205

@app.route('/get_current_solution')
def get_current_solution():
    if request.method == 'GET' and os.path.isfile("tmp/solution.json"):
        f = open('tmp/solution.json')
        data = json.load(f)
        f.close()
        f = open('tmp/solution_curve.json')
        extra_data = json.load(f)
        data['temp'] = extra_data[1]
        data['current_process'] = extra_data[2]
        data['tec_status'] = extra_data[3]
        return data, 200
    else:
        return "",204

@app.route('/get_status')
def get_status():
    if request.method == 'GET':
        #lsr = LSR_comm(device_port)
        lsr.ask_for_status()
        data = {}
        data["temp"] = lsr.block_temp
        data["current_process"] = lsr.current_process
        data["tec_status"] = lsr.tec_status
        data["connected"] = True

        return data, 200
    else:
        return "", 404

@app.route('/set_lsr_temp')
def set_lsr_temp():
    if request.method == 'GET':
        task = request.args.get('task')
        value = request.args.get('value')
        if value != None:
            value = float(value) * 10.0
            #22.6, 226
            lsr.set_block_temp(int(value))

        return "{}", 200
    else:
        return "{}", 205


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    clearTmp()
    app.debug = False
    app.run()



