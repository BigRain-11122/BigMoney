"""Append the two r1315 methodology cards (append-only, no rewrite of the file)."""
import io
import os

PATH = os.path.join("knowledge", "METHODOLOGY_ASSETS.md")

CARDS = """

## E159 A spread with no noise floor is read as an edge; publish the floor with the spread (2026-10-27 r1314/r1315 bm-c)

E155 gave the forward book a daily spread against a buy-and-hold basket. The first reading was +0.75 pp over
three bars, and nothing on the face said whether 0.75 pp in three days was signal or weather. The fix is
arithmetic on the series the published marks are a prefix of -- NOT an estimate fitted to the three bars, which
would be noise wearing a number:
- dispersion of the daily book-minus-basket return over the WHOLE grid (1649 bars, 2020-01-02..2026-10-27):
  0.54146 %/day = 8.458 %/yr;
- an edge of E per year shows up as a daily mean of E/244, so a t-test reaches 2 at N = (2*244*sd/E)^2 bars:
  3 pp/yr -> 7758 bars (31.8 years), 5 pp/yr -> 2793 (11.4), 10 pp/yr -> 699 (2.9);
- a spread accumulated over n bars carries a 95 % band of 1.96*sd*sqrt(n) -- 3 bars = +-1.838 pp;
- the same identity inverted (E = 2*244*sd/sqrt(N)) answers the question a reader asks next: inside a fixed
  horizon the smallest edge that could clear the noise is 16.9 pp/yr over 1 year, 9.8 over 3, 7.6 over 5. So a
  book claiming a 3 pp edge is not "not yet proven" -- it is unprovable at any horizon a holder actually keeps.
The published +0.75 pp is inside that band, so the face now says so in the same breath as the number, and the
band is published at 1m/3m/1y/3y so a reader can see it shrinking as sqrt(bars) rather than faster.
Rules that keep it honest:
1) The floor is measured off the parent series, never off the published prefix; a one-bar ledger would otherwise
   publish a zero-width band and call everything significant.
2) The bars-needed figure is the t=2 identity, asserted in selftest and again in a smoke leg (t in [0.999, 1.02)
   after the ceil -- the lower bound is float slack from the published 5-dp vol) -- a floor that is not the
   formula will drift silently when the vol changes.
3) Publish the band at the ACTUAL published bar count, not a nominal horizon, so the sentence a reader quotes
   matches the day they read it.
4) Say the finite-horizon consequence out loud: at 8.5 %/yr excess vol this question is unanswerable inside a
   normal holding horizon for a 3 pp edge, which is a statement about the question, not about the book.
Evidence: results/etf_book_forward/LEDGER.json (benchmark.significance, incl. min_detectable_edge_pp),
scripts/etf_book_forward.py excess_series / significance / _sig_line / _attach_sig (selftest 33 -> 39: band
identity, sqrt scaling, t=2 per edge, the inverted horizon reading, the line carrying the floor, the
too-short-series guard), smoke_test.py (+1 leg reading the LEDGER rather than the script).
NOTE (r1315): this card was written by a window that died before committing, and its code was then lost by a
closeout that restored the tree from HEAD. It was re-implemented this round against the same identities and
reproduces the published readings to the digit; the CEO-page line (single writer, bm-a) is still NOT wired.

## E160 Two records of the same decision are not evidence until something compares them (2026-10-27 r1315 bm-c)

The card (what to hold) and the forward ledger (what the paper book says it holds) are two independent
records of ONE frozen decision, and for many rounds nothing compared them. r1290 caught the card vs ticket,
r1291 a lookup keyed on width only, r1293 the list of faces -- all three were found by a human asking a
question the tree could not answer. scripts/etf_book_card_track.py now answers the next one on every chain
run: same decision bar, same names (set and order), max |weight| difference, scale and cash, then the nav
re-derived from those same weights. 2026-10-27: agree at 2.1e-6 on weights and 2.5e-5 on scale, nav identity
1e-10; the frozen decision has drifted 0.145pp on one name since the fill bar, so undoing that drift would cost
0.11 bp of nav at the next decision -- the part of the bill that buys no new view.

Three rules it took to get that right:
1) An identity leg must re-derive the convention the face ACTUALLY uses. The ledger books constant target
   weights every bar (sum(w*r) with the frozen w) plus carry -- i.e. a costless implicit rebalance, not
   buy-and-hold. Re-deriving buy-and-hold and asserting equality at a loose tolerance published 1.1e-4 as
   noise; re-deriving the constant-weight path lands at 1e-10 and the buy-and-hold gap becomes a MEASUREMENT
   (1.1 bp over 3 bars, reported as the convention's footprint) instead of a fudge factor.
2) The published per-bar carry is already portfolio-level (cash weight x ladder rate). Multiplying by the
   cash weight again under-charges it by 30 % and the identity leg then reads a phantom trade -- caught
   in-window only because the tolerance was tight enough to look.
3) A grid countdown must be counted on the ENGINE's calendar. grid_position on the raw panel index (which
   carries pre-2020 bars) shifts the modulo-20 grid and printed 14 bars where the card says 11.
Evidence: results/etf_book_card_track.json, scripts/etf_book_card_track.py (selftest 19 legs), chain leg
etf_book_card_track (after etf_book_order), smoke leg "the paper book owns the book the card sells".
"""

with io.open(PATH, "r", encoding="utf-8", newline="") as fh:
    before = fh.read()
n0 = before.count("\n")
assert "## E160 Two records of the same decision" not in before, "already appended"
assert "## E159 A spread with no noise floor" not in before, "already appended"
with io.open(PATH, "a", encoding="utf-8", newline="") as fh:
    fh.write(CARDS)
with io.open(PATH, "r", encoding="utf-8", newline="") as fh:
    after = fh.read()
print("lines %d -> %d, bytes %d -> %d" % (n0, after.count("\n"), len(before), len(after)))
assert after.startswith(before)