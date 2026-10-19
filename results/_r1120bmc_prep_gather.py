# -*- coding: utf-8 -*-
# r1120 bm-c: W279 prereg PREP facts gather (r1115 recipe one-generation roll).
# Machine-freezes ALL W279 derive anchors into results/_w279bmc_prep_facts.json -- zero hand
# transcription: every git value read live via subprocess, every number read from the
# fivekeys/results/receipt jsons (r587 live-read law; r1077 measured law for the floors is the
# builder's own SIM duty at derive time, NOT this prep's).
import io, os, json, hashlib, subprocess, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git_out(args):
    r = subprocess.run(["git"] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("GIT FAIL %r: %s" % (args, r.stderr[:200]))
    return r.stdout.strip()

# --- chain commits (W278 cycle, machine-read) ---
FREEZE = "df1aaba72a"           # W278 prereg freeze (r1116, PRE-backfill face per r1049/r1052)
SPLICE = "b6f486af35"            # W278 five-face freeze splice (r1118)
BATCH1 = "60e630918f"            # W278 engine self-burn batch 1 (six shards)
BATCH2 = "b965e2ecf0"            # W278 engine self-burn batch 2 (six shards)
SEAT   = "900c23fe7d"            # W279 seat publish (r1119)
for sha in (FREEZE, SPLICE, BATCH1, BATCH2, SEAT):
    git_out(["cat-file", "-e", sha + "^{commit}"])

# finalize estate = the commit that landed n1_w278_results.json (machine-queried, not assumed)
FIN = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w278_results.json"])
assert FIN == "0a92fcc28f", "W278 finalize product landed by unexpected commit: %s" % FIN

_sp_ci = git_out(["show", "-s", "--format=%ci", SPLICE])   # 2026-10-19 13:53:19 +0800
_m = re.match(r"2026-10-19 13:(\d{2})", _sp_ci)
assert _m, "splice commit ts unexpected: %r" % _sp_ci
SPLICE_T = "13:%sx" % _m.group(1)[0]                         # 13:5x
_fz_ci = git_out(["show", "-s", "--format=%ci", FIN])       # 2026-10-19 15:13:26 +0800
assert _fz_ci.startswith("2026-10-19 15:1"), "finalize estate ts unexpected: %r" % _fz_ci
_st_ci = git_out(["show", "-s", "--format=%ci", SEAT])      # 2026-10-19 15:09:11 +0800
assert _st_ci.startswith("2026-10-19 15:0"), "seat commit ts unexpected: %r" % _st_ci
assert git_out(["show", "-s", "--format=%ci", BATCH1]).startswith("2026-10-19 13:5")
assert git_out(["show", "-s", "--format=%ci", BATCH2]).startswith("2026-10-19 13:5")

# --- frozen template face (PRE-backfill @ FREEZE; byte-identity vs blob) ---
_blob_expect = git_out(["rev-parse", FREEZE + ":research/PERPETUAL_N1_W278_PREREG.md"])
_ho = git_out(["hash-object", "results/_w279bmc_w278_frozen_face.txt"])
assert _ho == _blob_expect, "frozen face disk hash-object mismatch: %s vs %s" % (_ho, _blob_expect)
_face = io.open(os.path.join(REPO, "results", "_w279bmc_w278_frozen_face.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
_face_b = _face.encode("utf-8")
FACE_SHA16 = hashlib.sha256(_face_b).hexdigest()[:16]
FACE_BYTES = len(_face_b)
assert FACE_BYTES == 23814 and FACE_SHA16 == "99001d3d3f337942", "frozen face drift: %dB %s" % (FACE_BYTES, FACE_SHA16)
_head_twin = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W278_PREREG.md"])
assert _head_twin == "1c93e077c2b64476fb55041a7f59f7591f67db68", "HEAD twin drift: %s" % _head_twin
_head_twin_size = int(git_out(["cat-file", "-s", "HEAD:research/PERPETUAL_N1_W278_PREREG.md"]))
assert _head_twin_size == 28082, "HEAD twin size drift: %d" % _head_twin_size

# --- W278 finalize anchors (fivekeys receipt + results json, FULL-PRECISION live-read) ---
fk = json.load(io.open(os.path.join(REPO, "results", "_r1118bmc_w278_fivekeys.json"), encoding="utf-8"))
assert fk["all_pass"] is True
assert fk["merged"]["k"] == 609520 and fk["ledger_identity"]["total"] == 1035935 and fk["ledger_identity"]["exact"]
res = json.load(io.open(os.path.join(REPO, "results", "perpetual_faces", "n1_w278_results.json"), encoding="utf-8"))
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1033735
_proj_k = fk["merged"]["k"] + fk["ledger_identity"]["batch_trials"]      # 609,520 + 2,200
_proj_ledger = fk["ledger_identity"]["total"] + fk["ledger_identity"]["batch_trials"]  # 1,035,935 + 2,200
_proj_neff = fk["ledger_identity"]["total"]                               # n_eff held face = prev ledger total? NO:
# n_eff_held for wave N+1 = the ledger total of wave N-1 per chain (W278 fivekeys n_eff_held 1,033,735
# = W276 ledger total). CHECK against the chain: W279 n_eff_held projection must equal the W277
# ledger total 1,033,735? -- W277 fivekeys ledger total = 1,033,735 (r1116 builder assert). The
# W278 fivekeys n_eff_held = 1,033,735 (== W276 total? NO: W277 total). Chain evidence:
#   W278 fivekeys: n_eff_held 1,033,735 == W277 ledger total (1,033,735)  [r1114-continuation finalize]
#   W277 fivekeys: n_eff_held 1,031,535 == W276 ledger total (1,031,535)
# So n_eff_held(wave N) = ledger_total(wave N-1) = the PREV wave's total. For W279: = W278 ledger total
# = 1,035,935.
_proj_neff = fk["ledger_identity"]["total"]  # 1,035,935 == W278 total -> W279 n_eff_held projection
assert _proj_k == 611720 and _proj_ledger == 1038135 and _proj_neff == 1035935, \
    "projection drift: %r %r %r" % (_proj_k, _proj_ledger, _proj_neff)

# --- W279 seat receipt (bands verbatim machine-read) ---
rcp = json.load(io.open(os.path.join(REPO, "results", "_w279bmc_20261019_probe_receipt.json"), encoding="utf-8"))
assert rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [629101, 631100] and rcp["bands"]["B"] == [631101, 631300]
_seat_files = git_out(["show", "--name-only", "--format=", SEAT])
assert "fleet/inbox/MSG-20261019-145x-bmc-w279-seat.md" in _seat_files, "seat MSG not carried by seat commit: %r" % _seat_files[:300]

# --- W280p projections from the seat receipt leg4 (for the W279 prereg sec.5 item5) ---
_l4 = rcp["legs"]["leg4"]
assert _l4["W280p_A_naive"] == "631101..633100" and _l4["W280p_B_naive"] == "631301..631500"

facts = {
  "prep_window": "r1120 (bm-c loop, 2026-10-19 15:2x, W279 prereg PREP per r1096/r1115 honest-split law)",
  "target_wave": 279,
  "prereg_freeze": {"commit": FREEZE, "blob_sha1": _blob_expect,
                    "head_twin_sha1": _head_twin, "head_twin_size": _head_twin_size,
                    "face_bytes": FACE_BYTES, "face_sha256_16": FACE_SHA16,
                    "law": "PRE-backfill frozen face per r1049/r1052 (HEAD twin = post-sec78-backfill, disclosed NOT used)"},
  "splice": {"commit": SPLICE, "splice_t": SPLICE_T},
  "engine_batches": [{"commit": BATCH1}, {"commit": BATCH2}],
  "finalize_estate": {"commit": FIN, "ts": _fz_ci},
  "seat": {"commit": SEAT, "msg": "MSG-20261019-145x-bmc-w279-seat.md", "ts": _st_ci},
  "fivekeys_file": "results/_r1118bmc_w278_fivekeys.json",
  "results_file": "results/perpetual_faces/n1_w278_results.json",
  "w278_merged": {"k": fk["merged"]["k"], "mu": fk["merged"]["mu"], "sigma": fk["merged"]["sigma"],
                  "se_mu_k609520": fk["merged"]["se_mu_k609520"],
                  "mu_8dp": round(fk["merged"]["mu"], 8), "sigma_8dp": round(fk["merged"]["sigma"], 8)},
  "w278_only": {"mu": fk["w278_only"]["mu"], "sigma": fk["w278_only"]["sigma"],
                "mu_8dp": round(fk["w278_only"]["mu"], 8)},
  "a_band": {"p95": fk["a_band"]["full_sharpe_p95"], "p99": fk["a_band"]["full_sharpe_p99"]},
  "skill_line": {k: v for k, v in fk["skill_line"].items()},
  "key1": [c for c in fk["checks"] if c["name"] == "key1_w278_vs_merged_mu_gap"][0],
  "ledger_identity": {k: v for k, v in fk["ledger_identity"].items()},
  "k_projection_w279": _proj_k,
  "ledger_projection_w279": _proj_ledger,
  "n_eff_held_projection_w279": _proj_neff,
  "bands": {"A": rcp["bands"]["A"], "B": rcp["bands"]["B"]},
  "seat_semantics": {
    "A_hop": "TWENTY-EIGHTH consecutive A-hop (naive 628_901..630_900 refused at registered W278 B 628_901..629_100; live walk hops past W278 B tail 629_100 -> A first-clean 629_101..631_100, hops=1)",
    "B_hop": "TWENTY-NINTH consecutive above-own-A (naive 629_101..629_300 refused by own-A reservation cascade -> hop past own-A tail 631_100 -> 631_101..631_300, hops=1)",
  },
  "seed_admit": rcp["legs"]["leg2"]["seed_admit_gate"],
  "w280p_projection": {"A_naive": _l4["W280p_A_naive"], "B_naive": _l4["W280p_B_naive"],
                       "note": _l4["note"][:400]},
  "next_action": "r1121 FIRST ACTION: builder one-generation roll _r1116bmc_build_w278_derive.py -> _r1121bmc_build_w279_derive.py (E63 canon law; span OLD sides verified line-level against results/_w278bmc_prereg_derive.py ACTUAL text per heal (i) r1116 law) -> derive _w279bmc_prereg_derive.py -> research/PERPETUAL_N1_W279_PREREG.md ALL GATES PASS -> banned ADMIT -> freeze commit + push",
}
out = os.path.join(REPO, "results", "_w279bmc_prep_facts.json")
io.open(out, "w", encoding="utf-8").write(json.dumps(facts, ensure_ascii=False, indent=1))
print("PREP FACTS LANDED -> %s (%d bytes)" % (out, len(json.dumps(facts, ensure_ascii=False))))
print("anchors: freeze %s (blob %s, twin %s %dB) | splice %s %s | batches %s+%s | finalize %s | seat %s" % (
    FREEZE, _blob_expect[:16], _head_twin[:16], _head_twin_size, SPLICE, SPLICE_T, BATCH1, BATCH2, FIN, SEAT))
print("W278 actuals: mu %.8f sigma %.8f K %d ledger %d se_mu %s p95 %s klift %s" % (
    facts["w278_merged"]["mu_8dp"], facts["w278_merged"]["sigma_8dp"], fk["merged"]["k"],
    fk["ledger_identity"]["total"], fk["merged"]["se_mu_k609520"], facts["a_band"]["p95"],
    fk["skill_line"]["k_lift_delta"]))
print("W279 projections: K %d / ledger %d / n_eff_held %d" % (_proj_k, _proj_ledger, _proj_neff))
print("bands A %s B %s | W280p A naive %s B naive %s" % (rcp["bands"]["A"], rcp["bands"]["B"], _l4["W280p_A_naive"], _l4["W280p_B_naive"]))
