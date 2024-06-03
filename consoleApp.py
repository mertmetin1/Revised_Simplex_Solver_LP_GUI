import numpy as np
import sys
import warnings

if not sys.warnoptions:
    warnings.simplefilter("ignore")

# Dosyadan oku.
with open("input.txt", ) as dosya:
    veri = dosya.read()  # Bu, dosyayı bir dize olarak okur.

# Geçerlilik kontrolü için veriyi yazdır.
print(">>>>>>>>>> giriş <<<<<<<<<<<")
print(veri)

# Satırları bölerek bir satır listesi al.
veri = veri.splitlines()

# Her bir satırdaki her karakteri ayır.
LP_Problem = []
for satir in veri:
    LP_Problem.append(satir.split())

# LP Problem'i bir dizi listesinden bir dizi diziye dönüştür.
for i in range(len(LP_Problem)):
    LP_Problem[i] = np.asarray(LP_Problem[i]).astype(float)

print(">>>>>>>>>> çıkış <<<<<<<<<<")

# m kısıtlama, n değişken
m = int(LP_Problem[0][0])
n = int(LP_Problem[0][1])
print("Kısıtlamalar m =", m, "\tDeğişkenler n =", n)
LP_Problem.pop(0)  # Bunları kolaylaştırmak için düşür.

# c = amaç fonksiyonu
c = LP_Problem[0]
c = np.append(c, [0] * m)
print("c = ", *c)
LP_Problem.pop(0)  # Amaç fonksiyonunu düşür.

LP_Problem = np.asarray(LP_Problem)  # LP problemini bir diziye dönüştür.
b = LP_Problem[:, -1]  # Son sütunu al.
print("b = ", *b)
A = np.delete(LP_Problem, -1, axis=1)  # Katsayı matrisini elde etmek için son sütunu sil.
A = np.concatenate((A, np.identity(m)), axis=1)  # Kimlik matrisi katsayı matrisine katılır.
print("A =\n", A)

N = []
BFS = []
for i in range(1, n + 1):
    N.append("x{}".format(i))
    BFS.append("x{}={}".format(i, float(0)))
B = []
for i in range(m):
    B.append("x{}".format(n + i + 1))
    BFS.append("x{}={}".format(n + i + 1, b[i]))
x = N + B
N_idx = list(range(1, n + 1))
B_idx = list(range(n + 1, n + m + 1))
N_idx_orijinal = np.copy(N_idx)
B_idx_original = np.copy(B_idx)
print("x = {", *x, "}")
print("N = {", *N, "}", "\tB = {", *B, "}")
print("\nBaşlangıç BFS:", *BFS[:n], "\n\t    ", *BFS[n:])
print(N)
print(B)

Basic_coef = np.identity(m)
Basic_coef_inv = np.linalg.inv(Basic_coef)
cb = np.array([[0]] * m)
cb_transpose = np.transpose(cb)
kapa = np.dot(cb_transpose, Basic_coef_inv)
M_inverse = np.identity(m + 1)
initial_resulting_matrix = np.dot(M_inverse, np.concatenate(([0], b), 0))

z = np.array([0] * len(c))
y = [0] * m
a = 1
E = []
xb = b
entering_var_candidates = [-1]

np.set_printoptions(precision=4, suppress=True)

