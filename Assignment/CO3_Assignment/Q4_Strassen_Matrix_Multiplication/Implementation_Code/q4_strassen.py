"""Q4 - Conventional vs Strassen matrix multiplication.
Part 1: pure-Python lists with exact operation counters (multiplications, additions/subtractions) and timings.
Part 2: NumPy (BLAS base case) timing, to see what happens with a highly tuned conventional kernel and cache effects."""
import random, time, csv, os, math
import numpy as np

# ---------------- pure Python ----------------
def conv(A, B, c):
    n = len(A); Bt = list(zip(*B))
    c["mul"] += n ** 3; c["add"] += n * n * (n - 1)
    return [[sum(a * b for a, b in zip(row, col)) for col in Bt] for row in A]

def madd(X, Y, c): c["add"] += len(X) ** 2; return [[a + b for a, b in zip(r, s)] for r, s in zip(X, Y)]
def msub(X, Y, c): c["add"] += len(X) ** 2; return [[a - b for a, b in zip(r, s)] for r, s in zip(X, Y)]

def strassen(A, B, c, cut=1):
    n = len(A)
    if n <= cut: return conv(A, B, c)
    h = n // 2
    q = lambda M, r, k: [row[k * h:(k + 1) * h] for row in M[r * h:(r + 1) * h]]
    A11, A12, A21, A22 = q(A, 0, 0), q(A, 0, 1), q(A, 1, 0), q(A, 1, 1)
    B11, B12, B21, B22 = q(B, 0, 0), q(B, 0, 1), q(B, 1, 0), q(B, 1, 1)
    M1 = strassen(madd(A11, A22, c), madd(B11, B22, c), c, cut)
    M2 = strassen(madd(A21, A22, c), B11, c, cut)
    M3 = strassen(A11, msub(B12, B22, c), c, cut)
    M4 = strassen(A22, msub(B21, B11, c), c, cut)
    M5 = strassen(madd(A11, A12, c), B22, c, cut)
    M6 = strassen(msub(A21, A11, c), madd(B11, B12, c), c, cut)
    M7 = strassen(msub(A12, A22, c), madd(B21, B22, c), c, cut)
    C11 = madd(msub(madd(M1, M4, c), M5, c), M7, c); C12 = madd(M3, M5, c)
    C21 = madd(M2, M4, c); C22 = madd(msub(madd(M1, M3, c), M2, c), M6, c)
    return [r1 + r2 for r1, r2 in zip(C11, C12)] + [r1 + r2 for r1, r2 in zip(C21, C22)]

def pad(M, m): n = len(M); return [row + [0] * (m - n) for row in M] + [[0] * m for _ in range(m - n)]
def strassen_any(A, B, c, cut):
    n = len(A); m = 1
    while m < n: m *= 2
    P = strassen(pad(A, m), pad(B, m), c, cut) if m != n else strassen(A, B, c, cut)
    return [row[:n] for row in P[:n]], m

def rmat(n, rnd): return [[rnd.randint(-9, 9) for _ in range(n)] for _ in range(n)]
def best(f, reps):
    b = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); b = min(b, time.perf_counter() - t)
    return b

