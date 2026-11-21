# does every mark in the carry book still have a quote behind it?

verdict **BOOK_MARKS_SUPPORTED** | book (results\idx_fut_carry_paper\LEDGER.json) | generated 2026-11-21T23:29:59

12 bar(s) of 2 account(s) carry **0 mark(s) no contract panel on disk can reproduce**, holding **CNY 0** of absolute P&L. A bar that cannot be re-derived is not a wrong number -- it is a number whose evidence is gone.

| product | holds | bars | last bar | panel last quote | unbacked | what they are |
|---|---|---|---|---|---|---|
| IC | IC2612 | 6 | 2026-11-20 | 2026-11-20 | 0 |  |
| IM | IM2612 | 6 | 2026-11-20 | 2026-11-20 | 0 |  |

## the bars, one by one

## what the files say

| product | csv files | newest file | written | directory written |
|---|---|---|---|---|
| IC | 121 | IC2611.csv | 2026-11-21T05:51:09 | 2026-11-21T05:54:05 |
| IM | 55 | IM2612.csv | 2026-11-21T05:54:05 | 2026-11-21T05:54:05 |

A book bar dated after every file in the panel cannot have come from those files. When that is true the two readings above stop being symmetric: the splice reading needs a writer that is not on this disk, while the lost-row reading needs the panel to have gone backwards without a file being written. This face says which dates and which files; it does not pick between them.

`matches_continuous` = the printed close equals the main-continuous close of that date to the tick. Two readings fit and this disk cannot separate them: either the contract quoted that number that day and the panel has since lost the row, or the bar was marked from the other panel under this contract's label. `no_quote_on_disk` = no panel on disk produces that number at all.

This face retracts nothing. Taking a bar off a forward series is the book owner's decision; what is printed here is only that the evidence for it is not on this disk today.
