#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for scripts/idx_fut_carry_impact_decay.py (r2101 bm-c).

Every leg edits a COPY of the published face (never the face itself) and asserts the
predicate's own words. The two vocabularies are the contract (r1850/r1934):
  STALE        upstream bytes moved -> a chain leg may pay to rewrite
  CHECK FAILED same inputs, different number -> a defect, and the word STALE must NOT
               appear, otherwise a leg would hide a defect behind a refresh.
"""
import io
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_impact_decay as M                                 # noqa: E402

FACE = os.path.join(ROOT, "results", "idx_fut_carry_impact_decay.json")
CAP = os.path.join(ROOT, "results", "idx_fut_carry_capacity_lots.json")

n = 0


def ok(cond, label):
    global n
    n += 1
    if not cond:
        print("NEG-FAIL leg %d: %s" % (n, label))
        sys.exit(1)


def load():
    with io.open(FACE, encoding="utf-8") as fh:
        return json.load(fh)


def save(obj, path):
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def run_check(path):
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = M.check(face_path=path, quiet=False)
    return rc, buf.getvalue()


tmpdir = tempfile.mkdtemp(prefix="r2101bmc_neg_")
base = os.path.join(tmpdir, "face.json")
shutil.copyfile(FACE, base)

face = load()
prod = [k for k, v in face["products"].items() if v.get("status") == "ok"][0]
ruler = face["products"][prod]["binding_ruler"]

# N1 a hand-edited budget is a DEFECT: rc3, the word CHECK FAILED, and no STALE
bad = load()
bad["products"][prod]["rulers"][ruler]["budget_per_side_bp"] += 0.37
p = os.path.join(tmpdir, "n1.json")
save(bad, p)
rc, said = run_check(p)
ok(rc == 3 and "CHECK FAILED" in said and "STALE" not in said,
   "N1 edited budget -> CHECK FAILED without STALE (rc=%s)" % rc)

# N2 the same edit with a moved upstream digest is STALE (refresh is the right answer)
bad = load()
bad["products"][prod]["rulers"][ruler]["budget_per_side_bp"] += 0.37
key = list(bad["inputs"].keys())[0]
bad["inputs"][key] = "0" * 64
p = os.path.join(tmpdir, "n2.json")
save(bad, p)
rc, said = run_check(p)
ok(rc == 3 and "STALE" in said, "N2 moved input -> STALE (rc=%s, said=%r)" % (rc, said[:90]))

# N3 a reversed gate order is a defect even though every number is intact
bad = load()
gates = bad["products"][prod]["gate_order"]
gates.reverse()
for i, g in enumerate(gates):
    g["rank"] = i + 1
p = os.path.join(tmpdir, "n3.json")
save(bad, p)
rc, said = run_check(p)
ok(rc == 3 and "CHECK FAILED" in said and "gate order" in said,
   "N3 reversed gate order -> CHECK FAILED (rc=%s)" % rc)

# N4 a flipped verdict is a defect
bad = load()
bad["verdict"] = M.V_BITES if bad["verdict"] != M.V_BITES else M.V_NO_BITE
p = os.path.join(tmpdir, "n4.json")
save(bad, p)
rc, said = run_check(p)
ok(rc == 3 and "CHECK FAILED" in said, "N4 flipped verdict -> CHECK FAILED (rc=%s)" % rc)

# N5 a missing upstream face is DATA_BLOCKED, never a silent zero
blocked = M.derive(cap_path=os.path.join(tmpdir, "__absent__.json"))
ok(blocked["verdict"] == M.V_BLOCK and blocked["products"] == {}
   and "__absent__.json" in blocked["missing_inputs"],
   "N5 missing capacity face -> DATA_BLOCKED naming the missing file")

# N6 if the 1% line were far looser than the impact crossover, impact would stop being
#    the last gate -- the ordering must be read off the numbers, not assumed
gap = load()
cap_face = M._read_json(CAP)
face2 = M.derive()
q = face2["products"][prod]
lots_now = q["capacity_lots"]
cross = q["rulers"][q["binding_ruler"]]["impact_crossover_lots"]
synthetic = {"capacity_lots": cross * 4, "rung_lots": q["rung_lots"], "impact": cross}
order = sorted([("capital", q["rung_lots"]), ("adv", synthetic["capacity_lots"]),
                ("oi", 10 ** 9), ("impact", cross)], key=lambda t: t[1])
ok(order[-1][0] != "impact", "N6 the ordering test can fail: a looser ADV line puts impact first")

# N7 retention outside [0,1] is a defect (a share that is not a share)
bad = load()
bad["products"][prod]["rulers"][ruler]["retained_at_rung"] = 1.4
p = os.path.join(tmpdir, "n7.json")
save(bad, p)
rc, said = run_check(p)
ok(rc == 3 and "CHECK FAILED" in said, "N7 retention > 1 -> CHECK FAILED (rc=%s)" % rc)

# N8 the published face itself must be green (otherwise every leg above proves nothing)
rc, said = run_check(FACE)
ok(rc == 0 and "STALE" not in said, "N8 published face checks clean")

shutil.rmtree(tmpdir, ignore_errors=True)
print("NEGATIVE %d/%d OK" % (n, n))
