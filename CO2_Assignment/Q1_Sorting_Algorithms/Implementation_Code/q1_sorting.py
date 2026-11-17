"""Q1 - Sorting under different data conditions (Selection, Bubble, Insertion).
Counts key comparisons and swaps/movements. Fixed seeds -> reproducible."""
import random, time, csv, os

def selection_sort(a):
    a = a[:]; comps = moves = 0; n = len(a)
    for i in range(n - 1):
        m = i
        for j in range(i + 1, n):
            comps += 1
            if a[j] < a[m]:
                m = j
        if m != i:
            a[i], a[m] = a[m], a[i]; moves += 1      # one swap
    return a, comps, moves

def bubble_sort(a):
    """Bubble sort with the usual early-exit flag (stop if a pass makes no swap)."""
    a = a[:]; comps = moves = 0; n = len(a)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            comps += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]; moves += 1; swapped = True
        if not swapped:
            break
    return a, comps, moves

def insertion_sort(a):
    a = a[:]; comps = moves = 0
    for i in range(1, len(a)):
        v = a[i]; j = i - 1
        while j >= 0:
            comps += 1
            if a[j] > v:
                a[j + 1] = a[j]; moves += 1; j -= 1   # one shift
            else:
                break
        a[j + 1] = v
    return a, comps, moves

ALGS = [("Selection", selection_sort), ("Bubble", bubble_sort), ("Insertion", insertion_sort)]

def datasets(n, seed=42):
    rnd = random.Random(seed)
    base = list(range(1, n + 1))
    rand = base[:]; rnd.shuffle(rand)
    # 95% already in order: ~5% of the orders are new arrivals appended at the END with random priority
    k = n // 20
    nearly = sorted(rnd.sample(base, n - k))
    nearly += [rnd.randint(1, n) for _ in range(k)]
    return {
        "A_Random": rand,
        "B_Nearly_Sorted_95pct": nearly,
        "C_Already_Sorted": base[:],
        "D_Reverse_Sorted (edge)": base[::-1],
        "E_Many_Duplicates (edge)": [rnd.randint(1, 5) for _ in range(n)],
    }

def run(n):
    rows = []
    for dname, data in datasets(n).items():
        for aname, f in ALGS:
            t = time.perf_counter(); out, c, m = f(data); t = time.perf_counter() - t
            assert out == sorted(data), (aname, dname)
            rows.append([n, dname, aname, c, m, round(t * 1000, 3)])
    return rows

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    allrows = []
    for n in (200, 1000):
        rows = run(n); allrows += rows
        print(f"\n===== n = {n} =====")
        print(f"{'Dataset':28}{'Algorithm':11}{'Comparisons':>13}{'Swaps/Moves':>13}{'Time(ms)':>11}")
        for r in rows:
            print(f"{r[1]:28}{r[2]:11}{r[3]:>13,}{r[4]:>13,}{r[5]:>11}")
    with open(os.path.join(here, "q1_raw_data.csv"), "w", newline="") as fh:
        w = csv.writer(fh); w.writerow(["n", "dataset", "algorithm", "comparisons", "swaps_or_moves", "time_ms"]); w.writerows(allrows)
    # chart
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    rows = [r for r in allrows if r[0] == 1000]
    ds = list(dict.fromkeys(r[1] for r in rows))
    fig, axs = plt.subplots(1, 2, figsize=(13, 4.8))
    for ax, idx, title in ((axs[0], 3, "Comparisons"), (axs[1], 4, "Swaps / Moves")):
        for k, (an, _) in enumerate(ALGS):
            vals = [next(r[idx] for r in rows if r[1] == d and r[2] == an) for d in ds]
            ax.bar([i + 0.27 * (k - 1) for i in range(len(ds))], vals, 0.27, label=an)
        ax.set_xticks(range(len(ds))); ax.set_xticklabels([d.split(" ")[0].replace("_", "\n", 1) for d in ds], fontsize=8)
        ax.set_yscale("log"); ax.set_title(f"{title} (n=1000, log scale)"); ax.legend(); ax.grid(axis="y", alpha=.3)
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q1_chart.png"), dpi=130)
