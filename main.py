import json
import os
import shutil

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import sqlite3

from werkzeug.utils import secure_filename

import admin

from LSR.GeneticAlg import GeneticAlg
from LSR.LSR_comm import LSR_comm
from LSR.utils import readAndCurateCurve, findLSRTenNumberRange, computeRange


if not admin.isUserAdmin():
    admin.runAsAdmin()

device_port = "COM3"
app = Flask(__name__)

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
@app.route('/set_lsr_temp')
def set_lsr_temp():
    if request.method == 'GET':
        task = request.args.get('task')
        value = request.args.get('value')
        print(task, value)

        lsr = LSR_comm(device_port)
        lsr.set_block_temp(value)
        lsr.run()

        return "{}", 200
    else:
        return "{}", 205

@app.route('/abort_lsr')
def abort_lsr():
    if request.method == 'GET':

        lsr = LSR_comm(device_port)
        lsr.stop()

        return "{}", 200
    else:
        return "{}", 205

@app.route('/findCurve',methods=['POST'])
def findCurve():
    if request.method == 'POST':
        f = request.files['file']
        f.save("tmp/ref.IRR")
        curve, log10curve = readAndCurateCurve("tmp/ref.IRR")
        simulated_range = findLSRTenNumberRange(log10curve)
        ten_num_range, init_range_low, init_range_high = computeRange(simulated_range)
        #print(ten_num_range, init_range_low, init_range_high)

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
        lsr = LSR_comm(device_port)
        lsr.ask_for_status()
        data = {}
        data["temp"] = lsr.block_temp
        data["current_process"] = lsr.current_process
        data["tec_status"] = lsr.tec_status
        data["connected"] = True
        return data, 200
    else:
        return "", 404

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    clearTmp()
    app.debug = True
    app.run()