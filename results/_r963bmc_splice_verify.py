# r963 (bm-c): W230 splice estate machine verification before commit
# (clone of _r962bmc_splice_verify.py, adapted W229->W230 per r812 bloodline law;
#  18th absorb instance: dead r963 window ran prereg (committed 91de0ae83) +
#  five-face freeze splice on disk 11:39 (receipt _w230bmc_freeze_receipt.json) +
#  engine mtime-watch self-burn 12/12 (ledger appends 0ef11a120+aec41c57c
#  self-committed), then died pre-commit -- this window verifies+lands)
# - receipt sha16 asserts vs on-disk bytes (fail-closed)
# - py_compile both spliced faces
# - pf N1_BANDS[230] bands == receipt bands (live import, zero-literal)
# - n1 WAVE_CONFIGS[230] row: batch/a_seed_base/b_exit_seed_base/shard_subdir (live import)
# - WAVE row census 229/230 = 1/1 both faces shape-correct
# - shards n1_w230 12/12 (results/p2cal_ext/n1_w230/)
# - finalize product absent (PRE-FINALIZE phase proof)
import hashlib
import json
import os
import py_compile
import re
import sys

BASE = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
rec = json.load(open(BASE + r"\results\_w230bmc_freeze_receipt.json", encoding="utf-8"))
fails = []

# 1) sha16 receipt-match both faces + py_compile
for path, key in [
    (BASE + r"\scripts\perpetual_faces.py", "pf_sha16_post"),
    (BASE + r"\scripts\perpetual_faces_n1.py", "n1_sha16_post"),
]:
    b = open(path, "rb").read()
    sha16 = hashlib.sha256(b).hexdigest()[:16]
    expect = rec[key]
    ok = sha16 == expect
    print(path.split("\\")[-1], "sha16", sha16, "expect", expect, "MATCH" if ok else "MISMATCH")
    if not ok:
        fails.append("sha16 mismatch: " + path)
    try:
        py_compile.compile(path, doraise=True)
        print(path.split("\\")[-1], "py_compile OK")
    except Exception as e:
        fails.append("py_compile fail: %s: %s" % (path, e))

sys.path.insert(0, BASE + r"\scripts")
import perpetual_faces as pf_mod
import perpetual_faces_n1 as n1_mod

# 2) pf N1_BANDS[230] bands == receipt bands (live import, zero-literal)
bands = rec["bands"]
row = dict(pf_mod.N1_BANDS.get(230) or {})
bands_ok = (row.get("a") == (bands["a_lo"], bands["a_hi"])
            and row.get("b_exit") == (bands["b_lo"], bands["b_hi"])
            and row.get("engine_owner") == "bm-c")
print("pf N1_BANDS[230]:", row, "| bands match receipt:", bands_ok)
if not bands_ok:
    fails.append("pf N1_BANDS[230] bands/owner drift vs receipt: %s" % row)

# 3) n1 WAVE_CONFIGS[230] row (live import)
cfg = n1_mod.WAVE_CONFIGS.get(230) or {}
cfg_ok = (bool(cfg) and cfg.get("engine_owner") == "bm-c"
          and cfg.get("a_seed_base") == bands["a_lo"]
          and cfg.get("b_exit_seed_base") == bands["b_lo"]
          and cfg.get("shard_subdir") == "n1_w230"
          and cfg.get("out_name") == "n1_w230_results.json")
print("n1 WAVE_CONFIGS[230] row present:", bool(cfg), "| cfg_ok:", cfg_ok,
      "| a_seed_base:", cfg.get("a_seed_base"), "| b_exit_seed_base:", cfg.get("b_exit_seed_base"))
if not cfg_ok:
    fails.append("n1 WAVE_CONFIGS[230] row drift: %s" % {k: cfg.get(k) for k in ("engine_owner", "a_seed_base", "b_exit_seed_base", "shard_subdir", "out_name")})

# 4) WAVE row census 229/230 = 1/1 shape-correct (both faces)
src_pf = open(BASE + r"\scripts\perpetual_faces.py", encoding="utf-8").read()
src_n1 = open(BASE + r"\scripts\perpetual_faces_n1.py", encoding="utf-8").read()
pat_229_pf = len(re.findall(r"229: \{\"a\"", src_pf))
pat_230_pf = len(re.findall(r"230: \{\"a\"", src_pf))
pat_229_n1 = len(re.findall(r"229: \{\"batch\"", src_n1))
pat_230_n1 = len(re.findall(r"230: \{\"batch\"", src_n1))
print("pf WAVE row 229/230:", pat_229_pf, "/", pat_230_pf, "| n1 WAVE row 229/230:", pat_229_n1, "/", pat_230_n1)
if pat_229_pf != 1 or pat_230_pf != 1 or pat_229_n1 != 1 or pat_230_n1 != 1:
    fails.append("WAVE row census fail (pf 229=%d 230=%d; n1 229=%d 230=%d)" % (pat_229_pf, pat_230_pf, pat_229_n1, pat_230_n1))

# 5) shards n1_w230 12/12 (results/p2cal_ext/n1_w230/)
shd = BASE + r"\results\p2cal_ext\n1_w230"
expect = {"shard-%d-of-12.json" % k for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
print("shards present:", len(expect & files), "/ 12")
if not expect.issubset(files):
    fails.append("shards incomplete: %s" % sorted(expect - files))

# 6) finalize product absent (PRE-FINALIZE phase proof)
fin_absent = not os.path.exists(BASE + r"\results\perpetual_faces\n1_w230_results.json")
print("finalize product n1_w230_results.json absent:", fin_absent)
if not fin_absent:
    fails.append("finalize product ALREADY PRESENT -- phase proof violated")

if fails:
    print("VERIFY-FAIL")
    for f in fails:
        print(" -", f)
    sys.exit(1)
print("VERIFY-PASS")
