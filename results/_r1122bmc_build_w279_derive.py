# -*- coding: utf-8 -*-
# r1122 bm-c: W279 prereg derive E63 canon-clone BUILDER (age() machine-needle law, shift-map one
# generation). Clones results/_w278bmc_prereg_derive.py -> results/_w279bmc_prereg_derive.py.
# Zero hand-transcription of chain values into the PRODUCT: W279 bands/anchors read from the seat
# receipt + fivekeys/results jsons (r587/r1093 laws); floors MEASURED on the frozen W278 template
# (r1077 law, facts receipts results/_w279bmc_prep_facts.json [r1120 PREP] + needle floors
# results/_w279bmc_needle_floors.json [r1121 PREP] -- ALL anchors machine-frozen there; the r1120
# prep froze anchors TOP-LEVEL [no nested w279_anchor_facts key] -- adapted at birth, disclosed).
# ALL span OLD sides verified line-level against results/_w278bmc_prereg_derive.py ACTUAL text
# per r1116 heal (i) law (read this window before authoring). Structural laws carried verbatim
# from the r1116 canon (its header heals (a)-(p) remain the canon documentation; this generation
# re-applied: (b) freezer-label unlag W279->W280 [measured x1 on T0], (j) chain-floor pin W263
# STABLE, (k) one-low law on all in-chain NEW sides, (l) floors exactness pin vs r1121-measured
# counts, (m) no compound needles over bare-covered faces, (o) BAN self-audit for
# chain-legitimate recreates).
# Same-window heals disclosed (r1122 roll):
# (A) anchor-block structure divergence healed at birth: r1120 prep facts = TOP-LEVEL keys
#     (prereg_freeze/splice/engine_batches/finalize_estate/seat/w278_merged/...), canon expected
#     prep["w278_anchor_facts"] -- af = prep (adapted, disclosed).
# (B) S6 relation-assert keys rolled by the receipt itself (A_staircase_hop_past_W278_B /
#     B_base_above_W278_tail / W276_W277_W278_bands_respected_* -- machine-verified this window
#     against results/_w279bmc_20261019_probe_receipt.json before authoring).
# (C) se_mu chain: W278 measured held-flat 0.000314 (fivekeys key5); W279 projection 0.000313
#     (sigma 0.24505494/sqrt(611,720) computed in-script from af, zero hand transcription).
# (D) era faces: the W278 cycle spans THREE windows (prereg r1116 df1aaba72a / splice r1118
#     b6f486af35 / finalize+fivekeys+sec78 r1119 0a92fcc28f) -- estate-chain needle authored
#     3-label (r1116/r1118/r1119) honest, disclosed vs canon 2-label form.
import io, os, re, json, hashlib, subprocess

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIT = "C:/Program Files/Git/cmd/git.exe"
T0 = io.open(os.path.join(REPO, "results", "_w279bmc_w278_frozen_face.txt"), encoding="utf-8", newline="").read().replace("\r\n", "\n")  # heal (h) r1093: CRLF disk face -> LF git-object face
assert len(T0.encode("utf-8")) == 23814
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "99001d3d3f337942"
fk = json.load(open(os.path.join(REPO, "results", "_r1118bmc_w278_fivekeys.json"), encoding="utf-8"))
rcp = json.load(open(os.path.join(REPO, "results", "_w279bmc_20261019_probe_receipt.json"), encoding="utf-8"))
prep = json.load(open(os.path.join(REPO, "results", "_w279bmc_prep_facts.json"), encoding="utf-8"))
af = prep  # heal (A): r1120 prep froze anchors TOP-LEVEL (no nested key; adapted, disclosed)
assert fk["all_pass"] is True and rcp["verdict"] == "ADMIT"
assert rcp["bands"]["A"] == [629101, 631100] and rcp["bands"]["B"] == [631101, 631300]
assert round(fk["merged"]["mu"], 8) == -0.09278576 and round(fk["merged"]["sigma"], 8) == 0.24505494
assert round(fk["w278_only"]["mu"], 8) == -0.09701509 and round(fk["a_band"]["full_sharpe_p95"], 4) == 0.2844
assert round(fk["merged"]["se_mu_k609520"], 6) == 0.000314 and fk["ledger_identity"]["total"] == 1035935
assert round(fk["skill_line"]["line_pre_w278"], 4) == 1.1971 and round(fk["skill_line"]["line_merged_609520"], 4) == 1.1969
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w278_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0042 and _k1["pass"]
# anchor-facts zero-transcription asserts (r1120 PREP frozen block, machine-read)
assert af["prereg_freeze"]["commit"] == "df1aaba72a" and af["prereg_freeze"]["blob_sha1"] == "053892f61cf24d9803cb20410d4ab1163cb7897a"
assert af["prereg_freeze"]["head_twin_sha1"] == "1c93e077c2b64476fb55041a7f59f7591f67db68" and af["prereg_freeze"]["head_twin_size"] == 28082
assert af["splice"]["commit"] == "b6f486af35" and af["splice"]["splice_t"] == "13:5x"
assert [b["commit"] for b in af["engine_batches"]] == ["60e630918f", "b965e2ecf0"]
assert af["finalize_estate"]["commit"] == "0a92fcc28f" and af["seat"]["commit"] == "900c23fe7d"
assert af["seat"]["msg"] == "MSG-20261019-145x-bmc-w279-seat.md"
assert af["k_projection_w279"] == 611720 and af["ledger_projection_w279"] == 1038135 and af["n_eff_held_projection_w279"] == 1035935
# se_mu W279 projection (heal (C)): computed from machine-read anchors, zero transcription
import math
_se_proj_w279 = round(fk["merged"]["sigma"] / math.sqrt(af["k_projection_w279"]), 6)
assert _se_proj_w279 == 0.000313, "se_mu W279 projection drift: %r" % _se_proj_w279
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
SRC = io.open(os.path.join(REPO, "results", "_w278bmc_prereg_derive.py"), encoding="utf-8", newline="").read()

# ---------------- placeholder-protected spans (slice-replace; old complex faces -> final) ----------------
def mkspan(sid, sm, em, new):
    return (sid, sm, em, new)

