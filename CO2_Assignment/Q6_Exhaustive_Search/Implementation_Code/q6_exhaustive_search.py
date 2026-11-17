"""Q6 - Exhaustive search for the humanitarian airlift (0/1 selection under a payload limit).
A candidate solution is a bitmask: bit j = 1 means package j is loaded. Total candidates = 2^n."""
import random, time, math, csv, os, itertools

def exhaustive(items, cap):
    """items = [(id, weight, value)]. Returns best_value, best_mask, candidates, feasible, item_inspections."""
    n = len(items); best_v = -1; best_m = 0; feasible = 0; insp = 0
    for mask in range(1 << n):                 # GENERATE every subset
        w = v = 0
        for j in range(n):                     # EVALUATE: add up weight and value
            insp += 1
            if mask >> j & 1:
                w += items[j][1]; v += items[j][2]
        if w <= cap:                           # FEASIBILITY check
            feasible += 1
            if v > best_v:                     # RETAIN best
                best_v = v; best_m = mask
    return best_v, best_m, 1 << n, feasible, insp

def decode(mask, items):
    return [items[j][0] for j in range(len(items)) if mask >> j & 1]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    # ---------- correctness instance ----------
    small = [("P1", 5, 10), ("P2", 4, 40), ("P3", 6, 30), ("P4", 3, 50), ("P5", 2, 15)]; CAP = 10
    print("CORRECTNESS INSTANCE  (payload limit = 10)")
    for it in small: print("  ", it)
    print(f"\n{'mask':>6} {'subset':18}{'weight':>7}{'value':>7}  feasible")
    for m in range(1 << 5):
        s = decode(m, small); w = sum(small[j][1] for j in range(5) if m >> j & 1); v = sum(small[j][2] for j in range(5) if m >> j & 1)
        print(f"{m:>6b} {str(s):18}{w:>7}{v:>7}  {'YES' if w <= CAP else 'no'}")
    bv, bm, c, f, _ = exhaustive(small, CAP)
    # independent verification using itertools (different enumeration method)
    ind = max((sum(i[2] for i in comb), comb) for r in range(6) for comb in itertools.combinations(small, r) if sum(i[1] for i in comb) <= CAP)
    print(f"\nAlgorithm result : best value {bv} with {decode(bm, small)}  ({c} candidates, {f} feasible)")
    print(f"Independent check: best value {ind[0]} with {[i[0] for i in ind[1]]}")
    assert bv == ind[0] == 105
    # ---------- growth ----------
    rnd = random.Random(99)
    print("\nGROWTH INVESTIGATION  (weights 1-20, values 1-100, payload = 40% of total weight)")
    print(f"{'n':>4}{'2^n (predicted)':>17}{'candidates':>13}{'feasible':>10}{'item inspections':>18}{'time (s)':>10}{'time ratio':>12}")
    rows = []; prev = None
    for n in (10, 12, 14, 16, 18, 20):
        items = [(f"P{i+1}", rnd.randint(1, 20), rnd.randint(1, 100)) for i in range(n)]
        cap = int(0.4 * sum(i[1] for i in items))
        t = time.perf_counter(); bv, bm, c, f, insp = exhaustive(items, cap); t = time.perf_counter() - t
        assert c == 2 ** n
        ratio = "" if prev is None else f"x{t / prev:.1f}"
        print(f"{n:>4}{2**n:>17,}{c:>13,}{f:>10,}{insp:>18,}{t:>10.3f}{ratio:>12}")
        rows.append([n, 2 ** n, c, f, insp, round(t, 4), bv]); prev = t
    # boundary: time ~ k * n * 2^n
    k = sum(r[5] for r in rows[-2:]) / sum(r[0] * 2 ** r[0] for r in rows[-2:])
    print(f"\nFitted model: time = {k * 1e9:.1f} ns x n x 2^n")
    for T in (1, 10, 60):
        nmax = max(m for m in range(5, 60) if k * m * 2 ** m <= T)
        print(f"Response-time budget {T:>3} s -> largest n approx {nmax}")
    print("Predicted time for n=22: %.1f s,  n=25: %.0f s,  n=30: %.1f hours,  n=40: %.1f years" % (
        k * 22 * 2 ** 22, k * 25 * 2 ** 25, k * 30 * 2 ** 30 / 3600, k * 40 * 2 ** 40 / 3.15e7))
    with open(os.path.join(here, "q6_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["n", "2^n", "candidates", "feasible", "item_inspections", "time_s", "best_value"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    axs[0].semilogy([r[0] for r in rows], [r[2] for r in rows], "o-"); axs[0].set_title("Candidate subsets = 2^n (log scale)"); axs[0].set_xlabel("n"); axs[0].grid(alpha=.3, which="both")
    axs[1].semilogy([r[0] for r in rows], [r[5] for r in rows], "s-r"); axs[1].axhline(1.0, ls="--", c="k", label="1 s budget"); axs[1].set_title("Execution time (s, log scale)"); axs[1].set_xlabel("n"); axs[1].legend(); axs[1].grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q6_chart.png"), dpi=130)
