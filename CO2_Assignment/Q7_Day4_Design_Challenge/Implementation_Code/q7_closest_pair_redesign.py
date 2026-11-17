"""Q7 - Redesign of the Q4 brute-force closest pair.
Idea (derived from the Q4 diagnosis): most examined pairs are FAR apart and can never beat the best distance
found so far. Sort once by x. For point i, scan only following points while their x-gap is still smaller than
the current best distance; as soon as x-gap >= best, no later point can be closer, so STOP that inner loop."""
import random, time, math, csv, os, itertools

def brute(pts):
    n = len(pts); best = float("inf"); dists = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            dx = pts[i][0] - pts[j][0]; dy = pts[i][1] - pts[j][1]
            d = dx * dx + dy * dy; dists += 1
            if d < best: best = d
    return math.sqrt(best), dists

def sweep(pts, adaptive=False):
    """Redesigned strategy. adaptive=True first chooses the axis with the larger spread (O(n) extra)."""
    axis = 0
    if adaptive:
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        axis = 0 if (max(xs) - min(xs)) >= (max(ys) - min(ys)) else 1
    P = sorted(pts, key=lambda p: p[axis]); n = len(P)
    best = float("inf"); dists = 0; gap_checks = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            gap = P[j][axis] - P[i][axis]; gap_checks += 1
            if gap * gap >= best:              # no later point can be closer -> prune the rest of this scan
                break
            dx = P[i][0] - P[j][0]; dy = P[i][1] - P[j][1]
            d = dx * dx + dy * dy; dists += 1
            if d < best: best = d
    return math.sqrt(best), dists, gap_checks

def gen(kind, n, rnd):
    if kind == "uniform":   return [(rnd.uniform(0, 10000), rnd.uniform(0, 10000)) for _ in range(n)]
    if kind == "clustered": return [(rnd.gauss(cx, 150), rnd.gauss(cy, 150)) for cx, cy in [(2000, 2000), (7000, 3000), (4000, 8000)] for _ in range(n // 3)] + \
                                   [(rnd.gauss(5000, 150), rnd.gauss(5000, 150)) for _ in range(n - 3 * (n // 3))]
    if kind == "same_x":    return [(5000.0, rnd.uniform(0, 10000)) for _ in range(n)]   # worst case for x-sweep

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(2026)
    # correctness: redesign must equal brute force on many inputs
    for _ in range(300):
        p = [(rnd.randint(0, 50), rnd.randint(0, 50)) for _ in range(rnd.randint(2, 40))]
        ref = min(math.dist(a, b) for a, b in itertools.combinations(p, 2))
        assert abs(sweep(p)[0] - ref) < 1e-9 and abs(sweep(p, True)[0] - ref) < 1e-9 and abs(brute(p)[0] - ref) < 1e-9
    print("Correctness: redesign == brute force on 300 random inputs (incl. duplicates): PASSED\n")
    rows = []
    for kind in ("uniform", "clustered", "same_x"):
        print(f"--- Input type: {kind} ---")
        print(f"{'n':>7}{'BF dist calcs':>15}{'Sweep dist calcs':>18}{'reduction':>11}{'BF time(s)':>12}{'Sweep time(s)':>15}{'speed-up':>10}")
        for n in (100, 500, 1000, 2000, 3000):
            pts = gen(kind, n, rnd)
            t = time.perf_counter(); d1, c1 = brute(pts); tb = time.perf_counter() - t
            t = time.perf_counter(); d2, c2, g2 = sweep(pts); ts = time.perf_counter() - t
            assert abs(d1 - d2) < 1e-9
            print(f"{n:>7}{c1:>15,}{c2:>18,}{c1 / max(c2, 1):>10.1f}x{tb:>12.4f}{ts:>15.4f}{tb / ts:>9.1f}x")
            rows.append([kind, n, c1, c2, g2, round(tb, 5), round(ts, 5)])
        print()
    print("--- Scaling the redesign beyond the brute-force limit (uniform) ---")
    print(f"{'n':>8}{'dist calcs':>14}{'gap checks':>13}{'time (s)':>10}{'(n^2/2 would be)':>20}")
    for n in (10000, 50000, 100000, 200000):
        pts = gen("uniform", n, rnd)
        t = time.perf_counter(); d, c, g = sweep(pts); t = time.perf_counter() - t
        print(f"{n:>8,}{c:>14,}{g:>13,}{t:>10.3f}{n * (n - 1) // 2:>20,}")
        rows.append(["uniform_large", n, n * (n - 1) // 2, c, g, None, round(t, 5)])
    print("\n--- Degenerate case: all drones on one vertical line (x identical) ---")
    pts = gen("same_x", 2000, rnd)
    _, c1, _ = sweep(pts, False); _, c2, g2 = sweep(pts, True)
    print(f"x-sweep (fixed axis): {c1:,} distance calcs (= n(n-1)/2 = {2000 * 1999 // 2:,}) -> no pruning at all")
    print(f"adaptive-axis sweep : {c2:,} distance calcs -> pruning restored (extra O(n) spread check)")
    with open(os.path.join(here, "q7_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["input", "n", "bf_distance_calcs", "sweep_distance_calcs", "sweep_gap_checks", "bf_time_s", "sweep_time_s"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    for kind, mk in (("uniform", "o-"), ("clustered", "s-"), ("same_x", "^-")):
        rr = [r for r in rows if r[0] == kind]
        axs[0].plot([r[1] for r in rr], [r[3] for r in rr], mk, label=f"Sweep ({kind})")
    rr = [r for r in rows if r[0] == "uniform"]
    axs[0].plot([r[1] for r in rr], [r[2] for r in rr], "k--", label="Brute force n(n-1)/2")
    axs[0].set_yscale("log"); axs[0].set_xlabel("n"); axs[0].set_ylabel("Distance calculations"); axs[0].legend(fontsize=8); axs[0].grid(alpha=.3, which="both"); axs[0].set_title("Distance calculations: original vs redesign")
    rl = [r for r in rows if r[0] == "uniform_large"]
    axs[1].plot([r[1] for r in rl], [r[6] for r in rl], "s-r"); axs[1].set_xlabel("n"); axs[1].set_ylabel("Time (s)"); axs[1].set_title("Redesign at large n (uniform)"); axs[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q7_chart.png"), dpi=130)
