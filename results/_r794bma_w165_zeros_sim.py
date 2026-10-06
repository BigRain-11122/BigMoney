# -*- coding: utf-8 -*-
"""r794 bm-a: simulate the deriver's EXPECT rebuild to adjudicate the
zero-count assert expectation before fixing the unpacking bug."""
import io
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

s = io.open(r"results/_r792bma_w164_prereg_build.py", encoding="utf-8").read()
PH0 = [
    ("r792 pre-seat", "r793 pre-seat"),
    ("gate-derived r792", "gate-derived r793"),
    ("r792 gate leg3", "r793 gate leg3"),
    ("the r792 gate + probe receipts", "the r793 gate + probe receipts"),
    ("469d40896", "4bdf63090"),
    ("MSG-2026-10-06-194x", "MSG-2026-10-06-205x"),
    ("seat MSG-194x tail", "seat MSG-205x tail"),
]
PH1 = [
    ("W165", "W166"), ("W164", "W165"), ("W163", "W164"), ("W162", "W163"),
    ("w164", "w165"), ("w163", "w164"),
]
PH2 = [
    ("r792", "r794"), ("r790", "r793"), ("r789", "r792"), ("r788", "r790"),
    ("r787", "r789"),
]
for a, b in PH0:
    s = s.replace(a, b)
for a, b in PH1:
    s = s.replace(a, b)
for a, b in PH2:
    s = s.replace(a, b)

m = re.search(r"EXPECT = \{.*?\n\}", s, re.S)
pairs = re.findall(r'"([^"]+)": (\d+)', m.group(0))
raw_src = subprocess.run(
    ["git", "show", "f7d34e5a7:research/PERPETUAL_N1_W164_PREREG.md"],
    capture_output=True).stdout
src_txt = raw_src.decode("utf-8")

rows, zeros = [], []
for k, old in pairs:
    kk = "164" if k == "163" else k
    cnt = src_txt.count(kk)
    rows.append((kk, cnt))
    if cnt == 0:
        zeros.append(kk)

print("derived EXPECT keys/counts:", rows)
print("ZEROS:", zeros)
