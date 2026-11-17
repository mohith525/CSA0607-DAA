"""Q2 - Sequential search on tool-issue records. Counts record comparisons."""
import random, csv, os, math

def make_records(n, rnd):
    ids = rnd.sample(range(1, 10 * n + 1), n)
    return [(f"T-{i}", f"TECH-{rnd.randint(1, 50)}", f"{rnd.randint(6,22)}:{rnd.randint(0,59):02d}", f"Bay-{rnd.randint(1,8)}") for i in ids]

def seq_search(records, tool_id):
    comps = 0
    for idx, rec in enumerate(records):
        comps += 1
        if rec[0] == tool_id:
            return idx, comps
    return -1, comps

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(7)
    sizes = [50, 200, 1000, 5000, 20000]
    rows = []
    print("EXPERIMENT 1: comparisons by search position / outcome")
    print(f"{'n':>7}{'first':>8}{'middle':>8}{'last':>8}{'avg(successful,500 rand)':>26}{'unsuccessful':>14}")
    for n in sizes:
        recs = make_records(n, rnd)
        first = seq_search(recs, recs[0][0])[1]
        mid = seq_search(recs, recs[n // 2][0])[1]
        last = seq_search(recs, recs[-1][0])[1]
        avg = sum(seq_search(recs, recs[rnd.randrange(n)][0])[1] for _ in range(500)) / 500
        miss = seq_search(recs, "T-NOT-ISSUED")[1]
        print(f"{n:>7}{first:>8}{mid:>8}{last:>8}{avg:>26.1f}{miss:>14}")
        rows.append([n, first, mid, last, round(avg, 1), miss, (n + 1) / 2])
    with open(os.path.join(here, "q2_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["n", "first", "middle", "last", "avg_successful_measured", "unsuccessful", "theory_avg_(n+1)/2"]); w.writerows(rows)

    print("\nEXPERIMENT 2: daily workload, sequential search vs. hash index on Tool ID")
    print("Assumes: one hangar ~ 300 active records, 200 lookups/day; 20 facilities pooled: 6,000 records, 4,000 lookups/day (ASSUMED figures)")
    print("Also a 'busy' scenario: pooled live system, 6,000 records, 50 lookups/second")
    scen = [("One hangar", 300, 200 / (8 * 3600)), ("20 hangars, separate lists", 300, 20 * 200 / (8 * 3600)),
            ("20 hangars pooled (central)", 6000, 20 * 200 / (8 * 3600)), ("Pooled, busy (50 look-ups/s)", 6000, 50)]
    print(f"{'Scenario':34}{'records':>9}{'lookups/s':>11}{'avg comps/lookup':>18}{'comps/second':>14}")
    for name, n, rate in scen:
        avgc = (n + 1) / 2
        print(f"{name:34}{n:>9}{rate:>11.3f}{avgc:>18.1f}{avgc * rate:>14.1f}")
    print("Hash index: ~1 comparison per lookup regardless of n (plus O(1) update on issue/return).")

    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot([r[0] for r in rows], [r[3] for r in rows], "o-", label="Worst: last position / unsuccessful (n)")
    ax.plot([r[0] for r in rows], [r[4] for r in rows], "s-", label="Average successful (measured)")
    ax.plot([r[0] for r in rows], [r[1] for r in rows], "^-", label="Best: first position (1)")
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlabel("List size n"); ax.set_ylabel("Comparisons")
    ax.set_title("Sequential search growth"); ax.legend(); ax.grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q2_chart.png"), dpi=130)
