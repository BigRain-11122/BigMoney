# -*- coding: utf-8 -*-
# r934 bm-c: W223 six-gate probe -- PRE-FINALIZE in the burn window.
# Standing law = six-gate must run PRE-FINALIZE (W218/W219/W220/W221 clean
# chain; W222 = burn-window miss #5 healed at absorb r932). This window
# runs the gate at the CORRECT phase: splice landed 17:4x (448c4d8c2 pushed),
# engine mtime-watch self-burn in flight (ledger append 7b4236f85 6 shards
# at script-write time), gate fires before finalize one-pass.
# Gates: (0) splice integrity = N1_BANDS[223] bands facts == freeze receipt
#         + pf whole-file sha16 NOW == freeze receipt post value; n1 sha16
#         NOW != freeze post BY THIS WINDOW'S REPAIR, disclosed below
# (1) banned gate ADMIT on W223 prereg (fresh re-run)
# (2) pf selftest 9/9 (3) n1 selftest PASS (4) shards 12/12 present on disk
# (5) seed_admit evidence = seat-time FREE x2 + freeze-time FREE x2
# (6) WAVE_CONFIGS[223] row registered engine_owner bm-c (live import)
# + ledger_pre derived PROGRAMMATICALLY from n1_w222_results.json
# (r583 zero-literal law). Receipt -> results/_r934bmc_w223_sixgate_receipt.json
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 223,
           "phase": "PRE-FINALIZE six-gate at r934 burn window (correct phase per W217+ standing law; splice 448c4d8c2 pushed 17:4x, engine self-burn in flight; W222 was burn-window miss #5 healed at absorb r932)",
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

# gate 0: splice integrity -- N1_BANDS[223] bands facts == freeze receipt;
# pf whole-file sha16 NOW must EQUAL freeze receipt post value (clean splice).
# (0b) r934 window REPAIR disclosed: n1 selftest W223 face LHS boundary
# w<222 was a stale template face (editor r931-snapshot lineage: n1 W222
# section had been bound-repaired at r932 but the fix does not backflow
# into the editor template, so the derive inherited the pre-repair bound)
# while RHS said range(16,223) -- atomic-pair violation family #5
# (r923 x2 + r928 x1 + r932 x1 + this); fixed LHS+comment together,
# zero scientific fields (bands/N/criteria untouched); n1_sha16 NOW !=
# freeze post BY THIS REPAIR, r928/r932 pattern.
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w223bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w223_row = dict(pf_mod.N1_BANDS.get(223) or {})
bands_ok = (w223_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w223_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w223_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "repair_note": "n1 selftest W223 LHS boundary repair at r934 burn window (w<222 -> w<223 + comment, atomic pair; family #5 stale-template-copy, r923/r928/r932 lineage; derive inherited the pre-r932-repair editor snapshot face, fix does not backflow into editor templates): n1_sha16_now != n1_sha16_freeze_post BY THIS REPAIR, zero scientific fields -- bands/N/criteria unchanged, engine burn consumed the bands face, unaffected; pf file UNREPAIRED (sha16 equality asserted)"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"], \
    f"splice integrity FAIL: bands {w223_row} vs receipt {freeze_rec['bands']}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W223_PREREG.md"])
receipt["gates"]["banned"] = {"rc": g1.returncode, "tail": (g1.stdout or "").strip().splitlines()[-1][:120] if g1.stdout.strip() else ""}
assert g1.returncode == 0, f"banned gate FAIL: {g1.stdout} {g1.stderr}"

# gate 2: pf selftest (9/9)
g2 = run(["scripts/perpetual_faces.py", "selftest"], timeout=300)
m = re.search(r"selftest: (\d+)/(\d+) PASS", g2.stdout or "")
pf_pass = (m.group(1), m.group(2)) if m else ("?", "?")
receipt["gates"]["pf_selftest"] = {"rc": g2.returncode, "summary": f"{pf_pass[0]}/{pf_pass[1]} PASS"}
assert g2.returncode == 0 and pf_pass == ("9", "9"), f"pf selftest FAIL: {pf_pass}"

# gate 3: n1 selftest
g3 = run(["scripts/perpetual_faces_n1.py", "selftest"], timeout=900)
receipt["gates"]["n1_selftest"] = {"rc": g3.returncode, "ok": g3.returncode == 0}
assert g3.returncode == 0, f"n1 selftest FAIL: {(g3.stdout or '')[-500:]} {(g3.stderr or '')[-500:]}"

# gate 4: shards 12/12
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w223")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence = seat-time ADMIT probe receipt leg2 (ran on the
# PRE-W223 universe at r932 seat time = the scientifically valid face) + the
# freeze-window re-run recorded in the freeze receipt. A FRESH gate run
# post-freeze is semantically wrong: the W223 bands are now REGISTERED in
# N1_BANDS, so the gate would collide with the wave's own row (r914 disclosed;
# W215..W223 six-gate precedent consumed the seat-time FREE evidence likewise).
seat_rec = json.load(open(os.path.join(REPO, "results", "_w223bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(223) or {}
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name")}
assert cfg and cfg.get("engine_owner") == "bm-c" and cfg.get("a_seed_base") == 505_404 \
    and cfg.get("b_exit_seed_base") == 507_404 and cfg.get("shard_subdir") == "n1_w223" \
    and cfg.get("out_name") == "n1_w223_results.json", f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition (W222 finalize landed = prev anchor) -- derived
# PROGRAMMATICALLY from n1_w222_results.json (r583 zero-literal law), with
# the +2,200 per-wave N identity asserted (A 2,000 + B 200, frozen v1 design).
w222_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w222_results.json"), encoding="utf-8"))
prev_total = w222_out["science_gates"]["ledger"]["total"]
prev_merged = w222_out["null_pool_cumulative"]["merged"]["n_values"]
assert w222_out["science_gates"]["ledger"]["prev_total"] + w222_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W222 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}

out = os.path.join(REPO, "results", "_r934bmc_w223_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN (W223, r934 burn window, correct phase)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("expect ledger", prev_total, "+2200 =", prev_total + 2200, "| expect K", prev_merged, "+2200 =", prev_merged + 2200)
