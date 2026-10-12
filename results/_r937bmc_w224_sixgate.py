# -*- coding: utf-8 -*-
# r937 bm-c: W224 six-gate probe -- PRE-FINALIZE at the correct phase
# (standing law W217+; W219/W220/W221/W222/W223 clean chain, 5 consecutive).
# This window: splice executed on disk by dead-session r937 (18:56, receipt
# _w224bmc_freeze_receipt.json, never committed -- absorb window lands it),
# engine mtime-watch self-burned 12/12 (ledger appends 7ae27e58b + 9ad2edbf5
# self-committed 18:58/19:01), gate fires before finalize one-pass.
# Gates: (0) splice integrity = N1_BANDS[224] bands facts == freeze receipt
#         + pf whole-file sha16 NOW == freeze receipt post value (clean splice);
#         n1 sha16 NOW != freeze post BY THIS WINDOW'S REPAIR, disclosed:
#         n1 selftest W224 set-derivation LHS bound `w < 223` was not bumped
#         with the RHS range(16, 224) by the r937 dead-session editor
#         (atomic-pair violation family #6: r923 x2 + r928 x1 + r932 x1 +
#         r934 x1 + this); fixed LHS w<223 -> w<224 + comment line together,
#         zero scientific fields (bands/N/criteria untouched)
# (1) banned gate ADMIT on W224 prereg (fresh re-run)
# (2) pf selftest 9/9 (3) n1 selftest PASS (4) shards 12/12 present on disk
# (5) seed_admit evidence = seat-time FREE x2 + freeze-time FREE x2
# (6) WAVE_CONFIGS[224] row registered engine_owner bm-c (live import)
# + ledger_pre derived PROGRAMMATICALLY from n1_w223_results.json
# (r583 zero-literal law). Receipt -> results/_r937bmc_w224_sixgate_receipt.json
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 224,
           "phase": "PRE-FINALIZE six-gate at r937 absorb window (correct phase per W217+ standing law; splice executed 18:56 dead-session estate landed this window; engine self-burn 12/12 complete; correct-phase chain W218/W219/W220/W221 + W223, W222 = burn-window miss #5 post-hoc healed -- this wave extends the post-miss correct-phase run to 2)",
           "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "gates": {}}

def run(args, **kw):
    return subprocess.run([PY] + args, cwd=REPO, capture_output=True,
                          text=True, encoding="utf-8", errors="replace", **kw)

def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

# gate 0: splice integrity
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w224bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w224_row = dict(pf_mod.N1_BANDS.get(224) or {})
bands_ok = (w224_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w224_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w224_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "repair_note": "n1 selftest W224 set-derivation LHS bound repair at r937 absorb window (w<223 -> w<224 + comment, atomic pair; family #6 stale-editor-face, r923/r928/r932/r934 lineage; the r937 dead-session editor bumped RHS range(16,223)->range(16,224) and the W2..W223 comment but left the LHS w<223 stale): n1_sha16_now != n1_sha16_freeze_post BY THIS REPAIR, zero scientific fields -- bands/N/criteria unchanged, engine burn consumed the bands face, unaffected; pf file UNREPAIRED (sha16 equality asserted)"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"], \
    f"splice integrity FAIL: bands {w224_row} vs receipt {freeze_rec['bands']}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W224_PREREG.md"])
receipt["gates"]["banned"] = {"rc": g1.returncode, "tail": (g1.stdout or "").strip().splitlines()[-1][:120] if g1.stdout.strip() else ""}
assert g1.returncode == 0, f"banned gate FAIL: {g1.stdout} {g1.stderr}"

# gate 2: pf selftest (9/9)
g2 = run(["scripts/perpetual_faces.py", "selftest"], timeout=300)
m = re.search(r"selftest: (\d+)/(\d+) PASS", g2.stdout or "")
pf_pass = (m.group(1), m.group(2)) if m else ("?", "?")
receipt["gates"]["pf_selftest"] = {"rc": g2.returncode, "summary": f"{pf_pass[0]}/{pf_pass[1]} PASS"}
assert g2.returncode == 0 and pf_pass == ("9", "9"), f"pf selftest FAIL: {pf_pass}"

# gate 3: n1 selftest (post-repair PASS consumed this window; re-run for receipt)
g3 = run(["scripts/perpetual_faces_n1.py", "selftest"], timeout=900)
receipt["gates"]["n1_selftest"] = {"rc": g3.returncode, "ok": g3.returncode == 0}
assert g3.returncode == 0, f"n1 selftest FAIL: {(g3.stdout or '')[-500:]} {(g3.stderr or '')[-500:]}"

# gate 4: shards 12/12
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w224")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence (seat-time + freeze-time FREE x2; post-freeze
# fresh gate run semantically wrong: W224 bands now REGISTERED in N1_BANDS
# would collide with the wave's own row -- r914 disclosed, W215..W224
# six-gate precedent consumed the seat-time FREE evidence likewise)
seat_rec = json.load(open(os.path.join(REPO, "results", "_w224bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(224) or {}
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name")}
assert cfg and cfg.get("engine_owner") == "bm-c" and cfg.get("a_seed_base") == 507_604 \
    and cfg.get("b_exit_seed_base") == 509_604 and cfg.get("shard_subdir") == "n1_w224" \
    and cfg.get("out_name") == "n1_w224_results.json", f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition (W223 finalize landed = prev anchor) -- derived
# PROGRAMMATICALLY from n1_w223_results.json (r583 zero-literal law), with
# the +2,200 per-wave N identity asserted (A 2,000 + B 200, frozen v1 design).
w223_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w223_results.json"), encoding="utf-8"))
prev_total = w223_out["science_gates"]["ledger"]["total"]
prev_merged = w223_out["null_pool_cumulative"]["merged"]["n_values"]
assert w223_out["science_gates"]["ledger"]["prev_total"] + w223_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W223 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}

out = os.path.join(REPO, "results", "_r937bmc_w224_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN (W224, r937 absorb window, correct phase)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("expect ledger", prev_total, "+2200 =", prev_total + 2200, "| expect K", prev_merged, "+2200 =", prev_merged + 2200)
