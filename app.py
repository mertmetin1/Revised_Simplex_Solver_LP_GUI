from flask import Flask, request, render_template, send_file
import os
import tempfile
from RSLP_Solver import SimplexSolver

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/solve', methods=['POST'])
def solve():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    objective = request.form.get('objective')
    if file and objective:
        filepath = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(filepath)
        solver = SimplexSolver(filepath, objective)
        solver.run()
        solution = solver.get_solution_output()
        return render_template('result.html', solution=solution)
    return 'Invalid input', 400

@app.route('/solve-manual', methods=['POST'])
def solve_manual():
    try:
        m = int(request.form['m'])
        n = int(request.form['n'])
        c = list(map(float, request.form['objective-coefficients'].split()))
        constraints = []
        for i in range(m):
            row = list(map(float, request.form[f'constraint-coefficients-{i+1}'].split()))
            constraints.append(row)
        b = [row.pop() for row in constraints]
        A = [row for row in constraints]
        objective = request.form.get('objective')
        
        with tempfile.NamedTemporaryFile(delete=False) as temp:
            temp.write(f"{m} {n}\n".encode())
            temp.write(" ".join(map(str, c)).encode() + b"\n")
            for i in range(m):
                temp.write(" ".join(map(str, A[i])).encode() + b" " + str(b[i]).encode() + b"\n")
            temp_filepath = temp.name
        
        solver = SimplexSolver(temp_filepath, objective)
        solver.run()
        solution = solver.get_solution_output()
        os.remove(temp_filepath)
        return render_template('result.html', solution=solution)
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(debug=True)