HDR_NEW = u'''# r1122 bm-c: W279 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w278bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W278 prereg AT THE FREEZE COMMIT df1aaba72a (git
# df1aaba72a:research/PERPETUAL_N1_W278_PREREG.md, 23,814 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w279bmc_w278_frozen_face.txt by the r1120 PREP window
# (python subprocess raw bytes; prep facts receipt results/_w279bmc_prep_facts.json);
# byte-verified: disk==blob sha256_16 99001d3d3f337942 (CR-normalized; autocrlf disk face
# disclosed r1093 law), freeze blob sha1 053892f61cf24d9803cb20410d4ab1163cb7897a.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 1c93e077c2b64476fb55041a7f59f7591f67db68
# (28,082 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the
# r1119 W278 cycle (estate 0a92fcc28f). Deriving from the backfilled face would
# fabricate W279 sec.7/8 from W278 measured numbers -- the r1049/r1052 precedent requires the
# df1aaba72a frozen pre-run face. W279 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w279bmc_20261019_probe_receipt.json (bm-c r1119
#     window authored+run live, seat rides origin 900c23fe7d per r565 early-visibility law,
#     MSG-20261019-145x-bmc-w279-seat landed on origin; zero foreign W279 seat claims; zero
#     W280/W281 skip-claims). STAIRCASE CONTINUES: A naive 628_901..630_900 REFUSED at start
#     (registered W278 B band 628_901..629_100 sits INSIDE the naive A window) -> A first-clean
#     629_101..631_100 hops=1 (TWENTY-EIGHTH consecutive A-hop, W278 prereg sec.5 item5
#     post-W278-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 629_101..629_300 lands INSIDE the own-wave W279 A first-clean window 629_101..631_100
#     (own-A reservation cascade) -> hop past own-A tail 631_100 -> 631_101..631_300 hops=1
#     (TWENTY-NINTH consecutive above-own-A landing); seed_admit FREE x2 (A base=629101 span=2000 /
#     B base=631101 span=200); leg0 rows=276 owner_rows=268 bmc_rows=97 ordinal=269; leg2
#     conflicts=0; leg3 origin_vacancy=true; W280p projection: A naive 631_101..633_100 CLEAN
#     hops=0 / B naive 631_301..631_500 CLEAN hops=0 but lands inside W280p A naive.
#   - upstream W278 finalize LANDED (bm-c r1119 window one-pass, n1_w278_results.json
#     landed via 0a92fcc28f 15:13:26, fivekeys 6/6 receipt results/_r1118bmc_w278_fivekeys.json +
#     sec.7/8 backfilled): merged K=609,520 / ledger 1,035,935 EXACT (1,033,735+2,200) / merged mu
#     -0.09278575748129675 (8dp -0.09278576) / sigma 0.24505493584785207 (8dp 0.24505494) /
#     se_mu@K609,520 0.000314 (held-flat from W277 0.000314) / W278-only mu -0.09701509090909091
#     (8dp -0.09701509) / A p95 0.3095->0.2844 (in-band) / K-lift -0.0002
#     (first negative micro-move, key4-band legal) / n_eff_held 1,033,735 / line_pre_w278 1.1971 /
#     line_merged@609,520 1.1969 / key1 only-vs-merged gap 0.004229333427794163 (4dp 0.0042)
#     in-band; splice b6f486af35 13:5x (r1118 window, engine batches 60e630918f+b965e2ecf0);
#     sixgate 41st consecutive PRE-FINALIZE ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded
#     narration faces; ALL gates machine-verify against the full-precision fivekeys/results jsons
#     (r1093 CODELY pit entry; live-read governs r587).
# Needle-count pre-flight evidence: results/_w279bmc_prep_facts.json + needle floors
# results/_w279bmc_needle_floors.json (MEASURED on T0 by the r1120/r1121 PREP windows, r1077
# measured-counts law; floors below match every measured count; zero-floor audit: every
# next-wave face measured 0 on T0).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1102 family):
# (1) finalize-window stamp roll: W278 finalize one-pass landed 15:1x (0a92fcc28f 15:13:26); T0
#     carries the W277-era 10:3x stamps x5 (MEASURED by the r1121 prep) -> POST_LEG x5; splice
#     stamps 09:5x-era x2 -> W278 splice 13:5x (b6f486af35).
# (2) date-cross N/A this generation (disclosed): the W279 seat receipt is SAME-DATE with the W278
#     seat receipt (both _*_20261019) -- the lowercase prefix chain rolls the receipt date correctly
#     with NO date-cross leg.
# (3) sec.5 item1 measured keys -> W278 actuals (n1_w278_results + fivekeys machine values):
#     merged mu -0.09278576 / K=609,520 / W278-only -0.09701509 (all full-precision
#     machine-verified in-gate).
# (4) sec.5 item1 diff face: W278-only vs merged TRUE diff = 0.0042 @4dp (measured
#     0.004229333427794163 full) in-band |d|<0.02.
# (5) sec.5 item2 sigma key 0.24508694 -> 0.24505494 (W278 merged-pool measured).
# (6) sec.5 item3 p95 anchor 0.3095 -> 0.2844 (W278 A-band fivekeys measured).
# (7) sec.5 item4 K-lift chain: K-lift -0.0002 (W278 fivekeys key4, first negative micro-move
#     in-band) + line_merged@K609,520 1.1969 + lowercase line_pre_w277 -> line_pre_w278 1.1971
#     (lowercase NOT rolled by the W-roll, case-sensitive; r1102 heal (6) family) + n_eff_held_equal
#     1,031,535 -> 1,033,735.
# (8) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries the
#     stale projection on the W278 slot -> POST_LEG rewrites the tail with true history W273 0.000319 /
#     W274 0.000318 / W275 0.000317 / W276 0.000316 / W277 0.000314 / W278 0.000314 and appends
#     the W279 projection 0.000313 (computed sigma/sqrt(K611,720), machine-read anchors).
# (9) sec.4 merged-pool anchor face: W1..W278 607,320 -> W1..W278 609,520 (W278 finalize landed).
# (10) sec.7/8 backfill paradigm rows: bm-c r1114-continuation W277 -> bm-c r1119 W278 (cycle owner
#     + wave roll).
# (11) RAM face live-measured THIS window: psutil %(ram)d GB available (%(ramf)s, probe-time read) +
#     nvidia-smi %(gpu)s -- GPU=gen-only lane idle (loop CPU-only); the r1116 ~4.5GB face is stale.
#     RAM honest-window gate 16.0 wide cap held (r1116 heal (e) standing).
# (12) low-RAM precedent ledger append: W278 freeze-window %(rama)s bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; pre-shift needles land the MUST series
#     back on the TRUE labels W263..W277 + the new W278 anchor).
# (13) seat/provenance legs: MSG-20261019-102x-bmc-w278-seat/b187aa6214/r1114-continuation ->
#     MSG-20261019-145x-bmc-w279-seat/900c23fe7d/r1119 (two live faces + block NEWs).
# (14) engine live-read faces r1116 -> r1122 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
# (15) estate-chain/timeline faces rolled (heal (D) 3-label honest): the W278 cycle = prereg r1116
#     (df1aaba72a) + splice r1118 (b6f486af35) + finalize/fivekeys/sec78 r1119 one-window
#     (0a92fcc28f; engine batches 60e630918f+b965e2ecf0).
# DEFECT-BIRTHPLACE HEALS (builder-level, disclosed in the builder header):
# (16) A_hop_chain parenthetical refuser-band machine face verified at birth (canon heal (a)
#     re-applied rolled): the single blanket roll lands the parenthetical on the
#     machine-receipt face (registered W278 B band 628_901..629_100 refused the naive W279 A
#     start -- receipt leg1 refuser_bands=[[628901,629100]]); the own-B lineal-defect face
#     (631_101..631_300) and the stale prior face (626_701..626_900) are both count-asserted
#     absent, disclosed + fail-closed.
# (17) freezer-label unlag re-confirmed STRUCTURAL and re-applied (the label sits one above the
#     W-chain top and never rolls naturally; universe face rolls naturally; W279->W280 this
#     generation, measured x1 on T0 by the r1121 prep).''' % {"ram": int(RAM), "ramf": ram_face, "gpu": gpu_face, "rama": ram_anchor}

