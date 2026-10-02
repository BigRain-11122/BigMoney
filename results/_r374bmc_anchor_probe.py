# -*- coding: utf-8 -*-
"""r374 bm-c: W99 freeze anchor probe (repr probe law r581) + machine-derive counts.

Probes exact anchor bytes for the W99 five-face freeze generator:
  edit1 anchor = pf.py W98 row + closing brace
  edit2 anchor = n1.py W98 entry tail
  edit3 anchor = _set_wave(2) + T-141 comment (full-line law r580)
  edit5 anchor = summary 'law sec.4 W98 row' single-line literal (+post-anchor)
  edit4 anchor = canon '每波 finalize 后' line
Plus: engine_owner counts, landed-finalize set (chain head derive), W94
finalize measured keys for the W99 prereg §5 anchor (r576 anchor-roll law).
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "research"))
sys.path.insert(0, os.path.join(REPO, "scripts"))


def load(fp):
    b = open(fp, "rb").read()
    t = b.decode("utf-8")
    eol = "\r\n" if t.count("\r\n") * 2 > t.count("\n") else "\n"
    return t, eol


pf, eol_pf = load(os.path.join(REPO, "scripts", "perpetual_faces.py"))
n1, eol_n1 = load(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
canon, eol_canon = load(os.path.join(REPO, "research", "PERPETUAL_FACES.md"))

print("== EOLS ==")
print("pf eol:", repr(eol_pf), "| n1 eol:", repr(eol_n1),
      "| canon eol:", repr(eol_canon))

print("== EDIT1 ANCHOR (pf W98 row + brace) ==")
i = pf.find('    98: {"a": (239_004')
print(repr(pf[i:i + 200]))

print("== EDIT2 ANCHOR (n1 W98 entry tail) ==")
j = n1.find('"shard_subdir": "n1_w98"')
print(repr(n1[j - 40:j + 160]))

print("== EDIT5 ANCHOR (summary law sec.4 W98 row) ==")
k = n1.find('law sec.4 W98 row')
print("found:", k >= 0)
print(repr(n1[k - 80:k + 120]))

print("== EDIT3 ANCHOR (leg _set_wave(2) + T-141) ==")
a3_lf = '        _set_wave(2)\n    # --- T-141 s2 lane face'
a3_any = a3_lf.replace('\n', eol_n1)
print("count(eol-adapted):", n1.count(a3_any))
m = n1.find(a3_any)
print(repr(n1[m:m + 120]) if m >= 0 else "NOT FOUND")

print("== EDIT4 ANCHOR (canon 每波 finalize line) ==")
a4_lf = '\n- 每波 finalize 后：`science_gates.append_ledger` 落行'
a4_any = a4_lf.replace('\n', eol_canon)
print("count:", canon.count(a4_any))

print("== MACHINE-DERIVE COUNTS ==")
import perpetual_faces as pfm
rows = pfm.N1_BANDS
owner_rows = {w: c.get("engine_owner") for w, c in rows.items() if c.get("engine_owner")}
bmc = sorted(w for w, o in owner_rows.items() if o == "bm-c")
bma = [w for w, o in owner_rows.items() if o == "bm-a"]
bmb = [w for w, o in owner_rows.items() if o == "bm-b"]
print("total rows:", len(rows), "| owner rows:", len(owner_rows))
print("bm-c rows:", len(bmc), bmc)
print("bm-a rows:", len(bma), "| bm-b rows:", len(bmb))
keys = sorted(rows)
print("keys head/tail:", keys[:14], "...", keys[-4:])

print("== LANDED FINALIZE SET (chain head derive) ==")
pfdir = os.path.join(REPO, "results", "perpetual_faces")
landed = []
for fn in sorted(os.listdir(pfdir)):
    if fn.startswith("n1_w") and fn.endswith("_results.json"):
        landed.append(fn)
print("landed finalize files:", landed[-6:] if landed else "none")

print("== W94 FINALIZE MEASURED KEYS (W99 prereg sec.5 anchor) ==")
w94 = json.load(open(os.path.join(pfdir, "n1_w94_results.json"), encoding="utf-8"))
for key in ("batch", "n_values", "evidence_cutoff", "ledger", "skill_line", "summary"):
    v = w94.get(key)
    s = json.dumps(v, ensure_ascii=False)
    print(f"[{key}]", s[:500])

print("== PREREG PRESENCE (W95..W99) ==")
for w in (95, 96, 97, 98, 99):
    p = os.path.join(REPO, "research", f"PERPETUAL_N1_W{w}_PREREG.md")
    print(f"W{w}:", os.path.exists(p))
