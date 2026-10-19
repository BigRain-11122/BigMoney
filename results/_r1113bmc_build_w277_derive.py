# -*- coding: utf-8 -*-
# r1113 bm-c: W277 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w276bmc_prereg_derive.py -> results/_w277bmc_prereg_derive.py.
# Zero hand-transcription of chain values into the PRODUCT: W277 bands/anchors read from the seat
# receipt + fivekeys/results jsons (r587/r1093 laws); floors MEASURED on the frozen W276 template
# (r1077 law, facts receipt results/_w277bmc_prep_facts.json). Complex value spans
# placeholder-protected before the general rolls. The builder pre-flights the ENTIRE derive
# transform in-memory (exec data segments + full gate run) before writing the script (r1052
# idempotent pattern). Needle evidence receipt -> results/_w277bmc_needle_probe.json.
# Same-window heals disclosed (builder-level, defect-birthplace law 2026-10-16):
# (a) A_hop_chain parenthetical refuser-band LINEAL DEFECT fixed at birth (r1107-family residue,
#     disclosed): the W275/W276 preregs' b_band parenthetical carried the OWN-B value in the
#     "refuser band" slot while the machine receipt's A refuser_bands = the PRIOR-wave registered B
#     (W276 receipt [[622301,622500]] vs prereg prose "refuser band 624_501..624_700"; W275
#     receipt [[620101,620300]] vs prose "refuser band 622_301..622_500"). The band needles roll
#     the parenthetical to "refuser band 626_701..626_900" (own-B, lineal); the post-W-chain pass
#     restores it to the machine-receipt face "refuser band 624_501..624_700" (W277 receipt leg1
#     A refuser_bands=[[624501,624700]] = the registered W276 B) -- count-asserted both sides.
# (b) r1110 heal (16) refuser-prose restore is DEAD this generation (the SRC face is already
#     correct: prose "注册 W275 B 带 622_301..622_500 落 naive A 窗内" rolls naturally to
#     "注册 W276 B 带 624_501..624_700 落 naive A 窗内" via needle+W-chain) -- per the r1110
#     dead-needle law the pass is DELETED, 0-hit confirmed. r1110 heal (17) freezer-label unlag
#     is re-confirmed STRUCTURAL (the label sits ONE ABOVE the W-chain top and never rolls
#     naturally: r1110 "W276 freezer"->"W277 freezer" needed the pass; this window
#     "W277 freezer"->"W278 freezer" needs it again) -- the pass is RE-APPLIED as a standing
#     leg, count-asserted.
# (c) floors stamp entries rolled to measured (05:3x=4 / 05:2x=2 / 05:5x=1 positive floors for
#     the T0-consumed stamps + 07:2x/07:4x/08:1x zero-floors); MUST_NOT stamp run extended with
#     the W275-era 05:xx bans (S10).
# (d) date-cross N/A this generation (W277 seat receipt same-date 20261019 with the W276 -- the
#     lowercase prefix chain rolls the receipt date with no date-cross leg).
# (e) GPU doubled-prose ban ("MV 车道已收官 GPU idle 回释·MV 车道已收官 GPU idle 回释") DROPPED -- the
#     r1110 POST_LEG healed the doubling at birth, the face is 0 on this SRC (dead ban deleted);
#     the ancient "95%·7.9G VRAM" ban carried (lineage, sweep-verified).
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w277bmc_w276_frozen_face.txt"), encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23554
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "5352c7cf343fc5e5"
fk = json.load(open(os.path.join(REPO, "results", "_r1111bmc_w276_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w277bmc_20261019_probe_receipt.json"), encoding="utf-8"))
prep = json.load(open(os.path.join(REPO, "results", "_w277bmc_prep_facts.json"), encoding="utf-8"))
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [624701, 626700] and rcp["bands"]["B"] == [626701, 626900]
assert round(fk["merged"]["mu"], 8) == -0.09278451 and round(fk["merged"]["sigma"], 8) == 0.24508562
assert round(fk["w276_only"]["mu"], 8) == -0.08705886 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.305
assert round(fk["merged"]["se_mu_k605120"], 6) == 0.000315 and fk["ledger_identity"]["total"] == 1031535
assert round(fk["skill_line"]["line_pre_w276"], 4) == 1.1968 and round(fk["skill_line"]["line_merged_605120"], 4) == 1.1969
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w276_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0057 and _k1["pass"]
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
SRC = io.open(os.path.join(REPO, "results", "_w276bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected spans (slice-replace; old complex faces -> final) ----------------
def mkspan(sid, sm, em, new):
    return (sid, sm, em, new)

HDR_NEW = u'''# r1113 bm-c: W277 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w276bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W276 prereg AT THE FREEZE COMMIT 770a47fa1f (git
# 770a47fa1f:research/PERPETUAL_N1_W276_PREREG.md, 23,554 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w277bmc_w276_frozen_face.txt by the r1113 derive window
# prep leg (python subprocess raw bytes; prep facts receipt results/_w277bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 5352c7cf343fc5e5, freeze blob sha1 daa87d01f7a9deb0238b5ddd3112498f64409c0d.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 46f0b537a01a8cb12e2bfeff5547431c23492341
# (27745 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1111
# W276 cycle (estate e781164e41). Deriving from the backfilled face would fabricate W277 sec.7/8
# from W276 measured numbers -- the r1049/r1052 precedent requires the 770a47fa1f frozen pre-run
# face. W277 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w277bmc_20261019_probe_receipt.json (bm-c r1112 window
#     authored+run live, seat rides origin c5f8b88f91 per r565 early-visibility law,
#     MSG-20261019-080x-bmc-w277-seat landed on origin; zero foreign W277 seat claims; zero
#     W278/W279 skip-claims). STAIRCASE CONTINUES: A naive 624_501..626_500 REFUSED at start
#     (registered W276 B band 624_501..624_700 sits INSIDE the naive A window) -> A first-clean
#     624_701..626_700 hops=1 (TWENTY-SIXTH consecutive A-hop, W276 prereg sec.5 item5
#     post-W276-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 624_701..624_900 lands INSIDE the own-wave W277 A first-clean window 624_701..626_700
#     (own-A reservation cascade) -> hop past own-A tail 626_700 -> 626_701..626_900 hops=1
#     (TWENTY-SEVENTH consecutive above-own-A landing); seed_admit FREE x2 (A base=624701 span=2000 /
#     B base=626701 span=200); leg0 rows=274 owner_rows=266 bmc_rows=95 ordinal=267; leg2
#     conflicts=0; leg3 origin_vacancy=true; W278p projection: A naive 626_701..628_700 CLEAN
#     hops=0 / B naive 626_901..627_100 CLEAN hops=0 but lands inside W278p A naive.
#   - upstream W276 finalize LANDED (bm-c r1111 window one-pass, n1_w276_results.json landed via
#     e781164e41 07:47:43, fivekeys 6/6 receipt results/_r1111bmc_w276_fivekeys.json + sec.7/8
#     backfilled): merged K=605,120 / ledger 1,031,535 EXACT (1,029,335+2,200) / merged mu
#     -0.09278451381544156 (8dp -0.09278451) / sigma 0.2450856226849218 (8dp 0.24508562) /
#     se_mu@K605,120 0.000315 (narrowing-held from W275 0.000316) / W276-only mu -0.08705886363636364
#     (8dp -0.08705886) / A p95 0.3088->0.305 (in-band) / K-lift +0.0001
#     (sign-flip positive) / n_eff_held 1,029,335 / line_pre_w276 1.1968 / line_merged@605,120
#     1.1969 / key1 only-vs-merged gap 0.005725650179077918 (4dp 0.0057) in-band; splice
#     354a645155 07:28:56 (r1111 window, engine batches df7dedfd07+627c4e10f2 tail-shard carried);
#     sixgate 39th consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w277bmc_prep_facts.json (MEASURED live on T0 THIS
# window, r1077 measured-counts law; floors below match every measured count; zero-floor audit:
# every next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W276 finalize one-pass landed 07:4x (e781164e41 07:47:43); T0
#     carries the W275-era 05:3x stamps x4 (MEASURED live THIS build, r1077 law) -> POST_LEG x4.
# (2) date-cross N/A this generation (disclosed): the W277 seat receipt is SAME-DATE with the W276
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg.
# (3) sec.5 item1 measured keys -> W276 actuals (n1_w276_results + fivekeys machine values):
#     merged mu -0.09278451 / K=605,120 / W276-only -0.08705886 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W276-only vs merged TRUE diff = 0.0057 @4dp (measured
#     0.005725650179077918 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24507989 -> 0.24508562 (W276 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3088 -> 0.305 (W276 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift +0.0001 (W276 fivekeys key4, sign-flip positive) +
#     line_merged@K605,120 1.1969 + lowercase line_pre_w275 -> line_pre_w276 1.1968 (lowercase
#     NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,027,135 -> 1,029,335.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries the
#     stale projection on the W276 slot -> POST_LEG rewrites the tail with true history W271 0.000319 /
#     W272 0.000319 / W273 0.000318 / W274 0.000317 / W275 0.000316 / W276 0.000315 and appends
#     the W277 projection 0.000315.
# (9) sec.4 merged-pool anchor face: W1..W276 602,920 -> W1..W276 605,120 (W276 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1108 W275 -> bm-c r1111 W276 (cycle owner + wave roll).
# (11) RAM face live-measured THIS window: psutil %(ram)d GB available (%(ramf)s, probe-time read) +
#     nvidia-smi %(gpu)s -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); the r1110
#     ~3.8GB face is stale.
# (12) low-RAM precedent ledger append: W276 freeze-window %(rama)s bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; pre-shift needles land the MUST series
#     back on the TRUE labels W263..W275 + the new W276 anchor).
# (13) seat/provenance legs: MSG-20261019-055x-bmc-w276-seat/21b51a102/r1109 ->
#     MSG-20261019-080x-bmc-w277-seat/c5f8b88f91/r1112 (two live faces + block NEWs).
# (14) engine live-read faces r1110 -> r1113 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled two-window: the W276 cycle = prereg r1110 (770a47fa1f)
#     + splice/burn/sixgate/finalize/fivekeys/sec78 r1111 one-window (354a645155+e781164e41).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) A_hop_chain parenthetical refuser-band lineal defect fixed at birth (see builder heal (a)):
#     post-W-chain pass restores the parenthetical to the machine-receipt face (registered W276 B
#     band 624_501..624_700 refused the naive W277 A start -- receipt leg1
#     refuser_bands=[[624501,624700]]); the band needles had rolled it to the own-B value
#     (r1107-family lineal residue, disclosed + count-asserted).
# (17) r1110 heal (17) freezer-label unlag re-confirmed STRUCTURAL and re-applied (the label
#     sits one above the W-chain top and never rolls naturally; universe face rolls naturally).''' % {"ram": int(RAM), "ramf": ram_face, "gpu": gpu_face, "rama": ram_anchor}

SPANS = [
 mkspan("S1", "# r1110 bm-c: W276 prereg derive (count-asserted ordered transform + marker-extracted block replaces).",
        "#     (the W277 freezer consumes the post-W276 universe per the W276 seat receipt leg4 note).", HDR_NEW),
 mkspan("S2", '_blob_expect = "e62f3bcbdfe458863bc1b98c176b6f591bcdc14e"',
        'assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "e4e1ce44f5afd03b", "SRC sha mismatch"',
 u'''_blob_expect = "daa87d01f7a9deb0238b5ddd3112498f64409c0d"   # freeze-commit face @ 770a47fa1f
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "770a47fa1f:research/PERPETUAL_N1_W276_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W276_PREREG.md"])
assert _hb == "46f0b537a01a8cb12e2bfeff5547431c23492341", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23554, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "5352c7cf343fc5e5", "SRC sha mismatch"'''),
 mkspan("S3", "# --- chain-fact existence gates (zero transcription) ---",
        'assert "MSG-20261019-055x-bmc-w276-seat.md" in _seat_files, "W276 seat MSG not carried by seat commit 21b51a102: %r" % _seat_files[:200]',
 u'''# --- chain-fact existence gates (zero transcription) ---
for sha in ("770a47fa1f", "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41", "c5f8b88f91"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "354a645155"])    # 2026-10-19 07:28:56 +0800
_m = re.match(r"2026-10-19 07:(\\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "07:%sx" % _m.group(1)[0]   # 07:2x
_fz = git_out(["show", "-s", "--format=%ci", "e781164e41"])    # 2026-10-19 07:47:43 +0800
assert _fz.startswith("2026-10-19 07:4"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "c5f8b88f91"])   # 2026-10-19 08:13:22 +0800
assert _st.startswith("2026-10-19 08:1"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w276_results.json"])
assert _fin_log == "e781164e41", "W276 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "c5f8b88f91"])
assert "MSG-20261019-080x-bmc-w277-seat.md" in _seat_files, "W277 seat MSG not carried by seat commit c5f8b88f91: %r" % _seat_files[:200]'''),
 mkspan("S4", 'with open(os.path.join(REPO, "results", "_r1108bmc_w275_fivekeys.json"), encoding="utf-8") as f:',
        'assert fk["all_pass"] is True, "fivekeys not all_pass"',
 u'''# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1111bmc_w276_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 605120, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09278451, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24508562, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k605120"], 6) == 0.000315, "se_mu drift: %r" % fk["merged"]["se_mu_k605120"]
assert round(fk["w276_only"]["mu"], 8) == -0.08705886, "w276-only mu drift: %r" % fk["w276_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.305, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1029335, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w276"], 4) == 1.1968, "line_pre drift: %r" % fk["skill_line"]["line_pre_w276"]
assert round(fk["skill_line"]["line_merged_605120"], 4) == 1.1969, "line_merged drift: %r" % fk["skill_line"]["line_merged_605120"]
assert fk["ledger_identity"]["total"] == 1031535 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w276_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0057 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"'''),
 mkspan("S5", 'with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8") as f:',
        'assert round(res9["null_pool_cumulative"]["se_mu_at_k600720"], 6) == 0.000316, "W274 se_mu chain verify"',
 u'''with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w276_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1029335
assert round(res["skill_line_v2_k_lift"]["line_pre_w276"], 4) == 1.1968
assert round(res["skill_line_v2_k_lift"]["line_merged_605120"], 4) == 1.1969
assert round(res["null_pool_cumulative"]["se_mu_at_k605120"], 6) == 0.000315, "W276 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k602920"], 6) == 0.000316, "W275 se_mu chain verify"'''),
 mkspan("S6", 'with open(os.path.join(REPO, "results", "_w276bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:',
        'assert pr["legs"]["leg4"]["W277p_B_lands_inside_W277p_A_naive"] is True',
 u'''with open(os.path.join(REPO, "results", "_w277bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [624701, 626700] and pr["bands"]["B"] == [626701, 626900]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [624501, 626500], "jump_to": 624701,
                              "refuser_pts": [], "refuser_bands": [[624501, 624700]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [624701, 624900], "jump_to": 626701,
                              "refuser_pts": [], "refuser_bands": [[624701, 626700]]}]
assert l1["B_naive"] == [624701, 624900] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W276_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W276_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W274_W275_W276_bands_respected_A"] is True and _ra["W274_W275_W276_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 274 and _l0["owner_rows"] == 266 and _l0["bmc_rows"] == 95
assert _l0["ordinal"] == 267 and _l0["w276_finalize_landed"] is True
assert _l0["w276_finalize_anchors"]["ledger_total"] == 1031535
assert _l0["w276_finalize_anchors"]["merged_n"] == 605120
assert round(_l0["w276_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=624701 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=626701 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W278p_A_naive"] == "626701..628700"
assert pr["legs"]["leg4"]["W278p_B_naive"] == "626901..627100"
assert pr["legs"]["leg4"]["W278p_B_lands_inside_W278p_A_naive"] is True'''),
 mkspan("S7", "# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---",
        'assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free',
 u'''# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1113 window face: probe-time read = %s available (MV lane drained, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %%.2f" %% _ram_free''' % ram_face),
 mkspan("S8", "VMAP_POST_LEGS = [", "    T1 = T1.replace(o, n)",
 u'''VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W276 finalize one-pass landed 07:4x (e781164e41
    # 07:47:43); T1 carries the W275-era 05:3x stamps x4 (MEASURED live THIS build, r1077 law)
    ("05:3x", "07:4x", 4),
    # date-cross N/A this generation (heal (2), disclosed): W277 seat receipt same-date 20261019
    # with the W276 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg.
    # sec.5 item1 measured keys -> W276 actuals (n1_w276_results + fivekeys machine values)
    ("（W276 实测键 **−0.09280541**·K=602,920 合并池·W276-only 实测 **−0.09398255**）",
     "（W276 实测键 **−0.09278451**·K=605,120 合并池·W276-only 实测 **−0.08705886**）", 1),
    ("W2..W276 共二百七十四面实测 mu 稳定先例", "W2..W276 共二百七十五面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W276 diff = 0.0057 @4dp (measured
    # 0.005725650179077918 full), in-band
    ("W276-only vs merged 实差 0.0012 在带内", "W276-only vs merged 实差 0.0057 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24507989**=W276 合并池实测", "键 **0.24508562**=W276 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W276 A 档 p95（**0.3088** 实测锚）", "与 W276 A 档 p95（**0.305** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w275 NOT rolled by the
    # W-roll; true W276 anchors K-lift +0.0001 sign-flip + line_merged@K605,120 1.1969 +
    # line_pre_w276 1.1968 + n_eff_held 1,029,335)
    ("键 W276 实测 K-lift **−0.0001**·line_merged@K602,920 **1.1967**·line_pre_w275 1.1968·n_eff_held_equal 1,027,135",
     "键 W276 实测 K-lift **+0.0001**·line_merged@K605,120 **1.1969**·line_pre_w276 1.1968·n_eff_held_equal 1,029,335", 1),
    # se_mu chain true-history correction (heal (8); W276 fivekeys key5 measured 0.000315
    # narrowing-held from W275 0.000316)
    ("→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000316**→W277 投影 0.000316】",
     "→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000315**→W277 投影 0.000315】", 1),
    # sec.4 merged-pool anchor face (heal (9): W276 finalize landed)
    ("W1..W276 已落账 602,920 实测", "W1..W276 已落账 605,120 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W276 cycle (heal (10): bm-c r1111; OLD faces are
    # POST-VMAP faces -- the raw T0' W275-cycle rows already shifted W275->W276 before this leg
    # fires; the leg fixes the window number r1108->r1111, measured post-VMAP count=1)
    ("bm-c r1108 W276 §7 范式", "bm-c r1111 W276 §7 范式", 1),
    ("bm-c r1108 W276 §8 范式", "bm-c r1111 W276 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil %s available (%s) + %s
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1110 ~3.8GB face
    ("本窗 free RAM ~3.8GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM %s（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（%s）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W276 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- pre-shift needles land the MUST series on the TRUE labels W263..W275;
    # this leg restores the POST-VMAP shifted ledger and appends the true W276 anchor
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚·W276 冻结窗 ~3.8G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 %s bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %%r count=%%d floor=%%d" %% (o, c, f))
    T1 = T1.replace(o, n)''' % (RAM, ram_face, gpu_face, ram_face, gpu_face, ram_anchor)),
 mkspan("S9",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276=A/B 双 1-hop 形态连续二十五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276=A/B 双 1-hop 形态连续二十五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277=A/B 双 1-hop 形态连续二十六波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"),
 mkspan("S10", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x",'),
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
 ("r1107/r1108 W275 全周期先例实时间线：prereg 1fcc0bc30f 落于 r1107 窗·splice 018782314d 落于 r1108 执行窗", "r1110/r1111 W275 全周期先例实时间线：prereg 770a47fa1f 落于 r1110 窗·splice 354a645155 落于 r1111 执行窗"),
 ("estate chain r1107/r1108 W275 全周期 1fcc0bc30f+018782314d+fc01636095", "estate chain r1110/r1111 W275 全周期 770a47fa1f+354a645155+e781164e41"),
 ("席位 r1109 窗+prereg r1110 窗", "席位 r1112 窗+prereg r1113 窗"),
 ("bm-c r1108 五面冻结 splice", "bm-c r1111 五面冻结 splice"),
 ("finalize one-pass bm-c r1108 窗 05:3x", "finalize one-pass bm-c r1111 窗 07:4x"),
 # bare form (post-gates MUST list; fires AFTER the suffix needle above so it only hits the
 # MUST bare face -- the prose faces are already suffix-rolled; W275-low new side, the
 # W-chain completes W275->W276)
 ("W275 finalize one-pass bm-c r1108", "W275 finalize one-pass bm-c r1111"),
 ("bm-c r1109 席位 MSG-", "bm-c r1112 席位 MSG-"),
 ("bm-c 循环班 r1109 席位窗", "bm-c 循环班 r1112 席位窗"),
 ("2026-10-19 05:5x", "2026-10-19 08:1x"),
 ("（r1109 窗算法", "（r1112 窗算法"),
 ("bm-c r1109 席·", "bm-c r1112 席·"),
 ("r1109 席位窗实跑：origin inbox 零 W276 席位外机命中", "r1112 席位窗实跑：origin inbox 零 W277 席位外机命中"),
 ("bm-c r1108 W275 §7 范式", "bm-c r1111 W275 §7 范式"),
 ("bm-c r1108 W275 §8 范式", "bm-c r1111 W275 §8 范式"),
 ('"r1108 W275 §7 范式": 0', '"r1111 W275 §7 范式": 0'),
 ('"r1108 W275 §8 范式": 0', '"r1111 W275 §8 范式": 0'),
 # -- r blanket REPLACED with three specific engine-stamp needles (r1110 disclosed-heal family):
 ("saturation_engine.py status live-read r1110：", "saturation_engine.py status live-read r1113："),
 ("本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗", "本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗"),
 ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读"),
 # -- r old-side rolls (create the T0 faces) --
 ("（r1106 窗算法", "（r1109 窗算法"),
 ("bm-c r1106 席·", "bm-c r1109 席·"),
 ("r1106 席位窗实跑", "r1109 席位窗实跑"),
 ("live-read r1107：", "live-read r1110："),
 ("新鲜实读 r1107 窗", "新鲜实读 r1110 窗"),
 ("新鲜 r1107 窗实读", "新鲜 r1110 窗实读"),
 # -- MSG/sha descending chains --
 ("MSG-20261019-055x", "MSG-20261019-080x"),
 ("MSG-20261019-034x", "MSG-20261019-055x"),
 ("MSG-20261019-012x", "MSG-20261019-034x"),
 ("MSG-055x owner", "MSG-080x owner"),
 ("MSG-034x owner", "MSG-055x owner"),
 ("MSG-012x owner", "MSG-034x owner"),
 ("bmc-w276-seat", "bmc-w277-seat"),
 ("bmc-w275-seat", "bmc-w276-seat"),
 ("bmc-w274-seat", "bmc-w275-seat"),
 ("21b51a102", "c5f8b88f91"),
 ("bf4bbbde1e", "21b51a102"),
 ("70b21a0264", "bf4bbbde1e"),
 ("39e1bb32f1", "70b21a0264"),
 ("f608ff1cee", "39e1bb32f1"),
 ("87d2697cdc", "f608ff1cee"),
 ("1fcc0bc30f", "770a47fa1f"),
 ("018782314d", "354a645155"),
 # derive-script print faces (outside the S2 span; cosmetic but must not print stale
 # canon shas -- the committed script's stdout stays honest)
 ("e62f3bcbdfe458863bc1b98c176b6f591bcdc14e", "daa87d01f7a9deb0238b5ddd3112498f64409c0d"),
 ("twin 52b42b83 disclosed", "twin 46f0b537 disclosed"),
 ("5089f02250", "df7dedfd07"),
 ("e639699d59", "627c4e10f2"),
 ("fc01636095", "e781164e41"),
 ("acf37937ec", "fc01636095"),
 # -- G+1 projection/vacancy consumes (descending) --
 ("W278 冻结方", "W279 冻结方"), ("W277 冻结方", "W278 冻结方"), ("W276 冻结方", "W277 冻结方"),
 ("W278p_", "W279p_"), ("W277p_", "W278p_"), ("W276p_", "W277p_"),
 ("verify at W277 prereg", "verify at W278 prereg"), ("verify at W276 prereg", "verify at W277 prereg"),
 ("零 skip-ahead W277/W278 席位声明", "零 skip-ahead W278/W279 席位声明"),
 ("零 skip-ahead W276/W277 席位声明", "零 skip-ahead W277/W278 席位声明"),
 # W+ blankets ALONE (needle-order heal, r1107 family: compounds subsumed by the blankets)
 ("W277+ 投影", "W278+ 投影"),
 ("W276+ 投影", "W277+ 投影"),
 # R-record horizon face (disclosed heal, r1107 family)
 ("对 W277+ 的拒面影响", "对 W278+ 的拒面影响"),
 ("R278", "R279"), ("R277", "R278"), ("R276", "R277"), ("R275", "R276"),
 # -- Chinese ordinals descending --
 ("第二十六次连续 A-hop", "第二十七次连续 A-hop"),
 ("第二十五次连续 A-hop", "第二十六次连续 A-hop"),
 ("第二十四次连续 A-hop", "第二十五次连续 A-hop"),
 ("第二十六次连续 above-own-A", "第二十七次连续 above-own-A"),
 ("第二十五次连续 above-own-A", "第二十六次连续 above-own-A"),
 ("第二十四次连续 above-own-A", "第二十五次连续 above-own-A"),
 ("〔第二十六次连续〕", "〔第二十七次连续〕"), ("〔第二十五次连续〕", "〔第二十六次连续〕"),
 ("连续二十六波", "连续二十七波"),
 ("连续二十五波", "连续二十六波"),
 ("连续二十四波", "连续二十五波"),
 ("共二百七十四面", "共二百七十五面"),
 ("共二百七十三面", "共二百七十四面"),
 # -- ledger/K chains (newest first; b_prev projection BEFORE the 602,920 blanket) --
 # K-lift sign-flip compound (W276 fivekeys key4 +0.0001 vs W275 -0.0001) + line_merged value
 # move (1.1967 -> 1.1969 @K605,120): MUST-list faces must land on the W276 actuals, and these
 # compound needles must fire BEFORE the bare 602,920 blanket consumes the K face.
 ("键 W275 实测 K-lift **−0.0001**", "键 W275 实测 K-lift **+0.0001**"),
 ("line_merged@K602,920 **1.1967**", "line_merged@K605,120 **1.1969**"),
 ("1,029,335", "1,031,535"), ("1,027,135", "1,029,335"), ("1,024,935", "1,027,135"),
 ("1029335", "1031535"), ("1027135", "1029335"), ("1024935", "1027135"),
 ("**605,120 投影**", "**607,320 投影**"),
 ('"605,120": 0', '"607,320": 0'),
 ("602,920", "605,120"),
 ("600,720", "602,920"),
 ("605120", "607320"), ("602920", "605120"), ("600720", "602920"),
 # -- value faces (W276 actuals; newest first; SPAN-protected asserts exempt) --
 ("−0.09280541", "−0.09278451"), ("−0.09280110", "−0.09280541"), ("−0.09278822", "−0.09280110"),
 ("-0.09280541", "-0.09278451"), ("-0.09280110", "-0.09280541"),
 ("0.24507989", "0.24508562"), ("0.24508947", "0.24507989"), ("0.24510975", "0.24508947"),
 ("−0.09398255", "−0.08705886"), ("−0.09630486", "−0.09398255"), ("−0.095021", "−0.09630486"),
 ("-0.09398255", "-0.08705886"), ("-0.09630486", "-0.09398255"),
 ("0.3088", "0.305"), ("0.3009", "0.3088"), ("0.3124", "0.3009"),
 ("实差 0.0012 在带内", "实差 0.0057 在带内"), ("实差 0.0035 在带内", "实差 0.0012 在带内"), ("实差 0.0022 在带内", "实差 0.0035 在带内"),
 ("line_pre_w275 1.1968", "line_pre_w276 1.1968"), ("line_pre_w274 1.1968", "line_pre_w275 1.1968"),
 # se_mu chain MUST-entry T2-face protection (r1107/r1110 disclosed-heal family): the chain would
 # roll the MUST entry onto the stale projection value; one-low needle corrects the W275 slot to
 # the W276 measured 0.000315 (the W-chain lands it on the W276 slot) + the projection value --
 # SAME slot structure as the r1110 precedent (never add a slot: the final entry must equal the
 # POST_LEG NEW side exactly).
 ("→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000316**→W275 **0.000316**→W276 投影 0.000316】",
  "→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000316**→W275 **0.000315**→W276 投影 0.000315】"),
 # -- band faces (descending; own-before-prior heals the r1107 double-roll disease; NEW blocks +
 # VMAP legs + FLOORS + zero-floors + MUST + pinned all ride the same blankets) --
 ("624_701..624_900", "626_901..627_100"),
 ("624_501..626_500", "626_701..628_700"),
 ("622_501..622_700", "624_701..624_900"),
 ("622_301..624_300", "624_501..626_500"),
 ("622_501..624_500", "624_701..626_700"),
 ("624_501..624_700", "626_701..626_900"),
 ("620_301..622_300", "622_501..624_500"),
 ("622_301..622_500", "624_501..624_700"),
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
 ("entry rng=**622_501+j**（与 A[j] 同源配对语义逐字", "entry rng=**624_701+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng=**620_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng seed=**622_501+j**（法典", "entry rng seed=**624_701+j**（法典"),
 ("entry rng seed=**620_301+j**", "entry rng seed=**622_501+j**"),
 ("exit rng=**624_501+j**（法典", "exit rng=**626_701+j**（法典"),
 ("exit rng=**622_301+j**", "exit rng=**624_501+j**"),
 ("622_500+1", "624_700+1"), ("624_500+1", "626_700+1"), ("622_300+1", "624_500+1"), ("620_300+1", "622_500+1"), ("620_100+1", "622_300+1"), ("618_100+1", "620_300+1"), ("615_900+1", "618_100+1"), ("615_700+1", "617_900+1"),
 ("613_700+1", "615_900+1"), ("613_500+1", "615_700+1"),
 ("A 尾 622_300 续", "A 尾 624_500 续"), ("A 尾 620_100 续", "A 尾 622_300 续"),
 ("→jump 622_501·", "→jump 624_701·"),
 ("B 尾 622_500", "B 尾 624_700"),
 ("B 尾 620_300", "B 尾 622_500"),
 # -- stamps --
 ("@ 05:5x", "@ 08:1x"),
 ('"05:2x": 0, "05:3x": 0, "05:5x": 0', '"07:2x": 0, "07:4x": 0, "08:1x": 0'),
 ('"03:2x": 4, "03:0x": 2, "03:3x": 1', '"05:3x": 4, "05:2x": 2, "05:5x": 1'),
 ('"05:3x",', '"07:4x",'),
 ("2026-10-19 05:22:20", "2026-10-19 07:28:56"), (" 05:22:20 (", " 07:28:56 ("), ('"2026-10-19 05:("', '"2026-10-19 07:("'),
 ("2026-10-19 05:3", "2026-10-19 07:4"), ("05:31:54", "07:47:43"),
 ("2026-10-19 05:5", "2026-10-19 08:1"), ("05:55:17", "08:13:22"),
 ("@ 05:3x", "@ 07:4x"),
 # -- RAM faces (MUST + floors-key collision flip + print note; S7/S8 SPAN-protected) --
 ('"本窗 free RAM ~4.4GB": 0', '"本窗 free RAM ~4.0GB": 0'),
 ("本窗 free RAM ~3.8GB", "本窗 free RAM " + ram_face),
 # NOTE: the r1110 canon carried a one-more-down roll ("本窗 free RAM ~3.3GB" ->
 # "本窗 free RAM ~4.0GB") -- DELETED there per the live-state bomb law and stays deleted:
 # 0 hits on this canon (measured) AND its OLD side could equal the live face at psutil ~3.3GB.
 ("(~3.8GB written, MV 车道已收官 idle)", "(%s written, MV 车道已收官 idle)" % ram_face),
 # stale-face ban must be CONTEXT-SCOPED, not bare-value: the live RAM face is injected by the
 # POST_LEG/MUST needles; the ancient "95%·7.9G VRAM" ban is lineage-carried (sweep-verified);
 # the r1110 doubled-GPU-prose ban is DROPPED (0 hits on this SRC -- the doubling was healed at
 # birth by the r1110 POST_LEG; dead ban deleted per the r1110 pit law).
 ('"GPU idle 回释·MV 车道已收官 GPU idle 回释", "95%·7.9G VRAM",', '"95%·7.9G VRAM",'),
 # live GPU face roll (MUST entry; prose handled by S8 POST_LEG)
 ("nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释", gpu_face),
 # -- RAM-anchor ledger chain protection (r1110 disclosed-heal family): the anchors are STABLE
 # historical labels; the W-chain would shift them one generation -- down-one needles let the
 # chain land the MUST series back on the TRUE labels (and extend the chain with the W275
 # ~3.8G anchor) while the BAN series keeps the shifted-label bans stable.
 ('"W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",', '"W262 冻结窗 26G bm-a 实锚", "W263 冻结窗 7G bm-c 实锚",'),
 ('"W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",', '"W264 冻结窗 3G bm-c 实锚", "W265 冻结窗 ~5G bm-c 实锚", "W266 冻结窗 ~0.1G bm-c 实锚",'),
 ('"W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",', '"W267 冻结窗 ~1.4G bm-c 实锚", "W268 冻结窗 ~2.1G bm-c 实锚", "W269 冻结窗 ~3.3G bm-c 实锚",'),
 ('"W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚",', '"W270 冻结窗 ~1.4G bm-c 实锚", "W271 冻结窗 ~0.3G bm-c 实锚", "W272 冻结窗 ~4.4G bm-c 实锚", "W273 冻结窗 ~4.0G bm-c 实锚", "W274 冻结窗 ~3.8G bm-c 实锚",'),
 ('"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",', '"W263 冻结窗 26G", "W264 冻结窗 7G", "W265 冻结窗 3G", "W266 冻结窗 ~5G",'),
 ('"W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",', '"W267 冻结窗 ~0.1G", "W268 冻结窗 ~1.4G", "W269 冻结窗 ~2.1G", "W270 冻结窗 ~3.3G", "W271 冻结窗 ~1.4G", "W272 冻结窗 ~0.3G",'),
 # -- rows/ordinals descending --
 ("行 265 注册在册", "行 266 注册在册"), ("行 264 注册在册", "行 265 注册在册"),
 ("engine_owner==bm-c 94 行注册", "engine_owner==bm-c 95 行注册"), ("engine_owner==bm-c 93 行注册", "engine_owner==bm-c 94 行注册"),
 ("bmc_rows=94", "bmc_rows=95"), ("bmc_rows=93", "bmc_rows=94"),
 ("bmc rows 94+候选", "bmc rows 95+候选"), ("bmc rows 93+候选", "bmc rows 94+候选"),
 ("live rows 94 实读", "live rows 95 实读"), ("live rows 93 实读", "live rows 94 实读"),
 ("第 266 波", "第 267 波"), ("第 265 波", "第 266 波"), ("第 264 波", "第 265 波"),
 ("第九十五枚", "第九十六枚"), ("第九十四枚", "第九十五枚"), ("第九十三枚", "第九十四枚"),
 ("第 95 枚", "第 96 枚"), ("第 94 枚", "第 95 枚"), ("第 93 枚", "第 94 枚"),
 ("池第 274 枚", "池第 275 枚"), ("池第 273 枚", "池第 274 枚"), ("池第 272 枚", "池第 273 枚"),
 ("波号 276", "波号 277"), ("波号 275", "波号 276"), ("波号 274", "波号 275"),
 ("零 276 行", "零 277 行"), ("零 275 行", "零 276 行"), ("零 274 行", "零 275 行"),
 ("--wave 276/finalize --wave 276", "--wave 277/finalize --wave 277"),
 ("--wave 275/finalize --wave 275", "--wave 276/finalize --wave 276"),
 ("--wave 274/finalize --wave 274", "--wave 275/finalize --wave 275"),
 ("39th consecutive", "40th consecutive"), ("38th consecutive", "39th consecutive"),
 ("CLEAN-AT-BIRTH 8th gen", "CLEAN-AT-BIRTH 9th gen"),
 ("CLEAN-AT-BIRTH 7th gen", "CLEAN-AT-BIRTH 8th gen"),
 # -- floors wave-count lines (one-below; W-chain completes the roll; values = prep measured) --
 ('"W275": 45, "W274": 62, "W273": 4, "W272": 4, "W271": 3, "W270": 3, "W269": 2, "W268": 2, "W267": 2,',
  '"W275": 44, "W274": 62, "W273": 4, "W272": 4, "W271": 3, "W270": 3, "W269": 3, "W268": 2, "W267": 2,'),
 ('"W265": 2, "W264": 2, "W263": 2, "W262": 1, "W261": 1, "W259": 1,',
  '"W264": 2, "W263": 2, "W262": 2, "W261": 1, "W260": 1, "W259": 1,'),
]
needle_counts = {}
for old, new in NEEDLES:
    needle_counts[old] = txt.count(old)
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the new VMAP roll floor) --
P1 = "\x01W\x01"
txt2 = txt
for w in range(276, 260, -1):  # W276..W261 consume descending
    if w == 276:
        txt2 = txt2.replace("W276", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W277")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w276", P2).replace("n1_w275", "n1_w276").replace("n1_w274", "n1_w275").replace(P2, "n1_w277")
txt = txt.replace("_w276bmc", P3).replace("_w275bmc", "_w276bmc").replace("_w274bmc", "_w275bmc").replace(P3, "_w277bmc")
# frozen-face filename generation component (canon derive SRC line + its pre-span header note
# reference _w27Xbmc_w27Y_frozen_face.txt; the bmc chain above rolls the prefix side only --
# this rolls the w27Y side; T0 prereg-md carries zero such refs so the SIM is unaffected)
txt = txt.replace("w275_frozen_face", "w276_frozen_face")

# ---------------- post-W-chain defect-birthplace correction pass (heal (16)) ----------------
# A_hop_chain parenthetical refuser-band lineal defect (r1107-family residue, disclosed): the
# band needles rolled the parenthetical "refuser band" slot to the OWN-B value (626_701..626_900);
# the W277 receipt leg1 A refuser_bands=[[624501,624700]] = the registered W276 B band. The pass
# restores the machine-receipt face, count-asserted fail-closed on both sides.
_fix_hits = txt.count("refuser band 626_701..626_900〕")
assert _fix_hits == 1, "refuser-band heal anchor count=%d (expect 1)" % _fix_hits
txt = txt.replace("refuser band 626_701..626_900〕", "refuser band 624_501..624_700〕")
assert txt.count("refuser band 626_701..626_900〕") == 0, "refuser-band heal residue"
assert txt.count("refuser band 624_501..624_700〕") == 1, "refuser-band healed face count"
# r1110 heal-17 family re-confirmed STRUCTURAL (not dead): the b_claim freezer label sits ONE
# ABOVE the W-chain top (W277 vs top W276) and never rolls naturally -- every generation needs
# the post-W-chain unlag pass (the r1110 window needed the same; universe face post-W276 rolls
# naturally, label does not).
_fix_freezer = txt.count("W277 freezer 承接面强制注记")
assert _fix_freezer == 1, "freezer heal anchor count=%d (expect 1)" % _fix_freezer
txt = txt.replace("W277 freezer 承接面强制注记", "W278 freezer 承接面强制注记")
assert txt.count("W277 freezer 承接面强制注记") == 0, "freezer heal residue"
# r1110 heal-16 (refuser PROSE) dead-pass confirmed (0 hits; the natural own-before-prior chain
# lands the prose correct this generation -- disclosed, NOT re-applied)
_dead_refuser = txt.count("注册 W276 B 带 626_701..626_900 落 naive A 窗内")
assert _dead_refuser == 0, "r1110 heal-16 would double-roll: face present"

# ---------------- substitute spans ----------------
for sid, sm, em, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- FULL PRE-FLIGHT SIMULATION (exec data segments + run every gate on T0) ----------------
def seg(start, end):
    i = txt.index(start)
    j = txt.index(end, i)
    return txt[i:j]

ns = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01", "SPLICE_T": "07:2x"}
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
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", "07:2x")
    T2 = T2[:i] + NEWTXT + T2[j:]
for s in MUST:
    assert s in T2, "SIM MUST missing: %r" % s
for s in MUST_NOT:
    assert s not in T2, "SIM MUST_NOT present: %r (count=%d)" % (s, T2.count(s))
exec(seg("# ---------------- post gates ----------------", 'io.open(OUT, "w"'), dict(ns, T2=T2, re=re))
out_sha = hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16]

# ---------------- builder-level audits ----------------
MUST_NEW = ["r1113 bm-c: W277 prereg derive", "PERPETUAL_N1_W277_PREREG.md", "624_701..626_700",
            "626_701..626_900", "607,320 投影", "MSG-20261019-080x-bmc-w277-seat", "c5f8b88f91",
            "770a47fa1f", "第二十六次连续 A-hop", "第二十七次连续 above-own-A",
            "daa87d01f7a9deb0238b5ddd3112498f64409c0d", "46f0b537a01a8cb12e2bfeff5547431c23492341",
            "2026-10-19 07:28:56", "bm-c r1111 W276 §7 范式", "_r1111bmc_w276_fivekeys.json",
            "−0.09278451", "0.24508562", "−0.08705886", "（**0.305** 实测锚）", "1,031,535", "605,120",
            "0.000315", "第 96 枚", "第 267 波", "池第 275 枚", "W276 冻结窗",
            "engine_owner==bm-c 95 行注册", "engine_owner 行 266 注册在册",
            "probe leg0 bmc_rows=95 attempt-continuity face", "bm-c 循环班 r1112 席位窗 2026-10-19 08:1x",
            "本机 bm-c 实例", "W277=bm-c own-wave window per chain-order law",
            "354a645155", "df7dedfd07", "627c4e10f2", "e781164e41",
            "W278+ 投影", "W278p_B_lands_inside_W278p_A_naive", "verify at W278 prereg",
            "_w277bmc_freeze_edits.py", "_w276bmc_freeze_edits.py 模板派生", "bm-c r1111 W276 §8 范式",
            "（上游 W276 席位已闭链=注册+烧录+finalize 全落地·零在飞）", "（W276 注册+烧录+finalize 全落地）",
            "W206/W211..W276 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "席位时即解锁", "（见 §5 item5）。",
            "R278：W277 带", "→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000315**→W277 投影 0.000315】",
            "624_700+1", "626_700+1", "624_501..624_700", "A_staircase_hop_past_W276_B=true",
            "B_lands_above_own_A=true", "seed_admit_gate rc0 双带 FREE", "波号 277", "零 277 行",
            "零 skip-ahead W278/W279 席位声明", "07:4x", "（占位·finalize one-pass 后回填",
            "saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
            "本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle",
            "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读",
            "r1112 席位窗实跑：origin inbox 零 W277 席位外机命中", "results/p2cal_ext/n1_w276/ 12/12",
            "base=624701 span=2000", "base=626701 span=200", '"626701..628700"', '"626901..627100"',
            "estate chain r1110/r1111 W276 全周期", "CLEAN-AT-BIRTH 9th gen", "39th consecutive",
            "实差 0.0057 在带内", "n_eff_held_equal 1,029,335", "607,320",
            "键 W276 实测 K-lift **+0.0001**", "line_merged@K605,120 **1.1969**",
            "注册 W276 B 带 624_501..624_700 落 naive A 窗内", "W278 freezer 承接面强制注记",
            "refuser band 624_501..624_700〕",
            "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277=A/B 双 1-hop 形态连续二十六波"]
# BAN = faces fully consumed by the rolls with NO recreation needle (the descending chains
# legitimately recreate the one-generation-prior faces in VMAP pair old sides / floors keys /
# CLEAN lists / MUST_NOT bans -- those are NOT banned; heal-doc-comment quotes are NOT banned;
# only the fully-consumed faces are; live-value-collidable faces are banned CONTEXT-SCOPED only).
BAN = ["1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "6659a0e362",
       "39e1bb32f1", "87d2697cdc", "f608ff1cee", "70b21a0264", "acf37937ec",
       "第 264 波", "波号 274", "第 93 枚", "bmc_rows=93", "第 263 波", "波号 273",
       "TWENTY-FIFTH consecutive", "05:22:20", "05:31:54", "05:55:17",
       "r1097", "18:4x=5", "PERPETUAL_N1_W275_PREREG.md",
       "B 尾 620_300", "→jump 622_501·", "行 263 注册在册", "（r1106 窗算法", "r1106 席位窗实跑",
       "live-read r1107：", "新鲜实读 r1107 窗", "2026-10-19 05:22:20",
       "MSG-20261019-012x", "MSG-012x owner", "（bm-c r1106 席·",
       "620_101..620_300", "618_101..618_300",
       "注册 W276 B 带 626_701..626_900 落 naive A 窗内", "refuser band 626_701..626_900〕"]
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

OUT = os.path.join(REPO, "results", "_w277bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"spans": len(SPANS), "needles": len(NEEDLES), "needle_counts": needle_counts,
           "floor_heals": floor_heals, "floor_report": floor_report,
           "ram_face": ram_face, "gpu_face": gpu_face, "sim_out_sha256_16": out_sha,
           "sim_out_bytes": len(T2.encode("utf-8")), "sim_out_lines": T2.count("\n") + 1,
           "sim_must": len(MUST), "sim_must_not": len(MUST_NOT),
           "fix_refuser_paren_hits": _fix_hits, "fix_freezer_hits": _fix_freezer,
           "dead_refuser_pass_hits": _dead_refuser}
io.open(os.path.join(REPO, "results", "_w277bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("SIM: derive pre-flight ALL GATES PASS | out %d bytes / %d lines sha256_16 %s" % (
    receipt["sim_out_bytes"], receipt["sim_out_lines"], out_sha))
print("floor heals: %r" % (floor_heals,))
print("defect-birthplace fixes: refuser_paren=%d freezer=%d (dead r1110 heal-16 refuser-prose: %d)" % (
    _fix_hits, _fix_freezer, _dead_refuser))
print("ram face %s | gpu %s" % (ram_face, gpu_face))
print("zero-needle hits (count=0, expected for consumed/protected faces): %d" % sum(1 for v in needle_counts.values() if v == 0))