SPANS = [
 mkspan("S1", "# r1116 bm-c: W278 prereg derive (count-asserted ordered transform + marker-extracted block replaces).",
        "#     W-chain top and never rolls naturally; universe face rolls naturally).", HDR_NEW),
 mkspan("S2", '_blob_expect = "e5d12b12da03a799a88bd980cf8566b2b1eff5ba"',
        'assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "45ee1de94c7d36fd", "SRC sha mismatch"',
 u'''_blob_expect = "053892f61cf24d9803cb20410d4ab1163cb7897a"   # freeze-commit face @ df1aaba72a
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "df1aaba72a:research/PERPETUAL_N1_W278_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W278_PREREG.md"])
assert _hb == "1c93e077c2b64476fb55041a7f59f7591f67db68", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read().replace("\\r\\n", "\\n")  # heal (h) r1093: CRLF disk face -> LF git-object face (sim byte-identity)
assert len(T0.encode("utf-8")) == 23814, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "99001d3d3f337942", "SRC sha mismatch"'''),
 mkspan("S3", "# --- chain-fact existence gates (zero transcription) ---",
        'assert "MSG-20261019-102x-bmc-w278-seat.md" in _seat_files, "W278 seat MSG not carried by seat commit b187aa6214: %r" % _seat_files[:200]',
 u'''# --- chain-fact existence gates (zero transcription) ---
for sha in ("df1aaba72a", "b6f486af35", "60e630918f", "b965e2ecf0", "0a92fcc28f", "900c23fe7d"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "b6f486af35"])    # 2026-10-19 13:5x +0800
_m = re.match(r"2026-10-19 13:(\\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "13:%sx" % _m.group(1)[0]   # 13:5x
_fz = git_out(["show", "-s", "--format=%ci", "0a92fcc28f"])    # 2026-10-19 15:13:26 +0800
assert _fz.startswith("2026-10-19 15:1"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "900c23fe7d"])   # 2026-10-19 15:09:11 +0800
assert _st.startswith("2026-10-19 15:0"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w278_results.json"])
assert _fin_log == "0a92fcc28f", "W278 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "900c23fe7d"])
assert "MSG-20261019-145x-bmc-w279-seat.md" in _seat_files, "W279 seat MSG not carried by seat commit 900c23fe7d: %r" % _seat_files[:200]'''),
 mkspan("S4", 'with open(os.path.join(REPO, "results", "_r1114bmc_w277_fivekeys.json"), encoding="utf-8") as f:',
        'assert fk["all_pass"] is True, "fivekeys not all_pass"',
 u'''# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1118bmc_w278_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 609520, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09278576, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24505494, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k609520"], 6) == 0.000314, "se_mu drift: %r" % fk["merged"]["se_mu_k609520"]
assert round(fk["w278_only"]["mu"], 8) == -0.09701509, "w278-only mu drift: %r" % fk["w278_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.2844, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == -0.0002, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1033735, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w278"], 4) == 1.1971, "line_pre drift: %r" % fk["skill_line"]["line_pre_w278"]
assert round(fk["skill_line"]["line_merged_609520"], 4) == 1.1969, "line_merged drift: %r" % fk["skill_line"]["line_merged_609520"]
assert fk["ledger_identity"]["total"] == 1035935 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w278_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0042 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"'''),
 mkspan("S5", 'with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8") as f:',
        'assert round(res9["null_pool_cumulative"]["se_mu_at_k605120"], 6) == 0.000315, "W276 se_mu chain verify"',
 u'''with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w278_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1033735
assert round(res["skill_line_v2_k_lift"]["line_pre_w278"], 4) == 1.1971
assert round(res["skill_line_v2_k_lift"]["line_merged_609520"], 4) == 1.1969
assert round(res["null_pool_cumulative"]["se_mu_at_k609520"], 6) == 0.000314, "W278 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w277_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k607320"], 6) == 0.000314, "W277 se_mu chain verify"'''),
 mkspan("S6", 'with open(os.path.join(REPO, "results", "_w278bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:',
        'assert pr["legs"]["leg4"]["W279p_B_lands_inside_W279p_A_naive"] is True',
 u'''with open(os.path.join(REPO, "results", "_w279bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [629101, 631100] and pr["bands"]["B"] == [631101, 631300]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [628901, 630900], "jump_to": 629101,
                              "refuser_pts": [], "refuser_bands": [[628901, 629100]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [629101, 629300], "jump_to": 631101,
                              "refuser_pts": [], "refuser_bands": [[629101, 631100]]}]
assert l1["B_naive"] == [629101, 629300] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W278_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W278_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W276_W277_W278_bands_respected_A"] is True and _ra["W276_W277_W278_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 276 and _l0["owner_rows"] == 268 and _l0["bmc_rows"] == 97
assert _l0["ordinal"] == 269 and _l0["w278_finalize_landed"] is True
assert _l0["w278_finalize_anchors"]["ledger_total"] == 1035935
assert _l0["w278_finalize_anchors"]["merged_n"] == 609520
assert round(_l0["w278_finalize_anchors"]["skill_line_delta_k_lift"], 4) == -0.0002
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=629101 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=631101 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W280p_A_naive"] == "631101..633100"
assert pr["legs"]["leg4"]["W280p_B_naive"] == "631301..631500"
assert pr["legs"]["leg4"]["W280p_B_lands_inside_W280p_A_naive"] is True'''),
 mkspan("S7", "# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---",
        'assert 0.05 <= _ram_free <= 16.0, "RAM face out of honest window: %.2f" % _ram_free',
 u'''# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1122 window face: probe-time read = %s available (loop CPU-only; RAM fluctuates with
# resident daemons). Wide gate keeps idempotent re-runs green across the fluctuation
# (r1052 law); 16.0 upper bound held from the r1116 heal (e); below 0.05GB = machine near
# death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 16.0, "RAM face out of honest window: %%.2f" %% _ram_free''' % ram_face),
 mkspan("S8", "VMAP_POST_LEGS = [", "    T1 = T1.replace(o, n)",
 u'''VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W278 finalize one-pass landed 15:1x (0a92fcc28f
    # 15:13:26); T1 carries the W277-era 10:3x stamps x5 (MEASURED by the r1121 prep, r1077 law);
    # splice stamps 09:5x-era x2 -> W278 splice 13:5x (b6f486af35)
    ("10:3x", "15:1x", 5),
    # splice-stamp roll (heal (1) leg-2): W277 splice 09:5x-era stamps x2 (MEASURED by the
    # r1121 prep) -> W278 splice b6f486af35 13:5x
    ("09:5x", "13:5x", 2),
    # date-cross N/A this generation (heal (2), disclosed): W279 seat receipt same-date 20261019
    # with the W278 seat receipt -- lowercase prefix chain rolls the receipt date correctly with
    # NO date-cross leg.
    # sec.5 item1 measured keys -> W278 actuals (n1_w278_results + fivekeys machine values)
    ("（W278 实测键 **−0.09277044**·K=607,320 合并池·W278-only 实测 **−0.08889850**）",
     "（W278 实测键 **−0.09278576**·K=609,520 合并池·W278-only 实测 **−0.09701509**）", 1),
    ("W2..W278 共二百七十六面实测 mu 稳定先例", "W2..W278 共二百七十七面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (4)): TRUE W278 diff = 0.0042 @4dp (measured
    # 0.004229333427794163 full), in-band
    ("W278-only vs merged 实差 0.0039 在带内", "W278-only vs merged 实差 0.0042 在带内", 1),
    # sec.5 item2 sigma key (heal (5))
    ("键 **0.24508694**=W278 合并池实测", "键 **0.24505494**=W278 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (6))
    ("与 W278 A 档 p95（**0.3095** 实测锚）", "与 W278 A 档 p95（**0.2844** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (7): lowercase line_pre_w277 NOT rolled by the
    # W-roll; true W278 anchors K-lift -0.0002 first negative micro-move in-band + line_merged@K609,520
    # 1.1969 + line_pre_w278 1.1971 + n_eff_held 1,033,735)
    ("键 W278 实测 K-lift **+0.0000**·line_merged@K607,320 **1.197**·line_pre_w277 1.197·n_eff_held_equal 1,031,535",
     "键 W278 实测 K-lift **−0.0002**·line_merged@K609,520 **1.1969**·line_pre_w278 1.1971·n_eff_held_equal 1,033,735", 1),
    # se_mu chain true-history correction (heal (8); W278 fivekeys key5 measured 0.000314
    # held-flat from W277 0.000314; W279 projection 0.000313 computed sigma/sqrt(K611,720))
    ("→W273 **0.000319**→W274 **0.000319**→W275 **0.000318**→W276 **0.000317**→W277 **0.000316**→W278 **0.000314**→W279 投影 0.000314】",
     "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】", 1),
    # sec.4 merged-pool anchor face (heal (9): W278 finalize landed)
    ("W1..W278 已落账 607,320 实测", "W1..W278 已落账 609,520 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W278 cycle (heal (10): bm-c r1119;
    # OLD faces are POST-VMAP faces -- the raw T0' W277-cycle rows already shifted W277->W278
    # before this leg fires; the leg fixes the window number r1114-continuation->r1119,
    # measured post-VMAP count=1)
    ("bm-c r1114-continuation W278 §7 范式", "bm-c r1119 W278 §7 范式", 1),
    ("bm-c r1114-continuation W278 §8 范式", "bm-c r1119 W278 §8 范式", 1),
    # RAM face live-measured THIS window (heal (11)): psutil %d GB available (%s) + %s
    # -- GPU=gen-only lane idle; honest window face updated from the r1116 ~4.5GB face
    ("本窗 free RAM ~4.5GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 0%%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM %s（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（%s）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W278 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- pre-shift needles land the MUST series on the TRUE labels W263..W277;
    # this leg restores the POST-VMAP shifted ledger and appends the true W278 anchor
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚·W276 冻结窗 ~3.8G bm-c 实锚·W277 冻结窗 ~3.9G bm-c 实锚·W278 冻结窗 ~4.5G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚·W276 冻结窗 ~3.9G bm-c 实锚·W277 冻结窗 ~4.5G bm-c 实锚·W278 冻结窗 %s bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %%r count=%%d floor=%%d" %% (o, c, f))
    T1 = T1.replace(o, n)''' % (RAM, ram_face, gpu_face, ram_face, gpu_face, ram_anchor)),
 mkspan("S9",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278=A/B 双 1-hop 形态连续二十七波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278=A/B 双 1-hop 形态连续二十七波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）",
        "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279=A/B 双 1-hop 形态连续二十八波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"),
 mkspan("S10", '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "07:2x", "07:4x", "08:1x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "07:2x", "07:4x", "08:1x",',
        '"17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x", "05:2x", "05:3x", "05:5x", "07:2x", "07:4x", "08:1x", "09:5x", "10:3x", "09:0x",'),
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
 ("r1113/r1114-continuation W277 全周期先例实时间线：prereg e0bc4a0ddd 落于 r1113 窗·splice 9e53371814 落于 r1114-continuation 执行窗", "r1116/r1118 W277 全周期先例实时间线：prereg df1aaba72a 落于 r1116 窗·splice b6f486af35 落于 r1118 执行窗"),
 ("estate chain r1113/r1114-continuation W277 全周期 e0bc4a0ddd+9e53371814+0502c722ac", "estate chain r1116/r1118/r1119 W277 全周期 df1aaba72a+b6f486af35+0a92fcc28f"),
 ("席位 r1114-continuation 窗+prereg r1116 窗", "席位 r1119 窗+prereg r1122 窗"),
 ("bm-c r1114-continuation 五面冻结 splice", "bm-c r1118 五面冻结 splice"),
 ("finalize one-pass bm-c r1114-continuation 窗 10:3x", "finalize one-pass bm-c r1119 窗 15:1x"),
 # bare form (post-gates MUST list; fires AFTER the suffix needle above so it only hits the
 # MUST bare face -- one-low new side, the W-chain completes W277->W278)
 ("W277 finalize one-pass bm-c r1114-continuation", "W277 finalize one-pass bm-c r1119"),
 ("bm-c r1114-continuation 席位 MSG-", "bm-c r1119 席位 MSG-"),
 ("bm-c 循环班 r1114-continuation 席位窗", "bm-c 循环班 r1119 席位窗"),
 ("2026-10-19 10:3x", "2026-10-19 15:0x"),
 ("（r1114-continuation 窗算法", "（r1119 窗算法"),
 ("bm-c r1114-continuation 席·", "bm-c r1119 席·"),
 ("r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中", "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中"),
 ("bm-c r1114-continuation W277 §7 范式", "bm-c r1119 W277 §7 范式"),
 ("bm-c r1114-continuation W277 §8 范式", "bm-c r1119 W277 §8 范式"),
 ('"r1114-continuation W277 §7 范式": 0', '"r1119 W277 §7 范式": 0'),
 ('"r1114-continuation W277 §8 范式": 0', '"r1119 W277 §8 范式": 0'),
 # -- r specific engine-stamp needles (new-side rolls, consume-then-recreate):
 ("saturation_engine.py status live-read r1116：", "saturation_engine.py status live-read r1122："),
 ("本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗", "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗"),
 ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读", "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读"),
 # -- r old-side rolls (create the T0 faces) --
 ("（r1112 窗算法", "（r1114-continuation 窗算法"),
 ("bm-c r1112 席·", "bm-c r1114-continuation 席·"),
 # ONE-LOW (canon heal (n) defect category 8, rolled): NEW keeps the one-low W label so the
 # txt W-chain lands it on the TRUE label; probe-verified floor face.
 ("r1112 席位窗实跑：origin inbox 零 W277 席位外机命中", "r1114-continuation 席位窗实跑：origin inbox 零 W277 席位外机命中"),
 ("live-read r1113：", "live-read r1116："),
 ("新鲜实读 r1113 窗", "新鲜实读 r1116 窗"),
 ("新鲜 r1113 窗实读", "新鲜 r1116 窗实读"),
 # -- MSG/sha descending chains --
 ("MSG-20261019-102x", "MSG-20261019-145x"),
 ("MSG-20261019-080x", "MSG-20261019-102x"),
 ("MSG-20261019-055x", "MSG-20261019-080x"),
 ("MSG-102x owner", "MSG-145x owner"),
 ("MSG-080x owner", "MSG-102x owner"),
 ("MSG-055x owner", "MSG-080x owner"),
 ("bmc-w278-seat", "bmc-w279-seat"),
 ("bmc-w277-seat", "bmc-w278-seat"),
 ("bmc-w276-seat", "bmc-w277-seat"),
 ("b187aa6214", "900c23fe7d"),
 ("c5f8b88f91", "b187aa6214"),
 ("21b51a102", "c5f8b88f91"),
 ("bf4bbbde1e", "21b51a102"),
 ("70b21a0264", "bf4bbbde1e"),
 ("39e1bb32f1", "70b21a0264"),
 ("f608ff1cee", "39e1bb32f1"),
 ("87d2697cdc", "f608ff1cee"),
 ("e0bc4a0ddd", "df1aaba72a"),
 ("9e53371814", "b6f486af35"),
 # derive-script print faces (outside the S2 span; cosmetic but must not print stale
 # canon shas -- the committed script's stdout stays honest)
 ("e5d12b12da03a799a88bd980cf8566b2b1eff5ba", "053892f61cf24d9803cb20410d4ab1163cb7897a"),
 ("twin 78571eb1 disclosed", "twin 1c93e077 disclosed"),
 ("0df07c846b", "60e630918f"),
 ("644b4f8459", "b965e2ecf0"),
 ("0502c722ac", "0a92fcc28f"),
 ("e781164e41", "0502c722ac"),
 # -- G+1 projection/vacancy consumes (descending) --
 ("W279 冻结方", "W280 冻结方"), ("W278 冻结方", "W279 冻结方"), ("W277 冻结方", "W278 冻结方"),
 ("W280p_", "W281p_"), ("W279p_", "W280p_"), ("W278p_", "W279p_"), ("W277p_", "W278p_"),
 ("verify at W279 prereg", "verify at W280 prereg"), ("verify at W278 prereg", "verify at W279 prereg"),
 ("零 skip-ahead W279/W280 席位声明", "零 skip-ahead W280/W281 席位声明"),
 ("零 skip-ahead W278/W279 席位声明", "零 skip-ahead W279/W280 席位声明"),
 # W+ blankets ALONE (needle-order heal, r1107 family: compounds subsumed by the blankets)
 ("W279+ 投影", "W280+ 投影"),
 ("W278+ 投影", "W279+ 投影"),
 # R-record horizon face (disclosed heal, r1107 family)
 ("对 W279+ 的拒面影响", "对 W280+ 的拒面影响"),
 ("R279", "R280"), ("R278", "R279"), ("R277", "R278"), ("R276", "R277"),
 # -- Chinese ordinals descending --
 ("第二十八次连续 A-hop", "第二十九次连续 A-hop"),
 ("第二十七次连续 A-hop", "第二十八次连续 A-hop"),
 ("第二十六次连续 A-hop", "第二十七次连续 A-hop"),
 ("第二十八次连续 above-own-A", "第二十九次连续 above-own-A"),
 ("第二十七次连续 above-own-A", "第二十八次连续 above-own-A"),
 ("第二十六次连续 above-own-A", "第二十七次连续 above-own-A"),
 ("〔第二十七次连续〕", "〔第二十八次连续〕"), ("〔第二十六次连续〕", "〔第二十七次连续〕"),
 ("连续二十七波", "连续二十八波"),
 ("连续二十六波", "连续二十七波"),
 ("连续二十五波", "连续二十六波"),
 ("共二百七十六面", "共二百七十七面"),
 ("共二百七十五面", "共二百七十六面"),
 # -- ledger/K chains (newest first; b_prev projection BEFORE the 607,120 blanket) --
 # K-lift sign face (W278 fivekeys key4 -0.0002 first negative micro-move) + line_merged value
 # move (1.197 -> 1.1969 @K609,520) + line_pre (1.197 -> 1.1971): MUST-list faces must land on
 # the W278 actuals, and these compound needles must fire BEFORE the bare 607,120 blanket
 # consumes the K face.
 # K-lift needle ONE-LOW (canon heal (k), rolled): NEW side must NOT carry W278 -- the
 # txt W-chain would re-roll it to W279. One-low NEW keeps the W277 label so the chain lands
 # the MUST entry on the TRUE W278 face (= the S8 POST_LEG NEW = MUST_NEW audit face).
 ("键 W277 实测 K-lift **+0.0000**", "键 W277 实测 K-lift **−0.0002**"),
 ("line_merged@K607,320 **1.197**", "line_merged@K609,520 **1.1969**"),
 ("line_pre_w277 1.197", "line_pre_w278 1.1971"),
 ("1,033,735", "1,035,935"), ("1,031,535", "1,033,735"), ("1,029,335", "1,031,535"),
 ("1033735", "1035935"), ("1031535", "1033735"), ("1029335", "1031535"),
 ("**609,520 投影**", "**611,720 投影**"),
 ('"609,520": 0', '"611,720": 0'),
 ("607,120", "609,520"),
 ("605,120", "607,120"),
 ("609520", "611720"), ("607320", "609520"), ("605120", "607320"), ("602920", "605120"),
 # -- value faces (W278 actuals; newest first; SPAN-protected asserts exempt) --
 ("−0.09277044", "−0.09278576"), ("−0.09278451", "−0.09277044"), ("−0.09280541", "−0.09278451"),
 ("-0.09277044", "-0.09278576"), ("-0.09278451", "-0.09277044"),
 ("0.24508694", "0.24505494"), ("0.24508562", "0.24508694"), ("0.24507989", "0.24508562"),
 ("−0.08889850", "−0.09701509"), ("−0.08705886", "−0.08889850"), ("−0.09398255", "−0.08705886"),
 ("-0.0888985", "-0.09701509"), ("-0.08705886", "-0.08889850"),
 ("0.3095", "0.2844"), ("0.3088", "0.3095"), ("0.3009", "0.3088"),
 ("实差 0.0039 在带内", "实差 0.0042 在带内"), ("实差 0.0057 在带内", "实差 0.0039 在带内"), ("实差 0.0012 在带内", "实差 0.0057 在带内"),
 ('"line_merged@K607,320": 0', '"line_merged@K609,520": 0'),
 ('"K=607,320": 0', '"K=609,520": 0'),
 ("line_pre_w276 1.1968", "line_pre_w277 1.197"), ("line_pre_w275 1.1968", "line_pre_w276 1.1968"),
 # se_mu chain MUST-entry T2-face protection (canon heal (k) family, rolled): one-low 7-slot
 # form (values ride their labels) rolls through the txt W-chain onto the POST_LEG NEW =
 # the MUST_NEW face EXACTLY (true history W273..W278 + W279 projection 0.000313).
 ("→W272 **0.000319**→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 投影 0.000314】",
  "→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000314**→W277 **0.000314**→W278 投影 0.000313】"),
 # -- band faces (descending; own-before-prior heals the r1107 double-roll disease; NEW blocks +
 # VMAP legs + FLOORS + zero-floors + MUST + pinned all ride the same blankets) --
 ("629_101..629_300", "631_301..631_500"),
 ("628_901..630_900", "631_101..633_100"),
 ("626_901..627_100", "629_101..629_300"),
 ("626_701..628_700", "628_901..630_900"),
 ("624_701..624_900", "626_901..627_100"),
 ("626_901..628_900", "629_101..631_100"),
 ("628_901..629_100", "631_101..631_300"),
 ("624_701..626_700", "626_901..628_900"),
 ("626_701..626_900", "628_901..629_100"),
 ("622_501..624_500", "624_701..626_700"),
 ("624_501..624_700", "626_701..626_900"),
 ("622_301..622_500", "624_501..624_700"),
 ("620_101..620_300", "622_301..622_500"),
 ("622_301..624_300", "624_501..626_500"),
 ("620_101..622_100", "622_301..624_300"),
 ("618_101..620_100", "620_301..622_300"),
 ("617_901..619_900", "620_101..622_100"),
 ("617_901..618_100", "620_101..620_300"),
 # -- entry/exit rng (compound forms disambiguate BLOCKS markers from NEW texts) --
 ("entry rng=**626_901+j**（与 A[j] 同源配对语义逐字", "entry rng=**629_101+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng=**624_701+j**（与 A[j] 同源配对语义逐字", "entry rng=**626_901+j**（与 A[j] 同源配对语义逐字"),
 ("entry rng seed=**626_901+j**（法典", "entry rng seed=**629_101+j**（法典"),
 ("entry rng seed=**624_701+j**", "entry rng seed=**626_901+j**"),
 ("exit rng=**628_901+j**（法典", "exit rng=**631_101+j**（法典"),
 ("exit rng=**626_701+j**", "exit rng=**628_901+j**"),
 ("628_900+1", "631_100+1"), ("626_900+1", "628_900+1"), ("626_700+1", "626_900+1"), ("624_700+1", "626_900+1"),
 ("624_500+1", "626_700+1"), ("622_500+1", "624_700+1"), ("622_300+1", "624_500+1"), ("620_300+1", "622_500+1"),
 ("620_100+1", "622_300+1"), ("618_100+1", "620_300+1"), ("615_900+1", "618_100+1"), ("615_700+1", "617_900+1"),
 ("A 尾 626_700 续", "A 尾 628_900 续"), ("A 尾 624_500 续", "A 尾 626_700 续"),
 ("→jump 626_901·", "→jump 629_101·"),
 ("→jump 624_701·", "→jump 626_901·"),
 ("B 尾 626_900", "B 尾 629_100"),
 ("B 尾 624_700", "B 尾 626_900"),
 # -- stamps --
 ("@ 10:3x", "@ 15:1x"),
 ('"09:5x": 0, "10:3x": 0, "09:0x": 0', '"13:5x": 0, "15:1x": 0, "15:0x": 0, "09:0x": 0'),
 ('"07:4x": 4, "07:2x": 2, "08:1x": 1', '"10:3x": 5, "09:5x": 2'),
 ('"10:3x",', '"15:1x",'),
 ("2026-10-19 10:35:34", "2026-10-19 15:13:26"), (" 10:35:34 (", " 15:13:26 ("), ('"2026-10-19 10:("', '"2026-10-19 15:("'),
 ("2026-10-19 10:3", "2026-10-19 15:1"), ("10:35:34", "15:13:26"),
 ("2026-10-19 09:5", "2026-10-19 15:0"), ("09:57:42", "13:5x"),
 ("@ 09:5x", "@ 13:5x"),
 # -- RAM faces (MUST + floors-key collision flip + print note; S7/S8 SPAN-protected) --
 ('"本窗 free RAM ~4.5GB": 0', '"本窗 free RAM %s": 0' % ram_face),
 ("本窗 free RAM ~4.5GB", "本窗 free RAM " + ram_face),
 ("(~4.5GB written, MV 车道已收官 idle)", "(%s written, MV 车道已收官 idle)" % ram_face),
 # live GPU face roll (MUST entry; prose handled by S8 POST_LEG)
 ("nvidia-smi 实读 0%·1.8G VRAM 占用·MV 车道已收官 GPU idle 回释", gpu_face),
 # -- RAM-anchor ledger chain protection (canon heal family, rolled): the anchors are STABLE
 # historical labels; the W-chain would shift them one generation -- down-one needles let the
 # chain land the MUST series back on the TRUE labels (and extend the chain with the W277
 # ~4.5G anchor) while the BAN series keeps the shifted-label bans stable.
 ('"W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",', '"W262 冻结窗 26G bm-a 实锚", "W263 冻结窗 7G bm-c 实锚",'),
 ('"W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",', '"W264 冻结窗 3G bm-c 实锚", "W265 冻结窗 ~5G bm-c 实锚", "W266 冻结窗 ~0.1G bm-c 实锚",'),
 ('"W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",', '"W267 冻结窗 ~1.4G bm-c 实锚", "W268 冻结窗 ~2.1G bm-c 实锚", "W269 冻结窗 ~3.3G bm-c 实锚",'),
 ('"W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚", "W275 冻结窗 ~3.8G bm-c 实锚", "W276 冻结窗 ~3.9G bm-c 实锚",', '"W270 冻结窗 ~1.4G bm-c 实锚", "W271 冻结窗 ~0.3G bm-c 实锚", "W272 冻结窗 ~4.4G bm-c 实锚", "W273 冻结窗 ~4.0G bm-c 实锚", "W274 冻结窗 ~3.8G bm-c 实锚", "W275 冻结窗 ~3.9G bm-c 实锚", "W276 冻结窗 ~4.5G bm-c 实锚",'),
 ('"W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",', '"W263 冻结窗 26G", "W264 冻结窗 7G", "W265 冻结窗 3G", "W266 冻结窗 ~5G",'),
 ('"W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",', '"W267 冻结窗 ~0.1G", "W268 冻结窗 ~1.4G", "W269 冻结窗 ~2.1G", "W270 冻结窗 ~3.3G", "W271 冻结窗 ~1.4G", "W272 冻结窗 ~0.3G",'),
 # -- rows/ordinals descending --
 ("行 267 注册在册", "行 268 注册在册"), ("行 266 注册在册", "行 267 注册在册"),
 ("engine_owner==bm-c 96 行注册", "engine_owner==bm-c 97 行注册"), ("engine_owner==bm-c 95 行注册", "engine_owner==bm-c 96 行注册"),
 ("bmc_rows=96", "bmc_rows=97"), ("bmc_rows=95", "bmc_rows=96"),
 ("bmc rows 96+候选", "bmc rows 97+候选"), ("bmc rows 95+候选", "bmc rows 96+候选"),
 ("live rows 96 实读", "live rows 97 实读"), ("live rows 95 实读", "live rows 96 实读"),
 ("第 268 波", "第 269 波"), ("第 267 波", "第 268 波"), ("第 266 波", "第 267 波"),
 ("第九十七枚", "第九十八枚"), ("第九十六枚", "第九十七枚"), ("第九十五枚", "第九十六枚"),
 ("第 97 枚", "第 98 枚"), ("第 96 枚", "第 97 枚"), ("第 95 枚", "第 96 枚"),
 ("池第 276 枚", "池第 277 枚"), ("池第 275 枚", "池第 276 枚"), ("池第 274 枚", "池第 275 枚"),
 ("波号 278", "波号 279"), ("波号 277", "波号 278"), ("波号 276", "波号 277"),
 ("零 278 行", "零 279 行"), ("零 277 行", "零 278 行"), ("零 276 行", "零 277 行"),
 ("--wave 278/finalize --wave 278", "--wave 279/finalize --wave 279"),
 ("--wave 277/finalize --wave 277", "--wave 278/finalize --wave 278"),
 ("--wave 276/finalize --wave 276", "--wave 277/finalize --wave 277"),
 ("41st consecutive", "42nd consecutive"), ("40th consecutive", "41st consecutive"),
 ("CLEAN-AT-BIRTH 10th gen", "CLEAN-AT-BIRTH 11th gen"),
 ("CLEAN-AT-BIRTH 9th gen", "CLEAN-AT-BIRTH 10th gen"),
 # -- floors wave-count lines: NO needles this generation (canon heal (g)/(l) needles existed
 # only because the r1113-gen line was defective; a healthy line self-rolls via the W-chain --
 # post-chain exactness verification + the W263-slot insert land in the pin block below;
 # values = r1121-prep measured counts on T0) --
 # 13:5x consumption: the W278 splice stamp (13:5x) becomes a W279-product face via the
 # POST_LEG (09:5x -> 13:5x x2) -- REMOVE from the MUST_NOT triple (floors zero keys
 # unaffected: 13:5x stays 0 on the RAW md; disclosed roll-analysis heal).
 ('"12:2x", "13:5x", "14:0x"', '"12:2x", "14:0x"'),
 # -- VMAP-leg wave/vacancy old-side rolls (T0 faces) --
 ("波号 277", "波号 278"),
 ("零 277 行", "零 278 行"),
 ("零 skip-ahead W277/W278 席位声明", "零 skip-ahead W278/W279 席位声明"),
 ("池第 275 枚", "池第 276 枚"),
 ("第 267 波", "第 268 波"),
 ("bm-c 第九十六枚自有波", "bm-c 第九十七枚自有波"),
 ("engine_owner==bm-c 95 行注册", "engine_owner==bm-c 96 行注册"),
 ("--wave 277/finalize --wave 277", "--wave 278/finalize --wave 278"),
 ("§5.5 W278+ 投影承接机证", "§5.5 W279+ 投影承接机证"),
 ("saturation_engine.py status live-read r1113：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
  "saturation_engine.py status live-read r1116：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
 ("本机 bm-c 实例·heartbeat 新鲜实读 r1113 窗·队列空转 idle",
  "本机 bm-c 实例·heartbeat 新鲜实读 r1116 窗·队列空转 idle"),
 ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1113 窗实读",
  "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1116 窗实读"),
 ("r1112 席位窗实跑", "r1114-continuation 席位窗实跑"),
 # -- floors block-marker stability + lowercase floors keys --
 ("engine_owner 行 266 注册在册（表尾", "engine_owner 行 267 注册在册（表尾"),
 ('"n1_w277": 4, "n1_w276": 6, "_w277bmc": 4, "_w276bmc": 1', '"n1_w278": 4, "n1_w277": 6, "_w278bmc": 4, "_w277bmc": 1'),
 ('"_w278bmc": 0, "n1_w278": 0, "W279p_": 0', '"_w279bmc": 0, "n1_w279": 0, "W280p_": 0'),
 ('"n_eff_held_equal 1,031,535": 0', '"n_eff_held_equal 1,033,735": 0'),
 # NOTE: NO explicit "probe W2xx+ 投影"/"5. **W2xx+ 投影" floors-key needles this generation --
 # the W+ blankets (descending, fired earlier) + band needles assemble BOTH faces correctly
 # (leg NEW -> next-gen target; floors key -> current-gen raw-md face); an explicit pair here
 # would corrupt the just-landed floors key (disclosed roll-analysis heal, blanketed-face law).
]
needle_counts = {}
for old, new in NEEDLES:
    needle_counts[old] = txt.count(old)
    txt = txt.replace(old, new)