while 1:

    print("#################################################################################")
    print("{}.döngü".format(a))
    print("y =", *y)
    I_m = np.identity(m)
    if a == 1:
        print("cbar\t", end=" ")
        for i in range(n):
            print("x{}:".format(N_idx[i]), c[i], "\t", end=" ")
        print()

    entering_var_candidates = []
    carpan = np.concatenate(([1], kapa[0]))

    for i in range(len(c)):
        zj_cj = np.transpose(np.concatenate(([[-c[i]]], [A[:, i]]), axis=1))
        entering_var_candidates.append(np.dot(carpan, zj_cj))
    entering_var_candidates = np.asarray(entering_var_candidates)

    if a > 1:
        print("cbar\t", end=" ")
        for i in range(n):
            print("x{}:{}".format(N_idx[i], -entering_var_candidates[N_idx[i] - 1]), "\t", end=" ")
        print()

    if all(i >= 0 for i in np.around(entering_var_candidates, decimals=4)):

        print()
        print("Optimal Çözüm\nDöngü sayısı:{}".format(a))
        print("Optimal değer", current_sol[0], "ulaşıldı.")
        
        # Optimal çözümün değerlerini ve değişkenlerini raporla
        print("Optimal Çözüm")
        print("Döngü sayısı:", a)
        print("Optimal Değer:", current_sol[0])

        # Değişkenlerin değerlerini raporla
        print("Değişkenler:")
        for i in range(len(N)):
            print("x{} = {:.2f}".format(N_idx[i], current_sol[i + 1]))

        # Sınırlayıcıların değerlerini raporla
        print("Sınırlayıcılar:")
        for i in range(len(B)):
            print("x{} = {:.2f}".format(B_idx[i], current_sol[i +1]))

        # Amaç fonksiyonunu raporla
        print("Amaç Fonksiyonu:")
        print("z =", current_sol[0], end=" ")
        for i in range(len(N_idx) - 1):
            print("({:.2f})x{}".format(-c[i], N_idx[i]), end=" + ")
        print("({:.2f})x{}".format(-c[-1], N_idx[-1]))

        break

    entering_var = min(entering_var_candidates)
    entering_var_idx = np.argmin(entering_var_candidates)
    p = entering_var_idx
    print("Giren değişken x{}".format(entering_var_idx + 1))

    t = np.dot(Basic_coef_inv, A[:, p])
    print("abarj ={}".format(t))

    # Sınırsız çözüm için:
    if all(i <= 0 for i in np.round(t, decimals=4)):
        print("Bu çözüm sınırsızdır. Döngü sayısı:{}".format(a))
        print("Orijinal:", end=" ")
        B_dict = {}
        original_variables = [0] * n
        slack_variables = [0] * m
        for i in range(len(B_idx)):
            B_dict[B_idx[i]] = np.float(bbar[i])

        for var in N_idx_orijinal:
            if var in B_dict:
                original_variables[var - 1] = (B_dict[var])

        for var in B_idx_original:
            if var in B_dict:
                slack_variables[var - B_idx_original[0]] = B_dict[var]
            # print(var, m, B_idx_original, B_dict, slack_variables)
        for i in range(n):
            print("x{} = {:.2f}".format((i + 1), original_variables[i]), end=" ")
        print()
        print("Slack:", end=" ")
        for i in range(m):
            print("x{} = {:.2f}".format((i + n + 1), slack_variables[i]), end=" ")
        print()

        print("z =", current_sol[0], end=" + ")
        for i in range(len(N_idx)-1):
            print("({:.2f})x{}".format(*-entering_var_candidates[N_idx[i]-1], N_idx[i]), end=" + ")
        print("({:.2f})x{}".format(*-entering_var_candidates[N_idx[-1]-1], N_idx[-1]))
        #print(M_inverse[1:, 1:])
        sol = M_inverse[1:, 1:]
        print()

        break

    positive_values = t[t > 0]

    idx_of_positive_values = np.array(np.where(t > 0)).reshape((-1, 1))

    ratio = xb[idx_of_positive_values]
    ratio = ratio / t[idx_of_positive_values]
    print("Oran", end=" ")
    for i in range(len(ratio)):
        print("x{}:".format(B_idx[idx_of_positive_values[i][0]]), "{:3.4f}\t".format(*ratio[i]), end="")
    print()

    leaving_var_idx = idx_of_positive_values[np.argmin(ratio)]

    leaving_var = (n + 1) + leaving_var_idx
    print("Ayrılan değişken x{}".format(*leaving_var))
    q = leaving_var_idx

    eta_vector = -t

    eta_vector[q] = 1
    print("E{} = sütun {}:{}".format(a, *leaving_var - n, t))
    eta_vector = eta_vector / t[q]

    I_m[:, q] = eta_vector.reshape((-1, 1))
    eta_matrix = I_m

    Basic_coef_inv = np.dot(eta_matrix, Basic_coef_inv)

    cb[q] = c[p]
    cb_transpose = np.transpose(cb)

    kapa = np.dot(cb_transpose, Basic_coef_inv)

    M_inverse = np.concatenate(([[1]], kapa), axis=1)
    dim = len(M_inverse[0]) - 1
    dim = np.array([[0]] * dim)
    expanded_B_inv = np.concatenate((dim, Basic_coef_inv), axis=1)
    M_inverse = np.concatenate((M_inverse, expanded_B_inv))

    current_sol = np.dot(M_inverse, np.concatenate(([0], b)))

    xb = np.dot(eta_matrix, xb)

    # Temel ve temel olmayan değişkenleri düzenle.
    N_copy = np.copy(N)
    B_copy = np.copy(B)
    N[int(p)] = B_copy[int(q)]
    B[int(q)] = N_copy[int(p)]
    print("N = {", *N, "}", "\tB = {", *B, "}")
    # cbar'ı hesaplamak için değişken indekslerini kullanmamız gerekir.
    N_idx_copy = np.copy(N_idx)
    B_idx_copy = np.copy(B_idx)
    N_idx[int(p)] = B_idx_copy[int(q)]
    B_idx[int(q)] = N_idx_copy[int(p)]

    bbar = current_sol[1:]
    print("bbar =", bbar)

    y = kapa
    a += 1
