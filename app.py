import os
import numpy as np
from RSLP_Solver import SimplexSolver
from flask import Flask, request, render_template



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    file = request.files['file']
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    solver = SimplexSolver(filepath)
    solutions = solver.run()
    initial_values = " ".join(solver.BFS)
    return render_template('result.html', solutions=solutions, initial_values=initial_values)

@app.route('/solve-manual', methods=['POST'])
def solve_manual():
    m = int(request.form['m'])
    n = int(request.form['n'])
    objective_coefficients = [float(coeff) for coeff in request.form['objective-coefficients'].split()]
    constraint_coefficients = []
    for i in range(m):
        coefficients = [float(coeff) for coeff in request.form[f'constraint-coefficients-{i+1}'].split()]
        constraint_coefficients.append(coefficients)
    A = np.array(constraint_coefficients)
    solver = SimplexSolver()
    solver.m = m
    solver.n = n
    solver.c = np.append(np.array(objective_coefficients), [0] * m)
    solver.A = np.concatenate((A[:, :-1], np.identity(m)), axis=1)
    solver.b = A[:, -1]
    solver.initialize_variables()
    solutions = solver.run()
    initial_values = " ".join(solver.BFS)
    return render_template('result.html', solutions=solutions, initial_values=initial_values)

if __name__ == '__main__':
    app.run(debug=True)
