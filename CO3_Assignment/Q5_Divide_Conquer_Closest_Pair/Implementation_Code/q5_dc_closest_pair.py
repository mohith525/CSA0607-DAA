"""Q5 - Divide-and-conquer closest pair vs brute force. Counts DISTANCE CALCULATIONS (squared distances)."""
import random, time, math, csv, os, itertools

def brute(pts):
    n = len(pts); best = float("inf"); calcs = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):
            dx = xi - pts[j][0]; dy = yi - pts[j][1]; d = dx * dx + dy * dy; calcs += 1
            if d < best: best = d
    return math.sqrt(best), calcs

def dc(pts):
    """Divide and conquer. Returns (distance, distance calcs, strip statistics)."""
    P = [(x, y, i) for i, (x, y) in enumerate(pts)]
    Px = sorted(P); Py = sorted(P, key=lambda p: p[1])
    st = {"calcs": 0, "strip_pts": 0, "strip_calls": 0, "max_nb": 0}
    def d2(p, q): st["calcs"] += 1; return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    def rec(Px, Py):
        n = len(Px)
        if n <= 3:                                           # base case: brute force on <= 3 points
            b = float("inf")
            for i in range(n - 1):
                for j in range(i + 1, n): b = min(b, d2(Px[i], Px[j]))
            return b
        mid = n // 2; midx = Px[mid][0]
        left_ids = {p[2] for p in Px[:mid]}
        Pyl = [p for p in Py if p[2] in left_ids]; Pyr = [p for p in Py if p[2] not in left_ids]
        d = min(rec(Px[:mid], Pyl), rec(Px[mid:], Pyr))      # best distance inside either half
        strip = [p for p in Py if (p[0] - midx) ** 2 < d]    # points closer than d to the dividing line, sorted by y
        st["strip_pts"] += len(strip); st["strip_calls"] += 1
        for i in range(len(strip)):
            j = i + 1; nb = 0
            while j < len(strip) and (strip[j][1] - strip[i][1]) ** 2 < d:     # only points within d in y
                d = min(d, d2(strip[i], strip[j])); j += 1; nb += 1
            st["max_nb"] = max(st["max_nb"], nb)
        return d
    r = rec(Px, Py)
    return math.sqrt(r), st["calcs"], st

def gen(kind, n, rnd):
    if kind == "uniform": return [(rnd.uniform(0, 10000), rnd.uniform(0, 10000)) for _ in range(n)]
    if kind == "clustered": return [(rnd.gauss(cx, 150), rnd.gauss(cy, 150)) for cx, cy in [(2000, 2000), (7000, 3000), (4000, 8000)] for _ in range(n // 3)] + [(rnd.gauss(5000, 150), rnd.gauss(5000, 150)) for _ in range(n - 3 * (n // 3))]
    if kind == "same_x": return [(5000.0, rnd.uniform(0, 10000)) for _ in range(n)]

def tmin(f, reps):
    b = 1e9
    for _ in range(reps):
        t = time.perf_counter(); f(); b = min(b, time.perf_counter() - t)
    return b

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(5)
    for _ in range(400):                                     # correctness incl. duplicates & collinear points
        p = [(rnd.randint(0, 40), rnd.randint(0, 40)) for _ in range(rnd.randint(2, 60))]
        ref = min(math.dist(a, b) for a, b in itertools.combinations(p, 2)); assert abs(dc(p)[0] - ref) < 1e-9
    print("Correctness: D&C == brute force on 400 random inputs (with duplicates and collinear points): PASSED\n")
    rows = []
    for kind in ("uniform", "clustered", "same_x"):
        print(f"--- {kind} ---")
        print(f"{'n':>7}{'BF calcs':>14}{'D&C calcs':>12}{'calc ratio':>11}{'BF time':>10}{'D&C time':>10}{'speed-up':>9}{'max strip nb':>13}")
        for n in (8, 16, 32, 64, 128, 256, 512, 1000, 2000, 3000):
            pts = gen(kind, n, rnd); reps = 7 if n <= 256 else 2
            tb = tmin(lambda: brute(pts), reps); td = tmin(lambda: dc(pts), reps)
            db, cb = brute(pts); dd, cd, st = dc(pts); assert abs(db - dd) < 1e-9
            rows.append([kind, n, cb, cd, round(tb, 6), round(td, 6), st["max_nb"], st["strip_pts"]])
            print(f"{n:>7}{cb:>14,}{cd:>12,}{cb / cd:>11.2f}{tb:>10.5f}{td:>10.5f}{tb / td:>9.2f}{st['max_nb']:>13}")
        print()
    print("--- D&C beyond the brute-force limit (uniform) ---")
    print(f"{'n':>8}{'D&C calcs':>12}{'calcs per point':>17}{'time (s)':>10}{'n(n-1)/2 for brute force':>27}")
    big = []
    for n in (10000, 50000, 100000):
        pts = gen("uniform", n, rnd); t = time.perf_counter(); d, c, st = dc(pts); t = time.perf_counter() - t
        big.append([n, c, round(t, 3)]); print(f"{n:>8,}{c:>12,}{c / n:>17.2f}{t:>10.3f}{n * (n - 1) // 2:>27,}")
    with open(os.path.join(here, "q5_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["dataset", "n", "bf_calcs", "dc_calcs", "bf_time_s", "dc_time_s", "max_strip_neighbours", "total_strip_points"]); w.writerows(rows)
        for r in big: w.writerow(["uniform_large", r[0], r[0] * (r[0] - 1) // 2, r[1], "", r[2], "", ""])
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rr = [r for r in rows if r[0] == "uniform"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].loglog([r[1] for r in rr], [r[2] for r in rr], "o--", label="Brute force n(n-1)/2"); ax[0].loglog([r[1] for r in rr], [r[3] for r in rr], "s-", label="Divide and conquer"); ax[0].legend(); ax[0].set_title("Distance calculations (uniform)"); ax[0].set_xlabel("n"); ax[0].grid(alpha=.3, which="both")
    ax[1].loglog([r[1] for r in rr], [r[4] for r in rr], "o--", label="Brute force"); ax[1].loglog([r[1] for r in rr], [r[5] for r in rr], "s-", label="Divide and conquer"); ax[1].legend(); ax[1].set_title("Execution time (s, uniform)"); ax[1].set_xlabel("n"); ax[1].grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q5_chart.png"), dpi=130)
