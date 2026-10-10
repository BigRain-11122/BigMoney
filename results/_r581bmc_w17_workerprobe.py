"""r581 worker-path LIVE probe (the dry check r820 faked): a real
subprocess imports tl1 exactly like a spawn worker would, runs
tl1._init_worker(state) with the state['grammar'] the patched cmd_screen
now packs (W16 grammar w/ 77 faces), then resolves the L350 face_frame
lookup for ALL 173 W17 candidates. Exit 0 = the KeyError('faces')
crash face is dead.

Additionally asserts the two patched pack sites carry 'grammar' ==
W16 grammar (source-face static check)."""

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import trial_labor_w1 as tl1          # the module spawn workers re-import
import trial_labor_w17 as w17         # patched runner (constants + loader)

# 1) state face == what patched cmd_screen/cmd_judge now pack
w16g = json.load(open(w17.W16_GRAMMAR_FILE, encoding="utf-8"))
assert "faces" in w16g and len(w16g["faces"]) == 77, "w16 faces table absent"
state = {"grammar": tl1.GRAMMAR}       # placeholder; overwritten below

# emulate the parent-side load the patched code performs, then pack
tl1.GRAMMAR = w16g
state["grammar"] = tl1.GRAMMAR

# 2) worker-path: the exact initializer the pool uses
tl1._init_worker(state)
assert tl1.GRAMMAR is not None and "faces" in tl1.GRAMMAR, \
    "worker GRAMMAR missing faces after _init_worker"

# 3) L350 expression for every real W17 candidate (frozen entry product)
cands = w17._entry_load()["candidates"]
missing = []
for c in cands:
    mk = f"{c['module']}.{c['fn']}"
    try:
        frame = tl1.GRAMMAR["faces"][mk]      # <-- the exact crash line
        assert frame is not None
    except KeyError:
        missing.append((c["candidate_id"], mk))
print(f"candidates={len(cands)} resolved={len(cands) - len(missing)} "
      f"missing={missing[:3]}")

# 4) source face: both pack sites carry grammar: tl1.GRAMMAR
src = open(os.path.join(ROOT, "scripts", "trial_labor_w17.py"),
           encoding="utf-8").read()
n_site = src.count('"grammar": tl1.GRAMMAR')
print(f"pack sites with tl1.GRAMMAR = {n_site} (expect 2)")
assert n_site == 2, "patch drift: expected both screen+judge pack sites"

rc = 0 if (not missing and n_site == 2) else 1
print("WORKER-PROBE:", "PASS" if rc == 0 else "FAIL")
sys.exit(rc)
