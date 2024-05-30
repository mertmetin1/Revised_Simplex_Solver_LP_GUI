import numpy as np
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

class SimplexSolver:
    def __init__(self, filepath=None):
        self.filepath = filepath
        if filepath:
            self.read_file()
            self.parse_data()
        self.iteration_solutions = []

    def read_file(self):
        with open(self.filepath, 'r') as file:
            self.data = file.read()

    def parse_data(self):
        lines = self.data.splitlines()
        self.m = int(lines[0].split()[0])
        self.n = int(lines[0].split()[1])
        self.c = np.array(list(map(float, lines[1].split())) + [0] * self.m)
        self.A = []
        self.b = []
        for line in lines[2:]:
            *row, b_val = map(float, line.split())
            self.A.append(row)
            self.b.append(b_val)
        self.A = np.array(self.A)
        self.b = np.array(self.b)
        self.A = np.concatenate((self.A, np.identity(self.m)), axis=1)
        self.initialize_variables()

    def initialize_variables(self):
        self.N = [f"x{i+1}" for i in range(self.n)]
        self.B = [f"x{self.n + i+1}" for i in range(self.m)]
        self.BFS = [f"x{i+1}=0" for i in range(self.n)] + [f"x{self.n + i+1}={self.b[i]}" for i in range(self.m)]
        self.x = self.N + self.B
        self.N_idx = list(range(1, self.n + 1))
        self.B_idx = list(range(self.n + 1, self.n + self.m + 1))
        self.Basic_coef = np.identity(self.m)
        self.Basic_coef_inv = np.linalg.inv(self.Basic_coef)
        self.cb = np.zeros((self.m, 1))
        self.kapa = np.dot(np.transpose(self.cb), self.Basic_coef_inv)
        self.M_inverse = np.identity(self.m + 1)
        self.current_sol = np.dot(self.M_inverse, np.concatenate(([0], self.b)))
        self.z = np.zeros(len(self.c))
        self.y = np.zeros(self.m)
        self.a = 1
        self.xb = self.b

    def run(self):
        while True:
            I_m = np.identity(self.m)
            entering_var_candidates = self.compute_entering_variable_candidates()
            if all(i >= 0 for i in np.around(entering_var_candidates, decimals=4)):
                self.iteration_solutions.append(self.get_optimal_solution())
                break
            entering_var = min(entering_var_candidates)
            entering_var_idx = np.argmin(entering_var_candidates)
            p = int(entering_var_idx)
            t = np.dot(self.Basic_coef_inv, self.A[:, p])
            if all(i <= 0 for i in np.round(t, decimals=4)):
                self.iteration_solutions.append(self.get_unbounded_solution(entering_var_candidates))
                break
            self.perform_pivoting(t, p)
            self.a += 1
            self.iteration_solutions.append(self.get_iteration_solution())
        return self.iteration_solutions

    def compute_entering_variable_candidates(self):
        carpan = np.concatenate(([1], self.kapa[0]))
        entering_var_candidates = []
        for i in range(len(self.c)):
            zj_cj = np.transpose(np.concatenate(([[-self.c[i]]], [self.A[:, i]]), axis=1))
            entering_var_candidates.append(np.dot(carpan, zj_cj))
        return np.asarray(entering_var_candidates)

    def perform_pivoting(self, t, p):
        positive_values = t[t > 0]
        idx_of_positive_values = np.array(np.where(t > 0)).reshape((-1, 1))
        ratio = self.xb[idx_of_positive_values] / t[idx_of_positive_values]
        leaving_var_idx = idx_of_positive_values[np.argmin(ratio)]
        q = int(leaving_var_idx)

        # Debug statements to track the pivoting process
        print(f"Entering variable index: {p}")
        print(f"Leaving variable index: {q}")
        print(f"N before pivoting: {self.N}")
        print(f"B before pivoting: {self.B}")
        print(f"N_idx before pivoting: {self.N_idx}")
        print(f"B_idx before pivoting: {self.B_idx}")

        eta_vector = -t
        eta_vector[q] = 1
        eta_vector = eta_vector / t[q]
        eta_vector = eta_vector.reshape((-1,))
        I_m = np.identity(self.m)
        I_m[:, q] = eta_vector
        self.Basic_coef_inv = np.dot(I_m, self.Basic_coef_inv)
        self.cb[q] = self.c[p]
        self.kapa = np.dot(np.transpose(self.cb), self.Basic_coef_inv)
        self.M_inverse = np.concatenate(([[1]], self.kapa), axis=1)
        dim = len(self.M_inverse[0]) - 1
        dim = np.array([[0]] * dim)
        expanded_B_inv = np.concatenate((dim, self.Basic_coef_inv), axis=1)
        self.M_inverse = np.concatenate((self.M_inverse, expanded_B_inv))
        self.current_sol = np.dot(self.M_inverse, np.concatenate(([0], self.b)))
        self.xb = np.dot(I_m, self.xb)
        self.N[p], self.B[q] = self.B[q], self.N[p]
        self.N_idx[p], self.B_idx[q] = self.B_idx[q], self.N_idx[p]
        self.y = self.kapa

        # Debug statements to verify the updates
        print(f"N after pivoting: {self.N}")
        print(f"B after pivoting: {self.B}")
        print(f"N_idx after pivoting: {self.N_idx}")
        print(f"B_idx after pivoting: {self.B_idx}")

    def get_iteration_solution(self):
        iteration_solution = {
            "type": "iteration",
            "iteration_number": self.a,
            "variables": [{"x{}".format(self.N_idx[i]): self.current_sol[i + 1]} for i in range(len(self.N))],
            "constraints": [{"x{}".format(self.B_idx[i]): self.current_sol[i + 1]} for i in range(len(self.B))],
            "objective_function": "z = {} ".format(self.current_sol[0]) + " + ".join(
                ["({:.2f})x{}".format(-self.c[i], self.N_idx[i]) for i in range(len(self.N_idx))]
            ),
        }
        return iteration_solution

    def get_optimal_solution(self):
        optimal_solution = {
            "type": "optimal",
            "iterations": self.a,
            "optimal_value": self.current_sol[0],
            "variables": [{"x{}".format(self.N_idx[i]): self.current_sol[i + 1]} for i in range(len(self.N))],
            "constraints": [{"x{}".format(self.B_idx[i]): self.current_sol[i + 1]} for i in range(len(self.B))],
            "objective_function": "z = {} ".format(self.current_sol[0]) + " + ".join(
                ["({:.2f})x{}".format(-self.c[i], self.N_idx[i]) for i in range(len(self.N_idx))]
            ),
        }
        return optimal_solution

    def get_unbounded_solution(self, entering_var_candidates):
        entering_var_candidates_formatted = [-candidate.item() for candidate in entering_var_candidates]
        unbounded_solution = {
            "type": "unbounded",
            "iterations": self.a,
            "variables": [{"x{}".format(i + 1): self.current_sol[i + 1]} for i in range(len(self.N))],
            "slack_variables": [{"x{}".format(i + self.n + 1): self.current_sol[i + 1]} for i in range(self.m)],
            "objective_function": "z = {} ".format(self.current_sol[0]) + " + ".join(
                ["({:.2f})x{}".format(entering_var_candidates_formatted[i], self.N_idx[i]) for i in range(len(self.N_idx))]
            ),
        }
        return unbounded_solution

    def get_solution_output(self):
        output = ""
        output += ">>>>>>>>>> giriş <<<<<<<<<<<\n"
        output += "{} {}\n".format(self.m, self.n)
        output += "{}\n".format(" ".join(map(str, self.c)))
        output += "{}\n".format(" ".join(map(str, self.b)))
        output += "A =\n{}\n".format(self.A)
        output += "x = { " + " ".join(["x{}".format(i) for i in range(1, self.n + 1)]) + " }\n"
        output += "N = { " + " ".join(["x{}".format(i) for i in self.N_idx]) + " }\n"
        output += "B = { " + " ".join(["x{}".format(i) for i in self.B_idx]) + " }\n"
        for i, solution in enumerate(self.iteration_solutions):
            output += "{}.döngü\n".format(i + 1)
            output += "cbar     {}\n".format(" ".join(["x{}:{}".format(self.N_idx[j], solution['cbar'][j]) for j in range(len(self.N_idx))]))
            output += "Giren değişken x{}\n".format(solution['entering_variable_idx'])
            output += "abarj = {}\n".format(solution['abarj'])
            output += "Oran {}\n".format(" ".join(["x{}:{:.4f}".format(self.N_idx[j], solution['ratio'][j]) for j in range(len(self.N_idx))]))
            output += "Ayrılan değişken x{}\n".format(solution['leaving_variable_idx'])
            output += "{}\n".format(solution['E'])
            output += "N = { " + " ".join(["x{}".format(i) for i in self.N_idx]) + " }\n"
            output += "B = { " + " ".join(["x{}".format(i) for i in self.B_idx]) + " }\n"
            output += "bbar = {}\n".format(solution['bbar'])
            output += "#################################################################################\n"
        solution = self.iteration_solutions[-1]
        output += "{}.döngü\n".format(len(self.iteration_solutions) + 1)
        output += "y = {}\n".format(" ".join(map(str, self.y)))
        output += "cbar     {}\n".format(" ".join(["x{}:{}".format(self.N_idx[j], solution['cbar'][j]) for j in range(len(self.N_idx))]))
        output += "Optimal Çözüm\n"
        output += "Döngü sayısı:{}\n".format(len(self.iteration_solutions))
        output += "Optimal değer {:.15f} ulaşıldı.\n".format(solution['optimal_value'])
        output += "Değişkenler:\n"
        output += "{}\n".format("\n".join(["x{} = {:.2f}".format(self.N_idx[i], self.current_sol[i + 1]) for i in range(len(self.N_idx))]))
        output += "Sınırlayıcılar:\n"
        output += "{}\n".format("\n".join(["x{} = {:.2f}".format(self.B_idx[i], self.current_sol[self.n + 1 + i]) for i in range(len(self.B_idx))]))
        output += "Amaç Fonksiyonu:\n"
        output += "{}\n".format(solution['objective_function'])
        return output