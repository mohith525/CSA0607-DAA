"""Q4 - Brute-force closest pair of drones. Examines each UNIQUE pair (i<j) once."""
import random, time, math, csv, os

def closest_pair_bf(pts):
    n = len(pts); best = float("inf"); bp = None; pairs = dists = 0
    for i in range(n - 1):
        xi, yi = pts[i]
        for j in range(i + 1, n):          # j>i avoids (j,i) duplicates and (i,i)
            pairs += 1
            dx = xi - pts[j][0]; dy = yi - pts[j][1]
            d = dx * dx + dy * dy; dists += 1   # squared distance: no sqrt needed to compare
            if d < best:
                best = d; bp = (i, j)
    return math.sqrt(best), bp, pairs, dists

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(2026)
    print("Derivation: unique pairs = C(n,2) = n(n-1)/2")
    # tiny correctness check against itertools
    import itertools
    p = [(rnd.random() * 100, rnd.random() * 100) for _ in range(60)]
    ref = min(math.dist(a, b) for a, b in itertools.combinations(p, 2))
    assert abs(closest_pair_bf(p)[0] - ref) < 1e-9
    print("Correctness check vs itertools.combinations: PASSED\n")
    sizes = [10, 100, 500, 1000, 2000, 3000]
    rows = []
    print(f"{'n':>6}{'n(n-1)/2':>12}{'pairs examined':>16}{'dist calcs':>12}{'time (s)':>10}{'time/pair (ns)':>16}")
    for n in sizes:
        pts = [(rnd.uniform(0, 10000), rnd.uniform(0, 10000)) for _ in range(n)]
        t = time.perf_counter(); d, bp, pr, ds = closest_pair_bf(pts); t = time.perf_counter() - t
        assert pr == n * (n - 1) // 2
        rows.append([n, n * (n - 1) // 2, pr, ds, round(t, 4), round(d, 3)])
        print(f"{n:>6}{n*(n-1)//2:>12,}{pr:>16,}{ds:>12,}{t:>10.4f}{t / pr * 1e9:>16.1f}")
    # growth ratios
    print("\nGrowth check (doubling n should ~quadruple the work):")
    for a, b in zip(rows[1:], rows[2:]):
        print(f"  n {a[0]:>5} -> {b[0]:>5}: pairs x{b[2] / a[2]:.2f} (theory x{(b[0] * (b[0]-1)) / (a[0] * (a[0]-1)):.2f}),  time x{b[4] / a[4]:.2f}")
    # acceptability criterion
    k = sum(r[4] for r in rows[3:]) / sum(r[2] for r in rows[3:])    # seconds per pair (from larger runs)
    print(f"\nFitted cost per pair (n>=1000) = {k * 1e9:.1f} ns")
    for T in (0.1, 1.0, 10.0):
        # solve n(n-1)/2 * k = T
        n_max = (1 + math.sqrt(1 + 8 * T / k)) / 2
        print(f"Acceptable response time {T:>5.1f} s  ->  largest n approx {int(n_max):,}")
    with open(os.path.join(here, "q4_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["n", "theory_pairs", "pairs_examined", "distance_calcs", "time_s", "min_distance"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.5))
    axs[0].plot([r[0] for r in rows], [r[2] for r in rows], "o-"); axs[0].set_title("Pairs examined = n(n-1)/2"); axs[0].set_xlabel("n"); axs[0].grid(alpha=.3)
    axs[1].plot([r[0] for r in rows], [r[4] for r in rows], "s-r"); axs[1].axhline(1.0, ls="--", c="k", label="1 s acceptable limit")
    axs[1].set_title("Execution time (s)"); axs[1].set_xlabel("n"); axs[1].legend(); axs[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q4_chart.png"), dpi=130)