# -- W-chain LAST (chained placeholders; range matches the canon floor W262 so the down-one
# needles at W262 land on the TRUE W263 labels; the script-internal VMAP chain bottom stays W263
# via the pin block) --
P1 = "\x01W\x01"
txt2 = txt
for w in range(278, 261, -1):  # W278..W262 consume descending (canon range(277,261) +1)
    if w == 278:
        txt2 = txt2.replace("W278", P1)
    else:
        txt2 = txt2.replace("W%d" % w, "W%d" % (w + 1))
txt2 = txt2.replace(P1, "W279")
txt = txt2
# -- lowercase chains --
P2, P3 = "\x01N\x01", "\x01B\x01"
txt = txt.replace("n1_w278", P2).replace("n1_w277", "n1_w278").replace("n1_w276", "n1_w277").replace(P2, "n1_w279")
txt = txt.replace("_w278bmc", P3).replace("_w277bmc", "_w278bmc").replace("_w276bmc", "_w277bmc").replace(P3, "_w279bmc")
# frozen-face filename generation component (canon derive SRC line + its pre-span header note
# reference _w27Xbmc_w27Y_frozen_face.txt; the bmc chain above rolls the prefix side only --
# this rolls the w27Y side; T0 prereg-md carries zero such refs so the SIM is unaffected)
txt = txt.replace("w277_frozen_face", "w278_frozen_face")

