# -*- coding: utf-8 -*-
# r1107 bm-c: W275 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w274bmc_prereg_derive.py -> results/_w275bmc_prereg_derive.py.
# Zero hand-transcription of chain values into the PRODUCT: W275 bands/anchors read from the seat
# receipt + fivekeys/results jsons (r587/r1093 laws); floors MEASURED on the frozen W274 template
# (r1077 law, facts receipt results/_w275bmc_prep_facts.json) and healed in-place; complex value
# spans placeholder-protected before the general rolls. The builder pre-flights the ENTIRE derive
# transform in-memory (exec data segments + full gate run) before writing the script (r1052
# idempotent pattern). Needle evidence receipt -> results/_w275bmc_needle_probe.json.
# Same-window heals disclosed (builder-level): (a) floors W273 61->62 + W263 1->2 measured-over-
# pattern (generation drift, r1104 W263 family); W259 floor entry appended (T0 carries W259=1);
# (b) date-cross POST_LEG REMOVED (W275 seat receipt same-date 20261019 with W274 -- the lowercase
# prefix chain rolls the receipt date correctly with no date-cross leg; r1104 needed one only
# because the W273 seat receipt was dated 10-18); (c) b5 staircase wave-list span-protected and
# rolled W274->W275 appended (r1104 S15 family); (d) estate-chain/timeline faces rolled to the
# two-window W274 cycle shape (prereg r1104 + splice/finalize r1105, replaces the W273 one-window
# r1102 prose); (e) stale finalize-ts comment 00:32:48 healed to the true 03:20:42 (comment-only
# face inherited from the W273 canon).
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w275bmc_w274_frozen_face.txt"), encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23550
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "ddc158b5047596ea"
fk = json.load(open(os.path.join(REPO, "results", "_r1105bmc_w274_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w275bmc_20261019_probe_receipt.json"), encoding="utf-8"))
prep = json.load(open(os.path.join(REPO, "results", "_w275bmc_prep_facts.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [620301, 622300] and rcp["bands"]["B"] == [622301, 622500]
assert round(fk["merged"]["mu"], 8) == -0.09280110 and round(fk["merged"]["sigma"], 8) == 0.24508947
assert round(fk["w274_only"]["mu"], 8) == -0.09630486 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3009
assert round(fk["merged"]["se_mu_k600720"], 6) == 0.000316 and fk["ledger_identity"]["total"] == 1027135
assert round(fk["skill_line"]["line_pre_w274"], 4) == 1.1968 and round(fk["skill_line"]["line_merged_600720"], 4) == 1.1967
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w274_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0035 and _k1["pass"]
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
SRC = io.open(os.path.join(REPO, "results", "_w274bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected spans (slice-replace; old complex faces -> final) ----------------
def mkspan(sid, sm, em, new):
    return (sid, sm, em, new)

HDR_NEW = u'''# r1107 bm-c: W275 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w274bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W274 prereg AT THE FREEZE COMMIT 6f31f6e073 (git
# 6f31f6e073:research/PERPETUAL_N1_W274_PREREG.md, 23,550 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w275bmc_w274_frozen_face.txt by the r1107 derive window
# via python subprocess raw bytes (r1103-prep precedent folded in-window; no separate prep window;
# prep facts receipt results/_w275bmc_prep_facts.json); byte-verified: disk==blob sha256_16
# ddc158b5047596ea, freeze blob sha1 8e726cb11abf8e9ebdb1536a35e87be42f83bee1.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 761d41e899e129d5437d3526c59f5d14e6512598
# (28148 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1105
# W274 cycle (estate acf37937ec). Deriving from the backfilled face would fabricate W275 sec.7/8
# from W274 measured numbers -- the r1049/r1052 precedent requires the 6f31f6e073 frozen pre-run
# face. W275 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w275bmc_20261019_probe_receipt.json (bm-c r1106 window
#     authored+run live, seat rides origin bf4bbbde1e per r565 early-visibility law,
#     MSG-20261019-034x-bmc-w275-seat landed on origin; zero foreign W275 seat claims; zero
#     W276/W277 skip-claims). STAIRCASE CONTINUES: A naive 620_101..622_100 REFUSED at start
#     (registered W274 B band 620_101..620_300 sits INSIDE the naive A window) -> A first-clean
#     620_301..622_300 hops=1 (TWENTY-FOURTH consecutive A-hop, W274 prereg sec.5 item5
#     post-W274-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 620_301..620_500 lands INSIDE the own-wave W275 A first-clean window 620_301..622_300
#     (own-A reservation cascade) -> hop past own-A tail 622_300 -> 622_301..622_500 hops=1
#     (TWENTY-FIFTH consecutive above-own-A landing); seed_admit FREE x2 (A base=620301 span=2000 /
#     B base=622301 span=200); leg0 rows=272 owner_rows=264 bmc_rows=93 ordinal=265; leg2
#     conflicts=0; leg3 origin_vacancy=true; W276p projection: A naive 622_301..624_300 CLEAN
#     hops=0 / B naive 622_501..622_700 CLEAN hops=0 but lands inside W276p A naive.
#   - upstream W274 finalize LANDED (bm-c r1105 window one-pass, n1_w274_results.json landed via
#     acf37937ec 03:20:42, fivekeys 6/6 receipt results/_r1105bmc_w274_fivekeys.json + sec.7/8
#     backfilled): merged K=600,720 / ledger 1,027,135 EXACT (1,024,935+2,200) / merged mu
#     -0.09280109518577706 (8dp -0.09280110) / sigma 0.24508946834133466 (8dp 0.24508947) /
#     se_mu@K600,720 0.000316 (narrowed from 0.000317) / W274-only mu -0.09630486363636363
#     (8dp -0.09630486) / A p95 0.3009 / K-lift -0.0001 (first negative micro-move since W260) /
#     n_eff_held 1,024,935 / line_pre_w274 1.1968 / line_merged@600,720 1.1967 / key1 only-vs-merged
#     gap 0.0035037684505865724 (4dp 0.0035) in-band; splice ec907d164 03:06:44 (r1105 window,
#     CLEAN-AT-BIRTH 7th gen); engine self-burn 12/12 batched ledger appends b3c8a83c5c+b4c0271044;
#     sixgate 37th consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w275bmc_prep_facts.json (MEASURED live on T0 THIS
# window, r1077 measured-counts law; floors below match every measured count; disclosed floor heals:
# W273 61->62 + W263 1->2 measured-over-pattern, generation drift, healed in-place; W259 floor
# entry appended, T0 carries W259=1; zero-floor audit: every next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W274 finalize one-pass landed 03:2x (acf37937ec 03:20:42); T0
#     carries the W273-era 00:3x stamps x4 (MEASURED live THIS build, r1077 law) -> POST_LEG x4.
# (2) date-cross N/A this generation (disclosed): the W275 seat receipt is SAME-DATE with the W274
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg (the r1104 W274 build needed one only because the W273 seat receipt
#     was dated 10-18; that leg is REMOVED here).
# (3) sec.5 item1 measured keys -> W274 actuals (n1_w274_results + fivekeys machine values):
#     merged mu -0.09280110 / K=600,720 / W274-only -0.09630486 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W274-only vs merged TRUE diff = 0.0035 @4dp (measured
#     0.0035037684505865724 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24510975 -> 0.24508947 (W274 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3124 -> 0.3009 (W274 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift -0.0001 (W274 fivekeys key4, first negative micro-move
#     since W260) + line_merged@K600,720 1.1967 + lowercase line_pre_w273 -> line_pre_w274 1.1968
#     (lowercase NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) +
#     n_eff_held_equal 1,022,735 -> 1,024,935.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries stale
#     values on the W269/W272/W274 slots -> POST_LEG rewrites the tail with true history W269
#     0.000319 / W270 0.000319 / W271 0.000318 / W272 0.000317 / W273 0.000317 / W274 0.000316
#     and appends the W275 projection 0.000316.
# (9) sec.4 merged-pool anchor face: W1..W273 598,520 -> W1..W274 600,720 (W274 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1102 W273 -> bm-c r1105 W274 (cycle owner + wave roll).
# (11) RAM face live-measured THIS window: psutil %(ram).1f GB available (%(ramf)s, probe-time read) +
#     nvidia-smi %(gpu)s -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); the r1104
#     ~4.4GB face is stale.
# (12) low-RAM precedent ledger append: W274 freeze-window %(rama)s bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W272 ~0.3G onto W273 -- both restored + true W274
#     anchor appended).
# (13) seat/provenance legs: MSG-20261019-012x-bmc-w274-seat/70b21a0264/r1102 ->
#     MSG-20261019-034x-bmc-w275-seat/bf4bbbde1e/r1106 (two live faces + block NEWs).
# (14) engine live-read faces r1104 -> r1107 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled two-window: the W274 cycle = prereg r1104 (6f31f6e073)
#     + splice/burn/sixgate/finalize/fivekeys/sec78 r1105 one-window (ec907d164+acf37937ec);
#     stale finalize-ts comment 00:32:48 -> true 03:20:42 healed (comment-only face, W273 canon
#     inheritance).''' % {"ram": int(RAM), "ramf": ram_face, "gpu": gpu_face, "rama": ram_anchor}

SPANS = [
 mkspan("S1", "# r1104 bm-c: W274 prereg derive (count-asserted ordered transform + marker-extracted block replaces).",
        "#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).", HDR_NEW),
 mkspan("S2", '_blob_expect = "9b56779c8ec9ae54d41aeca862b7d18d94f479d1"',
        'assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "2f289446a93fa102", "SRC sha mismatch"',
 u'''_blob_expect = "8e726cb11abf8e9ebdb1536a35e87be42f83bee1"   # freeze-commit face @ 6f31f6e073
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "6f31f6e073:research/PERPETUAL_N1_W274_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W274_PREREG.md"])
assert _hb == "761d41e899e129d5437d3526c59f5d14e6512598", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23550, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "ddc158b5047596ea", "SRC sha mismatch"'''),
 mkspan("S3", "# --- chain-fact existence gates (zero transcription) ---",
        'assert "MSG-20261019-012x-bmc-w274-seat.md" in _seat_files, "W274 seat MSG not carried by seat commit 70b21a0264: %r" % _seat_files[:200]',
 u'''# --- chain-fact existence gates (zero transcription) ---
for sha in ("6f31f6e073", "ec907d164", "b3c8a83c5c", "b4c0271044", "acf37937ec", "bf4bbbde1e"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "ec907d164"])    # 2026-10-19 03:06:44 +0800
_m = re.match(r"2026-10-19 03:(\\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "03:%sx" % _m.group(1)[0]   # 03:0x
_fz = git_out(["show", "-s", "--format=%ci", "acf37937ec"])    # 2026-10-19 03:20:42 +0800
assert _fz.startswith("2026-10-19 03:2"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "bf4bbbde1e"])   # 2026-10-19 03:37:36 +0800
assert _st.startswith("2026-10-19 03:3"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w274_results.json"])
assert _fin_log == "acf37937ec", "W274 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "bf4bbbde1e"])
assert "MSG-20261019-034x-bmc-w275-seat.md" in _seat_files, "W275 seat MSG not carried by seat commit bf4bbbde1e: %r" % _seat_files[:200]'''),
 mkspan("S4", 'with open(os.path.join(REPO, "results", "_r1102bmc_w273_fivekeys.json"), encoding="utf-8") as f:',
        'assert fk["all_pass"] is True, "fivekeys not all_pass"',
 u'''# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1105bmc_w274_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 600720, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09280110, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24508947, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k600720"], 6) == 0.000316, "se_mu drift: %r" % fk["merged"]["se_mu_k600720"]
assert round(fk["w274_only"]["mu"], 8) == -0.09630486, "w274-only mu drift: %r" % fk["w274_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3009, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == -0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1024935, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w274"], 4) == 1.1968, "line_pre drift: %r" % fk["skill_line"]["line_pre_w274"]
assert round(fk["skill_line"]["line_merged_600720"], 4) == 1.1967, "line_merged drift: %r" % fk["skill_line"]["line_merged_600720"]
assert fk["ledger_identity"]["total"] == 1027135 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w274_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0035 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"'''),
 mkspan("S5", 'with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w273_results.json"), encoding="utf-8") as f:',
        'assert round(res9["null_pool_cumulative"]["se_mu_at_k596320"], 6) == 0.000317, "W272 se_mu chain verify"',
 u'''with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1024935
assert round(res["skill_line_v2_k_lift"]["line_pre_w274"], 4) == 1.1968
assert round(res["skill_line_v2_k_lift"]["line_merged_600720"], 4) == 1.1967
assert round(res["null_pool_cumulative"]["se_mu_at_k600720"], 6) == 0.000316, "W274 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w273_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k598520"], 6) == 0.000317, "W273 se_mu chain verify"'''),
 mkspan("S6", 'with open(os.path.join(REPO, "results", "_w274bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:',
        'assert pr["legs"]["leg4"]["W275p_B_lands_inside_W275p_A_naive"] is True',
 u'''with open(os.path.join(REPO, "results", "_w275bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [620301, 622300] and pr["bands"]["B"] == [622301, 622500]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [620101, 622100], "jump_to": 620301,
                              "refuser_pts": [], "refuser_bands": [[620101, 620300]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [620301, 620500], "jump_to": 622301,
                              "refuser_pts": [], "refuser_bands": [[620301, 622300]]}]
assert l1["B_naive"] == [620301, 620500] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W274_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W274_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W272_W273_W274_bands_respected_A"] is True and _ra["W272_W273_W274_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 272 and _l0["owner_rows"] == 264 and _l0["bmc_rows"] == 93
assert _l0["ordinal"] == 265 and _l0["w274_finalize_landed"] is True
assert _l0["w274_finalize_anchors"]["ledger_total"] == 1027135
assert _l0["w274_finalize_anchors"]["merged_n"] == 600720
assert round(_l0["w274_finalize_anchors"]["skill_line_delta_k_lift"], 4) == -0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=620301 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=622301 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W276p_A_naive"] == "622301..624300"
assert pr["legs"]["leg4"]["W276p_B_naive"] == "622501..622700"
assert pr["legs"]["leg4"]["W276p_B_lands_inside_W276p_A_naive"] is True'''),
 mkspan("S7", "# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---",
        'assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free',
 u'''# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1107 window face: probe-time read = %s available (MV lane drained, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %%.2f" %% _ram_free''' % ram_face),
 mkspan("S8", "VMAP_POST_LEGS = [", "    T1 = T1.replace(o, n)",
 u'''VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W274 finalize one-pass landed 03:2x (acf37937ec
    # 03:20:42); T1 carries the W273-era 00:3x stamps x4 (MEASURED live THIS build, r1077 law)
    ("00:3x", "03:2x", 4),
    # date-cross N/A this generation (heal (2), disclosed): W275 seat receipt same-date 20261019
    # with the W274 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg (the r1104 build needed one only because the W273 seat receipt was 10-18).
    # sec.5 item1 measured keys -> W274 actuals (n1_w274_results + fivekeys machine values)
    ("（W274 实测键 **−0.09278822**·K=598,520 合并池·W274-only 实测 **−0.095021**）",
     "（W274 实测键 **−0.09280110**·K=600,720 合并池·W274-only 实测 **−0.09630486**）", 1),
    ("W2..W274 共二百七十二面实测 mu 稳定先例", "W2..W274 共二百七十三面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W274 diff = 0.0035 @4dp (measured
    # 0.0035037684505865724 full), in-band
    ("W274-only vs merged 实差 0.0022 在带内", "W274-only vs merged 实差 0.0035 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24510975**=W274 合并池实测", "键 **0.24508947**=W274 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W274 A 档 p95（**0.3124** 实测锚）", "与 W274 A 档 p95（**0.3009** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w273 NOT rolled by the
    # W-roll; true W274 anchors K-lift -0.0001 + line_merged@K600,720 1.1967 +
    # line_pre_w274 1.1968 + n_eff_held 1,024,935)
    ("键 W274 实测 K-lift **+0.0001**·line_merged@K598,520 **1.1967**·line_pre_w273 1.1966·n_eff_held_equal 1,022,735",
     "键 W274 实测 K-lift **−0.0001**·line_merged@K600,720 **1.1967**·line_pre_w274 1.1968·n_eff_held_equal 1,024,935", 1),
    # se_mu chain true-history correction (heal (8); W274 fivekeys key5 measured 0.000316
    # narrowed from W273 0.000317)
    ("→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000317**→W275 投影 0.000317】",
     "→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 **0.000316**→W275 投影 0.000316】", 1),
    # sec.4 merged-pool anchor face (heal (9): W274 finalize landed)
    ("W1..W274 已落账 598,520 实测", "W1..W274 已落账 600,720 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W274 cycle (heal (10): bm-c r1105; OLD faces are
    # POST-VMAP faces -- the generated VMAP carries the canon's bare W-chain, so the raw T0'
    # W273-cycle rows already shifted W273->W274 before this leg fires; the leg fixes the
    # window number r1102->r1105, measured post-VMAP count=1)
    ("bm-c r1102 W274 §7 范式", "bm-c r1105 W274 §7 范式", 1),
    ("bm-c r1102 W274 §8 范式", "bm-c r1105 W274 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil %s available (%s) + %s
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1104 ~4.4GB face
    ("本窗 free RAM ~4.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=MV PACK-A GPU 道 wave-3 收官后回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 18%%·2.8G VRAM 占用·MV PACK-A i2v wave-3 已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM %s（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（%s·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W274 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- the wave-roll had shifted the W263 26G bm-a anchor onto the W264
    # label and the W272 ~0.3G onto W273; both restored + true W274 anchor appended
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 %s bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %%r count=%%d floor=%%d" %% (o, c, f))
    T1 = T1.replace(o, n)''' % (RAM, ram_face, gpu_face, ram_face, gpu_face, ram_anchor)),
 mkspan("S9",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274=A/B 双 1-hop 形态连续二十三波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274=A/B 双 1-hop 形态连续二十三波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275=A/B 双 1-hop 形态连续二十四波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"),
 mkspan("S10", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x",'),
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
 ("r1102 W273 同窗全周期先例实时间线：prereg 839441a547 落于 r1102 窗·splice 04f2127db 落于 r1102 执行窗", "r1104/r1105 W273 全周期先例实时间线：prereg 6f31f6e073 落于 r1104 窗·splice ec907d164 落于 r1105 执行窗"),
 ("estate chain r1102 W273 同窗全周期（r1102-continuation absorb-healed）839441a547+04f2127db+6659a0e362", "estate chain r1104/r1105 W273 全周期 6f31f6e073+ec907d164+acf37937ec"),
 ("席位 r1102 窗+prereg r1104 窗", "席位 r1106 窗+prereg r1107 窗"),
 ("bm-c r1102 五面冻结 splice", "bm-c r1105 五面冻结 splice"),
 ("finalize one-pass bm-c r1102 窗 00:3x", "finalize one-pass bm-c r1105 窗 03:2x"),
 # bare form (post-gates MUST list; fires AFTER the suffix needle above so it only hits the
 # MUST bare face -- the prose faces are already suffix-rolled; W273-low new side, the
 # W-chain completes W273->W274)
 ("W273 finalize one-pass bm-c r1102", "W273 finalize one-pass bm-c r1105"),
 ("bm-c r1102 席位 MSG-", "bm-c r1106 席位 MSG-"),
 ("bm-c 循环班 r1102 席位窗", "bm-c 循环班 r1106 席位窗"),
 ("2026-10-19 01:0x", "2026-10-19 03:3x"),
 ("（r1102 窗算法", "（r1106 窗算法"),
 ("bm-c r1102 席·", "bm-c r1106 席·"),
 ("r1102 席位窗实跑：origin inbox 零 W274 席位外机命中", "r1106 席位窗实跑：origin inbox 零 W275 席位外机命中"),
 ("bm-c r1102 W273 §7 范式", "bm-c r1105 W273 §7 范式"),
 ("bm-c r1102 W273 §8 范式", "bm-c r1105 W273 §8 范式"),
 ('"r1102 W273 §7 范式": 0', '"r1105 W273 §7 范式": 0'),
 ('"r1102 W273 §8 范式": 0', '"r1105 W273 §8 范式": 0'),
 # -- r blanket REPLACED with three specific engine-stamp needles (disclosed heal): the bare
 # ("r1104","r1107") also rolled the HISTORICAL timeline tokens the compound needles create
 # (estate chain r1104/r1105 -> r1107/r1105 corruption). The blanket's only legitimate
 # targets are the canon's self-window engine/MUST stamp faces (the VMAP pair NEW sides);
 # the old-side r-rolls below create the T0' faces. Comments keeping a stale r1104 are
 # cosmetic and unbanned.
 ("saturation_engine.py status live-read r1104：", "saturation_engine.py status live-read r1107："),
 ("本机 bm-c 实例·heartbeat 新鲜实读 r1104 窗", "本机 bm-c 实例·heartbeat 新鲜实读 r1107 窗"),
 ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1104 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1107 窗实读"),
 # -- r old-side rolls (create the T0 faces) --
 ("（r1101 窗算法", "（r1102 窗算法"),
 ("bm-c r1101 席·", "bm-c r1102 席·"),
 ("r1101 席位窗实跑", "r1102 席位窗实跑"),
 ("live-read r1102：", "live-read r1104："),
 # SRC frozen-face path roll (disclosed): the canon SRC line points at the W273 face
 # (_w274bmc_w273_frozen_face.txt); lowercase w273 is OUTSIDE the uppercase W-chain and the
 # _wXXbmc lowercase chain only covers the prefix -- this needle retargets SRC at the
 # extracted W274 face (verified on disk, prep receipt sha16 ddc158b5047596ea).
 ("_w274bmc_w273_frozen_face.txt", "_w275bmc_w274_frozen_face.txt"),
 ("新鲜实读 r1102 窗", "新鲜实读 r1104 窗"),
 ("新鲜 r1102 窗实读", "新鲜 r1104 窗实读"),
 # -- MSG/sha descending chains --
 ("MSG-20261019-012x", "MSG-20261019-034x"),
 ("MSG-20261018-211x", "MSG-20261019-012x"),
 ("MSG-012x owner", "MSG-034x owner"),
 ("MSG-211x owner", "MSG-012x owner"),
 ("bmc-w274-seat", "bmc-w275-seat"),
 ("bmc-w273-seat", "bmc-w274-seat"),
 ("70b21a0264", "bf4bbbde1e"),
 ("39e1bb32f1", "70b21a0264"),
 ("f608ff1cee", "39e1bb32f1"),
 ("87d2697cdc", "f608ff1cee"),
 ("839441a547", "6f31f6e073"),
 ("04f2127db", "ec907d164"),
 # derive-script print faces (outside the S2 span; cosmetic but must not print stale
 # canon shas -- the committed script's stdout stays honest)
 ("9b56779c8ec9ae54d41aeca862b7d18d94f479d1", "8e726cb11abf8e9ebdb1536a35e87be42f83bee1"),
 ("twin e204ebdd disclosed", "twin 761d41e8 disclosed"),
 ("fbb4788c49", "b3c8a83c5c"),
 ("acc7fd02c0", "b4c0271044"),
 ("6659a0e362", "acf37937ec"),
 # -- G+1 projection/vacancy consumes (descending) --
 ("W276 冻结方", "W277 冻结方"), ("W275 冻结方", "W276 冻结方"),
 ("W276p_", "W277p_"), ("W275p_", "W276p_"), ("W274p_", "W275p_"),
 ("verify at W276 prereg", "verify at W277 prereg"), ("verify at W275 prereg", "verify at W276 prereg"), ("verify at W274 prereg", "verify at W275 prereg"),
 ("零 skip-ahead W275/W276 席位声明", "零 skip-ahead W276/W277 席位声明"),
 ("零 skip-ahead W274/W275 席位声明", "零 skip-ahead W275/W276 席位声明"),
 # W+ blankets ALONE (needle-order heal, disclosed): the original compound needles
 # (5.**/probe forms, fired before the blankets) created W275+ marker/floors faces that the
 # blankets then re-rolled one generation too far (b_claim_proj/b5 count=0 in the r1107 sim
 # probe); fired after the blankets, the 5.** compound caught the freshly-blanket-rolled
 # b5 marker the same way. Both compound families are fully subsumed by the two blankets
 # (NEW texts W275+->W276+; BLOCKS markers + floors keys W274+->W275+) and are REMOVED
 # (empirically verified by the sim probe: every marker/pinned/floors face correct).
 ("W275+ 投影", "W276+ 投影"),
 ("W274+ 投影", "W275+ 投影"),
 # R-record horizon face (disclosed): the canon's R-line horizon 对 W275+ is IMMUNE to the
 # W-chain (W275 outside range 274..259) and no blanket covers the 拒面影响 form -- without
 # this needle the W275-band record keeps the W274-era horizon (semantically wrong: the
 # W275 band's refuser surface affects W276+).
 ("对 W275+ 的拒面影响", "对 W276+ 的拒面影响"),
 # §5.5 投影承接机证 compounds REMOVED (same double-roll disease): the W+ blankets above
 # roll the canon VMAP pair + floors key + §8 live placeholder; the compounds fired after
 # the blankets re-rolled the pair's OLD side onto W276+ -> no-op pair -> the T0' §8
 # placeholder §5.5 face survived unrolled into T2 (r1107 sim MUST_NOT).
 ("R276", "R277"), ("R275", "R276"), ("R274", "R275"),
 # -- Chinese ordinals descending --
 ("第二十四次连续 A-hop", "第二十五次连续 A-hop"),
 ("第二十三次连续 A-hop", "第二十四次连续 A-hop"),
 ("第二十二次连续 A-hop", "第二十三次连续 A-hop"),
 ("第二十五次连续 above-own-A", "第二十六次连续 above-own-A"),
 ("第二十四次连续 above-own-A", "第二十五次连续 above-own-A"),
 ("第二十三次连续 above-own-A", "第二十四次连续 above-own-A"),
 ("〔第二十四次连续〕", "〔第二十五次连续〕"), ("〔第二十三次连续〕", "〔第二十四次连续〕"),
 ("连续二十三波", "连续二十四波"),
 ("连续二十二波", "连续二十三波"),
 ("共二百七十二面", "共二百七十三面"),
 ("共二百七十一面", "共二百七十二面"),
 # -- ledger/K chains (newest first; b_prev projection BEFORE the 598,520 blanket) --
 ("1,024,935", "1,027,135"), ("1,022,735", "1,024,935"),
 ("1024935", "1027135"), ("1022735", "1024935"),
 ("**600,720 投影**", "**602,920 投影**"),
 ('"600,720": 0', '"602,920": 0'),
 ("598,520", "600,720"),
 ("596,320", "598,520"),
 ("598520", "600720"), ("596320", "598520"),
 # -- value faces (W274 actuals; newest first; SPAN-protected asserts exempt) --
 ("**+0.0001**", "**−0.0001**"),
 ("−0.09278822", "−0.09280110"), ("−0.09277998", "−0.09278822"), ("−0.09276412", "−0.09277998"),
 ("-0.09278822", "-0.09280110"), ("-0.09277998", "-0.09278822"),
 ("0.24510975", "0.24508947"), ("0.24509581", "0.24510975"), ("0.24509040", "0.24509581"),
 ("−0.095021", "−0.09630486"), ("−0.09706318", "−0.095021"), ("−0.10277223", "−0.09706318"),
 ("-0.095021", "-0.09630486"), ("-0.09706318", "-0.095021"),
 ("0.3124", "0.3009"), ("0.3138", "0.3124"), ("**0.3042**", "**0.3138**"), ("0.3042", "0.3138"),
 ("实差 0.0022 在带内", "实差 0.0035 在带内"), ("实差 0.0043 在带内", "实差 0.0022 在带内"), ("实差 0.0010 在带内", "实差 0.0022 在带内"),
 ("line_pre_w273 1.1966", "line_pre_w274 1.1968"), ("line_pre_w272 1.1965", "line_pre_w273 1.1966"),
 # line_merged@K compound REMOVED (same double-roll disease): the bare 598,520->600,720
 # blanket already rolls every line_merged@K face; fired later it re-rolled the BAN-list
 # line_merged@K598,520 (created by the 596,320->598,520 blanket) onto the LIVE anchor
 # line_merged@K600,720 -> generated MUST_NOT banned a face T2 legitimately carries.
 # -- band faces (descending; NEW blocks + VMAP legs + FLOORS + zero-floors + MUST + pinned) --
 ("620_301..620_500", "622_501..622_700"),
 ("620_101..622_100", "622_301..624_300"),
 ("618_101..618_300", "620_301..620_500"),
 ("617_901..619_900", "620_101..622_100"),
 ("617_901..618_100", "620_101..620_300"),
 ("618_101..620_100", "620_301..622_300"),
 ("620_101..620_300", "622_301..622_500"),
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
 ("entry rng=**618_101+j**（与 A[j] 同源配对语义逐字", "entry rng=**620_301+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng=**615_901+j**（与 A[j] 同源配对语义逐字", "entry rng=**618_101+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng seed=**618_101+j**（法典", "entry rng seed=**620_301+j**（法典"),
 ("entry rng seed=**615_901+j**", "entry rng seed=**618_101+j**"),
 ("exit rng=**620_101+j**（法典", "exit rng=**622_301+j**（法典"),
 ("exit rng=**617_901+j**", "exit rng=**620_101+j**"),
 # A-ext/B-ext compound needles REMOVED (same disease as the W-projection blankets): the bare
 # band needles already roll the canon VMAP pair defs + floors keys + MUST/BAN entries one
 # generation; fired later, the compounds re-rolled the freshly-rolled OLD sides into no-op
 # pairs (old==new, T0' count 0 -> live A-ext face unrolled into T2, r1107 sim probe). The
 # entry/exit +j compounds above are KEPT -- no bare needle covers the *+j seed forms.
 ("620_100+1", "622_300+1"), ("618_100+1", "620_300+1"), ("615_900+1", "618_100+1"), ("615_700+1", "617_900+1"),
 ("613_700+1", "615_900+1"), ("613_500+1", "615_700+1"),
 ("A 尾 617_900 续", "A 尾 620_100 续"), ("A 尾 615_700 续", "A 尾 617_900 续"),
 ("→jump 618_101·", "→jump 620_301·"),
 ("B 尾 618_100", "B 尾 620_300"),
 # -- stamps --
 ("@ 01:0x", "@ 03:3x"),
 ('"00:2x": 0, "00:3x": 0, "01:0x": 0', '"03:0x": 0, "03:2x": 0, "03:3x": 0'),
 # bare MUST-list stamp entry (quote+comma form; fires BEFORE the 20:4x blanket so the
 # BAN-list 20:4x entry rolls to the banned 00:3x form, not onto the live 03:2x stamp)
 ('"00:3x",', '"03:2x",'),
 ("20:4x", "00:3x"), ("20:2x", "00:2x"),
 ("2026-10-19 00:20:20", "2026-10-19 03:06:44"), (" 00:20:20 (", " 03:06:44 ("), ('"2026-10-19 00:("', '"2026-10-19 03:('),
 ('"00:%sx" % _m.group(1)[0]   # 00:2x', '"03:%sx" % _m.group(1)[0]   # 03:0x'),
 ("2026-10-19 00:3", "2026-10-19 03:2"), ("00:39:01", "03:20:42"),
 ("2026-10-19 01:0", "2026-10-19 03:3"), ("01:03:27", "03:37:36"),
 ("@ 00:3x", "@ 03:2x"),
 # -- RAM faces (MUST + zero-floor; POST_LEG protected by S8) --
 ("本窗 free RAM ~4.4GB", "本窗 free RAM " + ram_face),
 ("本窗 free RAM ~3.3GB", "本窗 free RAM ~4.4GB"),
 # derive print note face (script stdout honesty): the canon's hardcoded r1104-window
 # note rolls to this window's live state
 ("(~0.3GB written, MV PACK-A burn window)", "(%s written, MV 车道已收官 idle)" % ram_face),
 # zero-floor collision heal (same-window, disclosed): live RAM measured ~4.4GB == the T0'
 # W274-window face (T0' count=1) -> the needle above is a no-op on the floors key and the
 # zero-floor would fail on a face the template legitimately carries. Floors-KEY form flipped
 # to ban the W273-era stale face (~3.3GB, measured 0 on T0') instead; RAM honesty stays on
 # the S7 live gate + S8 POST_LEG heal (11). Collision-free windows: this is a zero-hit
 # (the RAM needle above already rewrote the key to the live face).
 ('"本窗 free RAM ~4.4GB": 0', '"本窗 free RAM ~3.3GB": 0'),
 # RAM-anchor ledger chain protection (disclosed heal): the low-RAM precedent anchors are
 # STABLE historical labels (W263 26G bm-a .. W273 ~4.4G) recorded in the post-gates MUST
 # list and BAN list -- the W-chain would shift them one generation (W264 26G..) and the
 # generated MUST would miss T2's true-label chain (S8 heal 12 restores true labels at
 # runtime). Down-one needles let the chain roll them back to the exact canon faces:
 # MUST series -> T2 true labels W263..W273; BAN series -> the shifted-label bans stay.
 ("W263 冻结窗 26G bm-a 实锚\", \"W264 冻结窗 7G bm-c 实锚",
  "W262 冻结窗 26G bm-a 实锚\", \"W263 冻结窗 7G bm-c 实锚"),
 ("W265 冻结窗 3G bm-c 实锚\", \"W266 冻结窗 ~5G bm-c 实锚\", \"W267 冻结窗 ~0.1G bm-c 实锚",
  "W264 冻结窗 3G bm-c 实锚\", \"W265 冻结窗 ~5G bm-c 实锚\", \"W266 冻结窗 ~0.1G bm-c 实锚"),
 ("W268 冻结窗 ~1.4G bm-c 实锚\", \"W269 冻结窗 ~2.1G bm-c 实锚\", \"W270 冻结窗 ~3.3G bm-c 实锚",
  "W267 冻结窗 ~1.4G bm-c 实锚\", \"W268 冻结窗 ~2.1G bm-c 实锚\", \"W269 冻结窗 ~3.3G bm-c 实锚"),
 ("W271 冻结窗 ~1.4G bm-c 实锚\", \"W272 冻结窗 ~0.3G bm-c 实锚\", \"W273 冻结窗 ~4.4G bm-c 实锚",
  "W270 冻结窗 ~1.4G bm-c 实锚\", \"W271 冻结窗 ~0.3G bm-c 实锚\", \"W272 冻结窗 ~4.4G bm-c 实锚"),
 ("W264 冻结窗 26G\", \"W265 冻结窗 7G\", \"W266 冻结窗 3G\", \"W267 冻结窗 ~5G",
  "W263 冻结窗 26G\", \"W264 冻结窗 7G\", \"W265 冻结窗 3G\", \"W266 冻结窗 ~5G"),
 ("W268 冻结窗 ~0.1G\", \"W269 冻结窗 ~1.4G\", \"W270 冻结窗 ~2.1G\", \"W271 冻结窗 ~3.3G\", \"W272 冻结窗 ~1.4G\", \"W273 冻结窗 ~0.3G",
  "W267 冻结窗 ~0.1G\", \"W268 冻结窗 ~1.4G\", \"W269 冻结窗 ~2.1G\", \"W270 冻结窗 ~3.3G\", \"W271 冻结窗 ~1.4G\", \"W272 冻结窗 ~0.3G"),
 # se_mu chain T2-face protection (same class): the canon's post-gates MUST carries the W274
 # prereg's raw chain; the chain would roll it onto the T1' face (heal-8 OLD) instead of the
 # T2 face (heal-8 NEW). One-low needle -> chain lands it EXACTLY on the heal-8 NEW side
 # (true history W269..W273 + W274 measured 0.000316 + W275 projection).
 ("→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 投影 0.000317】",
  "→W268 **0.000319**→W269 **0.000319**→W270 **0.000318**→W271 **0.000317**→W272 **0.000317**→W273 **0.000316**→W274 投影 0.000316】"),
 ("MV PACK-A i2v wave-3 已收官 GPU idle 回释", gpu_face),
 # -- rows/ordinals descending --
 ("行 263 注册在册", "行 264 注册在册"), ("行 262 注册在册", "行 263 注册在册"),
 ("engine_owner==bm-c 92 行注册", "engine_owner==bm-c 93 行注册"), ("engine_owner==bm-c 91 行注册", "engine_owner==bm-c 92 行注册"),
 ("bmc_rows=92", "bmc_rows=93"), ("bmc_rows=91", "bmc_rows=92"),
 ("bmc rows 92+候选", "bmc rows 93+候选"), ("bmc rows 91+候选", "bmc rows 92+候选"),
 ("live rows 92 实读", "live rows 93 实读"), ("live rows 91 实读", "live rows 92 实读"),
 ("第 264 波", "第 265 波"), ("第 263 波", "第 264 波"), ("第 262 波", "第 263 波"),
 ("第九十三枚", "第九十四枚"), ("第九十二枚", "第九十三枚"), ("第九十一枚", "第九十二枚"),
 ("第 93 枚", "第 94 枚"), ("第 92 枚", "第 93 枚"), ("第 91 枚", "第 92 枚"),
 ("池第 272 枚", "池第 273 枚"), ("池第 271 枚", "池第 272 枚"), ("池第 270 枚", "池第 271 枚"),
 ("波号 274", "波号 275"), ("波号 273", "波号 274"), ("波号 272", "波号 273"),
 ("零 274 行", "零 275 行"), ("零 273 行", "零 274 行"), ("零 272 行", "零 273 行"),
 ("--wave 274/finalize --wave 274", "--wave 275/finalize --wave 275"),
 ("--wave 273/finalize --wave 273", "--wave 274/finalize --wave 274"),
 ("--wave 272/finalize --wave 272", "--wave 273/finalize --wave 273"),
 ("36th consecutive", "37th consecutive"), ("35th consecutive", "36th consecutive"),
 ("CLEAN-AT-BIRTH 6th gen", "CLEAN-AT-BIRTH 7th gen"),
 # -- floors dict W259 append (post-W-chain becomes the W260 entry) --
 ('"W262": 1, "W261": 1, "W260": 1,', '"W262": 1, "W261": 1, "W260": 1, "W259": 1,'),
]
needle_counts = {}
for old, new in NEEDLES:
    needle_counts[old] = txt.count(old)
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the new VMAP roll floor) --
P1 = "\x01W\x01"
txt2 = txt
for w in range(274, 258, -1):  # W274..W259 consume descending
    if w == 274:
        txt2 = txt2.replace("W274", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W275")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w274", P2).replace("n1_w273", "n1_w274").replace("n1_w272", "n1_w273").replace("n1_w271", "n1_w272").replace(P2, "n1_w275")
txt = txt.replace("_w274bmc", P3).replace("_w273bmc", "_w274bmc").replace("_w272bmc", "_w273bmc").replace(P3, "_w275bmc")

# ---------------- substitute spans ----------------
for sid, sm, em, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- FULL PRE-FLIGHT SIMULATION (exec data segments + run every gate on T0) ----------------
def seg(start, end):
    i = txt.index(start)
    j = txt.index(end, i)
    return txt[i:j]

ns = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01", "SPLICE_T": "03:0x"}
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
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", "03:0x")
    T2 = T2[:i] + NEWTXT + T2[j:]
for s in MUST:
    assert s in T2, "SIM MUST missing: %r" % s
for s in MUST_NOT:
    assert s not in T2, "SIM MUST_NOT present: %r (count=%d)" % (s, T2.count(s))
exec(seg("# ---------------- post gates ----------------", 'io.open(OUT, "w"'), dict(ns, T2=T2, re=re))
out_sha = hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16]

# ---------------- builder-level audits ----------------
MUST_NEW = ["r1107 bm-c: W275 prereg derive", "PERPETUAL_N1_W275_PREREG.md", "620_301..622_300",
            "622_301..622_500", "602,920 投影", "MSG-20261019-034x-bmc-w275-seat", "bf4bbbde1e",
            "6f31f6e073", "第二十四次连续 A-hop", "第二十五次连续 above-own-A",
            "8e726cb11abf8e9ebdb1536a35e87be42f83bee1", "761d41e899e129d5437d3526c59f5d14e6512598",
            "2026-10-19 03:06:44", "bm-c r1105 W274 §7 范式", "_r1105bmc_w274_fivekeys.json",
            "−0.09280110", "0.24508947", "−0.09630486", "（**0.3009** 实测锚）", "1,027,135", "600,720",
            "0.000316", "第 94 枚", "第 265 波", "池第 273 枚", "W274 冻结窗",
            "engine_owner==bm-c 93 行注册", "engine_owner 行 264 注册在册",
            "probe leg0 bmc_rows=93 attempt-continuity face", "bm-c 循环班 r1106 席位窗 2026-10-19 03:3x",
            "本机 bm-c 实例", "W275=bm-c own-wave window per chain-order law",
            "ec907d164", "b3c8a83c5c", "b4c0271044", "acf37937ec",
            "W276+ 投影", "W276p_B_lands_inside_W276p_A_naive", "verify at W276 prereg",
            "_w275bmc_freeze_edits.py", "_w274bmc_freeze_edits.py 模板派生", "bm-c r1105 W274 §8 范式",
            "（上游 W274 席位已闭链=注册+烧录+finalize 全落地·零在飞）", "（W274 注册+烧录+finalize 全落地）",
            "W206/W211..W274 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "席位时即解锁", "（见 §5 item5）。",
            "R276：W275 带", "→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 **0.000317**→W273 **0.000317**→W274 **0.000316**→W275 投影 0.000316】",
            "620_300+1", "622_300+1", "620_101..620_300", "A_staircase_hop_past_W274_B=true",
            "B_lands_above_own_A=true", "seed_admit_gate rc0 双带 FREE", "波号 275", "零 275 行",
            "零 skip-ahead W276/W277 席位声明", "03:2x", "（占位·finalize one-pass 后回填",
            "saturation_engine.py status live-read r1107：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
            "本机 bm-c 实例·heartbeat 新鲜实读 r1107 窗·队列空转 idle",
            "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1107 窗实读",
            "r1106 席位窗实跑：origin inbox 零 W275 席位外机命中", "results/p2cal_ext/n1_w274/ 12/12",
            "base=620301 span=2000", "base=622301 span=200", '"622301..624300"', '"622501..622700"',
            "estate chain r1104/r1105 W274 全周期", "CLEAN-AT-BIRTH 7th gen", "37th consecutive",
            "实差 0.0035 在带内", "n_eff_held_equal 1,024,935", "602,920", "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275=A/B 双 1-hop 形态连续二十四波"]
BAN = ["839441a547", "04f2127db", "fbb4788c49", "acc7fd02c0", "6659a0e362", "87d2697cdc",
       "c049a57623", "c99ee20a4", "434983cb65", "42549d6df1", "d914e1a3db",
       "第 263 波", "波号 273", "第 91 枚", "bmc_rows=91", "第 262 波", "波号 272",
       "TWENTY-SECOND consecutive", "20:28:33", "20:42:48", "21:15:53", "−0.09276412", "0.24509040",
       "−0.10277223", "**0.3042**", "r1097", "18:4x=5", "bmc-w272-seat", "PERPETUAL_N1_W272_PREREG.md",
       "B 尾 613_700", "→jump 613_701", "行 261 注册在册", "（r1101 窗算法", "r1101 席位窗实跑",
       "live-read r1102：", "新鲜实读 r1102 窗", "2026-10-19 00:20:20", "00:39:01", "01:03:27",
       "MSG-20261018-211x", "MSG-211x owner", "（bm-c r1101 席·",
       "2026-10-18 21:15:53", "2026-10-18 20:28:33", "2026-10-18 20:42:48"]
for s in MUST_NEW:
    assert s in txt, "AUDIT MUST missing: %r" % s
for s in BAN:
    assert s not in txt, "AUDIT MUST_NOT present: %r (count=%d)" % (s, txt.count(s))

OUT = os.path.join(REPO, "results", "_w275bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"spans": len(SPANS), "needles": len(NEEDLES), "needle_counts": needle_counts,
           "floor_heals": floor_heals, "floor_report": floor_report,
           "ram_face": ram_face, "gpu_face": gpu_face, "sim_out_sha256_16": out_sha,
           "sim_out_bytes": len(T2.encode("utf-8")), "sim_out_lines": T2.count("\n") + 1,
           "sim_must": len(MUST), "sim_must_not": len(MUST_NOT)}
io.open(os.path.join(REPO, "results", "_w275bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("SIM: derive pre-flight ALL GATES PASS | out %d bytes / %d lines sha256_16 %s" % (
    receipt["sim_out_bytes"], receipt["sim_out_lines"], out_sha))
print("floor heals: %r" % (floor_heals,))
print("ram face %s | gpu %s" % (ram_face, gpu_face))
print("zero-needle hits (count=0, expected for consumed/protected faces): %d" % sum(1 for v in needle_counts.values() if v == 0))
