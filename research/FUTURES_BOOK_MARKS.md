# does every mark in the carry book still have a quote behind it?

verdict **BOOK_MARKS_UNSUPPORTED** | book (results\idx_fut_carry_paper\LEDGER.json) | generated 2026-11-19T16:10:55

6 bar(s) of 2 account(s) carry **2 mark(s) no contract panel on disk can reproduce**, holding **CNY 84,480** of absolute P&L. A bar that cannot be re-derived is not a wrong number -- it is a number whose evidence is gone.

| product | holds | bars | last bar | panel last quote | unbacked | what they are |
|---|---|---|---|---|---|---|
| IC | IC2612 | 3 | 2026-11-17 | 2026-11-16 | 1 | matches_continuous (+1 session(s) past the panel) |
| IM | IM2612 | 3 | 2026-11-17 | 2026-11-16 | 1 | matches_continuous (+1 session(s) past the panel) |

## the bars, one by one

### IC

| date | contract | close printed | contract panel | main-continuous | cause | P&L on the bar |
|---|---|---|---|---|---|---|
| 2026-11-17 | IC2612 | 6194.8 | **no quote** | 6194.8 | matches_continuous | -18,880 |

### IM

| date | contract | close printed | contract panel | main-continuous | cause | P&L on the bar |
|---|---|---|---|---|---|---|
| 2026-11-17 | IM2612 | 6023.0 | **no quote** | 6023.0 | matches_continuous | -65,600 |

## what the files say

| product | csv files | newest file | written | directory written |
|---|---|---|---|---|
| IC | 121 | IC2607.csv | 2026-11-16T22:30:28 | 2026-11-15T04:34:00 |
| IM | 55 | IM2607.csv | 2026-11-16T22:30:33 | 2026-11-15T04:34:00 |

A book bar dated after every file in the panel cannot have come from those files. When that is true the two readings above stop being symmetric: the splice reading needs a writer that is not on this disk, while the lost-row reading needs the panel to have gone backwards without a file being written. This face says which dates and which files; it does not pick between them.

`matches_continuous` = the printed close equals the main-continuous close of that date to the tick. Two readings fit and this disk cannot separate them: either the contract quoted that number that day and the panel has since lost the row, or the bar was marked from the other panel under this contract's label. `no_quote_on_disk` = no panel on disk produces that number at all.

This face retracts nothing. Taking a bar off a forward series is the book owner's decision; what is printed here is only that the evidence for it is not on this disk today.