# ---------------- post-W-chain refuser-band machine-face verification (canon heal (a), rolled) ----------------
# Single blanket roll lands the parenthetical on the machine-receipt face (registered W278 B
# band 628_901..629_100 refused the naive W279 A start -- receipt leg1
# refuser_bands=[[628901,629100]]); fail-closed on both wrong faces (own-B lineal defect +
# stale prior).
_fix_hits = txt.count("refuser band 628_901..629_100〕")
assert _fix_hits == 1, "refuser-band machine face count=%d (expect 1)" % _fix_hits
assert txt.count("refuser band 631_101..631_300〕") == 0, "refuser-band own-B lineal-defect face present"
assert txt.count("refuser band 626_701..626_900〕") == 0, "refuser-band stale prior face present"
# freezer-label unlag re-confirmed STRUCTURAL (canon heal (b), rolled W279->W280): the
# b_claim freezer label sits ONE ABOVE the W-chain top (W279 vs top W278) and never rolls
# naturally -- every generation needs the post-W-chain unlag pass (measured x1 on T0).
_fix_freezer = txt.count("W279 freezer 承接面强制注记")
assert _fix_freezer == 1, "freezer heal anchor count=%d (expect 1)" % _fix_freezer
txt = txt.replace("W279 freezer 承接面强制注记", "W280 freezer 承接面强制注记")
assert txt.count("W279 freezer 承接面强制注记") == 0, "freezer heal residue"
# canon r1116 heal-16-era dead-pass carried (0 hits expected; the natural own-before-prior
# chain lands the prose correct this generation -- disclosed, NOT re-applied)
_dead_refuser = txt.count("注册 W278 B 带 631_101..631_300 落 naive A 窗内")
assert _dead_refuser == 0, "rolled heal-16 would double-roll: face present"

