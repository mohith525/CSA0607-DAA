# Median of Medians – Student A notes

**Grouping strategy.** Split the n elements into ⌈n/5⌉ groups of 5, sort each group (a constant number of comparisons per group) and take its median.

**How the pivot is determined.** The pivot is the median of the ⌈n/5⌉ group medians, found by a recursive call of the same selection algorithm on n/5 elements.

**Why disastrous partitions are prevented.** Half of the group medians are ≤ pivot, and each of those groups has 3 elements (the median and two smaller ones) that are ≤ pivot. So at least 3n/10 elements are ≤ pivot and at least 3n/10 are ≥ pivot. Neither side of the partition can exceed 7n/10 elements: the pivot is *guaranteed* to be reasonably central whatever the input order.

**Worst-case guarantee.** T(n) ≤ T(n/5) + T(7n/10) + cn. Because 1/5 + 7/10 = 9/10 < 1, the total work forms a decreasing geometric series, giving T(n) = O(n) in the worst case.

**Comparison with QuickSelect (experiment).** First-element pivot on ascending data: 24,006,000 comparisons for n = 8,000 (partition fraction 0.9999 at every level, quadratic). Random pivot: mean about 3.3n comparisons, but the worst partition seen in 300 runs was 0.9992 – randomisation makes poor partitions unlikely, not impossible. Median of Medians: 3.9n–8.4n comparisons for every input tested; the largest partition fraction observed was 0.519 (limit 0.7). Price: a larger constant factor (about 2–3 times the average randomised cost).

**Why randomisation reduces but does not eliminate poor partitions.** A random pivot lands in the middle 50% of the ranks with probability 1/2, so long runs of bad pivots are exponentially unlikely, but any single run can still get a bad pivot, and the guarantee is only in expectation.
