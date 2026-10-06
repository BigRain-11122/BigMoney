# -*- coding: utf-8 -*-
"""Settle the r775 assert discrepancy: does the contiguous needle exist in
the r775-landed n1 file (git) vs the current file?"""
import io
import re
import subprocess

raw = subprocess.run(["git", "show", "6957f509e:scripts/perpetual_faces_n1.py"],
                     capture_output=True).stdout.decode("utf-8")
print("r775-landed n1: contiguous 'refuse the naive W159 A window; W159 freezer' count:",
      raw.count("refuse the naive W159 A window; W159 freezer"))
i = raw.find("refuse the naive W159")
if i > 0:
    print("r775 context:", repr(raw[i - 60:i + 120]))

cur = io.open(r"scripts/perpetual_faces_n1.py", encoding="utf-8", newline="").read()
print("current n1: contiguous 'refuse the naive W160 A window; W160 freezer' count:",
      cur.count("refuse the naive W160 A window; W160 freezer"))
print("current n1: 'W160 A window; W160 freezer' count:", cur.count("W160 A window; W160 freezer"))
print("current n1: 'W160 A window; W160 freezer MUST re-derive on the' count:",
      cur.count('"W160 A window; W160 freezer MUST re-derive on the "'))
print("current n1: 'will refuse the naive \"' + next-frag W160 test:",
      cur.count('will refuse the naive "\r\n'))
