# -*- coding: utf-8 -*-
# r939 bm-c: W225 six-gate probe -- PRE-FINALIZE at the correct phase
# (standing law W217+; W219/W220/W221/W222/W223 clean + W224 = post-miss
# correct-phase run 2; this wave = run 3 consecutive).
# This window: splice executed + committed by THIS session (84ecb3a3a,
# receipt _w225bmc_freeze_receipt.json), engine mtime-watch self-burn 12/12,
# gate fires BEFORE finalize one-pass (standing law).
# Gates: (0) splice integrity = N1_BANDS[225] bands facts == freeze receipt
#         + pf whole-file sha16 NOW == freeze receipt post value AND n1
#         whole-file sha16 NOW == freeze receipt post value -- CLEAN
#         equality on BOTH faces this window (family #6 LHS/RHS/comment
#         atomic triple was absorbed INTO the r939 editor derive, so no
#         post-hoc repair is expected or disclosed; whole-file re-check:
#         the new W225 block carries 'if w < 225)' x3 + range(16,225) +
#         range(17,225) + below-225 comment atomically)
# (1) banned gate ADMIT on W225 prereg (fresh re-run)
# (2) pf selftest 9/9 (3) n1 selftest PASS (4) shards 12/12 present on disk
# (5) seed_admit evidence = seat-time FREE x2 + freeze-time FREE x2
# (6) WAVE_CONFIGS[225] row registered engine_owner bm-c (live import)
# + ledger_pre derived PROGRAMMATICALLY from n1_w224_results.json
# (r583 zero-literal law). Receipt -> results/_r939bmc_w225_sixgate_receipt.json
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 225,
           "phase": "PRE-FINALIZE six-gate at r939 window (correct phase per W217+ standing law; splice executed+committed this window 84ecb3a3a; engine self-burn 12/12 complete; correct-phase chain W218..W224 post-miss run 2 -> this wave extends it to run 3 consecutive)",
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

# gate 0: splice integrity (BOTH faces clean-equal; family-6 triple absorbed at derive time)
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w225bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w225_row = dict(pf_mod.N1_BANDS.get(225) or {})
bands_ok = (w225_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w225_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w225_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
n1_text = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), encoding="utf-8").read()
triple_ok = (n1_text.count("if w < 225)") == 3
             and n1_text.count("range(16, 225)") == 1
             and n1_text.count("range(17, 225)") == 1
             and n1_text.count("registered wave below 225 composes") == 1)
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "family6_triple_wholefile_recheck": triple_ok,
    "repair_note": "NO repair this window: family #6 LHS/RHS/comment atomic triple absorbed into the r939 editor derive (W224 sec.8 upgrade proposal executed); BOTH pf and n1 sha16 clean-equal to freeze receipt post values asserted (W224-window repair precedent not needed)"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"] and n1_now == freeze_rec["n1_sha16_post"] and triple_ok, \
    f"splice integrity FAIL: bands {w225_row} vs receipt {freeze_rec['bands']}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}; n1 {n1_now} vs {freeze_rec['n1_sha16_post']}; triple {triple_ok}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W225_PREREG.md"])
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
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w225")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence (seat-time + freeze-time FREE x2; post-freeze
# fresh gate run semantically wrong: W225 bands now REGISTERED in N1_BANDS
# would collide with the wave's own row -- r914 disclosed, W215..W224
# six-gate precedent consumed the seat-time FREE evidence likewise)
seat_rec = json.load(open(os.path.join(REPO, "results", "_w225bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(225) or {}
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name")}
assert cfg and cfg.get("engine_owner") == "bm-c" and cfg.get("a_seed_base") == 509_804 \
    and cfg.get("b_exit_seed_base") == 511_804 and cfg.get("shard_subdir") == "n1_w225" \
    and cfg.get("out_name") == "n1_w225_results.json", f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition (W224 finalize landed = prev anchor) -- derived
# PROGRAMMATICALLY from n1_w224_results.json (r583 zero-literal law), with
# the +2,200 per-wave N identity asserted (A 2,000 + B 200, frozen v1 design).
w224_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w224_results.json"), encoding="utf-8"))
prev_total = w224_out["science_gates"]["ledger"]["total"]
prev_merged = w224_out["null_pool_cumulative"]["merged"]["n_values"]
assert w224_out["science_gates"]["ledger"]["prev_total"] + w224_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W224 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}

out = os.path.join(REPO, "results", "_r939bmc_w225_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN (W225, r939 window, correct phase, run 3 consecutive)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("expect ledger", prev_total, "+2200 =", prev_total + 2200, "| expect K", prev_merged, "+2200 =", prev_merged + 2200)
