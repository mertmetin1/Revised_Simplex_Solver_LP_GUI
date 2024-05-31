# Simplex Solver

This project implements the Simplex method for solving linear programming (LP) problems. The Simplex method is an iterative algorithm for solving LP problems. It starts at an initial feasible solution and iteratively moves to adjacent feasible solutions in order to optimize the objective function.

## Overview

The project consists of a Python implementation of the Simplex method and a Flask web application to interactively solve LP problems. The Python implementation provides a `SimplexSolver` class that reads LP problems from files or accepts manual input and solves them using the Simplex method. The Flask web application allows users to upload LP problem files or input LP problems manually through a web interface and get the solutions displayed on the browser.

## Technical Details

### `SimplexSolver` Class

The `SimplexSolver` class implements the Simplex method. It has the following main components:

- `read_file()`: Reads LP problem data from a file.
- `parse_data()`: Parses the LP problem data and initializes the necessary variables.
- `initialize_variables()`: Initializes variables required for the Simplex method.
- `run()`: Runs the Simplex method iteratively until an optimal solution or an unbounded solution is found.
- `compute_entering_variable_candidates()`: Computes the entering variable candidates for the next iteration.
- `perform_pivoting()`: Performs pivoting operation to move to the next feasible solution.
- `get_optimal_solution()`, `get_unbounded_solution()`, `get_iteration_solution()`: Formats the solutions obtained during iterations.
- `get_solution_output()`: Retrieves the final solution output.

### Flask Web Application

The Flask web application provides a user-friendly interface for solving LP problems. It consists of the following routes:

- `/`: Renders the main page with options to upload a file or enter LP problem manually.
- `/solve`: Handles the file upload and solves the LP problem.
- `/solve-manual`: Handles manual input of LP problems and solves them.
- Templates: The HTML templates (`index.html` and `result.html`) provide the structure for the web pages and display the results of solving LP problems.

## Dependencies

- `numpy`: Used for numerical operations.
- `Flask`: Used to build the web application.
- `tempfile`: Used to create temporary files for manual input.
- `os`: Used for file operations.

## Usage

To use the Simplex solver:
1. Run the Flask web application by executing the `app.py` script.
2. Access the web interface in a browser.
3. Upload an LP problem file or enter the LP problem manually.
4. Select the objective (maximize or minimize) and click "Solve".
5. View the solution iterations and final solution on the result page.


Feel free to contribute by submitting bug reports, feature requests, or pull requests.

