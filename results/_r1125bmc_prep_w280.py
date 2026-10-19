# -*- coding: utf-8 -*-
# r1125 bm-c: W280 prereg PREP (facts + needle floors, combined per r1120+r1121 precedent --
# two PREP legs landed one window to shorten the prereg latency; every anchor machine-frozen,
# zero hand transcription r587). Derive builder = next window FIRST ACTION per r1096
# honest-split law (builder = ~62KB full-window canon-clone job).
# Products: results/_w280bmc_w279_frozen_face.txt (already extracted+verified by this window)
#           results/_w280bmc_prep_facts.json   (chain anchors + projections)
#           results/_w280bmc_needle_floors.json (T0 measured counts, r1077 law)
import io, os, re, json, hashlib, subprocess, math

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git_out(args):
    r = subprocess.run(["git", "-C", REPO] + args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SystemExit("GIT FAIL %r: %s" % (args, r.stderr[:200]))
    return r.stdout.strip()

# ---- T0 frozen W279 template face (PRE-backfill law r1049/r1052) ----
T0 = io.open(os.path.join(REPO, "results", "_w280bmc_w279_frozen_face.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n")
t0b = T0.encode("utf-8")
assert len(t0b) == 23681, "T0 size drift: %d" % len(t0b)
assert hashlib.sha256(t0b).hexdigest()[:16] == "c2fc7c34d0e41a68", "T0 sha mismatch"
_blob = git_out(["rev-parse", "ba5c725b42:research/PERPETUAL_N1_W279_PREREG.md"])
assert _blob == "51d7ca52a811bc22a4ada6f4635915d5219ec734", "freeze blob mismatch: %s" % _blob
_twin = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W279_PREREG.md"])
_twin_size = int(git_out(["cat-file", "-s", _twin]))

# ---- W279 actuals (fivekeys receipt, FULL-PRECISION machine-read) ----
fk = json.load(open(os.path.join(REPO, "results", "_r1124bmc_w279_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w280bmc_20261019_probe_receipt.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert fk["merged"]["k"] == 611720 and fk["ledger_identity"]["total"] == 1038135 and fk["ledger_identity"]["exact"]
assert round(fk["merged"]["mu"], 8) == -0.09282363 and round(fk["merged"]["sigma"], 8) == 0.24506025
assert round(fk["w279_only"]["mu"], 8) == -0.10331555 and round(fk["w279_only"]["sigma"], 8) == 0.24636052
assert round(fk["merged"]["se_mu_k611720"], 6) == 0.000313 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3104
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0 and fk["skill_line"]["n_eff_held"] == 1035935
assert round(fk["skill_line"]["line_pre_w279"], 4) == 1.197 and round(fk["skill_line"]["line_merged_611720"], 4) == 1.197
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w279_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0105 and _k1["pass"]
_k1b = [c for c in fk["checks"] if c["name"] == "key1b_merged_vs_w278_key"][0]
assert abs(_k1b["value"] - 3.7869504906085094e-05) < 1e-12 and _k1b["pass"]
# seat bands verbatim in-gate
assert rcp["bands"]["A"] == [631301, 633300] and rcp["bands"]["B"] == [633301, 633500]
l1 = rcp["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"][0]["refuser_bands"] == [[631101, 631300]]
assert l1["B_hop_chain"][0]["refuser_bands"] == [[631301, 633300]]
assert l1["B_naive_refused_at_start"] is True and l1["B_lands_above_own_A"] is True
_l0 = rcp["legs"]["leg0"]
assert _l0["rows"] == 277 and _l0["owner_rows"] == 269 and _l0["bmc_rows"] == 98 and _l0["ordinal"] == 270
assert _l0["w279_finalize_anchors"]["ledger_total"] == 1038135 and _l0["w279_finalize_anchors"]["merged_n"] == 611720
assert rcp["legs"]["leg2"]["conflicts"] == 0 and rcp["legs"]["leg3"]["origin_vacancy"] is True
assert rcp["legs"]["leg4"]["W281p_A_naive"] == "633301..635300" and rcp["legs"]["leg4"]["W281p_B_naive"] == "633501..633700"

# ---- W279 cycle chain commits (existence + timestamp gates) ----
chain = {}
for sha, expect_hhmm in (("ba5c725b42", "18:5"), ("3810f4a7ac", "19:3"), ("498d178d0b", "19:3"),
                         ("332e8e8656", "19:3"), ("6bdbdb9a07", "20:0"), ("900c23fe7d", "15:0"),
                         ("f96272d8b9", "20:0")):
    ci = git_out(["show", "-s", "--format=%ci", sha])
    assert ci.startswith("2026-10-19 " + expect_hhmm), "chain ts unexpected %s: %r" % (sha, ci)
    chain[sha] = ci
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w279_results.json"])
assert _fin_log == "6bdbdb9a07", "W279 finalize landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "f96272d8b9"])
assert "MSG-20261019-200x-bmc-w280-seat.md" in _seat_files, "W280 seat MSG not carried: %r" % _seat_files[:200]

# ---- projections (computed, zero transcription) ----
K_PROJ = fk["merged"]["k"] + 2200            # 613,920
LEDGER_PROJ = fk["ledger_identity"]["total"] + 2200   # 1,040,335
N_EFF_HELD = fk["ledger_identity"]["total"]  # 1,038,135
SE_PROJ = round(fk["merged"]["sigma"] / math.sqrt(K_PROJ), 6)
assert (K_PROJ, LEDGER_PROJ, N_EFF_HELD) == (613920, 1040335, 1038135)
assert SE_PROJ == 0.000313, "se_mu W280 projection drift: %r" % SE_PROJ

prep = {
  "prep_window": "r1125 (combined facts+floors PREP; r1120+r1121 two-leg precedent compressed one window)",
  "derive_window_planned": "r1126 FIRST ACTION (E63 canon-clone of _r1122bmc_build_w279_derive.py bloodline -> _r1126bmc_build_w280_derive.py -> _w280bmc_prereg_derive.py)",
  "t0": {"file": "results/_w280bmc_w279_frozen_face.txt", "bytes": len(t0b),
         "sha256_16": "c2fc7c34d0e41a68", "freeze_commit": "ba5c725b42",
         "freeze_blob_sha1": _blob,
         "head_twin_sha1": _twin, "head_twin_size": _twin_size,
         "head_twin_note": "POST-backfill twin (sec7/8 backfilled by r1124 W279 cycle) -- NOT used per r1049/r1052"},
  "prereg_freeze": {"commit": "ba5c725b42", "ci": chain["ba5c725b42"]},
  "splice": {"commit": "3810f4a7ac", "ci": chain["3810f4a7ac"], "splice_t": "19:3x"},
  "engine_batches": [{"commit": "498d178d0b", "ci": chain["498d178d0b"]},
                      {"commit": "332e8e8656", "ci": chain["332e8e8656"]}],
  "finalize_estate": {"commit": "6bdbdb9a07", "ci": chain["6bdbdb9a07"], "product": "results/perpetual_faces/n1_w279_results.json"},
  "seat_w279": {"commit": "900c23fe7d", "ci": chain["900c23fe7d"]},
  "seat": {"commit": "f96272d8b9", "ci": chain["f96272d8b9"],
           "msg": "MSG-20261019-200x-bmc-w280-seat.md",
           "receipt": "results/_w280bmc_20261019_probe_receipt.json",
           "bands": {"A": rcp["bands"]["A"], "B": rcp["bands"]["B"]}},
  "w279_merged": {"k": fk["merged"]["k"], "mu": fk["merged"]["mu"], "sigma": fk["merged"]["sigma"],
                  "se_mu_k611720": fk["merged"]["se_mu_k611720"]},
  "w279_only": {"mu": fk["w279_only"]["mu"], "sigma": fk["w279_only"]["sigma"]},
  "fivekeys_receipt": "results/_r1124bmc_w279_fivekeys.json",
  "k_projection_w280": K_PROJ, "ledger_projection_w280": LEDGER_PROJ,
  "n_eff_held_projection_w280": N_EFF_HELD, "se_mu_projection_w280": SE_PROJ,
  "key1_gap_w279": _k1["value"], "key1b_merged_vs_w278": _k1b["value"],
  "a_band_p95_w279": fk["a_band"]["full_sharpe_p95"],
  "line_pre_w279": fk["skill_line"]["line_pre_w279"],
  "line_merged_611720": fk["skill_line"]["line_merged_611720"],
  "k_lift_delta_w279": fk["skill_line"]["k_lift_delta"],
}
io.open(os.path.join(REPO, "results", "_w280bmc_prep_facts.json"), "w", encoding="utf-8").write(
    json.dumps(prep, ensure_ascii=False, indent=1))

# ---- needle floors MEASURED on T0 (r1077 law) ----
# Stamp faces: the W279 prereg (T0) carries the W278-cycle stamps -- the W280 derive must roll
# finalize-window stamps 15:1x (W278 finalize 0a92fcc28f 15:13:26 landed by r1119) -> 20:0x
# (W279 finalize 6bdbdb9a07 20:06:06) and splice stamps 13:5x (W278 splice b6f486af35) -> 19:3x
# (W279 splice 3810f4a7ac 19:33:30).
faces = {}
for pat in ("15:1x", "13:5x", "10:3x", "09:5x", "20:0x", "19:3x",
            "W280", "W279", "W278", "W279p_", "W280p_", "W281p_",
            "611,720", "609,520", "1,038,135", "1,035,935", "1,033,735",
            "613,920", "1,040,335",
            "631_301", "633_300", "633_301", "633_500",
            "629_101", "631_100", "631_101", "631_300",
            "−0.09282363", "−0.09278576", "0.24506025", "0.24505494",
            "−0.10331555", "−0.09701509", "0.3104", "0.2844",
            "第二十九次连续", "第三十次连续", "第二十八次连续",
            "第三十次连续", "连续二十八波", "连续二十七波",
            "0.000313", "0.000314", "n1_w279", "n1_w278", "_w279bmc", "_w278bmc",
            "bmc-w280-seat", "bmc-w279-seat", "f96272d8b9", "900c23fe7d",
            "第 269 波", "第 270 波", "波号 279", "波号 280", "bmc_rows=98", "bmc_rows=97",
            "42nd consecutive", "41st consecutive", "CLEAN-AT-BIRTH 12th", "CLEAN-AT-BIRTH 11th",
            "engine_owner==bm-c 98", "engine_owner==bm-c 97"):
    faces[pat] = T0.count(pat)
# structural zero-floor gates (fail-closed): every G+2 / current-actual face must be 0 on T0.
# Legitimate PRESENT faces (roll targets, NOT zero-floors -- ground-truthed this window):
#   W280p_ x2 (W279 seat leg4 projection), 631_301 x3 (W280p A first-clean), 0.000313 x1
#   (W279 se_mu projection), 第二十九次连续 A-hop x3 (W280p projection), 611,720 x1, 15:1x x4.
for z in ("W281p_", "613,920", "1,040,335", "633_300", "633_301", "633_500",
          "−0.09282363", "0.24506025", "−0.10331555", "0.3104", "第三十次连续", "f96272d8b9",
          "engine_owner==bm-c 98", "bmc_rows=98", "bmc-w280-seat", "20:0x", "19:3x",
          "第三十次连续 above-own-A", "第 270 波", "波号 280", "第 278 波"):
    c = T0.count(z)
    assert c == 0, "zero-floor FAIL: %r count=%d (next-wave face present on frozen T0)" % (z, c)
floors = {
  "measured_on": "results/_w280bmc_w279_frozen_face.txt (23,681B sha256_16 c2fc7c34d0e41a68)",
  "law": "r1077 measured-counts: derive-builder floors must match these counts; heals disclosed at birth",
  "stamp_rolls_expected": {"finalize_stamps": {"old": "15:1x", "new": "20:0x", "count": faces["15:1x"]},
                            "splice_stamps": {"old": "13:5x", "new": "19:3x", "count": faces["13:5x"]}},
  "faces": faces,
}
io.open(os.path.join(REPO, "results", "_w280bmc_needle_floors.json"), "w", encoding="utf-8").write(
    json.dumps(floors, ensure_ascii=False, indent=1))
print("PREP OK: facts + floors landed")
print("T0 23,681B sha c2fc7c34d0e41a68 | freeze blob %s | HEAD twin %s (%dB)" % (_blob[:12], _twin[:12], _twin_size))
print("projections: K=%d ledger=%d n_eff_held=%d se_mu_w280=%s" % (K_PROJ, LEDGER_PROJ, N_EFF_HELD, SE_PROJ))
print("stamp floors: 15:1x=%d 13:5x=%d | W279=%d W278=%d | 611,720=%d 1,038,135=%d" % (
    faces["15:1x"], faces["13:5x"], faces["W279"], faces["W278"], faces["611,720"], faces["1,038,135"]))
print("key value faces on T0: −0.09278576=%d 0.24505494=%d −0.09701509=%d 0.2844=%d | %r" % (
    faces["−0.09278576"], faces["0.24505494"], faces["−0.09701509"], faces["0.2844"],
    {k: v for k, v in faces.items() if k.startswith("第二十") or k.startswith("第三十") or k.startswith("连续")}))
