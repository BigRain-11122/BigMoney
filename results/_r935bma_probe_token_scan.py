# -*- coding: utf-8 -*-
"""r935 S'-construction analysis: enumerate every generation-shiftable
token (rNNN refs, 9-hex shas, band windows, MSG names, ledger numbers,
ordinals) in the four physical W202 fragments, with context. Read-only."""
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = (r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results"
        r"\_r935bma_probe_frag_%s.txt")
frags = {}
for nm in ("cfg202", "mat202", "pf202", "claim202"):
    frags[nm] = open(BASE % nm, encoding="utf-8", newline="").read()

pats = [
    ("round", re.compile(r"\br9\d{2}\b")),
    ("sha9", re.compile(r"\b[0-9a-f]{9}\b")),
    ("band", re.compile(r"\b\d{3}_\d{3}(?:\.\.\d{3}_\d{3})?\b")),
    ("msg", re.compile(r"MSG-2026-10-09-\d{4}")),
    ("ledger", re.compile(r"\b\d{3},\d{3}\b")),
    ("ordinal", re.compile(r"(?:[A-Z-]*HUNDRED[A-Z -]*|SIXTY-[A-Z]+|"
                           r"sixty-[a-z]+|one-hundred-[a-z]+)")),
]
for nm, txt in frags.items():
    print("=" * 25, nm, "len", len(txt), "=" * 25)
    for tag, pat in pats:
        hits = []
        for m in pat.finditer(txt):
            ctx = txt[max(0, m.start() - 45):m.end() + 25].replace("\n", " ")
            hits.append((m.group(), ctx))
        if hits:
            print("-- %s (%d)" % (tag, len(hits)))
            seen = set()
            for g, ctx in hits:
                if g in seen:
                    continue
                seen.add(g)
                print("   %-22r | ...%s..." % (g, ctx))
