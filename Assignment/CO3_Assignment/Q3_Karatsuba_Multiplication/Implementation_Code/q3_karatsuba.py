"""Q3 - Standard (school-book) vs Karatsuba multiplication of n-digit integers.
Numbers are little-endian digit lists. Both algorithms work on digit lists in pure Python so the timings are comparable.
Karatsuba works on the coefficient lists (polynomial view) and carries are normalised once at the end.
Counted operation: single-digit multiplications."""
import random, time, csv, os

def school(a, b, c):
    n = len(a); res = [0] * (2 * n - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            res[i + j] += ai * bj
    c[0] += n * n
    return res

def add(x, y): return [p + q for p, q in zip(x, y)]
def sub(x, y): return [p - q for p, q in zip(x, y)]

def karatsuba(a, b, c, T=1):
    """a, b : coefficient lists of equal length n (power of two).  T : recursion cut-off (use school-book if n <= T)."""
    n = len(a)
    if n <= T: return school(a, b, c)
    m = n // 2
    a0, a1, b0, b1 = a[:m], a[m:], b[:m], b[m:]
    z0 = karatsuba(a0, b0, c, T)                              # low  x low
    z2 = karatsuba(a1, b1, c, T)                              # high x high
    z1 = karatsuba(add(a0, a1), add(b0, b1), c, T)            # (a0+a1)(b0+b1)
    mid = sub(sub(z1, z0), z2)                                # a0*b1 + a1*b0 : the 3rd multiplication replaces 2
    res = [0] * (2 * n - 1)
    for i, v in enumerate(z0): res[i] += v
    for i, v in enumerate(mid): res[i + m] += v
    for i, v in enumerate(z2): res[i + 2 * m] += v
    return res

def to_digits(x, n): return [int(d) for d in str(x).zfill(n)[::-1]]
def from_coeffs(cs):
    carry = 0; out = []
    for v in cs:
        v += carry; out.append(v % 10); carry = v // 10
    while carry: out.append(carry % 10); carry //= 10
    return int("".join(map(str, out[::-1])))

def best_time(f, reps):
    best = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); best = min(best, time.perf_counter() - t)
    return best

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(31)
    for _ in range(200):                                   # correctness
        n = rnd.choice([1, 2, 4, 8, 16, 32]); x = rnd.randrange(10 ** n); y = rnd.randrange(10 ** n)
        c = [0]; assert from_coeffs(karatsuba(to_digits(x, n), to_digits(y, n), c)) == x * y
    print("Correctness: 200 random products agree with Python's built-in multiplication\n")
    print("MULTIPLICATION COUNTS (single-digit multiplications)")
    print(f"{'n digits':>9}{'school n^2':>12}{'Karatsuba (T=1)':>17}{'3^log2(n)':>11}{'ratio school/Kar':>18}")
    cnt = []
    for k in range(1, 12):
        n = 2 ** k; a = [rnd.randint(0, 9) for _ in range(n)]; b = [rnd.randint(0, 9) for _ in range(n)]
        c1 = [0]; school(a, b, c1)
        c2 = [0]
        if n <= 2048: karatsuba(a, b, c2, 1)
        cnt.append([n, c1[0], c2[0], 3 ** k]); print(f"{n:>9}{c1[0]:>12,}{c2[0]:>17,}{3 ** k:>11,}{c1[0] / c2[0]:>18.2f}")
    print("\nTIMING (pure Python, best of repeated runs, seconds)")
    T_list = (1, 8, 16, 32)
    hdr = f"{'n':>6}{'school':>10}" + "".join(f"{'Kar T=' + str(t):>11}" for t in T_list) + f"{'T=1 faster?':>13}"
    print(hdr); times = []
    for k in range(2, 12):
        n = 2 ** k; reps = 5 if n <= 256 else (3 if n <= 1024 else 2)
        a = [rnd.randint(0, 9) for _ in range(n)]; b = [rnd.randint(0, 9) for _ in range(n)]
        ts = best_time(lambda: school(a, b, [0]), reps)
        tk = [best_time(lambda t=t: karatsuba(a, b, [0], t), reps) for t in T_list]
        times.append([n, ts] + tk)
        print(f"{n:>6}{ts:>10.5f}" + "".join(f"{x:>11.5f}" for x in tk) + f"{'YES' if tk[0] < ts else 'no':>13}")
    cross = next((r[0] for r in times if r[2] < r[1]), None)
    print(f"\nFirst tested size where pure Karatsuba (T=1) beats school-book: n = {cross} digits")
    print("Best cut-off per size (min over T):", {r[0]: T_list[min(range(4), key=lambda i: r[2 + i])] for r in times})
    with open(os.path.join(here, "q3_counts_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "school_mults", "karatsuba_mults", "3_pow_log2n"]); w.writerows(cnt)
    with open(os.path.join(here, "q3_timing_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "school_s"] + [f"karatsuba_T{t}_s" for t in T_list]); w.writerows(times)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].loglog([r[0] for r in cnt], [r[1] for r in cnt], "o--", label="School-book n^2"); ax[0].loglog([r[0] for r in cnt], [r[2] for r in cnt], "s-", label="Karatsuba 3^log2 n"); ax[0].legend(); ax[0].set_title("Single-digit multiplications"); ax[0].set_xlabel("n digits"); ax[0].grid(alpha=.3, which="both")
    ax[1].loglog([r[0] for r in times], [r[1] for r in times], "o--", label="School-book")
    for i, t in enumerate(T_list): ax[1].loglog([r[0] for r in times], [r[2 + i] for r in times], "s-", label=f"Karatsuba cut-off {t}")
    ax[1].legend(); ax[1].set_title("Execution time (s)"); ax[1].set_xlabel("n digits"); ax[1].grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q3_chart.png"), dpi=130)
