# Q7 – Joint design record (Stages 2, 3 and 6)

## Stage 2 – Comparison of the two initial designs
| Aspect | Student A | Student B |
|---|---|---|
| Decomposition | halves at the middle | halves at the middle (**agree**) |
| Base case | one element | one element (**agree**) |
| Information returned | best sum only | (best, total) |
| Combine | max(left, right, crossing found by scanning outwards from the middle) | max(left, right, total_left + total_right) |
| Strength | handles the crossing case correctly | combine is O(1) – idea of *returning extra information* to avoid rescanning |
| Weakness | rescans elements at every level: Θ(n log n) | crossing case wrong (counter-example [-2,-5,8,7,-9,-1]) |

**Agreement:** halves, one-element base case, three cases for the best block (left, right, crossing).
**Missing information:** B's design lacks the best suffix of the left half and best prefix of the right half; A's design recomputes exactly those two quantities by scanning.
**Ideas retained:** from A – the three-case analysis and the meaning of the crossing block (best suffix of left + best prefix of right); from B – return extra information from each subproblem so that the combine step is constant time.

## Stage 3 – Joint final design
- **Decomposition:** halves at the middle.
- **Subproblems:** the left half and the right half (same problem, half size).
- **Base case:** one element a: (best, prefix, suffix, total) = (a, a, a, a).
- **Information returned:** best, best prefix, best suffix, total.
- **Combine:** best = max(bl, br, sl + pr); prefix = max(pl, tl + pr); suffix = max(sr, tr + sl); total = tl + tr.
- **Algorithm:** see `../Pseudocode/q7_pseudocode.txt`; code in `../Implementation_Code/q7_max_subarray.py`.

## Stage 6 – Joint evaluation
- **Why D&C suits the problem:** the answer for a segment is determined by the answers for its two halves plus a small amount of extra information (prefix, suffix, total); subproblems are independent and of the same form.
- **Work reduced:** brute force examines all n(n+1)/2 blocks; the decomposition shares work – every block is represented implicitly by combining a few numbers per segment.
- **Additional costs of recursion:** function-call overhead, a recursion stack of depth log2 n, and tuple creation. In the experiments the D&C solution took 0.62 s for n = 1,000,000 against 0.19 s for the simple one-pass Kadane scan.
- **When D&C might not be appropriate:** when a simpler or faster direct algorithm exists (Kadane here), when subproblems overlap heavily (dynamic programming is better), when the combine step is as expensive as the original problem, or when the problem is so small that overhead dominates.
- **What an algorithm designer should look for:** (1) the problem can be split into smaller independent instances of itself; (2) a clear base case; (3) a combine step that is cheaper than solving the whole problem – ideally the work at each level sums to less than the n^(log_b a) leaves (check with the recurrence); (4) the information that must cross the boundary is small and can be returned by the subproblems; (5) a balanced split.
