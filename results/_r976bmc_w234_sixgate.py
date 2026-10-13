# -*- coding: utf-8 -*-
# r976 bm-c absorb window: W234 six-gate probe -- PRE-FINALIZE (correct phase).
# W217+ standing law: the six-gate fires BEFORE finalize. W222/W225/W226/W227/
# W228/W229/W230/W231/W232/W233 fired pre-finalize correctly; THIS is the W234
# cycle firing PRE-FINALIZE on schedule (shards 12/12 landed via engine
# self-burn batched appends 39f7b8b0c+5022491bc+cbe25f1a4 absorb-tail,
# finalize NOT yet run -- correct phase face; splice estate landed de342250c
# pre-gate, prereg 252d5cc95 research/PERPETUAL_N1_W234_PREREG.md).
# Gates: (0) splice integrity both faces + family-6 triple (wave 234)
# (1) banned gate ADMIT (2) pf selftest 9/9 (3) n1 selftest
# (4) shards 12/12 (5) seed_admit seat-time+freeze-time FREE x2
# (6) WAVE_CONFIGS[234] row engine_owner bm-c (live import)
# precondition: ledger head + merged pool derived from n1_w233_results.json
# (zero-literal law) -- the finalize product will be identity-asserted against
# these anchors by the five-key probe after finalize.
import hashlib, json, os, re, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8")
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable
receipt = {"machine": "bm-c", "wave": 234,
           "phase": "PRE-FINALIZE six-gate (r976 absorb window; W217+ standing law executed on schedule -- shards 12/12 landed via engine self-burn 39f7b8b0c+5022491bc+cbe25f1a4, finalize not yet run, splice estate landed de342250c pre-gate, prereg 252d5cc95)",
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
freeze_rec = json.load(open(os.path.join(REPO, "results", "_w234bmc_freeze_receipt.json"), encoding="utf-8"))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf_mod
w234_row = dict(pf_mod.N1_BANDS.get(234) or {})
bands_ok = (w234_row.get("a") == (freeze_rec["bands"]["a_lo"], freeze_rec["bands"]["a_hi"])
            and w234_row.get("b_exit") == (freeze_rec["bands"]["b_lo"], freeze_rec["bands"]["b_hi"])
            and w234_row.get("engine_owner") == "bm-c")
pf_now, n1_now = sha16(os.path.join(REPO, "scripts", "perpetual_faces.py")), sha16(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"))
n1_text = open(os.path.join(REPO, "scripts", "perpetual_faces_n1.py"), encoding="utf-8").read()
triple_ok = (n1_text.count("if w < 234)") == 3
             and n1_text.count("range(16, 234)") == 1
             and n1_text.count("range(17, 234)") == 1
             and n1_text.count("registered wave below 234 composes") == 1)
prior_boundary_ok = (n1_text.count("if w < 233)") == 3
                     and n1_text.count("range(16, 233)") == 1)
receipt["gates"]["splice_integrity"] = {
    "bands_facts_match_freeze_receipt": bands_ok,
    "pf_sha16_now": pf_now, "n1_sha16_now": n1_now,
    "pf_sha16_freeze_post": freeze_rec["pf_sha16_post"], "n1_sha16_freeze_post": freeze_rec["n1_sha16_post"],
    "family6_triple_wholefile_recheck": triple_ok,
    "prior_wave_233_boundary_kept": prior_boundary_ok,
    "repair_note": "NO repair expected: family #6 triple carried atomically in the splice; both sha16 faces asserted clean-equal"}
assert bands_ok and pf_now == freeze_rec["pf_sha16_post"] and n1_now == freeze_rec["n1_sha16_post"] and triple_ok and prior_boundary_ok, \
    f"splice integrity FAIL: bands {w234_row}; pf {pf_now} vs {freeze_rec['pf_sha16_post']}; n1 {n1_now} vs {freeze_rec['n1_sha16_post']}; triple {triple_ok}; prior {prior_boundary_ok}"

# gate 1: banned gate
g1 = run(["Tools/banned_direction_gate.py", "--prereg", "research/PERPETUAL_N1_W234_PREREG.md"])
receipt["gates"]["banned"] = {"rc": g1.returncode, "tail": (g1.stdout or "").strip().splitlines()[-1][:120] if g1.stdout.strip() else ""}
assert g1.returncode == 0, f"banned gate FAIL: {g1.stdout} {g1.stderr}"

# gate 2: pf selftest (9/9)
g2 = run(["scripts/perpetual_faces.py", "selftest"], timeout=300)
m = re.search(r"selftest: (\d+)/(\d+) PASS", g2.stdout or "")
pf_pass = (m.group(1), m.group(2)) if m else ("?", "?")
receipt["gates"]["pf_selftest"] = {"rc": g2.returncode, "summary": f"{pf_pass[0]}/{pf_pass[1]} PASS"}
assert g2.returncode == 0 and pf_pass == ("9", "9"), f"pf selftest FAIL: {pf_pass}"

# gate 3: n1 selftest
g3 = run(["scripts/perpetual_faces_n1.py", "selftest"], timeout=1200)
receipt["gates"]["n1_selftest"] = {"rc": g3.returncode, "ok": g3.returncode == 0}
assert g3.returncode == 0, f"n1 selftest FAIL: {(g3.stdout or '')[-500:]} {(g3.stderr or '')[-500:]}"

# gate 4: shards 12/12
shd = os.path.join(REPO, "results", "p2cal_ext", "n1_w234")
expect = {f"shard-{k}-of-12.json" for k in range(12)}
files = set(os.listdir(shd)) if os.path.isdir(shd) else set()
receipt["gates"]["shards"] = {"present": len(expect & files), "of": 12}
assert expect.issubset(files), f"shards incomplete: {sorted(expect - files)}"

# gate 5: seed_admit evidence (seat-time FREE x2 + freeze-time FREE x2)
seat_rec = json.load(open(os.path.join(REPO, "results", "_w234bmc_20261013_probe_receipt.json"), encoding="utf-8"))
leg2 = seat_rec["legs"]["leg2"]["seed_admit_gate"]
assert len(leg2) == 2 and all("verdict=FREE" in s and "rc0" in s for s in leg2), f"ADMIT receipt leg2 not FREE x2: {leg2}"
fseeds = freeze_rec.get("seed_admit_gate") or []
assert len(fseeds) == 2 and all("FREE" in s for s in fseeds), f"freeze receipt gate_lines not FREE x2: {fseeds}"
receipt["gates"]["seed_admit"] = {"seat_receipt_leg2": leg2, "freeze_gate_lines": fseeds,
                                  "note": "post-freeze fresh gate run N/A (own row registered); seat-time + freeze-time FREE evidence consumed"}

# gate 6: WAVE_CONFIGS row (n1 import) + engine_owner; seed bases derived
# from freeze receipt bands (zero-literal law)
import perpetual_faces_n1 as n1_mod
cfg = n1_mod.WAVE_CONFIGS.get(234) or {}
cfg_ok = (bool(cfg) and cfg.get("engine_owner") == "bm-c"
          and cfg.get("a_seed_base") == freeze_rec["bands"]["a_lo"]
          and cfg.get("b_exit_seed_base") == freeze_rec["bands"]["b_lo"]
          and cfg.get("shard_subdir") == "n1_w234"
          and cfg.get("out_name") == "n1_w234_results.json")
receipt["gates"]["wave_configs_row"] = {"present": bool(cfg), "engine_owner": cfg.get("engine_owner"),
                                        "a_seed_base": cfg.get("a_seed_base"), "b_exit_seed_base": cfg.get("b_exit_seed_base"),
                                        "shard_subdir": cfg.get("shard_subdir"), "out_name": cfg.get("out_name"),
                                        "seed_bases_match_freeze_bands": cfg_ok}
assert cfg_ok, f"WAVE_CONFIGS row drift: {cfg}"

# ledger head precondition derived from n1_w233_results.json (zero-literal)
w233_out = json.load(open(os.path.join(REPO, "results", "perpetual_faces", "n1_w233_results.json"), encoding="utf-8"))
prev_total = w233_out["science_gates"]["ledger"]["total"]
prev_merged = w233_out["null_pool_cumulative"]["merged"]["n_values"]
assert w233_out["science_gates"]["ledger"]["prev_total"] + w233_out["science_gates"]["ledger"]["batch_trials"] == prev_total, \
    "W233 ledger identity assert failed on derive"
receipt["ledger_pre"] = {"prev_total": prev_total, "prev_merged_n": prev_merged,
                         "expect_total": prev_total + 2200, "expect_merged": prev_merged + 2200}
# finalize product must NOT exist yet (correct-phase proof)
assert not os.path.exists(os.path.join(REPO, "results", "perpetual_faces", "n1_w234_results.json")), \
    "finalize product already exists at six-gate time -- phase face broken (not PRE-FINALIZE); honest re-derive required"

out = os.path.join(REPO, "results", "_r976bmc_w234_sixgate_prereg.json")
open(out, "w", encoding="utf-8").write(json.dumps(receipt, indent=1, ensure_ascii=False))
print("SIX-GATE PRE-FINALIZE ALL GREEN (W234, r976 absorb window, correct phase on schedule -- standing law executed, ninth consecutive)")
print(json.dumps(receipt["gates"], ensure_ascii=False)[:700])
print("ledger pre:", prev_total, "+2200 =>", prev_total + 2200, "| K pre:", prev_merged, "+2200 =>", prev_merged + 2200)
