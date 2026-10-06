# -*- coding: utf-8 -*-
"""r793 bm-a W165 band-gate deriver: token-advance the r792 W164 gate bloodline
into the W165 freeze window. Same law set as the probe deriver (r631 single-pass,
r632 count-reconcile, r637 value anchors) plus gate-specific anchors: seat name,
seat commit, parity receipt path, bloodline pointer."""
import ast
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = r"results/_r792bma_w164_band_gate.py"
DST = r"results/_r793bma_w165_band_gate.py"

s = open(SRC, encoding="utf-8", newline="").read()

# phase 1: precise cross-wave strings first
s = s.replace("W164-B-refuses-W165-A", "W165-B-refuses-W166-A")
s = s.replace("W165p", "W166p")
s = s.replace("W165+", "W166+")
s = s.replace("PERPETUAL-N1-W164", "PERPETUAL-N1-W165")
s = s.replace("PERPETUAL_N1_W164_PREREG", "PERPETUAL_N1_W165_PREREG")
s = s.replace("_r792bma_w164", "_r793bma_w165")
s = s.replace("'164: {\"a\": ('", "'165: {\"a\": ('")

# phase 2: global token advance
s = s.replace("W164", "W165")
s = s.replace("W163", "W164")
s = s.replace("w164", "w165")

# phase 3: value anchors (post-advance)
s = s.replace("(373_404, 375_403)", "(375_604, 377_603)")
s = s.replace("(375_404, 375_603)", "(377_604, 377_803)")
s = s.replace("(371_204, 373_203)", "(373_404, 375_403)")
s = s.replace("(373_204, 373_403)", "(375_404, 375_603)")
s = s.replace("range(16, 164)", "range(16, 165)")
s = s.replace("len(owner_rows) == 153 and len(bma_rows) == 79", "len(owner_rows) == 154 and len(bma_rows) == 80")
s = s.replace('"ordinal": 154, "bma_ordinal": 80', '"ordinal": 155, "bma_ordinal": 81')
s = s.replace("TWENTY-THIRD", "TWENTY-FOURTH")
s = s.replace("W164 B band 375_404..375_603", "W164 B band 377_604..377_803")
s = s.replace("W165 B band 377_604..377_803", "W165 B band 379_804..380_003")
s = s.replace("W162 row drift", "W163 row drift")
# bare index advance (r-token pass cannot touch these): main 163->164, secondary 162->163
s = s.replace("N1_BANDS[163]", "N1_BANDS[164]")
s = s.replace("N1_BANDS[162]", "N1_BANDS[163]")
# gate-specific anchors
s = s.replace("MSG-2026-10-06-194x-bma-w165-seat.md", "MSG-2026-10-06-205x-bma-w165-seat.md")
s = s.replace('SEAT_NAME = "MSG-2026-10-06-194x-bma-w164-seat.md"', 'SEAT_NAME = "MSG-2026-10-06-205x-bma-w165-seat.md"')
s = s.replace('"r792 W165 band gate"', '"r793 W165 band gate"')
s = s.replace("r792 W165 band gate", "r793 W165 band gate")
s = s.replace("parity with the r792 pre-seat probe", "parity with the r793 pre-seat probe")
s = s.replace("r792 pre-seat probe receipt", "r793 pre-seat probe receipt")
s = s.replace("Bloodline: r789 _r789bma_w164_band_gate.py machinery (derive core verbatim)",
              "Bloodline: r792 _r792bma_w164_band_gate.py machinery (derive core verbatim)")
s = s.replace("Bloodline: r789 _r789bma_w163_band_gate.py machinery (derive core verbatim)",
              "Bloodline: r792 _r792bma_w164_band_gate.py machinery (derive core verbatim)")
s = s.replace('"seat_commit": "469d40896 published (r792 pre-seat push, r565 law; zero --no-verify)"',
              '"seat_commit": "4bdf63090 published (r793 pre-seat push, r565 law; zero --no-verify)"')
s = s.replace("469d40896 published", "4bdf63090 published")

# reconcile
bl = [l for l in s.splitlines() if "_r792bma" in l]
assert len(bl) == 1 and "Bloodline" in bl[0], f"r792 refs must be exactly the bloodline pointer: {bl}"
wl = [l for l in s.splitlines() if "w164" in l]
assert wl == bl, f"lowercase w164 must live only in the bloodline pointer: {wl}"
assert "194x" not in s, "old seat timestamp residue"
assert "N1_BANDS[162]" not in s
assert s.count("N1_BANDS[164]") == 3, f"main-row [164] sites: {s.count('N1_BANDS[164]')}"
assert s.count("N1_BANDS[163]") == 2, f"secondary-row [163] sites: {s.count('N1_BANDS[163]')}"
assert s.count("W163") == 1 and "W163 row drift" in s
assert "4bdf63090" in s and "469d40896" not in s, "seat commit anchor"
assert s.count("W165") >= 20 and s.count("W164") >= 10, "token advance incomplete"
ast.parse(s)
open(DST, "w", encoding="utf-8", newline="").write(s)
print("derived", DST, "OK (AST PASS, zero-residue PASS, gate anchors PASS)")
