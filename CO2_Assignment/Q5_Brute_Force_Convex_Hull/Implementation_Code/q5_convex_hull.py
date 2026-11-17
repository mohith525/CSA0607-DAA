"""Q5 - Brute-force convex hull derived from: 'segment PiPj is a hull edge if all other points
lie on one side of the line through Pi and Pj'."""
import random, math, csv, os, time

def side(p, q, r):
    """Sign of a*x + b*y - c for line through p,q evaluated at r:
       a = qy-py, b = px-qx, c = px*qy - py*qx.  >0 one side, <0 other, 0 on the line."""
    a = q[1] - p[1]; b = p[0] - q[0]; c = p[0] * q[1] - p[1] * q[0]
    return a * r[0] + b * r[1] - c

def hull_bf(points):
    pts = sorted(set(points))              # remove duplicate stations
    n = len(pts); ops = 0; edges = []
    if n < 3:
        return pts, edges, ops
    for i in range(n - 1):
        for j in range(i + 1, n):
            pos = neg = False; ok = True
            for k in range(n):
                if k == i or k == j:
                    continue
                s = side(pts[i], pts[j], pts[k]); ops += 1
                if s > 0: pos = True
                elif s < 0: neg = True
                else:                       # collinear with the line: must lie INSIDE segment ij
                    p, q, r = pts[i], pts[j], pts[k]
                    if not (min(p[0], q[0]) <= r[0] <= max(p[0], q[0]) and min(p[1], q[1]) <= r[1] <= max(p[1], q[1])):
                        ok = False; break   # r is beyond the segment, so ij is only part of a longer edge
                if pos and neg:
                    ok = False; break       # points on both sides -> not a boundary edge (early exit)
            if ok:
                edges.append((pts[i], pts[j]))
    verts = sorted({v for e in edges for v in e})
    if len(verts) > 2:                      # order boundary counter-clockwise around centroid
        cx = sum(v[0] for v in verts) / len(verts); cy = sum(v[1] for v in verts) / len(verts)
        verts.sort(key=lambda v: math.atan2(v[1] - cy, v[0] - cx))
    return verts, edges, ops

