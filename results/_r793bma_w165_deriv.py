# -*- coding: utf-8 -*-
"""r793 bm-a W165 pre-seat probe deriver: token-advance the r792 W164 probe
bloodline verbatim machinery into the W165 window (W164 row now registered).
Laws: r631 re.sub single-pass full-token advance; r632 needle-completeness
count-reconcile; r637 value-anchor maintenance belongs to the run window;
r587 facts always live-derived (only static W164-row anchors updated)."""
import ast
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = r"results/_r792bma_w164_probe.py"
DST = r"results/_r793bma_w165_probe.py"

s = open(SRC, encoding="utf-8", newline="").read()

# --- phase 1: precise cross-wave strings BEFORE global token advance -----------
s = s.replace("W164-B-refuses-W165-A", "W165-B-refuses-W166-A")
s = s.replace("W165p", "W166p")
s = s.replace("W165+", "W166+")
s = s.replace("PERPETUAL-N1-W164", "PERPETUAL-N1-W165")
s = s.replace("PERPETUAL_N1_W164_PREREG", "PERPETUAL_N1_W165_PREREG")
s = s.replace("_r792bma_w164", "_r793bma_w165")
s = s.replace("'164: {\"a\": ('", "'165: {\"a\": ('")

# --- phase 2: global token advance (single-pass ordered) ------------------------
s = s.replace("W164", "W165")
s = s.replace("W163", "W164")
s = s.replace("w164", "w165")

# --- phase 3: value-anchor maintenance (post-advance, W164-row facts) -----------
s = s.replace("r792 W165", "r793 W165")  # receipt label already advanced; retitle
s = s.replace("(373_404, 375_403)", "(375_604, 377_603)")  # W164 A anchor
s = s.replace("(375_404, 375_603)", "(377_604, 377_803)")  # W164 B anchor
s = s.replace("(371_204, 373_203)", "(373_404, 375_403)")  # W163 A anchor
s = s.replace("(373_204, 373_403)", "(375_404, 375_603)")  # W163 B anchor
s = s.replace("range(16, 164)", "range(16, 165)")
s = s.replace("len(owner_rows) == 153 and len(bma_rows) == 79", "len(owner_rows) == 154 and len(bma_rows) == 80")
s = s.replace('"ordinal": 154, "bma_ordinal": 80', '"ordinal": 155, "bma_ordinal": 81')
s = s.replace("TWENTY-THIRD", "TWENTY-FOURTH")
s = s.replace("twenty-THIRD", "twenty-FOURTH")
s = s.replace("W164 B band 375_404..375_603", "W164 B band 377_604..377_803")
s = s.replace("W164 B band 375_404..375_603", "W164 B band 377_604..377_803")  # prose safety
s = s.replace("W163 B band 375_404..375_603", "W164 B band 377_604..377_803")  # any pre-advance remnant
s = s.replace("r790 one-pass, ledger head 764,012, pool K=356,520", "r793 one-pass, ledger head 766,212, pool K=358,720")
s = s.replace("bm-a r789 freeze 18231a529", "bm-a r792 freeze pushed / r793 finalize f7d34e5a7")
s = s.replace("W162 row drift", "W163 row drift")
s = s.replace("18231a529", "f7d34e5a7")
# bare index advance (the W-token pass cannot touch these): main row 163->164 (3 sites),
# secondary row 162->163 (2 sites) -- ORDER MATTERS
s = s.replace("N1_BANDS[163]", "N1_BANDS[164]")
s = s.replace("N1_BANDS[162]", "N1_BANDS[163]")

# --- reconcile: counts + zero-residue + AST -------------------------------------
assert "_r792bma" not in s, "r792 residue"
assert "w164" not in s, "lowercase w164 residue"
assert "18231a529" not in s, "old freeze sha residue"
assert "N1_BANDS[162]" not in s, "bare index 162 residue (secondary row must be 163)"
assert s.count("N1_BANDS[164]") == 3, f"main-row [164] sites != 3: {s.count('N1_BANDS[164]')}"
assert s.count("N1_BANDS[163]") == 2, f"secondary-row [163] sites != 2: {s.count('N1_BANDS[163]')}"
assert s.count("W163") == 1 and "W163 row drift" in s, "W163 must survive only as the secondary-row drift message"
assert s.count("W165") >= 20 and s.count("W164") >= 10, "token advance incomplete"
ast.parse(s)
open(DST, "w", encoding="utf-8", newline="").write(s)

# --- reconcile details for the round report -------------------------------------
import collections

c = collections.Counter(re.findall(r"W16[456]", s))
print("W164 refs:", c["W164"], "| W165 refs:", c["W165"], "| W166 refs:", c["W166"])
print("derived", DST, "OK (AST parse PASS, zero-residue PASS)")
