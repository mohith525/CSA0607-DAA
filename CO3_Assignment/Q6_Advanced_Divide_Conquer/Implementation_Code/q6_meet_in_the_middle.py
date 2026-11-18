"""Q6 (Student B) - Meet-in-the-Middle for Subset-Sum: does some subset of w[0..n-1] sum exactly to T?
Naive: enumerate all 2^n subsets (Gray code, O(1) per subset, O(n) memory).
MITM : split into two halves, list all 2^(n/2) subset sums of each half, sort, then search for a pair summing to T."""
import random, time, csv, os, math, tracemalloc

def naive(w, T):
    n = len(w); s = 0; visited = 1; g = 0
    if T == 0: return True, 1
    for i in range(1, 1 << n):
        b = (i & -i).bit_length() - 1; g ^= 1 << b          # Gray code: flip exactly one item
        s += w[b] if g >> b & 1 else -w[b]; visited += 1
        if s == T: return True, visited
    return False, visited

def subset_sums(h):
    sums = [0]
    for x in h: sums += [s + x for s in sums]               # doubles the list for every item
    return sums

def mitm(w, T):
    h = len(w) // 2
    L = sorted(subset_sums(w[:h])); R = sorted(subset_sums(w[h:]))
    gen = len(L) + len(R)
    i, j, steps = 0, len(R) - 1, 0                          # two-pointer search: L ascending, R descending
    while i < len(L) and j >= 0:
        steps += 1; s = L[i] + R[j]
        if s == T: return True, gen, steps, len(L) + len(R)
        if s < T: i += 1
        else: j -= 1
    return False, gen, steps, len(L) + len(R)

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(12)
    for _ in range(500):                                    # correctness on small random instances (reachable and unreachable targets)
        n = rnd.randint(2, 14); w = [rnd.randint(1, 60) for _ in range(n)]
        T = sum(w[i] for i in range(n) if rnd.random() < .5) if rnd.random() < .5 else rnd.randint(1, sum(w) + 5)
        brute = any(sum(w[i] for i in range(n) if m >> i & 1) == T for m in range(1 << n))
        assert naive(w, T)[0] == mitm(w, T)[0] == brute
    print("Correctness: naive == Meet-in-the-Middle == brute force on 500 random instances\n")
    print("WORST CASE (target unreachable, so the whole search space must be examined). Weights are even; target is odd.")
    print(f"{'n':>4}{'naive 2^n':>16}{'naive time(s)':>15}{'MITM sums generated 2*2^(n/2)':>31}{'MITM search steps':>19}{'MITM time(s)':>14}{'stored sums':>13}{'speed-up':>10}")
    rows = []
    for n in (16, 20, 22, 24, 28, 32, 36, 40):
        w = [2 * rnd.randint(1, 10 ** 6) for _ in range(n)]; T = (sum(w) // 2) | 1       # odd -> unreachable
        tn = None
        if n <= 24:
            t = time.perf_counter(); ok, vis = naive(w, T); tn = time.perf_counter() - t; assert not ok
        t = time.perf_counter(); ok, gen, steps, stored = mitm(w, T); tm = time.perf_counter() - t; assert not ok
        rows.append([n, 2 ** n, round(tn, 4) if tn else "", gen, steps, round(tm, 4), stored])
        print(f"{n:>4}{2 ** n:>17,}{(f'{tn:.3f}' if tn else '(too slow)'):>15}{gen:>31,}{steps:>19,}{tm:>14.3f}{stored:>13,}{(f'{tn / tm:.1f}x' if tn else ''):>10}")
    print("\nMEMORY (peak Python allocation measured with tracemalloc)")
    mem = []
    for n in (20, 24, 28, 32):
        w = [2 * rnd.randint(1, 10 ** 6) for _ in range(n)]; T = (sum(w) // 2) | 1
        tracemalloc.start(); mitm(w, T); cur, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
        mem.append([n, round(peak / 1e6, 1)]); print(f"  n={n}: stored sums = {2 * 2 ** (n // 2):>9,}   peak memory = {peak / 1e6:8.1f} MB   (naive Gray-code enumeration needs O(n) memory)")
    print(f"\nExtrapolation: n=60 -> naive 2^60 = {2 ** 60:.2e} subsets; MITM 2*2^30 = {2 * 2 ** 30:,} sums (~{2 * 2 ** 30 * 8 / 1e9:.0f} GB at 8 bytes each) -> memory, not time, becomes the limit")
    with open(os.path.join(here, "q6_mitm_raw_data.csv"), "w", newline="") as f:
        w_ = csv.writer(f); w_.writerow(["n", "naive_subsets", "naive_time_s", "mitm_sums_generated", "mitm_search_steps", "mitm_time_s", "stored_sums"]); w_.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    ax[0].semilogy([r[0] for r in rows], [r[1] for r in rows], "o--", label="Naive 2^n subsets"); ax[0].semilogy([r[0] for r in rows], [r[3] for r in rows], "s-", label="MITM 2*2^(n/2) sums"); ax[0].legend(); ax[0].set_title("Work (log scale)"); ax[0].set_xlabel("n"); ax[0].grid(alpha=.3, which="both")
    ax[1].plot([r[0] for r in mem], [r[1] for r in mem], "o-r"); ax[1].set_title("MITM peak memory (MB)"); ax[1].set_xlabel("n"); ax[1].grid(alpha=.3)
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q6_mitm_chart.png"), dpi=130)
