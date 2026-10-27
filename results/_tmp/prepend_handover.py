import io

p = 'research/HANDOVER.md'
s = io.open(p, encoding='utf-8', errors='replace', newline='').read()
line = (
    '> bm-c round 1315 (5x handover refresh, 2026-10-27 22:4x): rounds 1311-1315 all landed on the ETF book lane. '
    'PRODUCTS in order: r1311 the staggered 6+6 book put through the same four-span regression (intercept +6.77%/yr t=2.36 vs single +5.85% t=1.94) '
    '+ docs/live_book registered as the fifth registry face; r1312 the same regression run OUTSIDE 2020-2026 on the 193 pre-2020 ETFs '
    '(single +2.03%/yr alpha t=1.04, staggered +1.00% t=0.48, basket 8.64%/yr beats the book 5.12% => the 9-10% headline is a window property); '
    'r1313 the forward ledger gains the four-ETF basket as a rival arm on its own grid/next-open/turnover (bar-level nav/book_nav/excess, first reading +0.75pp over 3 bars); '
    'r1314 the significance floor (excess vol 8.458%/yr -> 7758 bars for a 3pp/yr edge; inside one year only a 16.9pp/yr edge clears the noise) '
    '+ the inverted reading published with it; r1315 NEW THIS ROUND scripts/etf_book_card_track.py (selftest 19/19) reconciles the card against the forward ledger '
    '(same decision bar 2026-10-14, identical names in identical order, weights 2.1e-6 apart, scale 2.5e-5 apart, nav re-derived from those weights to 1e-10) '
    'and prices what the frozen decision has drifted to (max |dw| 0.145pp, re-target cost 0.11bp, 11 bars to the next decision). '
    'Faces: results/etf_book_card_track.json, chain leg etf_book_card_track (after etf_book_order), smoke leg "the paper book owns the book the card sells" (99/99). '
    'Pitfalls recorded this window: an identity leg must re-derive the convention the face ACTUALLY uses (constant target weights, not buy-and-hold) or it publishes 1.1e-4 as noise; '
    'the published per-bar carry is already portfolio-level (multiplying by the cash weight again reads a phantom trade); '
    'a grid countdown must be counted on the engine calendar (>= R.START) or the modulo-20 grid shifts (14 vs 11 bars). '
    'Still owed: the CEO page is a bm-a single writer, so this host cannot render it.\n'
)
io.open(p, 'w', encoding='utf-8', newline='').write(line + s)
print('prepended %d bytes; file now %d' % (len(line), len(s) + len(line)))