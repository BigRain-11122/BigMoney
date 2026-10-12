# -*- coding: utf-8 -*-
# r944 bm-c: W226 six-gate probe -- POST-FINALIZE HEAL (disclosed phase miss).
# W217+ standing law requires PRE-FINALIZE firing; the r943 dead window ran
# splice (committed 9b44d37d1) + engine self-burn 12/12 + finalize one-pass
# (n1_w226_results.json 22:41:33) but died BEFORE the six-gate receipt --
# W212-pattern recurrence #3 (W217-debt law family). This heal run verifies
# ALL six gates post-hoc on the landed faces + additionally asserts the
# finalize product ledger/K identities against the pre-wave anchors.
# W227 MUST fire pre-finalize (standing law; next window first action).
# Gates: (0) splice integrity both faces + family-6 triple (wave 226)
# (1) banned gate ADMIT (2) pf selftest 9/9 (3) n1 selftest
# (4) shards 12/12 (5) seed_admit seat-time+freeze-time FREE x2
# (6) WAVE_CONFIGS[226] row engine_owner bm-c (live import)
# (7 post-hoc) finalize product identity: ledger 918,789+2,200 EXACT +
# K 492,920+2,200 EXACT vs n1_w225_results.json anchors (r583 zero-literal).
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 226,
           "phase": "POST-FINALIZE six-gate heal (r944 window; W212-pattern recurrence #3 disclosed -- r943 dead window landed splice 9b44d37d1 + engine self-burn 12/12 + finalize 22:41:33 but died pre-six-gate; healed post-hoc per r917 precedent; W227 must run PRE-FINALIZE)",
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

# gate 0: splice integrity (BOTH faces clean-equal vs freeze receipt)
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w226bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w226_row = dict(pf_mod.N1_BANDS.get(226) or {})
bands_ok = (w226_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w226_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w226_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
n1_text = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), encoding="utf-8").read()
triple_ok = (n1_text.count("if w < 226)") == 3
             and n1_text.count("range(16, 226)") == 1
             and n1_text.count("range(17, 226)") == 1
             and n1_text.count("registered wave below 226 composes") == 1)
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "family6_triple_wholefile_recheck": triple_ok,
    "repair_note": "NO repair expected: family #6 triple carried atomically in the r943 splice; both sha16 faces asserted clean-equal"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"] and n1_now == freeze_rec["n1_sha16_post"] and triple_ok, \
    f"splice integrity FAIL: bands {w226_row}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}; n1 {n1_now} vs {freeze_rec['n1_sha16_post']}; triple {triple_ok}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W226_PREREG.md"])
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
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w226")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence (seat-time FREE x2 + freeze-time FREE x2)
seat_rec = json.load(open(os.path.join(REPO, "results", "_w226bmc_20261012_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner; seed bases derived
# from freeze receipt bands (zero-literal law)
sys.path.insert(0, os.path.join(REPO, "research"))
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(226) or {}
cfg_ok = (bool(cfg) and cfg.get("engine_owner") == "bm-c"
          and cfg.get("a_seed_base") == freeze_rec["bands"]["a_lo"]
          and cfg.get("b_exit_seed_base") == freeze_rec["bands"]["b_lo"]
          and cfg.get("shard_subdir") == "n1_w226"
          and cfg.get("out_name") == "n1_w226_results.json")
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name"),
                                        "seed_bases_match_freeze_bands": cfg_ok}
assert cfg_ok, f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition derived from n1_w225_results.json (zero-literal)
w225_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w225_results.json"), encoding="utf-8"))
prev_total = w225_out["science_gates"]["ledger"]["total"]
prev_merged = w225_out["null_pool_cumulative"]["merged"]["n_values"]
assert w225_out["science_gates"]["ledger"]["prev_total"] + w225_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W225 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}

# gate 7 (post-hoc heal addition): finalize product identities vs anchors
w226_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w226_results.json"), encoding="utf-8"))
sg226 = w226_out["science_gates"]["ledger"]
merged_n226 = w226_out["null_pool_cumulative"]["merged"]["n_values"]
ident_total = sg226["prev_total"] + sg226["batch_trials"] == sg226["total"]
ident_anchor = (sg226["prev_total"] == prev_total and sg226["total"] == prev_total + 2200
                and merged_n226 == prev_merged + 2200)
receipt["gates"]["finalize_identity_posthoc"] = {
    "ledger_prev": sg226["prev_total"], "ledger_batch": sg226["batch_trials"], "ledger_total": sg226["total"],
    "merged_n": merged_n226, "identity_assert": ident_total and ident_anchor,
    "note": "post-hoc verification of the dead-window finalize product against pre-wave anchors"}
assert ident_total and ident_anchor, f"finalize identity FAIL: {sg226} / merged {merged_n226} vs anchors {prev_total}/{prev_merged}"

out = os.path.join(REPO, "results", "_r944bmc_w226_sixgate_receipt.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE POST-FINALIZE HEAL ALL GREEN (W226, r944 window, phase miss disclosed, W227 must fire PRE-FINALIZE)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("ledger", prev_total, "+2200 =", sg226["total"], "| K", prev_merged, "+2200 =", merged_n226)