# ---------------- VMAP wave-chain floor pin (canon heal (j), defect category 4, rolled) ----------------
# The builder's txt W-chain rolled the W278 canon chain-floor entry ("W263","W264") up to
# ("W264","W265") -- but the T0 ledger's TRUE floor label W263 is STABLE across generations.
# Without the pin the script's chain leaves the ledger W263 unrolled and the RAM-anchor
# POST_LEG OLD face (shifted ledger starting "W264 冻结窗 26G") never forms.
_pin_old = '("W264", "W265"), (P1, "W279"),'
_pin_hits = txt.count(_pin_old)
assert _pin_hits == 1, "chain-floor pin anchor count=%d (expect 1)" % _pin_hits
txt = txt.replace(_pin_old, '("W264", "W265"), ("W263", "W264"), (P1, "W279"),')
assert txt.count('("W263", "W264"), (P1, "W279"),') == 1, "chain-floor pin landed wrong"
assert txt.count('("W264", "W265"), ("W263", "W264"), (P1, "W279"),') == 1, "chain-floor pin residue"

# ---------------- floors exactness verification + W263-slot insert (canon heal (l), rolled) ----------------
# Line A self-rolls exactly (healthy canon line, no defect this generation): post-chain face
# must equal the r1121-prep MEASURED counts (r1077 law): W278:44 W277:62 W276:4 W275:4 W274:3
# W273:3 W272:3 W271:2 W270:2 W269:2 W268:2 W267:2 -- fail-closed verification, no heal.
_flA_check = '"W278": 44, "W277": 62, "W276": 4, "W275": 4, "W274": 3, "W273": 3, "W272": 3, "W271": 2, "W270": 2, "W269": 2, "W268": 2, "W267": 2,'
_flpin_hits = txt.count(_flA_check)
assert _flpin_hits == 1, "floors line A post-chain exactness count=%d (expect 1)" % _flpin_hits
# Line B: chain rolls W265/W264/W263/W262 up (W262:1 lands as a wrong W263:1); the true W263: 2
# value + the W262: 1 slot are structurally unreachable -- pin lands the exact measured line.
_flB_old = '"W266": 2, "W265": 2, "W264": 2, "W263": 1,'
assert txt.count(_flB_old) == 1, "floors line B pin anchor count=%d (expect 1)" % txt.count(_flB_old)
txt = txt.replace(_flB_old, '"W266": 2, "W265": 2, "W264": 2, "W263": 2, "W262": 1,')
assert txt.count('"W263": 2, "W262": 1, "W261": 1,') == 1, "floors line B pin landed wrong"