def plot(points, hull, edges, title, fname):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    ax.scatter(*zip(*points), c="tab:blue", s=30, label="Monitoring stations", zorder=3)
    ax.scatter(*zip(*hull), c="tab:red", s=70, marker="D", label="Hull vertices", zorder=4)
    for a, b in edges:
        ax.plot([a[0], b[0]], [a[1], b[1]], "r-", lw=2, zorder=2)
    ax.set_title(title, fontsize=10); ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.07), ncol=2); ax.grid(alpha=.3); ax.set_aspect("equal")
    plt.tight_layout(); plt.savefig(fname, dpi=130); plt.close()

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(5)
    # Test 1: boundary + interior
    corners = [(0, 0), (12, 1), (14, 9), (7, 14), (-1, 10)]
    interior = [(rnd.randint(2, 11), rnd.randint(3, 10)) for _ in range(15)]
    t1 = corners + interior
    h, e, ops = hull_bf(t1)
    print("TEST 1 (boundary + interior points)"); print("  points:", len(set(t1)), " hull vertices (CCW):", h)
    print("  accepted edges:", len(e), " side-tests performed:", ops)
    assert set(h) == set(corners) or all(c in h for c in corners)
    plot(t1, h, e, "Test 1: boundary + interior points", os.path.join(here, "..", "Output_Screenshots", "q5_test1.png"))
    # Test 2: designed to challenge: collinear boundary points, duplicates, point exactly on an edge
    t2 = [(0, 0), (4, 0), (8, 0), (8, 4), (8, 8), (4, 8), (0, 8), (0, 4), (4, 4), (4, 4), (2, 2), (6, 6), (8, 0), (4, 8)]
    h2, e2, ops2 = hull_bf(t2)
    print("\nTEST 2 (collinear boundary points, duplicates, interior points)")
    print("  points given:", len(t2), "(distinct:", len(set(t2)), ")  hull vertices (CCW):", h2)
    print("  accepted edges:", len(e2), " side-tests performed:", ops2)
    assert set(h2) == {(0, 0), (8, 0), (8, 8), (0, 8)}
    plot(t2, h2, e2, "Test 2: collinear points on edges + duplicates", os.path.join(here, "..", "Output_Screenshots", "q5_test2.png"))
    # extra edge cases
    print("\nEXTRA edge cases")
    print("  all points collinear :", hull_bf([(0, 0), (1, 1), (2, 2), (5, 5), (3, 3)])[0])
    print("  fewer than 3 points  :", hull_bf([(1, 1), (2, 2)])[0])
    print("  triangle + inner pt  :", hull_bf([(0, 0), (6, 0), (3, 6), (3, 2)])[0])
    # brute force vs. monotone-chain reference on random sets
    def reference(points):
        P = sorted(set(points))
        if len(P) < 3: return P
        cr = lambda o, a, b: (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
        lo = []
        for p in P:
            while len(lo) >= 2 and cr(lo[-2], lo[-1], p) <= 0: lo.pop()
            lo.append(p)
        up = []
        for p in reversed(P):
            while len(up) >= 2 and cr(up[-2], up[-1], p) <= 0: up.pop()
            up.append(p)
        return lo[:-1] + up[:-1]
    for _ in range(200):
        pts = [(rnd.randint(0, 20), rnd.randint(0, 20)) for _ in range(rnd.randint(3, 25))]
        assert set(hull_bf(pts)[0]) == set(reference(pts)), pts
    print("  200 random sets cross-checked against an independent reference: ALL MATCH")
    # growth
    print("\nGROWTH: side-tests as n grows (random points in a 1000x1000 square)")
    print(f"{'n':>6}{'pairs':>10}{'worst-case tests n(n-1)(n-2)/2':>34}{'tests performed':>17}{'time (s)':>10}{'hull size':>11}")
    rows = []
    for n in (10, 20, 40, 80, 160, 320):
        pts = [(rnd.randint(0, 1000), rnd.randint(0, 1000)) for _ in range(n)]
        t = time.perf_counter(); hh, ee, oo = hull_bf(pts); t = time.perf_counter() - t
        wc = n * (n - 1) * (n - 2) // 2
        rows.append([n, n * (n - 1) // 2, wc, oo, round(t, 4), len(hh)])
        print(f"{n:>6}{n*(n-1)//2:>10,}{wc:>34,}{oo:>17,}{t:>10.4f}{len(hh):>11}")
    # Adversarial growth: all points on a circle -> every point is a hull vertex (little early-exit help)
    print("\nGROWTH, adversarial (all points on a circle: every point is a hull vertex)")
    print(f"{'n':>6}{'worst-case tests':>18}{'tests performed':>17}{'time (s)':>10}{'hull size':>11}")
    rows2 = []
    for n in (10, 20, 40, 80, 160):
        pts = list({(round(1000 * math.cos(2 * math.pi * k / n)), round(1000 * math.sin(2 * math.pi * k / n))) for k in range(n)})
        t = time.perf_counter(); hh, ee, oo = hull_bf(pts); t = time.perf_counter() - t
        wc = len(pts) * (len(pts) - 1) * (len(pts) - 2) // 2
        rows2.append([len(pts), wc, oo, round(t, 4), len(hh)])
        print(f"{len(pts):>6}{wc:>18,}{oo:>17,}{t:>10.4f}{len(hh):>11}")
    with open(os.path.join(here, "q5_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["case", "n", "worst_case_tests", "tests_performed", "time_s", "hull_size"])
        for r in rows: w.writerow(["random", r[0], r[2], r[3], r[4], r[5]])
        for r in rows2: w.writerow(["circle", r[0], r[1], r[2], r[3], r[4]])
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot([r[0] for r in rows], [r[2] for r in rows], "o--", label="Worst-case bound n(n-1)(n-2)/2")
    ax.plot([r[0] for r in rows], [r[3] for r in rows], "s-", label="Random points (measured)")
    ax.plot([r[0] for r in rows2], [r[2] for r in rows2], "^-", label="Points on circle (measured)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("n"); ax.set_ylabel("Side tests"); ax.legend(); ax.grid(alpha=.3, which="both")
    ax.set_title("Convex hull brute force: growth of work"); plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q5_growth.png"), dpi=130)
