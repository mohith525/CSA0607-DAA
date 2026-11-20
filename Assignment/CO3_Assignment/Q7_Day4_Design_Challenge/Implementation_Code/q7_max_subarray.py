"""Q7 - Divide and conquer for MAXIMUM SUBARRAY SUM (largest sum of a non-empty contiguous block).
 Student A initial idea : split in half, answer = max(left, right, best block crossing the middle found by scanning outwards).
 Student B initial idea : split in half, each half returns (best, total) only.  -> shown below to be insufficient.
 Joint FINAL design     : each half returns the 4-tuple (best, best_prefix, best_suffix, total); combine in O(1).
 Baselines              : brute force O(n^2) and Kadane O(n) (oracle for testing).
 Counted: additions and comparisons between sums."""
import random, time, csv, os, math, sys
sys.setrecursionlimit(10000)

def brute(a):
    best = -math.inf; adds = cmps = 0
    for i in range(len(a)):
        s = 0
        for j in range(i, len(a)):
            s += a[j]; adds += 1; cmps += 1
            if s > best: best = s
    return best, adds, cmps

def kadane(a):
    best = cur = a[0]
    for x in a[1:]: cur = max(x, cur + x); best = max(best, cur)
    return best

def design_A(a, lo, hi, c):                                   # Student A's initial design
    if lo == hi: return a[lo]
    mid = (lo + hi) // 2
    bl = design_A(a, lo, mid, c); br = design_A(a, mid + 1, hi, c)
    s = 0; ls = -math.inf
    for i in range(mid, lo - 1, -1): s += a[i]; c["add"] += 1; c["cmp"] += 1; ls = max(ls, s)       # scan left of the middle
    s = 0; rs = -math.inf
    for j in range(mid + 1, hi + 1): s += a[j]; c["add"] += 1; c["cmp"] += 1; rs = max(rs, s)      # scan right of the middle
    c["add"] += 1; c["cmp"] += 2
    return max(bl, br, ls + rs)

def design_B_initial(a, lo, hi):                              # Student B's initial design: returns (best, total) only
    if lo == hi: return a[lo], a[lo]
    mid = (lo + hi) // 2
    bl, tl = design_B_initial(a, lo, mid); br, tr = design_B_initial(a, mid + 1, hi)
    return max(bl, br, tl + tr), tl + tr                      # crossing block assumed to be the two WHOLE halves -> wrong

def final(a, lo, hi, c):
    """Returns (best, prefix, suffix, total) for a[lo..hi]; all four describe NON-EMPTY blocks."""
    if lo == hi: return a[lo], a[lo], a[lo], a[lo]            # base case: one element
    mid = (lo + hi) // 2
    bl, pl, sl, tl = final(a, lo, mid, c); br, pr, sr, tr = final(a, mid + 1, hi, c)
    c["add"] += 4; c["cmp"] += 4                              # tl+tr ; tl+pr ; tr+sl ; sl+pr  | compare for prefix, suffix, best(x2)
    return (max(bl, br, sl + pr), max(pl, tl + pr), max(sr, tr + sl), tl + tr)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(77)
    print("STAGE-1 CHECK: is Student B's initial design (best, total) enough?")
    for _ in range(100000):
        a = [rnd.randint(-9, 9) for _ in range(rnd.randint(2, 6))]
        if design_B_initial(a, 0, len(a) - 1)[0] != brute(a)[0]:
            print(f"  counter-example: {a}  true answer {brute(a)[0]}, B-initial gives {design_B_initial(a, 0, len(a) - 1)[0]}  (needs best suffix of left half and best prefix of right half)"); break
    print("\nCORRECTNESS TESTS (final design versus brute force and Kadane)")
    cases = {"single element": [5], "single negative": [-3], "all negative": [-8, -3, -6, -2, -5, -4], "all positive": [1, 2, 3, 4], "all zero": [0, 0, 0],
             "alternating": [4, -5, 4, -5, 4], "classic (CLRS)": [13, -3, -25, 20, -3, -16, -23, 18, 20, -7, 12, -5, -22, 15, -4, 7],
             "crossing the middle": [-2, 1, -3, 4, -1, 2, 1, -5, 4], "max at both ends": [9, -20, 1, -20, 9]}
    for nm, a in cases.items():
        r = final(a, 0, len(a) - 1, {"add": 0, "cmp": 0})[0]; assert r == brute(a)[0] == kadane(a) == design_A(a, 0, len(a) - 1, {"add": 0, "cmp": 0})
        print(f"  {nm:22} n={len(a):>2}  answer = {r}")
    for _ in range(3000):
        a = [rnd.randint(-50, 50) for _ in range(rnd.randint(1, 80))]
        assert final(a, 0, len(a) - 1, {"add": 0, "cmp": 0})[0] == brute(a)[0] == kadane(a)
    print("  plus 3000 random arrays (sizes 1-80): all agree\n")
    print("OPERATION COUNTS (additions + comparisons).  A = scan-crossing design, FINAL = 4-tuple design")
    print(f"{'n':>8}{'brute n(n+1)/2 x2':>19}{'A: scan':>12}{'FINAL':>10}{'FINAL/n':>9}{'brute time':>12}{'A time':>9}{'FINAL time':>12}{'Kadane time':>13}")
    rows = []
    for n in (64, 256, 1024, 2048, 4096, 100000, 1000000):
        a = [rnd.randint(-100, 100) for _ in range(n)]
        cb = None; tb = ""
        if n <= 4096: t = time.perf_counter(); b, ad, cm = brute(a); tb = time.perf_counter() - t; cb = ad + cm
        cA = {"add": 0, "cmp": 0}; t = time.perf_counter(); rA = design_A(a, 0, n - 1, cA); tA = time.perf_counter() - t
        cF = {"add": 0, "cmp": 0}; t = time.perf_counter(); rF = final(a, 0, n - 1, cF)[0]; tF = time.perf_counter() - t
        t = time.perf_counter(); rK = kadane(a); tK = time.perf_counter() - t; assert rA == rF == rK
        opsA = cA["add"] + cA["cmp"]; opsF = cF["add"] + cF["cmp"]
        rows.append([n, cb if cb else "", opsA, opsF, round(tb, 5) if tb != "" else "", round(tA, 5), round(tF, 5), round(tK, 5)])
        print(f"{n:>8,}{(f'{cb:,}' if cb else '-'):>19}{opsA:>12,}{opsF:>10,}{opsF / n:>9.2f}{(f'{tb:.4f}' if tb != '' else '-'):>12}{tA:>9.4f}{tF:>12.4f}{tK:>13.4f}")
    print("\nTheory: A -> T(n)=2T(n/2)+Theta(n)=Theta(n log n);  FINAL -> T(n)=2T(n/2)+Theta(1)=Theta(n): ops = 8(n-1) here (4 adds + 4 compares per combine, n-1 combines).")
    with open(os.path.join(here, "q7_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "brute_ops", "designA_ops", "final_ops", "brute_time_s", "designA_time_s", "final_time_s", "kadane_time_s"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    rb = [r for r in rows if r[1] != ""]
    ax.loglog([r[0] for r in rb], [r[1] for r in rb], "o--", label="Brute force"); ax.loglog([r[0] for r in rows], [r[2] for r in rows], "s-", label="A: scan crossing (n log n)"); ax.loglog([r[0] for r in rows], [r[3] for r in rows], "^-", label="Final: 4-tuple (n)")
    ax.set_xlabel("n"); ax.set_ylabel("Additions + comparisons"); ax.legend(); ax.grid(alpha=.3, which="both"); ax.set_title("Maximum subarray: operation counts")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q7_chart.png"), dpi=130)
