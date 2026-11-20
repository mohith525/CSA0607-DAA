"""Q2 - Merge Sort vs Quick Sort. Quick Sort pivot strategy: FIRST ELEMENT of the (sub)array, with a stable
list-based partition (left = elements < pivot, right = elements >= pivot). We record comparisons,
partition sizes and maximum recursion depth."""
import random, math, csv, os, sys
sys.setrecursionlimit(20000)

def merge_sort(a, st, depth=1):
    st["depth"] = max(st["depth"], depth)
    if len(a) <= 1: return a
    mid = len(a) // 2
    L = merge_sort(a[:mid], st, depth + 1); R = merge_sort(a[mid:], st, depth + 1)
    out = []; i = j = 0
    while i < len(L) and j < len(R):
        st["cmp"] += 1
        if L[i] <= R[j]: out.append(L[i]); i += 1
        else: out.append(R[j]); j += 1
    out += L[i:]; out += R[j:]
    return out

def quick_sort(a, st, pivot="first", rnd=None, depth=1, level=0):
    st["depth"] = max(st["depth"], depth)
    if len(a) <= 1: return a
    if pivot == "first": p = a[0]; rest = a[1:]
    elif pivot == "random":
        k = rnd.randrange(len(a)); p = a[k]; rest = a[:k] + a[k + 1:]
    elif pivot == "p10":                          # ORACLE pivot with rank at 10% (forces a 10:90 split)
        p = sorted(a)[len(a) // 10]; rest = list(a); rest.remove(p)
    left = []; right = []
    for x in rest:
        st["cmp"] += 1                            # one comparison of an element with the pivot
        (left if x < p else right).append(x)
    if level < 3: st["parts"].append((len(a), len(left), len(right)))
    return quick_sort(left, st, pivot, rnd, depth + 1, level + 1) + [p] + quick_sort(right, st, pivot, rnd, depth + 1, level + 1)

def balanced_input(s):
    """Permutation of sorted list s for which 'first element' pivots always split exactly in half."""
    if not s: return []
    m = len(s) // 2
    return [s[m]] + balanced_input(s[:m]) + balanced_input(s[m + 1:])

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__)); rnd = random.Random(8)
    sizes = [127, 255, 511, 1023, 2047]      # 2^k - 1 : perfect balance is possible
    rows = []
    print("PIVOT STRATEGY: first element.  Datasets: balanced (constructed), random, ascending, descending, all-equal")
    print(f"{'n':>6}{'dataset':>14}{'algorithm':>18}{'comparisons':>13}{'max depth':>10}{'root split (left,right)':>26}")
    for n in sizes:
        base = list(range(1, n + 1)); rp = base[:]; rnd.shuffle(rp)
        data = {"balanced": balanced_input(base), "random": rp, "ascending": base[:], "descending": base[::-1], "all-equal": [7] * n}
        for dn, a in data.items():
            runs = [("MergeSort", lambda x, st: merge_sort(x, st)), ("QuickSort(first)", lambda x, st: quick_sort(x, st, "first")),
                    ("QuickSort(random)", lambda x, st: quick_sort(x, st, "random", random.Random(1)))]
            for an, f in runs:
                st = {"cmp": 0, "depth": 0, "parts": []}; out = f(a, st); assert out == sorted(a)
                root = f"({st['parts'][0][1]},{st['parts'][0][2]})" if st["parts"] else "-"
                rows.append([n, dn, an, st["cmp"], st["depth"], root])
                if n in (127, 2047): print(f"{n:>6}{dn:>14}{an:>18}{st['cmp']:>13,}{st['depth']:>10}{root:>26}")
        if n in (127, 2047): print()
    # first three levels of partitions on the two contrasting inputs, n=127
    print("Partition sizes (subarray size, left, right) for the first levels, n = 127, first-element pivot")
    for dn, a in (("balanced", balanced_input(list(range(1, 128)))), ("ascending", list(range(1, 128)))):
        st = {"cmp": 0, "depth": 0, "parts": []}; quick_sort(a, st, "first"); print(f"  {dn:10}:", st["parts"][:7])
    print("\nTheory: balanced -> depth = log2(n+1) =", [int(math.log2(n + 1)) for n in sizes], "; ascending -> depth = n; comparisons n(n-1)/2 =", [n * (n - 1) // 2 for n in sizes])
    print("\n90:10 EXPERIMENT (oracle pivot at 10th percentile, random data):")
    print(f"{'n':>6}{'depth':>7}{'log_{10/9}(n)':>15}{'depth 50:50 = log2 n':>22}{'comparisons':>13}{'n*log2(n)':>11}")
    r910 = []
    for n in (127, 511, 2047):
        a = list(range(1, n + 1)); rnd.shuffle(a); st = {"cmp": 0, "depth": 0, "parts": []}; quick_sort(a, st, "p10")
        r910.append([n, st["depth"], st["cmp"]])
        print(f"{n:>6}{st['depth']:>7}{math.log(n) / math.log(10 / 9):>15.1f}{math.log2(n):>22.1f}{st['cmp']:>13,}{n * math.log2(n):>11,.0f}")
    with open(os.path.join(here, "q2_raw_data.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(["n", "dataset", "algorithm", "comparisons", "max_depth", "root_partition"]); w.writerows(rows)
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
    for dn, mk in (("balanced", "o-"), ("random", "s-"), ("ascending", "^-")):
        rr = [r for r in rows if r[1] == dn and r[2] == "QuickSort(first)"]
        ax[0].plot([r[0] for r in rr], [r[3] for r in rr], mk, label=f"Quick(first), {dn}")
    rr = [r for r in rows if r[1] == "random" and r[2] == "MergeSort"]; ax[0].plot([r[0] for r in rr], [r[3] for r in rr], "k--", label="Merge, random")
    ax[0].set_xscale("log"); ax[0].set_yscale("log"); ax[0].legend(fontsize=8); ax[0].set_title("Comparisons"); ax[0].set_xlabel("n"); ax[0].grid(alpha=.3, which="both")
    for dn, mk in (("balanced", "o-"), ("random", "s-"), ("ascending", "^-")):
        rr = [r for r in rows if r[1] == dn and r[2] == "QuickSort(first)"]
        ax[1].plot([r[0] for r in rr], [r[4] for r in rr], mk, label=f"Quick(first), {dn}")
    rr = [r for r in rows if r[1] == "random" and r[2] == "MergeSort"]; ax[1].plot([r[0] for r in rr], [r[4] for r in rr], "k--", label="Merge, any")
    ax[1].set_xscale("log"); ax[1].set_yscale("log"); ax[1].legend(fontsize=8); ax[1].set_title("Maximum recursion depth"); ax[1].set_xlabel("n"); ax[1].grid(alpha=.3, which="both")
    plt.tight_layout(); plt.savefig(os.path.join(here, "..", "Output_Screenshots", "q2_chart.png"), dpi=130)
