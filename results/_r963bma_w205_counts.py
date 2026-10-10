# -*- coding: utf-8 -*-
"""r963 estate-continuation probe: measure live W204 fragment token counts
after the pre-rebase absorb + rebase (prior session measured pre-rebase)."""
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1P = os.path.join(ROOT, "scripts", "perpetual_faces_n1.py")
PFP = os.path.join(ROOT, "scripts", "perpetual_faces.py")


def chunk(text, start, end):
    i = text.find(start)
    assert i >= 0, "start not found: %r" % start[:60]
    j = text.find(end, i)
    assert j > i, "end not found: %r" % end[:60]
    return text[i:j + len(end)]


n1n = open(N1P, encoding="utf-8", errors="replace", newline="").read().replace("\r\n", "\n")
pfn = open(PFP, encoding="utf-8", errors="replace", newline="").read().replace("\r\n", "\n")

cfg204 = chunk(n1n, '204: {"batch": "PERPETUAL-N1-W204",',
               '"engine_owner": "bm-c"},')
mat_start = n1n.find("    # --- W204 materializer face")
t141 = n1n.find("    # --- T-141 s2 lane face", mat_start)
mat204_full = n1n[mat_start:t141]
ci = mat204_full.find("_set_wave(204)")
body204 = mat204_full[ci:]

print("== cfg204 token counts ==")
for tok in ("bm-a r938", "860,945", "444,520", "n1_w204", "W203",
            "W204", "446,720", "864,387", "bm-c r837"):
    print("  cfg %r: %d" % (tok, cfg204.count(tok)))

print("== body204 token counts ==")
for tok in ("bm-a r938", "860,945", "444,520", "n1_w204", "W203",
            "W204", "446,720", "864,387", "bm-c r837", "PERPETUAL_N1_W204"):
    print("  body %r: %d" % (tok, body204.count(tok)))

print("== body204 residual contexts (W203 / n1_w204) ==")
for m in re.finditer(r"W203|n1_w204", body204):
    s = max(0, m.start() - 70)
    print("  ...%s..." % body204[s:m.end() + 70].replace("\n", " \\n "))

print("== cfg204 residual contexts (bm-a r938 / 860,945 / 444,520) ==")
for m in re.finditer(r"bm-a r938|860,945|444,520", cfg204):
    s = max(0, m.start() - 80)
    print("  ...%s..." % cfg204[s:m.end() + 80].replace("\n", " \\n "))

print("== law/pin blocks ==")
law_old = chunk(body204, 'assert WAVE_CONFIGS[203]["a_seed_base"]',
                'law mirror parity)"')
print("law_old W203 count:", law_old.count("W203"))
pin_old = chunk(body204, 'assert pf.N1_BANDS[203] == {"a": (461_404, 463_403),',
               'r307; bm-a r936)"')
print("pin_old W203 count:", pin_old.count("W203"))
for m in re.finditer(r"W203", pin_old):
    s = max(0, m.start() - 60)
    print("  pin W203 ctx: ...%s..." % pin_old[s:m.end() + 40].replace("\n", " \\n "))
