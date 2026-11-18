"""Q1 - Part A: Divide-and-conquer Max/Min (comparison counting). Part B: Binary Search (probe counting)."""
import random, math, csv, os, sys

# ---------------- Part A ----------------
def maxmin(a, lo, hi, c):
    """Returns (min, max) of a[lo..hi]. c[0] counts comparisons between ELEMENTS."""
    if lo == hi:                       # base case 1: one element, no comparison
        return a[lo], a[lo]
    if hi == lo + 1:                   # base case 2: two elements, ONE comparison decides both
        c[0] += 1
        return (a[lo], a[hi]) if a[lo] < a[hi] else (a[hi], a[lo])
    mid = (lo + hi) // 2
    mn1, mx1 = maxmin(a, lo, mid, c)
    mn2, mx2 = maxmin(a, mid + 1, hi, c)
    c[0] += 2                          # combine: compare the two minima, compare the two maxima
    return (mn1 if mn1 < mn2 else mn2), (mx1 if mx1 > mx2 else mx2)

def independent(a):
    """Straightforward: find max (n-1 comparisons) then min (n-1 comparisons)."""
    c = 0; mx = mn = a[0]
    for x in a[1:]:
        c += 1
        if x > mx: mx = x
    for x in a[1:]:
        c += 1
        if x < mn: mn = x
    return mn, mx, c

# ---------------- Part B ----------------
def binary_search(a, t):
    """Returns (index or -1, probes). One probe = one three-way comparison of t with a[mid]."""
    lo, hi, probes = 0, len(a) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2; probes += 1
        if a[mid] == t: return mid, probes
        if t < a[mid]: hi = mid - 1       # discard mid..hi
        else: lo = mid + 1                # discard lo..mid
    return -1, probes

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(3)
    print("PART A - MAX/MIN: D&C versus independent search")
    print(f"{'n':>7}{'dataset':>12}{'D&C obs':>9}{'3n/2-2':>9}{'ceil(3n/2)-2':>14}{'independent 2(n-1)':>20}{'saving':>8}")
    rowsA = []
    for n in (2, 4, 8, 16, 64, 256, 1024, 4096, 6, 10, 100, 1000, 3000):
        for name, a in (("random", [rnd.randint(0, 10**6) for _ in range(n)]), ("ascending", list(range(n))), ("descending", list(range(n, 0, -1)))):
            c = [0]; mn, mx = maxmin(a, 0, n - 1, c); mn2, mx2, ci = independent(a)
            assert (mn, mx) == (mn2, mx2) == (min(a), max(a))
            th = 3 * n / 2 - 2; th2 = math.ceil(3 * n / 2) - 2
            rowsA.append([n, name, c[0], th, th2, ci])
            if name == "random": print(f"{n:>7}{name:>12}{c[0]:>9}{th:>9.1f}{th2:>14}{ci:>20}{(1 - c[0] / ci) * 100:>7.1f}%")
    mism = []
    for n in range(2, 300):
        c = [0]; maxmin(list(range(n)), 0, n - 1, c)
        if c[0] != math.ceil(3 * n / 2) - 2: mism.append((n, c[0], math.ceil(3 * n / 2) - 2))
    print(f"\nCount is independent of data order (random/ascending/descending identical): {all(r[2] == next(q[2] for q in rowsA if q[0]==r[0]) for r in rowsA)}")
    print(f"Check n=2..299 against ceil(3n/2)-2: {len(mism)} mismatches", mism[:8])
    print("Power-of-two sizes match 3n/2-2 exactly; other sizes: see mismatches above.")

    print("\nPART B - BINARY SEARCH (probe = one comparison of target with a[mid])")
    print(f"{'n':>9}{'floor(log2 n)+1':>17}{'max succ':>10}{'avg succ':>10}{'max unsucc':>12}{'avg unsucc':>12}")
    rowsB = []
    for n in (7, 15, 100, 1000, 10**4, 10**5, 10**6, 2**20 - 1):
        a = [2 * i for i in range(n)]            # even numbers -> odd targets are guaranteed misses
        idx = list(range(n)) if n <= 2000 else rnd.sample(range(n), 2000)          # every element for small n, else 2000 random ones
        gaps = list(range(n + 1)) if n <= 2000 else rnd.sample(range(n + 1), 2000) # gap i = a value between a[i-1] and a[i] (incl. both ends)
        succ = [binary_search(a, a[i])[1] for i in idx]
        uns = [binary_search(a, 2 * i - 1)[1] for i in gaps]
        assert all(binary_search(a, a[i])[0] == i for i in idx)
        assert all(binary_search(a, 2 * i - 1)[0] == -1 for i in gaps)
        lg = math.floor(math.log2(n)) + 1
        rowsB.append([n, lg, max(succ), round(sum(succ) / len(succ), 2), max(uns), round(sum(uns) / len(uns), 2)])
        print(f"{n:>9,}{lg:>17}{max(succ):>10}{sum(succ) / len(succ):>10.2f}{max(uns):>12}{sum(uns) / len(uns):>12.2f}")
    print("Linear search would need up to n comparisons: n=1,000,000 -> 1,000,000 versus 20 probes.")
    with open(os.path.join(here, "q1_partA_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "dataset", "dc_comparisons", "theory_3n/2-2", "theory_ceil_3n/2-2", "independent"]); w.writerows(rowsA)
    with open(os.path.join(here, "q1_partB_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "floor_log2n_plus_1", "max_successful", "avg_successful", "max_unsuccessful", "avg_unsuccessful"]); w.writerows(rowsB)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    pw = [r for r in rowsA if r[1] == "random" and r[0] in (2, 4, 8, 16, 64, 256, 1024, 4096)]
    ax[0].plot([r[0] for r in pw], [r[5] for r in pw], "o--", label="Independent max & min: 2(n-1)"); ax[0].plot([r[0] for r in pw], [r[2] for r in pw], "s-", label="D&C: 3n/2 - 2")
    ax[0].set_xscale("log", base=2); ax[0].set_yscale("log"); ax[0].set_xlabel("n"); ax[0].set_ylabel("Comparisons"); ax[0].legend(); ax[0].grid(alpha=.3, which="both"); ax[0].set_title("Max/Min comparisons")
    ax[1].plot([r[0] for r in rowsB], [r[2] for r in rowsB], "o-", label="Max probes (successful)"); ax[1].plot([r[0] for r in rowsB], [r[3] for r in rowsB], "s-", label="Average (successful)")
    ax[1].plot([r[0] for r in rowsB], [r[1] for r in rowsB], "k--", label="floor(log2 n)+1"); ax[1].set_xscale("log"); ax[1].set_xlabel("n"); ax[1].set_ylabel("Probes"); ax[1].legend(); ax[1].grid(alpha=.3, which="both"); ax[1].set_title("Binary search probes")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q1_chart.png"), dpi=130)
