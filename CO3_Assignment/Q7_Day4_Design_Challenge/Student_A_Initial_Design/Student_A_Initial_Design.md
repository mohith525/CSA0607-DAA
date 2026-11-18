# Q7 – Student A – Initial design proposal (Stage 1, written independently)

> NOTE FOR THE STUDENTS: this is a SAMPLE initial proposal. Stage 1 is meant to record each student's own independent thinking, so replace it with the design you actually came up with before discussing it with your partner.

**Problem chosen:** Maximum Subarray Sum (largest sum of a non-empty contiguous block of an integer array that may contain negative numbers).

**Decomposition.** Split the array into a left half and a right half at the middle.

**Base case.** A segment with one element: the answer is that element.

**Information each subproblem must return.** Only the best block sum inside the segment.

**Combine strategy.** The best block is either entirely in the left half, entirely in the right half, or it crosses the middle. Compute the crossing block directly: scan from the middle leftwards keeping the best running sum, scan from the middle+1 rightwards in the same way, and add the two best sums. Answer = max(left, right, crossing).

**Own assessment.** Correct for all three cases, easy to explain. The crossing scan costs Θ(n) at every level, so I expect T(n) = 2T(n/2) + n and Θ(n log n).
