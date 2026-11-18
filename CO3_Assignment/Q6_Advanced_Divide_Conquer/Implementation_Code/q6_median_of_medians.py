"""Q6 (Student A) - Median of Medians vs QuickSelect for the k-th smallest element. Counted: comparisons between elements.
Groups of 5, pivot = median of the group medians (found recursively), 3-way partition."""
import random, math, csv, os, sys
sys.setrecursionlimit(10000)

def insertion_sort_count(g, c):
    g = g[:]
    for i in range(1, len(g)):
        v = g[i]; j = i - 1
        while j >= 0:
            c[0] += 1
            if g[j] > v: g[j + 1] = g[j]; j -= 1
            else: break
        g[j + 1] = v
    return g

def partition3(a, p, c):
    lo, eq, hi = [], [], []
    for x in a:
        c[0] += 1                                   # one comparison of an element with the pivot
        if x < p: lo.append(x)
        elif x == p: eq.append(x)
        else: hi.append(x)
    return lo, eq, hi

def mom_select(a, k, c, log=None):
    """k is 0-based. Worst-case O(n)."""
    if len(a) <= 5: return insertion_sort_count(a, c)[k]
    medians = [insertion_sort_count(a[i:i + 5], c)[len(a[i:i + 5]) // 2] for i in range(0, len(a), 5)]
    pivot = mom_select(medians, len(medians) // 2, c, None)          # median of the medians
    lo, eq, hi = partition3(a, pivot, c)
    if log is not None: log.append((len(a), max(len(lo), len(hi)) / len(a)))   # largest part that could remain
    if k < len(lo): return mom_select(lo, k, c, log)
    if k < len(lo) + len(eq): return pivot
    return mom_select(hi, k - len(lo) - len(eq), c, log)

def quickselect(a, k, c, mode, rnd=None, log=None):
    while True:
        if len(a) == 1: return a[0]
        p = a[0] if mode == "first" else a[rnd.randrange(len(a))]
        lo, eq, hi = partition3(a, p, c)
        if log is not None: log.append(max(len(lo), len(hi)) / len(a))
        if k < len(lo): a = lo
        elif k < len(lo) + len(eq): return p
        else: k -= len(lo) + len(eq); a = hi

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(6)
    for _ in range(300):
        n = rnd.randint(1, 120); a = [rnd.randint(0, 40) for _ in range(n)]; k = rnd.randrange(n)
        assert mom_select(a, k, [0]) == sorted(a)[k] == quickselect(a, k, [0], "first") == quickselect(a, k, [0], "random", rnd)
    print("Correctness: Median of Medians and QuickSelect agree with sorted(a)[k] on 300 random inputs (with duplicates)\n")
    print("COMPARISONS to find the MEDIAN (k = n/2).  Datasets: random permutation, ascending (adversarial for first-element pivot)")
    print(f"{'n':>7}{'dataset':>11}{'MoM':>11}{'MoM/n':>7}{'QS first':>12}{'QS first/n':>11}{'QS random (mean of 50)':>24}{'QS random max':>15}")
    rows = []
    for n in (1000, 2000, 4000, 8000):
        base = list(range(n)); rp = base[:]; rnd.shuffle(rp)
        for dn, a in (("random", rp), ("ascending", base)):
            cm = [0]; mom_select(a, n // 2, cm); cf = [0]; quickselect(a, n // 2, cf, "first")
            cr = []
            for t in range(50):
                c = [0]; quickselect(a, n // 2, c, "random", random.Random(t)); cr.append(c[0])
            rows.append([n, dn, cm[0], cf[0], round(sum(cr) / 50), max(cr)])
            print(f"{n:>7}{dn:>11}{cm[0]:>11,}{cm[0] / n:>7.2f}{cf[0]:>12,}{cf[0] / n:>11.2f}{sum(cr) / 50:>24,.0f}{max(cr):>15,}")
    print("\nPIVOT QUALITY: largest fraction of the array left for the recursive call (n = 8000, median search)")
    a = list(range(8000)); rnd.shuffle(a); lg = []; mom_select(a, 4000, [0], lg)
    big = [f for s, f in lg if s >= 100]
    print(f"  Median of Medians: worst fraction over calls with size>=100 = {max(big):.3f}   (guarantee: <= 7/10 + small)")
    lg2 = []; quickselect(list(range(8000)), 4000, [0], "first", None, lg2); print(f"  QuickSelect, first-element pivot on ascending data: fraction at the first 5 levels = {[round(x, 4) for x in lg2[:5]]}")
    worst_r = []
    for t in range(300):
        lg3 = []; quickselect(a, 4000, [0], "random", random.Random(1000 + t), lg3); worst_r.append(max(lg3))
    print(f"  QuickSelect, random pivot over 300 runs: worst single partition fraction seen = {max(worst_r):.4f}  (poor partitions still occur, just rarely)")
    print("\nMoM comparison growth (random data, median):")
    big_rows = []
    for n in (10000, 50000, 100000, 200000):
        a = list(range(n)); rnd.shuffle(a); c = [0]; mom_select(a, n // 2, c); big_rows.append([n, c[0]]); print(f"  n={n:>7,}  comparisons={c[0]:>10,}  comparisons/n={c[0] / n:.2f}")
    with open(os.path.join(here, "q6_mom_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "dataset", "mom", "quickselect_first", "quickselect_random_mean50", "quickselect_random_max50"]); w.writerows(rows)
        for r in big_rows: w.writerow([r[0], "random_large", r[1], "", "", ""])
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    asc = [r for r in rows if r[1] == "ascending"]; rn = [r for r in rows if r[1] == "random"]
    ax.loglog([r[0] for r in asc], [r[3] for r in asc], "^-", label="QuickSelect first pivot, ascending data"); ax.loglog([r[0] for r in rn], [r[3] for r in rn], "s-", label="QuickSelect first pivot, random data")
    ax.loglog([r[0] for r in asc], [r[2] for r in asc], "o-", label="Median of Medians"); ax.loglog([r[0] for r in rn], [r[4] for r in rn], "d--", label="QuickSelect random pivot (mean)")
    ax.set_xlabel("n"); ax.set_ylabel("Comparisons"); ax.legend(fontsize=8); ax.grid(alpha=.3, which="both"); ax.set_title("Selection of the median")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q6_mom_chart.png"), dpi=130)