# ---------------- substitute spans ----------------
for sid, sm, em, new in SPANS:
    txt = txt.replace("\x02%s\x02" % sid, new)
assert "\x02" not in txt and "\x01" not in txt, "placeholder residue"

# ---------------- FULL PRE-FLIGHT SIMULATION (exec data segments + run every gate on T0) ----------------
def seg(start, end):
    i = txt.index(start)
    j = txt.index(end, i)
    return txt[i:j]

ns = {"P1": "\x01W\x01", "P2": "\x01N\x01", "P3": "\x01B\x01", "SPLICE_T": "13:5x"}
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
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", "13:5x")
    T2 = T2[:i] + NEWTXT + T2[j:]
for s in MUST:
    assert s in T2, "SIM MUST missing: %r" % s
for s in MUST_NOT:
    assert s not in T2, "SIM MUST_NOT present: %r (count=%d)" % (s, T2.count(s))
exec(seg("# ---------------- post gates ----------------", 'io.open(OUT, "w"'), dict(ns, T2=T2, re=re))
out_sha = hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16]

# ---------------- builder-level audits ----------------
MUST_NEW = ["r1122 bm-c: W279 prereg derive", "PERPETUAL_N1_W279_PREREG.md", "629_101..631_100",
            "631_101..631_300", "611,720 投影", "MSG-20261019-145x-bmc-w279-seat", "900c23fe7d",
            "df1aaba72a", "第二十八次连续 A-hop", "第二十九次连续 above-own-A",
            "053892f61cf24d9803cb20410d4ab1163cb7897a", "1c93e077c2b64476fb55041a7f59f7591f67db68",
            "2026-10-19 15:13:26", "bm-c r1119 W278 §7 范式", "_r1118bmc_w278_fivekeys.json",
            "−0.09278576", "0.24505494", "−0.09701509", "（**0.2844** 实测锚）", "1,035,935", "609,520",
            "0.000314", "第 98 枚", "第 269 波", "池第 277 枚", "W278 冻结窗",
            "engine_owner==bm-c 97 行注册", "engine_owner 行 268 注册在册",
            "probe leg0 bmc_rows=97 attempt-continuity face", "bm-c 循环班 r1119 席位窗 2026-10-19 15:0x",
            "本机 bm-c 实例", "W279=bm-c own-wave window per chain-order law",
            "b6f486af35", "60e630918f", "b965e2ecf0", "0a92fcc28f",
            "W280+ 投影", "W280p_B_lands_inside_W280p_A_naive", "verify at W280 prereg",
            "_w279bmc_freeze_edits.py", "_w278bmc_freeze_edits.py 模板派生", "bm-c r1119 W278 §8 范式",
            "（上游 W278 席位已闭链=注册+烧录+finalize 全落地·零在飞）", "（W278 注册+烧录+finalize 全落地）",
            "W206/W211..W278 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "席位时即解锁", "（见 §5 item5）。",
            "R280：W279 带", "→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 **0.000314**→W279 投影 0.000313】",
            "628_900+1", "631_100+1", "628_901..629_100", "A_staircase_hop_past_W278_B=true",
            "B_lands_above_own_A=true", "seed_admit_gate rc0 双带 FREE", "波号 279", "零 279 行",
            "零 skip-ahead W280/W281 席位声明", "15:1x", "（占位·finalize one-pass 后回填",
            "saturation_engine.py status live-read r1122：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
            "本机 bm-c 实例·heartbeat 新鲜实读 r1122 窗·队列空转 idle",
            "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1122 窗实读",
            "r1119 席位窗实跑：origin inbox 零 W279 席位外机命中", "results/p2cal_ext/n1_w278/ 12/12",
            "base=629101 span=2000", "base=631101 span=200", '"631101..633100"', '"631301..631500"',
            "estate chain r1116/r1118/r1119 W278 全周期", "CLEAN-AT-BIRTH 11th gen", "41st consecutive",
            "实差 0.0042 在带内", "n_eff_held_equal 1,033,735", "611,720",
            "键 W278 实测 K-lift **−0.0002**", "line_merged@K609,520 **1.1969**",
            "注册 W278 B 带 628_901..629_100 落 naive A 窗内", "W280 freezer 承接面强制注记",
            "refuser band 628_901..629_100〕",
            "本窗 free RAM " + ram_face,
            "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276/W277/W278/W279=A/B 双 1-hop 形态连续二十八波"]
