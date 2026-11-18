# Q7 – Student B – Initial design proposal (Stage 1, written independently)

> NOTE FOR THE STUDENTS: this is a SAMPLE initial proposal. Stage 1 is meant to record each student's own independent thinking, so replace it with the design you actually came up with before discussing it with your partner.

**Problem chosen:** Maximum Subarray Sum (same problem as Student A).

**Decomposition.** Split the array into two halves.

**Base case.** One element.

**Information each subproblem must return.** The best block sum and the total sum of the segment: (best, total).

**Combine strategy.** The answer for the whole segment is max(best of left, best of right, total of left + total of right), so that the combine step takes constant time and no rescanning is needed.

**Own assessment.** If it worked, T(n) = 2T(n/2) + O(1) = Θ(n). I am not sure about the crossing case: the "total of left + total of right" is the block that covers both halves completely.

**Result of testing this idea (added after Stage 1 coding).** The proposal is **incorrect**: for [-2, -5, 8, 7, -9, -1] the true answer is 15 (the block 8, 7), but this design returns 8. A crossing block need not cover the whole of both halves – it needs the best *suffix* of the left half and the best *prefix* of the right half.
