"""Q3 - Brute-force string matching; counts CHARACTER comparisons. Finds all matches."""
import random, csv, os

def brute_force(text, pat):
    n, m = len(text), len(pat); comps = 0; matches = []
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comps += 1
            if text[i + j] != pat[j]:
                break
            j += 1
        if j == m:
            matches.append(i)
    return matches, comps

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(11)
    n, m = 10000, 50
    tests = []
    # Test 1 (BEST): first pattern char never occurs in the text -> 1 comparison per alignment
    tests.append(("T1 Best-case", "A" * n, "B" + "A" * (m - 1), n - m + 1,
                  "pattern[0] never matches -> exactly 1 comparison at each of n-m+1 alignments"))
    # Test 2 (WORST): long almost-matching prefix at every alignment
    tests.append(("T2 Worst-case", "A" * n, "A" * (m - 1) + "B", m * (n - m + 1),
                  "m-1 chars match then last fails at every alignment -> m comparisons x (n-m+1)"))
    # Test 3 (own): realistic log text over a 26-letter alphabet, random pattern
    alpha = "abcdefghijklmnopqrstuvwxyz"
    log = "".join(rnd.choice(alpha) for _ in range(n)); pat3 = log[7000:7000 + m]
    tests.append(("T3 Random log text", log, pat3, None,
                  "random text, large alphabet -> mismatch almost at once: approx (n-m+1)*alpha/(alpha-1) = ~1.04 per alignment"))
    # Test 4 (own, extra): small alphabet (binary, like bit-patterns) random text
    bits = "".join(rnd.choice("01") for _ in range(n)); pat4 = bits[5000:5000 + m]
    tests.append(("T4 Random binary text", bits, pat4, None,
                  "alphabet of 2 -> expected ~2 comparisons per alignment"))
    rows = []
    print(f"n (text) = {n}, m (pattern) = {m}, alignments = {n - m + 1}")
    print(f"{'Test':24}{'Predicted':>12}{'Observed':>12}{'Matches':>9}{'Comps/alignment':>17}")
    for name, t, p, pred, why in tests:
        mt, c = brute_force(t, p)
        a = len(alpha) if name.startswith("T3") else 2
        if pred is None:
            pred = round((n - m + 1) * (a / (a - 1)))        # expected comps for random text (approx.)
        print(f"{name:24}{pred:>12,}{c:>12,}{len(mt):>9}{c / (n - m + 1):>17.3f}")
        rows.append([name, n, m, pred, c, len(mt), why])
    # growth with m on the worst case
    print("\nWorst-case growth with pattern length m (text n=10000):")
    grow = []
    for mm in (5, 10, 25, 50, 100, 200):
        _, c = brute_force("A" * n, "A" * (mm - 1) + "B"); grow.append([mm, c])
        print(f"  m={mm:4}  comparisons={c:>10,}   m*(n-m+1)={mm * (n - mm + 1):>10,}")
    # correctness
    assert brute_force("abracadabra", "abra")[0] == [0, 7]
    print("\nSanity test: 'abra' in 'abracadabra' ->", brute_force("abracadabra", "abra")[0])
    with open(os.path.join(here, "q3_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["test", "n", "m", "predicted_comps", "observed_comps", "matches", "reason"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.bar([r[0] for r in rows], [r[4] for r in rows], color=["#4c9", "#e55", "#59d", "#da4"])
    ax.set_yscale("log"); ax.set_ylabel("Character comparisons (log)"); ax.set_title("Same text length, very different work")
    plt.xticks(fontsize=8); plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q3_chart.png"), dpi=130)
