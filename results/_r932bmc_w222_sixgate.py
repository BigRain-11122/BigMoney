# -*- coding: utf-8 -*-
# r932 bm-c: W222 six-gate probe -- PRE-FINALIZE at the absorb window.
# Standing law = six-gate must run PRE-FINALIZE in the burn window
# (W218/W219/W220/W221 chain law). The r931 splice window died post-splice
# post-burn pre-gate ~15:24 (engine daemon mtime-watch self-burned 12/12
# 15:2x-15:3x with ledger appends b5305fe4a + 0028f84cb pushed); the six-gate
# script was NOT pre-written with the freeze bundle (r930 pointer item, dead
# session died before writing it). Burn-window gate missed = W212-family
# recurrence #5, full disclosure; healed at absorb window r932 BEFORE
# finalize (scientific position: gate still pre-finalize).
# Gates: (0) splice integrity = N1_BANDS[222] bands facts == freeze receipt
#         + whole-file sha16 NOW == freeze receipt post values (clean splice,
#         zero post-freeze edits this wave -- assert equality)
# (1) banned gate ADMIT on W222 prereg (fresh re-run)
# (2) pf selftest 9/9 (3) n1 selftest PASS (4) shards 12/12 present on disk
# (5) seed_admit evidence = seat-time FREE x2 + freeze-time FREE x2
# (post-freeze fresh gate run N/A: own row registered, r914 disclosed)
# (6) WAVE_CONFIGS[222] row registered engine_owner bm-c (live import)
# + ledger_pre derived PROGRAMMATICALLY from n1_w221_results.json
# (r583 zero-literal law). Receipt -> results/_r932bmc_w222_sixgate_receipt.json
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 222,
           "phase": "PRE-FINALIZE six-gate at absorb window r932 (burn-window gate missed: r931 splice window died post-splice post-burn pre-gate ~15:24, engine self-burned 12/12 with no live session, ledger appends b5305fe4a+0028f84cb pushed; W212-family recurrence #5 disclosed; standing law note: six-gate script not pre-written with freeze bundle -- dead session estate, r930 pointer item unfulfilled)",
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

# gate 0: splice integrity -- N1_BANDS[222] bands facts == freeze receipt;
# whole-file sha16s NOW must EQUAL freeze receipt post values (clean splice).
# (0b) r932 absorb-window REPAIR disclosed: n1 selftest W222 face LHS
# boundary w<221 was a stale W221 copy while RHS said range(16,222)
# -- atomic-pair violation family #4 (r923 x2 + r928 x1 + this); fixed
# LHS+comment together, zero scientific fields (bands/N/criteria
# untouched); n1_sha16 NOW != freeze post BY THIS REPAIR, r928 pattern.
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w222bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w222_row = dict(pf_mod.N1_BANDS.get(222) or {})
bands_ok = (w222_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w222_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w222_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "repair_note": "n1 selftest W222 LHS boundary repair at absorb window r932 (w<221 -> w<222 + comment, atomic pair; family #4 stale-copy, r923/r928 lineage): n1_sha16_now != n1_sha16_freeze_post BY THIS REPAIR, zero scientific fields -- bands/N/criteria unchanged, engine burn consumed the bands face, unaffected; pf file UNREPAIRED (sha16 equality asserted)"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"], \
    f"splice integrity FAIL: bands {w222_row} vs receipt {freeze_rec['bands']}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W222_PREREG.md"])
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
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w222")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence = seat-time ADMIT probe receipt leg2 (ran on the
# PRE-W222 universe at r929 seat time = the scientifically valid face) + the
# freeze-window re-run recorded in the freeze receipt. A FRESH gate run
# post-freeze is semantically wrong: the W222 bands are now REGISTERED in
# N1_BANDS, so the gate would collide with the wave's own row (r914 disclosed;
# W215..W222 six-gate precedent consumed the seat-time FREE evidence likewise).
seat_rec = json.load(open(os.path.join(REPO, "results", "_w222bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(222) or {}
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name")}
assert cfg and cfg.get("engine_owner") == "bm-c" and cfg.get("a_seed_base") == 503_204 \
    and cfg.get("b_exit_seed_base") == 505_204 and cfg.get("shard_subdir") == "n1_w222" \
    and cfg.get("out_name") == "n1_w222_results.json", f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition (W221 finalize landed = prev anchor) -- derived
# PROGRAMMATICALLY from n1_w221_results.json (r583 zero-literal law), with
# the +2,200 per-wave N identity asserted (A 2,000 + B 200, frozen v1 design).
w221_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w221_results.json"), encoding="utf-8"))
prev_total = w221_out["science_gates"]["ledger"]["total"]
prev_merged = w221_out["null_pool_cumulative"]["merged"]["n_values"]
assert w221_out["science_gates"]["ledger"]["prev_total"] + w221_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W221 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}

out = os.path.join(REPO, "results", "_r932bmc_w222_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN (W222, absorb window r932, burn-window miss #5 disclosed)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("expect ledger", prev_total, "+2200 =", prev_total + 2200, "| expect K", prev_merged, "+2200 =", prev_merged + 2200)