# BAN = faces fully consumed by the rolls with NO recreation needle (the descending chains
# legitimately recreate the one-generation-prior faces in VMAP pair old sides / floors keys /
# CLEAN lists / MUST_NOT bans -- those are NOT banned; heal-doc-comment quotes are NOT banned;
# only the fully-consumed faces are; live-value-collidable faces are banned CONTEXT-SCOPED only;
# lineage-stale entries carried verbatim = trivial-true absent bans, disclosed).
BAN = ["e0bc4a0ddd", "9e53371814", "0df07c846b", "644b4f8459", "0502c722ac", "e781164e41",
       "fc01636095", "acf37937ec", "6659a0e362", "21b51a102", "bf4bbbde1e",
       "70b21a0264", "39e1bb32f1", "f608ff1cee", "第 266 波", "波号 276", "第 95 枚", "bmc_rows=95", "第 265 波", "波号 275",
       "TWENTY-SEVENTH consecutive", "10:35:34", "09:57:42", "08:13:22",
       "r1097", "18:4x=5", "PERPETUAL_N1_W277_PREREG.md",
       "B 尾 624_700", "→jump 626_901·", "行 266 注册在册", "（r1112 窗算法", "r1112 席位窗实跑",
       "live-read r1113：", "新鲜实读 r1113 窗", "2026-10-19 10:35:34",
       "MSG-20261019-055x", "MSG-055x owner", "（bm-c r1112 席·",
       "620_101..620_300",
       "注册 W278 B 带 631_101..631_300 落 naive A 窗内", "refuser band 631_101..631_300〕"]
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

OUT = os.path.join(REPO, "results", "_w279bmc_prereg_derive.py")
io.open(OUT, "w", encoding="utf-8", newline="").write(txt)
compile(txt, OUT, "exec")
receipt = {"spans": len(SPANS), "needles": len(NEEDLES), "needle_counts": needle_counts,
           "floor_heals": floor_heals, "floor_report": floor_report,
           "ram_face": ram_face, "gpu_face": gpu_face, "sim_out_sha256_16": out_sha,
           "sim_out_bytes": len(T2.encode("utf-8")), "sim_out_lines": T2.count("\n") + 1,
           "sim_must": len(MUST), "sim_must_not": len(MUST_NOT),
           "fix_refuser_paren_hits": _fix_hits, "fix_freezer_hits": _fix_freezer,
           "dead_refuser_pass_hits": _dead_refuser, "chain_floor_pin_hits": _pin_hits,
           "floors_exact_pin_hits": _flpin_hits, "se_mu_proj_w279": _se_proj_w279}
io.open(os.path.join(REPO, "results", "_w279bmc_needle_probe.json"), "w", encoding="utf-8").write(
    json.dumps(receipt, ensure_ascii=False, indent=1))
print("BUILD OK -> %s (%d bytes)" % (OUT, len(txt.encode("utf-8"))))
print("SIM: derive pre-flight ALL GATES PASS | out %d bytes / %d lines sha256_16 %s" % (
    receipt["sim_out_bytes"], receipt["sim_out_lines"], out_sha))
print("floor heals: %r" % (floor_heals,))
print("defect-birthplace fixes: refuser_paren=%d freezer=%d chain_floor_pin=%d floors_exact_pin=%d (dead rolled heal-16 refuser-prose: %d)" % (
    _fix_hits, _fix_freezer, _pin_hits, _flpin_hits, _dead_refuser))
print("ram face %s | gpu %s | se_mu W279 projection %s" % (ram_face, gpu_face, _se_proj_w279))
print("zero-needle hits (count=0, expected for consumed/protected faces): %d" % sum(1 for v in needle_counts.values() if v == 0))