# ---------------- NumPy ----------------
def np_strassen(A, B, cut):
    n = A.shape[0]
    if n <= cut: return A @ B
    h = n // 2
    A11, A12, A21, A22 = A[:h, :h], A[:h, h:], A[h:, :h], A[h:, h:]
    B11, B12, B21, B22 = B[:h, :h], B[:h, h:], B[h:, :h], B[h:, h:]
    M1 = np_strassen(A11 + A22, B11 + B22, cut); M2 = np_strassen(A21 + A22, B11, cut)
    M3 = np_strassen(A11, B12 - B22, cut); M4 = np_strassen(A22, B21 - B11, cut)
    M5 = np_strassen(A11 + A12, B22, cut); M6 = np_strassen(A21 - A11, B11 + B12, cut); M7 = np_strassen(A12 - A22, B21 + B22, cut)
    C = np.empty_like(A)
    C[:h, :h] = M1 + M4 - M5 + M7; C[:h, h:] = M3 + M5; C[h:, :h] = M2 + M4; C[h:, h:] = M1 - M2 + M3 + M6
    return C

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(4)
    for n in (1, 2, 4, 8, 16):                         # correctness
        A, B = rmat(n, rnd), rmat(n, rnd); assert strassen(A, B, {"mul": 0, "add": 0}, 1) == conv(A, B, {"mul": 0, "add": 0})
    for n in (3, 5, 10, 17, 33):                       # non power of two via padding
        A, B = rmat(n, rnd), rmat(n, rnd); assert strassen_any(A, B, {"mul": 0, "add": 0}, 1)[0] == conv(A, B, {"mul": 0, "add": 0})
    print("Correctness: Strassen == conventional for n = 1..16 (powers of 2) and for n = 3, 5, 10, 17, 33 (padded)\n")
    print("OPERATION COUNTS (cut-off 1: recurse down to 1x1)")
    print(f"{'n':>6}{'conv mults n^3':>16}{'Strassen mults 7^k':>20}{'conv adds':>14}{'Strassen adds':>15}{'mult ratio':>12}{'adds ratio':>12}")
    cnt = []
    for k in range(1, 9):
        n = 2 ** k; c1 = {"mul": n ** 3, "add": n * n * (n - 1)}
        # exact Strassen counts by recurrence: M(n)=7M(n/2), A(n)=7A(n/2)+18(n/2)^2
        M, Ad = 1, 0
        for j in range(k): Ad = 7 * Ad + 18 * (2 ** j) ** 2; M = 7 * M
        cnt.append([n, c1["mul"], M, c1["add"], Ad]); print(f"{n:>6}{c1['mul']:>16,}{M:>20,}{c1['add']:>14,}{Ad:>15,}{c1['mul'] / M:>12.2f}{c1['add'] / Ad:>12.2f}")
    A, B = rmat(16, rnd), rmat(16, rnd); cc = {"mul": 0, "add": 0}; strassen(A, B, cc, 1)
    assert cc["mul"] == 7 ** 4 and cc["add"] == cnt[3][4]; print("  (recurrence values verified by instrumented run at n=16)")
    print("\nTIMING, pure Python lists (seconds, best of repeats); Strassen with cut-off 16 and 32")
    print(f"{'n':>6}{'conventional':>14}{'Strassen cut=16':>17}{'Strassen cut=32':>17}{'total ops conv':>16}{'total ops S(16)':>17}")
    tim = []
    for n in (16, 32, 64, 128, 256):
        A, B = rmat(n, rnd), rmat(n, rnd); reps = 3 if n <= 128 else 1
        tc = best(lambda: conv(A, B, {"mul": 0, "add": 0}), reps)
        t16 = best(lambda: strassen(A, B, {"mul": 0, "add": 0}, 16), reps); t32 = best(lambda: strassen(A, B, {"mul": 0, "add": 0}, 32), reps)
        c1 = {"mul": 0, "add": 0}; conv(A, B, c1); c2 = {"mul": 0, "add": 0}; strassen(A, B, c2, 16)
        tim.append([n, tc, t16, t32, c1["mul"] + c1["add"], c2["mul"] + c2["add"]])
        print(f"{n:>6}{tc:>14.4f}{t16:>17.4f}{t32:>17.4f}{c1['mul'] + c1['add']:>16,}{c2['mul'] + c2['add']:>17,}")
    print("\nCUT-OFF SWEEP at n = 128 (pure Python): conventional = cut-off 128")
    sweep = []
    A, B = rmat(128, rnd), rmat(128, rnd)
    for cut in (2, 4, 8, 16, 32, 64, 128):
        c = {"mul": 0, "add": 0}; t = best(lambda: strassen(A, B, {"mul": 0, "add": 0}, cut), 2); strassen(A, B, c, cut)
        sweep.append([cut, c["mul"], c["add"], t]); print(f"  cut-off {cut:>4}: mults {c['mul']:>10,}  adds {c['add']:>10,}  time {t:.4f} s")
    print("\nPADDING COST (non power-of-two sizes, cut-off 16)")
    print(f"{'n':>6}{'padded to':>11}{'conv mults':>13}{'Strassen mults':>16}{'extra vs conv':>15}")
    padrows = []
    for n in (64, 65, 100, 128, 129, 200):
        A, B = rmat(n, rnd), rmat(n, rnd); c = {"mul": 0, "add": 0}; _, m = strassen_any(A, B, c, 16)
        padrows.append([n, m, n ** 3, c["mul"]]); print(f"{n:>6}{m:>11}{n ** 3:>13,}{c['mul']:>16,}{(c['mul'] / n ** 3 - 1) * 100:>14.0f}%")
    print("\nNUMPY (BLAS conventional kernel; Strassen recursion stops at cut-off), float64, seconds")
    print(f"{'n':>6}{'np @':>10}{'Strassen c=256':>16}{'Strassen c=512':>16}{'max |error| (c=256)':>21}")
    npr = []; rg = np.random.default_rng(1)
    for n in (256, 512, 1024, 2048):
        A = rg.standard_normal((n, n)); B = rg.standard_normal((n, n)); reps = 3
        t0 = best(lambda: A @ B, reps); t1 = best(lambda: np_strassen(A, B, 256), reps); t2 = best(lambda: np_strassen(A, B, 512), reps)
        err = float(np.abs(np_strassen(A, B, 256) - A @ B).max())
        npr.append([n, t0, t1, t2, err]); print(f"{n:>6}{t0:>10.4f}{t1:>16.4f}{t2:>16.4f}{err:>21.2e}")
    for fn, hdr, rows in (("q4_counts_raw_data.csv", ["n", "conv_mults", "strassen_mults", "conv_adds", "strassen_adds"], cnt), ("q4_python_timing_raw_data.csv", ["n", "conv_s", "strassen_c16_s", "strassen_c32_s", "conv_total_ops", "strassen_c16_total_ops"], tim),
                          ("q4_cutoff_sweep_raw_data.csv", ["cutoff", "mults", "adds", "time_s"], sweep), ("q4_padding_raw_data.csv", ["n", "padded", "conv_mults", "strassen_mults"], padrows), ("q4_numpy_timing_raw_data.csv", ["n", "numpy_s", "strassen_c256_s", "strassen_c512_s", "max_abs_error"], npr)):
        with open(os.path.join(here, fn), "w", newline="") as f: w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    ax[0].loglog([r[0] for r in cnt], [r[1] for r in cnt], "o--", label="Conventional n^3"); ax[0].loglog([r[0] for r in cnt], [r[2] for r in cnt], "s-", label="Strassen 7^k"); ax[0].legend(); ax[0].set_title("Multiplications"); ax[0].set_xlabel("n"); ax[0].grid(alpha=.3, which="both")
    ax[1].loglog([r[0] for r in tim], [r[1] for r in tim], "o--", label="Conventional"); ax[1].loglog([r[0] for r in tim], [r[2] for r in tim], "s-", label="Strassen cut=16"); ax[1].loglog([r[0] for r in tim], [r[3] for r in tim], "^-", label="Strassen cut=32"); ax[1].legend(); ax[1].set_title("Pure Python time (s)"); ax[1].set_xlabel("n"); ax[1].grid(alpha=.3, which="both")
    ax[2].loglog([r[0] for r in npr], [r[1] for r in npr], "o--", label="NumPy @ (BLAS)"); ax[2].loglog([r[0] for r in npr], [r[2] for r in npr], "s-", label="Strassen cut=256"); ax[2].loglog([r[0] for r in npr], [r[3] for r in npr], "^-", label="Strassen cut=512"); ax[2].legend(); ax[2].set_title("NumPy time (s)"); ax[2].set_xlabel("n"); ax[2].grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q4_chart.png"), dpi=125)
