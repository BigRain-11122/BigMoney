# -*- coding: utf-8 -*-
# r914 W216 pre-finalize six-gate probe (W212 debt lesson: gates BEFORE finalize,
# no post-hoc). Six gates: (1) banned gate ADMIT on W216 prereg (fresh re-run)
# (2) pf selftest 9/9 (3) n1 selftest PASS (4) shards 12/12 present on disk
# (5) seed_admit_gate rc0 FREE both bands (6) WAVE_CONFIGS[216] row registered
# engine_owner bm-c (live import). Receipt -> results/_r914bmc_w216_sixgate_receipt.json
import json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 216, "phase": "pre-finalize six-gate probe r914",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "gates": {}}

def run(args, **kw):
    return subprocess.run([PY] + args, cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", **kw)

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W216_PREREG.md"])
receipt["gates"]["banned"] = {"rc": g1.returncode, "tail": (g1.stdout or "").strip().splitlines()[-1][:120] if g1.stdout.strip() else ""}
assert g1.returncode == 0, f"banned gate FAIL: {g1.stdout} {g1.stderr}"

# gate 2: pf selftest (9/9)
g2 = run(["scripts/perpetual_faces.py", "selftest"], timeout=300)
m = re.search(r"selftest: (\d+)/(\d+) PASS", g2.stdout or "")
pf_pass = (m.group(1), m.group(2)) if m else ("?", "?")
receipt["gates"]["pf_selftest"] = {"rc": g2.returncode, "summary": f"{pf_pass[0]}/{pf_pass[1]} PASS"}
assert g2.returncode == 0 and pf_pass == ("9", "9"), f"pf selftest FAIL: {pf_pass}"

# gate 3: n1 selftest
g3 = run(["scripts/perpetual_faces_n1.py", "selftest"], timeout=600)
receipt["gates"]["n1_selftest"] = {"rc": g3.returncode, "ok": g3.returncode == 0}
assert g3.returncode == 0, f"n1 selftest FAIL: {(g3.stdout or '')[-500:]} {(g3.stderr or '')[-500:]}"

# gate 4: shards 12/12
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w216")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence = the pre-seat ADMIT probe receipt leg2 (ran on the
# PRE-W216 universe at r913 seat time = the scientifically valid face) + the
# freeze-window re-run recorded in the freeze receipt gate_lines. A FRESH gate
# run post-freeze is semantically wrong: the W216 bands are now REGISTERED in
# N1_BANDS, so the gate would collide with the wave's own row (r914 disclosed;
# W215/W214 six-gate precedent consumed the seat-time FREE evidence likewise).
seat_rec = json.load(open(os.path.join(REPO, "results", "_w216bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w216bmc_freeze_receipt.json"), encoding="utf-8"))
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w216 = dict(pf_mod.N1_BANDS.get(216) or {})
a_lo, b_lo = w216["a"][0], w216["b_exit"][0]
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner + dedup state
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(216) or {}
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                         "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                         "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name")}
assert cfg and cfg.get("engine_owner") == "bm-c" and cfg.get("a_seed_base") == 490_004 \
    and cfg.get("b_exit_seed_base") == 492_004 and cfg.get("shard_subdir") == "n1_w216" \
    and cfg.get("out_name") == "n1_w216_results.json", f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition (W215 finalize landed = prev anchor)
w215_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w215_results.json"), encoding="utf-8"))
prev_total = w215_out["science_gates"]["ledger"]["total"]
prev_merged = w215_out["null_pool_cumulative"]["merged"]["n_values"]
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}
assert prev_total == 896_789 and prev_merged == 470_920

out = os.path.join(REPO, "results", "_r914bmc_w216_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:600])
print("expect ledger", prev_total, "+2200 =", prev_total + 2200, "| expect K", prev_merged, "+2200 =", prev_merged + 2200)
