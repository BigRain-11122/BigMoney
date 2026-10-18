# -*- coding: utf-8 -*-
# r1110 bm-c: W276 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w275bmc_prereg_derive.py -> results/_w276bmc_prereg_derive.py.
# Zero hand-transcription of chain values into the PRODUCT: W276 bands/anchors read from the seat
# receipt + fivekeys/results jsons (r587/r1093 laws); floors MEASURED on the frozen W275 template
# (r1077 law, facts receipt results/_w276bmc_prep_facts.json). Complex value spans
# placeholder-protected before the general rolls. The builder pre-flights the ENTIRE derive
# transform in-memory (exec data segments + full gate run) before writing the script (r1052
# idempotent pattern). Needle evidence receipt -> results/_w276bmc_needle_probe.json.
# Same-window heals disclosed (builder-level, defect-birthplace law 2026-10-16):
# (a) b_band/b3_a REFUSER-BAND double-roll defect FIXED AT BIRTH: the r1107 build's band
#     descending chain (617_901..618_100 -> 620_101..620_300 -> 622_301..622_500) double-rolled
#     the W275 prereg's b_band/b3_a refuser prose ("注册 W274 B 带 622_301..622_500" -- label
#     W274 but band values = W275's own B; the machine receipt's refuser_bands=[[620101,620300]]
#     contradicted the prose). This build rolls the chain own-before-prior AND appends a
#     post-W-chain correction pass restoring the prose to the machine-receipt face
#     ("注册 W275 B 带 622_301..622_500" per W276 receipt leg1 refuser_bands=[[622301,622500]]).
# (b) freezer-label one-generation lag healed at birth: the W275 prereg's b_claim_proj carried
#     "W275 freezer 承接面强制注记：须在 post-W275 宇宙重 derive" (label==universe, lagged);
#     per the W276 seat receipt leg4 note ("the W277 freezer MUST re-derive on the post-W276
#     universe") the W276 prereg carries "W277 freezer ... post-W276 宇宙" via the same
#     post-W-chain pass.
# (c) floors stamp entries rolled to measured (03:0x=2 / 03:2x=4 / 03:3x=1 positive floors for
#     the T0-consumed stamps + 05:2x/05:3x/05:5x zero-floors); MUST_NOT stamp run extended with
#     the W274-era 03:xx bans (S10).
# (d) date-cross N/A this generation (W276 seat receipt same-date 20261019 with W275 -- the
#     lowercase prefix chain rolls the receipt date with no date-cross leg).
# (e) RAM prose doubling ("nvidia-smi nvidia-smi 实读...") healed at birth in the S8 POST_LEG
#     new side (cosmetic %-format artifact from r1107).
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w276bmc_w275_frozen_face.txt"), encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23551
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "e4e1ce44f5afd03b"
fk = json.load(open(os.path.join(REPO, "results", "_r1108bmc_w275_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w276bmc_20261019_probe_receipt.json"), encoding="utf-8"))
prep = json.load(open(os.path.join(REPO, "results", "_w276bmc_prep_facts.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [622501, 624500] and rcp["bands"]["B"] == [624501, 624700]
assert round(fk["merged"]["mu"], 8) == -0.09280541 and round(fk["merged"]["sigma"], 8) == 0.24507989
assert round(fk["w275_only"]["mu"], 8) == -0.09398255 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3088
assert round(fk["merged"]["se_mu_k602920"], 6) == 0.000316 and fk["ledger_identity"]["total"] == 1029335
assert round(fk["skill_line"]["line_pre_w275"], 4) == 1.1968 and round(fk["skill_line"]["line_merged_602920"], 4) == 1.1967
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w275_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0012 and _k1["pass"]
RAM = round(float(subprocess.run(["python", "-c", "import psutil;print(psutil.virtual_memory().available/1024**3)"],
           capture_output=True, text=True).stdout.strip() or 0), 1)
ram_face = "~%.1fGB" % RAM
ram_anchor = "~%.1fG" % RAM
try:
    _nvs = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used",
                           "--format=csv,noheader,nounits"], capture_output=True, text=True).stdout.strip()
    _util, _vram = [x.strip() for x in _nvs.split(",")]
    vram_g = "%.1fG" % (int(_vram) / 1024.0)
    gpu_face = "nvidia-smi 实读 %s%%·%s VRAM 占用·MV 车道已收官 GPU idle 回释" % (_util, vram_g)
except Exception:
    gpu_face = "nvidia-smi 实读 idle·MV 车道已收官 GPU idle 回释"
SRC = io.open(os.path.join(REPO, "results", "_w275bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected spans (slice-replace; old complex faces -> final) ----------------
def mkspan(sid, sm, em, new):
    return (sid, sm, em, new)

HDR_NEW = u'''# r1110 bm-c: W276 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w275bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W275 prereg AT THE FREEZE COMMIT 1fcc0bc30f (git
# 1fcc0bc30f:research/PERPETUAL_N1_W275_PREREG.md, 23,551 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w276bmc_w275_frozen_face.txt by the r1110 derive window
# prep leg (python subprocess raw bytes; prep facts receipt results/_w276bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 e4e1ce44f5afd03b, freeze blob sha1 e62f3bcbdfe458863bc1b98c176b6f591bcdc14e.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 52b42b83b57fbcd3748bf470ab32fc25d98f10e6
# (27803 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1108
# W275 cycle (estate fc01636095). Deriving from the backfilled face would fabricate W276 sec.7/8
# from W275 measured numbers -- the r1049/r1052 precedent requires the 1fcc0bc30f frozen pre-run
# face. W276 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w276bmc_20261019_probe_receipt.json (bm-c r1109 window
#     authored+run live, seat rides origin 21b51a102 per r565 early-visibility law,
#     MSG-20261019-055x-bmc-w276-seat landed on origin; zero foreign W276 seat claims; zero
#     W277/W278 skip-claims). STAIRCASE CONTINUES: A naive 622_301..624_300 REFUSED at start
#     (registered W275 B band 622_301..622_500 sits INSIDE the naive A window) -> A first-clean
#     622_501..624_500 hops=1 (TWENTY-FIFTH consecutive A-hop, W275 prereg sec.5 item5
#     post-W275-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 622_501..622_700 lands INSIDE the own-wave W276 A first-clean window 622_501..624_500
#     (own-A reservation cascade) -> hop past own-A tail 624_500 -> 624_501..624_700 hops=1
#     (TWENTY-SIXTH consecutive above-own-A landing); seed_admit FREE x2 (A base=622501 span=2000 /
#     B base=624501 span=200); leg0 rows=273 owner_rows=265 bmc_rows=94 ordinal=266; leg2
#     conflicts=0; leg3 origin_vacancy=true; W277p projection: A naive 624_501..626_500 CLEAN
#     hops=0 / B naive 624_701..624_900 CLEAN hops=0 but lands inside W277p A naive.
#   - upstream W275 finalize LANDED (bm-c r1108 window one-pass, n1_w275_results.json landed via
#     fc01636095 05:31:54, fivekeys 6/6 receipt results/_r1108bmc_w275_fivekeys.json + sec.7/8
#     backfilled): merged K=602,920 / ledger 1,029,335 EXACT (1,027,135+2,200) / merged mu
#     -0.09280540618987594 (8dp -0.09280541) / sigma 0.24507988853984436 (8dp 0.24507989) /
#     se_mu@K602,920 0.000316 (held-flat from W274 0.000316) / W275-only mu -0.09398254545454544
#     (8dp -0.09398255) / A p95 0.3009->0.3088 (in-band double-direction) / K-lift -0.0001
#     (held-flat-negative) / n_eff_held 1,027,135 / line_pre_w275 1.1968 / line_merged@602,920
#     1.1967 / key1 only-vs-merged gap 0.0011771392646695022 (4dp 0.0012) in-band; splice
#     018782314d 05:22:20 (r1108 window, CLEAN-AT-BIRTH 8th gen); engine self-burn 12/12 batched
#     ledger appends 5089f02250+e639699d59+final-2 engine-self; sixgate 38th consecutive
#     PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded narration faces; ALL
#     gates machine-verify against the full-precision fivekeys/results jsons (r1093 CODELY pit
#     entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w276bmc_prep_facts.json (MEASURED live on T0 THIS
# window, r1077 measured-counts law; floors below match every measured count; disclosed floor
# carries: W274 44->62 + W263 1->2 + W268 3->2 + W271 4->3 measured-over-pattern, generation
# drift, healed in-place; zero-floor audit: every next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W275 finalize one-pass landed 05:3x (fc01636095 05:31:54); T0
#     carries the W274-era 03:2x stamps x4 (MEASURED live THIS build, r1077 law) -> POST_LEG x4.
# (2) date-cross N/A this generation (disclosed): the W276 seat receipt is SAME-DATE with the W275
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg (the r1104 W274 build needed one only because the W273 seat receipt
#     was dated 10-18; that leg is REMOVED here).
# (3) sec.5 item1 measured keys -> W275 actuals (n1_w275_results + fivekeys machine values):
#     merged mu -0.09280541 / K=602,920 / W275-only -0.09398255 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W275-only vs merged TRUE diff = 0.0012 @4dp (measured
#     0.0011771392646695022 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24508947 -> 0.24507989 (W275 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3009 -> 0.3088 (W275 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift -0.0001 (W275 fivekeys key4, held-flat-negative) +
#     line_merged@K602,920 1.1967 + lowercase line_pre_w274 -> line_pre_w275 1.1968 (lowercase
#     NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,024,935 -> 1,027,135.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries stale
#     values on the W274 slot -> POST_LEG rewrites the tail with true history W270 0.000319 /
#     W271 0.000319 / W272 0.000318 / W273 0.000317 / W274 0.000316 / W275 0.000316 and appends
#     the W276 projection 0.000316.
# (9) sec.4 merged-pool anchor face: W1..W274 600,720 -> W1..W275 602,920 (W275 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1105 W274 -> bm-c r1108 W275 (cycle owner + wave roll).
# (11) RAM face live-measured THIS window: psutil %(ram).1f GB available (%(ramf)s, probe-time read) +
#     nvidia-smi %(gpu)s -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); the r1107
#     ~4.0GB face is stale; the r1107 %%-format doubling ("nvidia-smi nvidia-smi 实读") healed
#     at birth in the POST_LEG new side.
# (12) low-RAM precedent ledger append: W275 freeze-window %(rama)s bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W273 ~4.4G onto W274 -- both restored + true W275
#     anchor appended).
# (13) seat/provenance legs: MSG-20261019-034x-bmc-w275-seat/bf4bbbde1e/r1106 ->
#     MSG-20261019-055x-bmc-w276-seat/21b51a102/r1109 (two live faces + block NEWs).
# (14) engine live-read faces r1107 -> r1110 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled two-window: the W275 cycle = prereg r1107 (1fcc0bc30f)
#     + splice/burn/sixgate/finalize/fivekeys/sec78 r1108 one-window (018782314d+fc01636095).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) b_band/b3_a refuser-band restore: post-W-chain pass rewrites the double-rolled prose to the
#     machine-receipt face (registered W275 B band 622_301..622_500 refused the naive W276 A start
#     -- receipt leg1 refuser_bands=[[622301,622500]]); the r1107 chain had rolled it one band too
#     far (prose said the W275 own B while the label said W274).
# (17) freezer-label lag heal: "W276 freezer 承接面强制注记" -> "W277 freezer 承接面强制注记"
#     (the W277 freezer consumes the post-W276 universe per the W276 seat receipt leg4 note).''' % {"ram": int(RAM), "ramf": ram_face, "gpu": gpu_face, "rama": ram_anchor}

SPANS = [
 mkspan("S1", "# r1107 bm-c: W275 prereg derive (count-asserted ordered transform + marker-extracted block replaces).",
        "#     inheritance).", HDR_NEW),
 mkspan("S2", '_blob_expect = "8e726cb11abf8e9ebdb1536a35e87be42f83bee1"',
        'assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "ddc158b5047596ea", "SRC sha mismatch"',
 u'''_blob_expect = "e62f3bcbdfe458863bc1b98c176b6f591bcdc14e"   # freeze-commit face @ 1fcc0bc30f
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "1fcc0bc30f:research/PERPETUAL_N1_W275_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W275_PREREG.md"])
assert _hb == "52b42b83b57fbcd3748bf470ab32fc25d98f10e6", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23551, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "e4e1ce44f5afd03b", "SRC sha mismatch"'''),
 mkspan("S3", "# --- chain-fact existence gates (zero transcription) ---",
        'assert "MSG-20261019-034x-bmc-w275-seat.md" in _seat_files, "W275 seat MSG not carried by seat commit bf4bbbde1e: %r" % _seat_files[:200]',
 u'''# --- chain-fact existence gates (zero transcription) ---
for sha in ("1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "21b51a102"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "018782314d"])    # 2026-10-19 05:22:20 +0800
_m = re.match(r"2026-10-19 05:(\\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "05:%sx" % _m.group(1)[0]   # 05:2x
_fz = git_out(["show", "-s", "--format=%ci", "fc01636095"])    # 2026-10-19 05:31:54 +0800
assert _fz.startswith("2026-10-19 05:3"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "21b51a102"])   # 2026-10-19 05:55:17 +0800
assert _st.startswith("2026-10-19 05:5"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w275_results.json"])
assert _fin_log == "fc01636095", "W275 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "21b51a102"])
assert "MSG-20261019-055x-bmc-w276-seat.md" in _seat_files, "W276 seat MSG not carried by seat commit 21b51a102: %r" % _seat_files[:200]'''),
 mkspan("S4", 'with open(os.path.join(REPO, "results", "_r1105bmc_w274_fivekeys.json"), encoding="utf-8") as f:',
        'assert fk["all_pass"] is True, "fivekeys not all_pass"',
 u'''# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1108bmc_w275_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 602920, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09280541, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24507989, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k602920"], 6) == 0.000316, "se_mu drift: %r" % fk["merged"]["se_mu_k602920"]
assert round(fk["w275_only"]["mu"], 8) == -0.09398255, "w275-only mu drift: %r" % fk["w275_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3088, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == -0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1027135, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w275"], 4) == 1.1968, "line_pre drift: %r" % fk["skill_line"]["line_pre_w275"]
assert round(fk["skill_line"]["line_merged_602920"], 4) == 1.1967, "line_merged drift: %r" % fk["skill_line"]["line_merged_602920"]
assert fk["ledger_identity"]["total"] == 1029335 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w275_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0012 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"'''),
 mkspan("S5", 'with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8") as f:',
        'assert round(res9["null_pool_cumulative"]["se_mu_at_k598520"], 6) == 0.000317, "W273 se_mu chain verify"',
 u'''with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1027135
assert round(res["skill_line_v2_k_lift"]["line_pre_w275"], 4) == 1.1968
assert round(res["skill_line_v2_k_lift"]["line_merged_602920"], 4) == 1.1967
assert round(res["null_pool_cumulative"]["se_mu_at_k602920"], 6) == 0.000316, "W275 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k600720"], 6) == 0.000316, "W274 se_mu chain verify"'''),
 mkspan("S6", 'with open(os.path.join(REPO, "results", "_w275bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:',
        'assert pr["legs"]["leg4"]["W276p_B_lands_inside_W276p_A_naive"] is True',
 u'''with open(os.path.join(REPO, "results", "_w276bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [622501, 624500] and pr["bands"]["B"] == [624501, 624700]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [622301, 624300], "jump_to": 622501,
                              "refuser_pts": [], "refuser_bands": [[622301, 622500]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [622501, 622700], "jump_to": 624501,
                              "refuser_pts": [], "refuser_bands": [[622501, 624500]]}]
assert l1["B_naive"] == [622501, 622700] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W275_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W275_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W273_W274_W275_bands_respected_A"] is True and _ra["W273_W274_W275_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 273 and _l0["owner_rows"] == 265 and _l0["bmc_rows"] == 94
assert _l0["ordinal"] == 266 and _l0["w275_finalize_landed"] is True
assert _l0["w275_finalize_anchors"]["ledger_total"] == 1029335
assert _l0["w275_finalize_anchors"]["merged_n"] == 602920
assert round(_l0["w275_finalize_anchors"]["skill_line_delta_k_lift"], 4) == -0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=622501 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=624501 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W277p_A_naive"] == "624501..626500"
assert pr["legs"]["leg4"]["W277p_B_naive"] == "624701..624900"
assert pr["legs"]["leg4"]["W277p_B_lands_inside_W277p_A_naive"] is True'''),
 mkspan("S7", "# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---",
        'assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free',
 u'''# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1110 window face: probe-time read = %s available (MV lane drained, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %%.2f" %% _ram_free''' % ram_face),
 mkspan("S8", "VMAP_POST_LEGS = [", "    T1 = T1.replace(o, n)",
 u'''VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W275 finalize one-pass landed 05:3x (fc01636095
    # 05:31:54); T1 carries the W274-era 03:2x stamps x4 (MEASURED live THIS build, r1077 law)
    ("03:2x", "05:3x", 4),
    # date-cross N/A this generation (heal (2), disclosed): W276 seat receipt same-date 20261019
    # with the W275 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg (the r1104 build needed one only because the W273 seat receipt was 10-18).
    # sec.5 item1 measured keys -> W275 actuals (n1_w275_results + fivekeys machine values)
    ("（W275 实测键 **−0.09280110**·K=600,720 合并池·W275-only 实测 **−0.09630486**）",
     "（W275 实测键 **−0.09280541**·K=602,920 合并池·W275-only 实测 **−0.09398255**）", 1),
    ("W2..W275 共二百七十三面实测 mu 稳定先例", "W2..W275 共二百七十四面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W275 diff = 0.0012 @4dp (measured
    # 0.0011771392646695022 full), in-band
    ("W275-only vs merged 实差 0.0035 在带内", "W275-only vs merged 实差 0.0012 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24508947**=W275 合并池实测", "键 **0.24507989**=W275 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W275 A 档 p95（**0.3009** 实测锚）", "与 W275 A 档 p95（**0.3088** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w274 NOT rolled by the
    # W-roll; true W275 anchors K-lift -0.0001 + line_merged@K602,920 1.1967 +
    # line_pre_w275 1.1968 + n_eff_held 1,027,135)
    ("键 W275 实测 K-lift **−0.0001**·line_merged@K600,720 **1.1967**·line_pre_w274 1.1968·n_eff_held_equal 1,024,935",
     "键 W275 实测 K-lift **−0.0001**·line_merged@K602,920 **1.1967**·line_pre_w275 1.1968·n_eff_held_equal 1,027,135", 1),
    # se_mu chain true-history correction (heal (8); W275 fivekeys key5 measured 0.000316
    # held-flat from W274 0.000316)
    ("→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000317**→W275 **0.000316**→W276 投影 0.000316】",
     "→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000316**→W275 **0.000316**→W276 投影 0.000316】", 1),
    # sec.4 merged-pool anchor face (heal (9): W275 finalize landed)
    ("W1..W275 已落账 600,720 实测", "W1..W275 已落账 602,920 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W275 cycle (heal (10): bm-c r1108; OLD faces are
    # POST-VMAP faces -- the generated VMAP carries the canon's bare W-chain, so the raw T0'
    # W274-cycle rows already shifted W274->W275 before this leg fires; the leg fixes the
    # window number r1105->r1108, measured post-VMAP count=1)
    ("bm-c r1105 W275 §7 范式", "bm-c r1108 W275 §7 范式", 1),
    ("bm-c r1105 W275 §8 范式", "bm-c r1108 W275 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil %s available (%s) + %s
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1107 ~4.0GB face; %%-format doubling healed at birth
    ("本窗 free RAM ~4.0GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM %s（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（%s）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W275 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- the wave-roll had shifted the W263 26G bm-a anchor onto the W264
    # label and the W273 ~4.4G onto W274; both restored + true W275 anchor appended
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 %s bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %%r count=%%d floor=%%d" %% (o, c, f))
    T1 = T1.replace(o, n)''' % (RAM, ram_face, gpu_face, ram_face, gpu_face, ram_anchor)),
 mkspan("S9",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275=A/B 双 1-hop 形态连续二十四波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275=A/B 双 1-hop 形态连续二十四波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276=A/B 双 1-hop 形态连续二十五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"),
 mkspan("S10", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x",'),
]
txt = SRC
span_sites = []
for sid, sm, em, new in SPANS:
    c = txt.count(sm)
    assert c == 1, "SPAN %s start count=%d (expect 1)" % (sid, c)
    i = txt.index(sm)
    j = txt.find(em, i)
    assert j >= i, "SPAN %s end-marker not found" % sid
    j += len(em)
    txt = txt[:i] + "\x02%s\x02" % sid + txt[j:]

NEEDLES = [
 # -- compound provenance/timeline (BEFORE bare sha/r needles) --
 ("r1104/r1105 W274 全周期先例实时间线：prereg 6f31f6e073 落于 r1104 窗·splice ec907d164 落于 r1105 执行窗", "r1107/r1108 W274 全周期先例实时间线：prereg 1fcc0bc30f 落于 r1107 窗·splice 018782314d 落于 r1108 执行窗"),
 ("estate chain r1104/r1105 W274 全周期 6f31f6e073+ec907d164+acf37937ec", "estate chain r1107/r1108 W274 全周期 1fcc0bc30f+018782314d+fc01636095"),
 ("席位 r1106 窗+prereg r1107 窗", "席位 r1109 窗+prereg r1110 窗"),
 ("bm-c r1105 五面冻结 splice", "bm-c r1108 五面冻结 splice"),
 ("finalize one-pass bm-c r1105 窗 03:2x", "finalize one-pass bm-c r1108 窗 05:3x"),
 # bare form (post-gates MUST list; fires AFTER the suffix needle above so it only hits the
 # MUST bare face -- the prose faces are already suffix-rolled; W274-low new side, the
 # W-chain completes W274->W275)
 ("W274 finalize one-pass bm-c r1105", "W274 finalize one-pass bm-c r1108"),
 ("bm-c r1106 席位 MSG-", "bm-c r1109 席位 MSG-"),
 ("bm-c 循环班 r1106 席位窗", "bm-c 循环班 r1109 席位窗"),
 ("2026-10-19 03:3x", "2026-10-19 05:5x"),
 ("（r1106 窗算法", "（r1109 窗算法"),
 ("bm-c r1106 席·", "bm-c r1109 席·"),
 ("r1106 席位窗实跑：origin inbox 零 W275 席位外机命中", "r1109 席位窗实跑：origin inbox 零 W276 席位外机命中"),
 ("bm-c r1105 W274 §7 范式", "bm-c r1108 W274 §7 范式"),
 ("bm-c r1105 W274 §8 范式", "bm-c r1108 W274 §8 范式"),
 ('"r1105 W274 §7 范式": 0', '"r1108 W274 §7 范式": 0'),
 ('"r1105 W274 §8 范式": 0', '"r1108 W274 §8 范式": 0'),
 # -- r blanket REPLACED with three specific engine-stamp needles (r1107 disclosed-heal family):
 ("saturation_engine.py status live-read r1107：", "saturation_engine.py status live-read r1110："),
 ("本机 bm-c 实例·heartbeat 新鲜实读 r1107 窗", "本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗"),
 ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1107 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读"),
 # -- r old-side rolls (create the T0 faces) --
 ("（r1102 窗算法", "（r1106 窗算法"),
 ("bm-c r1102 席·", "bm-c r1106 席·"),
 ("r1102 席位窗实跑", "r1106 席位窗实跑"),
 ("live-read r1104：", "live-read r1107："),
 ("新鲜实读 r1104 窗", "新鲜实读 r1107 窗"),
 ("新鲜 r1104 窗实读", "新鲜 r1107 窗实读"),
 # -- MSG/sha descending chains --
 ("MSG-20261019-034x", "MSG-20261019-055x"),
 ("MSG-20261019-012x", "MSG-20261019-034x"),
 ("MSG-20261018-211x", "MSG-20261019-012x"),
 ("MSG-034x owner", "MSG-055x owner"),
 ("MSG-012x owner", "MSG-034x owner"),
 ("MSG-211x owner", "MSG-012x owner"),
 ("bmc-w275-seat", "bmc-w276-seat"),
 ("bmc-w274-seat", "bmc-w275-seat"),
 ("bmc-w273-seat", "bmc-w274-seat"),
 ("bf4bbbde1e", "21b51a102"),
 ("70b21a0264", "bf4bbbde1e"),
 ("39e1bb32f1", "70b21a0264"),
 ("f608ff1cee", "39e1bb32f1"),
 ("87d2697cdc", "f608ff1cee"),
 ("6f31f6e073", "1fcc0bc30f"),
 ("ec907d164", "018782314d"),
 # derive-script print faces (outside the S2 span; cosmetic but must not print stale
 # canon shas -- the committed script's stdout stays honest)
 ("8e726cb11abf8e9ebdb1536a35e87be42f83bee1", "e62f3bcbdfe458863bc1b98c176b6f591bcdc14e"),
 ("twin 761d41e8 disclosed", "twin 52b42b83 disclosed"),
 ("b3c8a83c5c", "5089f02250"),
 ("b4c0271044", "e639699d59"),
 ("acf37937ec", "fc01636095"),
 ("6659a0e362", "acf37937ec"),
 # -- G+1 projection/vacancy consumes (descending) --
 ("W277 冻结方", "W278 冻结方"), ("W276 冻结方", "W277 冻结方"), ("W275 冻结方", "W276 冻结方"),
 ("W277p_", "W278p_"), ("W276p_", "W277p_"), ("W275p_", "W276p_"),
 ("verify at W277 prereg", "verify at W278 prereg"), ("verify at W276 prereg", "verify at W277 prereg"), ("verify at W275 prereg", "verify at W276 prereg"),
 ("零 skip-ahead W276/W277 席位声明", "零 skip-ahead W277/W278 席位声明"),
 ("零 skip-ahead W275/W276 席位声明", "零 skip-ahead W276/W277 席位声明"),
 # W+ blankets ALONE (needle-order heal, r1107 family: compounds subsumed by the blankets)
 ("W276+ 投影", "W277+ 投影"),
 ("W275+ 投影", "W276+ 投影"),
 # R-record horizon face (disclosed heal, r1107 family)
 ("对 W276+ 的拒面影响", "对 W277+ 的拒面影响"),
 ("R277", "R278"), ("R276", "R277"), ("R275", "R276"), ("R274", "R275"),
 # -- Chinese ordinals descending --
 ("第二十五次连续 A-hop", "第二十六次连续 A-hop"),
 ("第二十四次连续 A-hop", "第二十五次连续 A-hop"),
 ("第二十三次连续 A-hop", "第二十四次连续 A-hop"),
 ("第二十五次连续 above-own-A", "第二十六次连续 above-own-A"),
 ("第二十四次连续 above-own-A", "第二十五次连续 above-own-A"),
 ("第二十三次连续 above-own-A", "第二十四次连续 above-own-A"),
 ("〔第二十五次连续〕", "〔第二十六次连续〕"), ("〔第二十四次连续〕", "〔第二十五次连续〕"),
 ("连续二十五波", "连续二十六波"),
 ("连续二十四波", "连续二十五波"),
 ("连续二十三波", "连续二十四波"),
 ("共二百七十三面", "共二百七十四面"),
 ("共二百七十二面", "共二百七十三面"),
 # -- ledger/K chains (newest first; b_prev projection BEFORE the 600,720 blanket) --
 ("1,027,135", "1,029,335"), ("1,024,935", "1,027,135"),
 ("1027135", "1029335"), ("1024935", "1027135"),
 ("**602,920 投影**", "**605,120 投影**"),
 ('"602,920": 0', '"605,120": 0'),
 ("600,720", "602,920"),
 ("598,520", "600,720"),
 ("600720", "602920"), ("598520", "600720"),
 # -- value faces (W275 actuals; newest first; SPAN-protected asserts exempt) --
 ("−0.09280110", "−0.09280541"), ("−0.09278822", "−0.09280110"), ("−0.09277998", "−0.09278822"),
 ("-0.09280110", "-0.09280541"), ("-0.09278822", "-0.09280110"),
 ("0.24508947", "0.24507989"), ("0.24510975", "0.24508947"), ("0.24509581", "0.24510975"),
 ("−0.09630486", "−0.09398255"), ("−0.095021", "−0.09630486"), ("−0.09706318", "−0.095021"),
 ("-0.09630486", "-0.09398255"), ("-0.095021", "-0.09630486"),
 ("0.3009", "0.3088"), ("0.3124", "0.3009"), ("**0.3138**", "**0.3124**"), ("0.3138", "0.3124"),
 ("实差 0.0035 在带内", "实差 0.0012 在带内"), ("实差 0.0022 在带内", "实差 0.0035 在带内"), ("实差 0.0010 在带内", "实差 0.0022 在带内"), ("实差 0.0043 在带内", "实差 0.0022 在带内"),
 ("line_pre_w274 1.1968", "line_pre_w275 1.1968"), ("line_pre_w273 1.1966", "line_pre_w274 1.1968"),
 # se_mu chain MUST-entry T2-face protection (r1107 disclosed-heal family): the chain would
 # roll the MUST entry onto the stale (heal-8 OLD) face; one-low needle lands it EXACTLY on
 # the heal-8 NEW side (true history W270..W273 + W274 measured 0.000316 + W275 0.000316 +
 # W276 projection).
 ("→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 **0.000316**→W275 投影 0.000316】",
  "→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000316**→W274 **0.000316**→W275 投影 0.000316】"),
 # -- band faces (descending; own-before-prior heals the r1107 double-roll disease; NEW blocks +
 # VMAP legs + FLOORS + zero-floors + MUST + pinned all ride the same blankets) --
 ("622_501..622_700", "624_701..624_900"),
 ("622_301..624_300", "624_501..626_500"),
 ("620_301..620_500", "622_501..622_700"),
 ("620_101..622_100", "622_301..624_300"),
 ("620_301..622_300", "622_501..624_500"),
 ("622_301..622_500", "624_501..624_700"),
 ("618_101..620_100", "620_301..622_300"),
 ("620_101..620_300", "622_301..622_500"),
 ("618_101..618_300", "620_301..620_500"),
 ("617_901..619_900", "620_101..622_100"),
 ("615_901..617_900", "618_101..620_100"),
 ("615_701..617_700", "617_901..619_900"),
 ("615_901..616_100", "618_101..618_300"),
 ("615_701..615_900", "617_901..618_100"),
 ("613_701..615_700", "615_901..617_900"),
 ("613_501..615_500", "615_701..617_700"),
 ("613_701..613_900", "615_901..616_100"),
 ("613_501..613_700", "615_701..615_900"),
 ("611_501..613_500", "613_701..615_700"),
 ("611_301..613_300", "613_501..615_500"),
 ("611_301..611_500", "613_501..613_700"),
 ("611_101..611_300", "613_301..613_500"),
 ("611_101..613_100", "613_301..615_300"),
 ("609_301..611_300", "611_501..613_500"),
 ("609_101..609_300", "611_301..611_500"),
 ("609_101..611_100", "611_301..613_300"),
 ("609_301..609_500", "611_501..611_700"),
 ("607_101..609_100", "609_301..611_300"),
 ("607_101..607_300", "609_301..609_500"),
 ("606_901..608_900", "609_101..611_100"),
 ("606_901..607_100", "609_101..609_300"),
 ("604_901..606_900", "607_101..609_100"),
 # -- entry/exit rng (compound forms disambiguate BLOCKS markers from NEW texts) --
 ("entry rng=**620_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng=**618_101+j**（与 A[j] 同源配对语义逐字", "entry rng=**620_301+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng seed=**620_301+j**（法典", "entry rng seed=**622_501+j**（法典"),
 ("entry rng seed=**618_101+j**", "entry rng seed=**620_301+j**"),
 ("exit rng=**622_301+j**（法典", "exit rng=**624_501+j**（法典"),
 ("exit rng=**620_101+j**", "exit rng=**622_301+j**"),
 ("620_300+1", "622_500+1"), ("622_300+1", "624_500+1"), ("620_100+1", "622_300+1"), ("618_100+1", "620_300+1"), ("615_900+1", "618_100+1"), ("615_700+1", "617_900+1"),
 ("613_700+1", "615_900+1"), ("613_500+1", "615_700+1"),
 ("A 尾 620_100 续", "A 尾 622_300 续"), ("A 尾 617_900 续", "A 尾 620_100 续"),
 ("→jump 620_301·", "→jump 622_501·"),
 ("B 尾 620_300", "B 尾 622_500"),
 ("B 尾 618_100", "B 尾 620_300"),
 # -- stamps --
 ("@ 03:3x", "@ 05:5x"),
 ('"03:0x": 0, "03:2x": 0, "03:3x": 0', '"05:2x": 0, "05:3x": 0, "05:5x": 0'),
 ('"00:3x": 4, "00:2x": 2', '"03:2x": 4, "03:0x": 2, "03:3x": 1'),
 ('"03:2x",', '"05:3x",'),
 ("20:4x", "00:3x"), ("20:2x", "00:2x"),
 ("2026-10-19 03:06:44", "2026-10-19 05:22:20"), (" 03:06:44 (", " 05:22:20 ("), ('"2026-10-19 03:("', '"2026-10-19 05:("'),
 ("2026-10-19 03:2", "2026-10-19 05:3"), ("03:20:42", "05:31:54"),
 ("2026-10-19 03:3", "2026-10-19 05:5"), ("03:37:36", "05:55:17"),
 ("@ 03:2x", "@ 05:3x"),
 # -- RAM faces (MUST + floors-key collision flip + print note; S7/S8 SPAN-protected) --
 ('"本窗 free RAM ~4.0GB": 0', '"本窗 free RAM ~4.4GB": 0'),
 ("本窗 free RAM ~4.0GB", "本窗 free RAM " + ram_face),
 # NOTE: the r1107 canon carried a one-more-down roll ("本窗 free RAM ~3.3GB" ->
 # "本窗 free RAM ~4.0GB") -- DELETED here: 0 hits on this canon (measured) AND its OLD
 # side equals the live face when psutil reads ~3.3GB, silently un-rolling the live
 # MUST entry above back to a literal ~4.0GB (live-state bomb, r1110 sweep-proven).
 ("(~4.0GB written, MV 车道已收官 idle)", "(%s written, MV 车道已收官 idle)" % ram_face),
 # stale-face ban must be CONTEXT-SCOPED, not bare-value: the canon's bare
 # "本窗 free RAM ~4.4GB" MUST_NOT ban false-fires when the live RAM *is* 4.4GB
 # (r1110 sweep-proven); the doubled GPU-prose tail is unique to the stale long
 # form (T0 count=1, inside the long needle's consumed OLD side; the live NEW side
 # heals the doubling at birth) -- collision-free at every live value.
 ('"本窗 free RAM ~4.4GB", "95%·7.9G VRAM",', '"GPU idle 回释·MV 车道已收官 GPU idle 回释", "95%·7.9G VRAM",'),
 # live GPU face roll (MUST entry; prose handled by S8 POST_LEG)
 ("nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释", gpu_face),
 # -- RAM-anchor ledger chain protection (r1107 disclosed-heal family): the anchors are STABLE
 # historical labels; the W-chain would shift them one generation -- down-one needles let the
 # chain land the MUST series back on the TRUE labels (and extend the chain with the W274
 # ~4.0G anchor) while the BAN series keeps the shifted-label bans stable.
 ('"W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",', '"W262 冻结窗 26G bm-a 实锚", "W263 冻结窗 7G bm-c 实锚",'),
 ('"W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",', '"W264 冻结窗 3G bm-c 实锚", "W265 冻结窗 ~5G bm-c 实锚", "W266 冻结窗 ~0.1G bm-c 实锚",'),
 ('"W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",', '"W267 冻结窗 ~1.4G bm-c 实锚", "W268 冻结窗 ~2.1G bm-c 实锚", "W269 冻结窗 ~3.3G bm-c 实锚",'),
 ('"W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚",', '"W270 冻结窗 ~1.4G bm-c 实锚", "W271 冻结窗 ~0.3G bm-c 实锚", "W272 冻结窗 ~4.4G bm-c 实锚", "W273 冻结窗 ~4.0G bm-c 实锚",'),
 ('"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",', '"W263 冻结窗 26G", "W264 冻结窗 7G", "W265 冻结窗 3G", "W266 冻结窗 ~5G",'),
 ('"W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",', '"W267 冻结窗 ~0.1G", "W268 冻结窗 ~1.4G", "W269 冻结窗 ~2.1G", "W270 冻结窗 ~3.3G", "W271 冻结窗 ~1.4G", "W272 冻结窗 ~0.3G",'),
 # -- rows/ordinals descending --
 ("行 264 注册在册", "行 265 注册在册"), ("行 263 注册在册", "行 264 注册在册"),
 ("engine_owner==bm-c 93 行注册", "engine_owner==bm-c 94 行注册"), ("engine_owner==bm-c 92 行注册", "engine_owner==bm-c 93 行注册"),
 ("bmc_rows=93", "bmc_rows=94"), ("bmc_rows=92", "bmc_rows=93"),
 ("bmc rows 93+候选", "bmc rows 94+候选"), ("bmc rows 92+候选", "bmc rows 93+候选"),
 ("live rows 93 实读", "live rows 94 实读"), ("live rows 92 实读", "live rows 93 实读"),
 ("第 265 波", "第 266 波"), ("第 264 波", "第 265 波"), ("第 263 波", "第 264 波"),
 ("第九十四枚", "第九十五枚"), ("第九十三枚", "第九十四枚"), ("第九十二枚", "第九十三枚"),
 ("第 94 枚", "第 95 枚"), ("第 93 枚", "第 94 枚"), ("第 92 枚", "第 93 枚"),
 ("池第 273 枚", "池第 274 枚"), ("池第 272 枚", "池第 273 枚"), ("池第 271 枚", "池第 272 枚"),
 ("波号 275", "波号 276"), ("波号 274", "波号 275"), ("波号 273", "波号 274"),
 ("零 275 行", "零 276 行"), ("零 274 行", "零 275 行"), ("零 273 行", "零 274 行"),
 ("--wave 275/finalize --wave 275", "--wave 276/finalize --wave 276"),
 ("--wave 274/finalize --wave 274", "--wave 275/finalize --wave 275"),
 ("--wave 273/finalize --wave 273", "--wave 274/finalize --wave 274"),
 ("38th consecutive", "39th consecutive"), ("37th consecutive", "38th consecutive"),
 ("CLEAN-AT-BIRTH 7th gen", "CLEAN-AT-BIRTH 8th gen"),
 # -- floors wave-count lines (one-below; W-chain completes the roll) --
 ('"W274": 44, "W273": 61, "W272": 4, "W271": 4, "W270": 3, "W269": 3, "W268": 3, "W267": 2, "W266": 2,',
  '"W274": 45, "W273": 62, "W272": 4, "W271": 4, "W270": 3, "W269": 3, "W268": 2, "W267": 2, "W266": 2,'),
 ('"W265": 2, "W264": 2, "W263": 1, "W262": 1, "W261": 1, "W260": 1,',
  '"W264": 2, "W263": 2, "W262": 2, "W261": 1, "W260": 1, "W259": 1,'),
]
needle_counts = {}
for old, new in NEEDLES:
    needle_counts[old] = txt.count(old)
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the new VMAP roll floor) --
P1 = "\x01W\x01"
txt2 = txt
for w in range(275, 259, -1):  # W275..W260 consume descending
    if w == 275:
        txt2 = txt2.replace("W275", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W276")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w275", P2).replace("n1_w274", "n1_w275").replace("n1_w273", "n1_w274").replace("n1_w272", "n1_w273").replace(P2, "n1_w276")
txt = txt.replace("_w275bmc", P3).replace("_w274bmc", "_w275bmc").replace("_w273bmc", "_w274bmc").replace(P3, "_w276bmc")
# frozen-face filename generation component (canon derive SRC line + its pre-span header note
# reference _w27Xbmc_w27Y_frozen_face.txt; the bmc chain above rolls the prefix side only --
# this rolls the w27Y side; T0 prereg-md carries zero such refs so the SIM is unaffected)
txt = txt.replace("w274_frozen_face", "w275_frozen_face")

# ---------------- post-W-chain defect-birthplace correction pass (heals (16)/(17)) ----------------
_fix_refuser = txt.count("注册 W275 B 带 624_501..624_700 落 naive A 窗内")
txt = txt.replace("注册 W275 B 带 624_501..624_700 落 naive A 窗内",
                  "注册 W275 B 带 622_301..622_500 落 naive A 窗内")
_fix_freezer = txt.count("W276 freezer 承接面强制注记")
txt = txt.replace("W276 freezer 承接面强制注记", "W277 freezer 承接面强制注记")

# ---------------- substitute spans ----------------
for sid, sm, em, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- FULL PRE-FLIGHT SIMULATION (exec data segments + run every gate on T0) ----------------
def seg(start, end):
    i = txt.index(start)
    j = txt.index(end, i)
    return txt[i:j]

ns = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01", "SPLICE_T": "05:2x"}
exec(seg("VMAP = [", "VMAP_FLOORS = {"), ns)
exec(seg("VMAP_FLOORS = {", "def xf(t):"), ns)
exec(seg("VMAP_POST_LEGS = [", "for o, n, f in VMAP_POST_LEGS:"), ns)
exec(seg("NEW = {", "# marker pairs:"), ns)
exec(seg("BLOCKS = [", "T2 = T1"), ns)
exec(seg("MUST = [", "for s in MUST:"), ns)
exec(seg("MUST_NOT = [", "for s in MUST_NOT:"), ns)
VMAP, VMAP_FLOORS, VMAP_POST_LEGS = ns["VMAP"], ns["VMAP_FLOORS"], ns["VMAP_POST_LEGS"]
NEW, BLOCKS = ns["NEW"], ns["BLOCKS"]
MUST, MUST_NOT = ns["MUST"], ns["MUST_NOT"]
floor_report, floor_heals = [], []
for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    if f == 0:
        assert c == 0, "SIM zero-floor FAIL: %r count=%d" % (o, c)
        continue
    if c < f:
        # r1077 measured heal: rewrite the floor value in the script text
        old_line = '"%s": %d,' % (o, f)
        new_line = '"%s": %d,' % (o, c)
        assert txt.count(old_line) == 1, "floor heal anchor missing: %s" % old_line
        txt = txt.replace(old_line, new_line)
        VMAP_FLOORS[o] = c
        floor_heals.append({"key": o, "pattern": f, "measured": c})
    floor_report.append([o, f, c])
T1 = T0
for o, n in VMAP:
    T1 = T1.replace(o, n)
for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    assert c >= f, "SIM POST_LEG FAIL: %r count=%d floor=%d" % (o, c, f)
    T1 = T1.replace(o, n)
T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "SIM BLOCK %s start count=%d" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "SIM BLOCK %s end not found" % name
    j += len(em)
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", "05:2x")
    T2 = T2[:i] + NEWTXT + T2[j:]
for s in MUST:
    assert s in T2, "SIM MUST missing: %r" % s
for s in MUST_NOT:
    assert s not in T2, "SIM MUST_NOT present: %r (count=%d)" % (s, T2.count(s))
exec(seg("# ---------------- post gates ----------------", 'io.open(OUT, "w"'), dict(ns, T2=T2, re=re))
out_sha = hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16]

# ---------------- builder-level audits ----------------
MUST_NEW = ["r1110 bm-c: W276 prereg derive", "PERPETUAL_N1_W276_PREREG.md", "622_501..624_500",
            "624_501..624_700", "605,120 投影", "MSG-20261019-055x-bmc-w276-seat", "21b51a102",
            "1fcc0bc30f", "第二十五次连续 A-hop", "第二十六次连续 above-own-A",
            "e62f3bcbdfe458863bc1b98c176b6f591bcdc14e", "52b42b83b57fbcd3748bf470ab32fc25d98f10e6",
            "2026-10-19 05:22:20", "bm-c r1108 W275 §7 范式", "_r1108bmc_w275_fivekeys.json",
            "−0.09280541", "0.24507989", "−0.09398255", "（**0.3088** 实测锚）", "1,029,335", "602,920",
            "0.000316", "第 95 枚", "第 266 波", "池第 274 枚", "W275 冻结窗",
            "engine_owner==bm-c 94 行注册", "engine_owner 行 265 注册在册",
            "probe leg0 bmc_rows=94 attempt-continuity face", "bm-c 循环班 r1109 席位窗 2026-10-19 05:5x",
            "本机 bm-c 实例", "W276=bm-c own-wave window per chain-order law",
            "018782314d", "5089f02250", "e639699d59", "fc01636095",
            "W277+ 投影", "W277p_B_lands_inside_W277p_A_naive", "verify at W277 prereg",
            "_w276bmc_freeze_edits.py", "_w275bmc_freeze_edits.py 模板派生", "bm-c r1108 W275 §8 范式",
            "（上游 W275 席位已闭链=注册+烧录+finalize 全落地·零在飞）", "（W275 注册+烧录+finalize 全落地）",
            "W206/W211..W275 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "席位时即解锁", "（见 §5 item5）。",
            "R277：W276 带", "→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000316**→W275 **0.000316**→W276 投影 0.000316】",
            "622_500+1", "624_500+1", "622_301..622_500", "A_staircase_hop_past_W275_B=true",
            "B_lands_above_own_A=true", "seed_admit_gate rc0 双带 FREE", "波号 276", "零 276 行",
            "零 skip-ahead W277/W278 席位声明", "05:3x", "（占位·finalize one-pass 后回填",
            "saturation_engine.py status live-read r1110：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
            "本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗·队列空转 idle",
            "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读",
            "r1109 席位窗实跑：origin inbox 零 W276 席位外机命中", "results/p2cal_ext/n1_w275/ 12/12",
            "base=622501 span=2000", "base=624501 span=200", '"624501..626500"', '"624701..624900"',
            "estate chain r1107/r1108 W275 全周期", "CLEAN-AT-BIRTH 8th gen", "38th consecutive",
            "实差 0.0012 在带内", "n_eff_held_equal 1,027,135", "605,120",
            "注册 W275 B 带 622_301..622_500 落 naive A 窗内", "W277 freezer 承接面强制注记",
            "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276=A/B 双 1-hop 形态连续二十五波"]
# BAN = faces fully consumed by the rolls with NO recreation needle (the descending chains
# legitimately recreate the one-generation-prior faces in VMAP pair old sides / floors keys /
# CLEAN lists / MUST_NOT bans -- those are NOT banned; a face quoted ONLY inside a
# heal-documentation comment (freezer lag heal quotes its own OLD side) is also NOT banned;
# only the fully-consumed faces are).
BAN = ["6f31f6e073", "ec907d164", "b3c8a83c5c", "b4c0271044", "acf37937ec", "6659a0e362",
       "39e1bb32f1", "87d2697cdc", "f608ff1cee",
       "第 263 波", "波号 273", "第 92 枚", "bmc_rows=92", "第 262 波", "波号 272",
       "TWENTY-FOURTH consecutive", "03:06:44", "03:20:42", "03:37:36",
       "r1097", "18:4x=5", "PERPETUAL_N1_W274_PREREG.md",
       "B 尾 616_100", "→jump 620_101·", "行 262 注册在册", "（r1101 窗算法", "r1101 席位窗实跑",
       "live-read r1102：", "新鲜实读 r1102 窗", "2026-10-19 03:06:44",
       "MSG-20261018-211x", "MSG-211x owner", "（bm-c r1101 席·",
       "620_101..620_300", "618_101..618_300",
       "注册 W275 B 带 624_501..624_700"]
for s in MUST_NEW:
    assert s in txt, "AUDIT MUST missing: %r" % s
# collect-all audit: report every BAN violation with line context in one run
_viol = [(s, txt.count(s)) for s in BAN if s in txt]
if _viol:
    for s, c in _viol:
        for _ln in txt.splitlines():
            if s in _ln:
                print("VIOL %r x%d :: %s" % (s, c, _ln.strip()[:160]))
    raise SystemExit("AUDIT MUST_NOT present: %r" % (_viol,))

OUT = os.path.join(REPO, "results", "_w276bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"spans": len(SPANS), "needles": len(NEEDLES), "needle_counts": needle_counts,
           "floor_heals": floor_heals, "floor_report": floor_report,
           "ram_face": ram_face, "gpu_face": gpu_face, "sim_out_sha256_16": out_sha,
           "sim_out_bytes": len(T2.encode("utf-8")), "sim_out_lines": T2.count("\n") + 1,
           "sim_must": len(MUST), "sim_must_not": len(MUST_NOT),
           "fix_refuser_hits": _fix_refuser, "fix_freezer_hits": _fix_freezer}
io.open(os.path.join(REPO, "results", "_w276bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("SIM: derive pre-flight ALL GATES PASS | out %d bytes / %d lines sha256_16 %s" % (
    receipt["sim_out_bytes"], receipt["sim_out_lines"], out_sha))
print("floor heals: %r" % (floor_heals,))
print("defect-birthplace fixes: refuser=%d freezer=%d" % (_fix_refuser, _fix_freezer))
print("ram face %s | gpu %s" % (ram_face, gpu_face))
print("zero-needle hits (count=0, expected for consumed/protected faces): %d" % sum(1 for v in needle_counts.values() if v == 0))
