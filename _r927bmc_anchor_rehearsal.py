# -*- coding: utf-8 -*-
# r927 bm-c anchor rehearsal for the W221 freeze editor derivation.
# Read-only: verifies every find-string/count the editor will assert,
# and rehearses the parity-estate extraction from the live W220 block.
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

pf_t = open(r"scripts\perpetual_faces.py", encoding="utf-8").read()
n1_t = open(r"scripts\perpetual_faces_n1.py", encoding="utf-8").read()

def eol_of(t):
    crlf = t.count("\r\n")
    lf = t.count("\n") - crlf
    return "\r\n" if crlf > lf else "\n"

EOL = eol_of(n1_t); PF_EOL = eol_of(pf_t)
checks = [
    ("pf '220: {\"a\"' rows", pf_t.count('220: {"a"'), 1),
    ("pf close anchor (owner+}+v1comment)", pf_t.count('"engine_owner": "bm-c"},' + PF_EOL + '}' + PF_EOL + '# v1 + ext(wave-1) in-use bands'), 1),
    ("n1 '220: {\"batch\"' entries", n1_t.count('220: {"batch"'), 1),
    ("n1 W220 materializer face", n1_t.count('    # --- W220 materializer face'), 1),
    ("n1 T-141 s2 lane face marker", n1_t.count('    # --- T-141 s2 lane face'), 1),
    ("n1 print anchor '+T-141", n1_t.count('          "+ T-141 s2 '), 1),
    ("n1 W220 prereg key line", n1_t.count('"prereg": ("research/PERPETUAL_N1_W220_PREREG.md'), 1),
    ("n1 a_seed_base 498804", n1_t.count('"a_seed_base": 498804'), 1),
    ("n1 cfg close anchor", n1_t.count('                       }' + EOL + 'PREREG = WAVE_CONFIGS[2]["prereg"]'), 1),
    ("n1 batch PERPETUAL-N1-W220", n1_t.count('"batch": "PERPETUAL-N1-W220"'), 1),
    ("pf 221 row pre-existing", pf_t.count('221: {"a"'), 0),
    ("n1 221 cfg pre-existing", n1_t.count('221: {"batch"'), 0),
    ("n1 221 batch pre-existing", n1_t.count('"batch": "PERPETUAL-N1-W221"'), 0),
    ("n1 W221 mat face pre-existing", n1_t.count('    # --- W221 materializer face'), 0),
]
bad = 0
for name, got, want in checks:
    ok = got == want
    bad += (not ok)
    print(("PASS " if ok else "FAIL ") + name + " = " + str(got) + " (want " + str(want) + ")")

# parity estate rehearsal from the live W220 block
a15 = '    # --- W220 materializer face'
a_t141 = '    # --- T-141 s2 lane face'
s = n1_t.find(a15); t = n1_t.find(a_t141)
assert s > 0 and t > s, "W220 block span not found"
blk = n1_t[s:t]
m_first = re.search(r"assert pf\.N1_BANDS\[", blk)
m_disj = re.search(r"        # prior-wave disjointness W2\.\.W\d+ \(single state", blk)
assert m_first and m_disj and m_disj.start() > m_first.start(), "parity span markers missing in W220 block"
row_ls = blk.rfind(EOL, 0, m_first.start()) + len(EOL)
par_full = blk[row_ls:m_disj.start()]
m219 = re.search(r" *assert pf\.N1_BANDS\[219\] ==", par_full)
assert m219, "W219 leg not found inside W220 parity span"
par_sec = par_full[:m219.start()]
assert par_sec.endswith(EOL), "estate segment must end with EOL"
ws = re.findall(r"assert pf\.N1_BANDS\[(\d+)\] ==", par_sec)
n_full = par_full.count("assert pf.N1_BANDS[")
n_sec = par_sec.count("assert pf.N1_BANDS[")
print("par_full rows =", n_full, "(want 78) | par_sec rows =", n_sec, "(want 77)")
print("estate 69 range ok =", [int(w) for w in ws[:69]] == list(range(138, 207)))
print("par_sec legs =", [int(w) for w in ws[69:]], "(want [211..218])")
bad += (n_full != 78) + (n_sec != 77)
bad += ([int(w) for w in ws[:69]] != list(range(138, 207)))
bad += ([int(w) for w in ws[69:]] != list(range(211, 219)))
print("EOL n1 =", repr(EOL), "| PF_EOL =", repr(PF_EOL))

# live registry faces for gate0.5 rehearsal
import os, importlib.util
REPO = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
owner_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner")]
bmc_rows = [w for w, c in pf_mod.N1_BANDS.items() if (c or {}).get("engine_owner") == "bm-c"]
print("owner_rows_live =", len(owner_rows), "(want 210) | bmc_rows_live =", len(bmc_rows), "(want 50)")
W220 = dict(pf_mod.N1_BANDS.get(220) or {})
print("W220 row =", W220)
bad += (len(owner_rows) != 210) + (len(bmc_rows) != 50)
bad += (W220.get("engine_owner") != "bm-c")
print("REHEARSAL", "ALL GREEN" if bad == 0 else ("RED x%d" % bad))
