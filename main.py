import json
import os
import matplotlib.pyplot as plt
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
import sqlite3

from werkzeug.utils import secure_filename

from LSR.FakeLSR_Comm import FakeLSR_comm
from LSR.GeneticAlg import GeneticAlg
from LSR.utils import readAndCurateCurve, findLSRTenNumberRange, computeRange

app = Flask(__name__)

ga_instance = None

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

@app.route('/create', methods=('GET', 'POST'))
def create():

    if request.method == 'POST':

        name = request.form['name']
        temp = request.form['current_temp']
        ref_curve = request.form['ref_curve']
        lsr_params = request.form['lsr_params']
        print(name, temp, ref_curve, lsr_params)


        conn = get_db_connection()
        conn.execute("INSERT INTO lsr_data (name, temp, input_curve,lsr_params) VALUES (?, ?, ?, ?)",
                (name,temp, ref_curve, lsr_params)
                     )
        conn.commit()
        conn.close()
        return redirect('/')
    else:

        return redirect('/')

@app.route('/set_lsr_temp')
def set_lsr_temp():
    if request.method == 'GET':
        task = request.args.get('task')
        value = request.args.get('value')
        print(task, value)

        lsr = FakeLSR_comm()
        lsr.set_block_temp(value)
        lsr.run()

        return "{\"response\": \"Success\"}"
    else:
        return "{\"response\": \"Fail\"}"

@app.route('/abort_lsr')
def abort_lsr():
    if request.method == 'GET':

        lsr = FakeLSR_comm()
        lsr.stop()

        return "{\"response\": \"Success\"}"
    else:
        return "{\"response\": \"Fail\"}"

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

        return "{\"response\": \"Success\"}"
    else:
        return "{\"response\": \"Fail\"}"

@app.route('/get_current_solution')
def get_current_solution():
    if request.method == 'GET' and os.path.isfile("tmp/solution.json"):
        f = open('tmp/solution.json')
        data = json.load(f)

        lsr = FakeLSR_comm()
        lsr.ask_for_status()
        data["temp"] = lsr.temp
        return data
    else:
        return "{\"response\": \"Fail\"}"

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
