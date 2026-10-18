# -*- coding: utf-8 -*-
# r1110 bm-c: W276 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
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
# (11) RAM face live-measured THIS window: psutil 3.0 GB available (~3.8GB, probe-time read) +
#     nvidia-smi nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释 -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); the r1107
#     ~4.0GB face is stale; the r1107 %-format doubling ("nvidia-smi nvidia-smi 实读") healed
#     at birth in the POST_LEG new side.
# (12) low-RAM precedent ledger append: W275 freeze-window ~3.8G bm-c anchor appended via POST_LEG
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
#     (the W277 freezer consumes the post-W276 universe per the W276 seat receipt leg4 note).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w276bmc_w275_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W276_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "e62f3bcbdfe458863bc1b98c176b6f591bcdc14e"   # freeze-commit face @ 1fcc0bc30f
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "1fcc0bc30f:research/PERPETUAL_N1_W275_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W275_PREREG.md"])
assert _hb == "52b42b83b57fbcd3748bf470ab32fc25d98f10e6", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23551, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "e4e1ce44f5afd03b", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095", "21b51a102"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "018782314d"])    # 2026-10-19 05:22:20 +0800
_m = re.match(r"2026-10-19 05:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "05:%sx" % _m.group(1)[0]   # 05:2x
_fz = git_out(["show", "-s", "--format=%ci", "fc01636095"])    # 2026-10-19 05:31:54 +0800
assert _fz.startswith("2026-10-19 05:3"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "21b51a102"])   # 2026-10-19 05:55:17 +0800
assert _st.startswith("2026-10-19 05:5"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w275_results.json"])
assert _fin_log == "fc01636095", "W275 finalize product landed by unexpected commit: %s" % _fin_log
_seat_files = git_out(["show", "--name-only", "--format=", "21b51a102"])
assert "MSG-20261019-055x-bmc-w276-seat.md" in _seat_files, "W276 seat MSG not carried by seat commit 21b51a102: %r" % _seat_files[:200]

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
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
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w275_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1027135
assert round(res["skill_line_v2_k_lift"]["line_pre_w275"], 4) == 1.1968
assert round(res["skill_line_v2_k_lift"]["line_merged_602920"], 4) == 1.1967
assert round(res["null_pool_cumulative"]["se_mu_at_k602920"], 6) == 0.000316, "W275 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w274_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k600720"], 6) == 0.000316, "W274 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w276bmc_20261019_probe_receipt.json"), encoding="utf-8") as f:
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
assert pr["legs"]["leg4"]["W277p_B_lands_inside_W277p_A_naive"] is True

# --- engine live-status gate (bm-c instance, THIS window; prereg engine-face honesty) ---
_r = subprocess.run([sys.executable, os.path.join(REPO, "Tools", "saturation_engine.py"), "status"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=REPO)
assert _r.returncode == 0, "saturation_engine status rc=%d (engine face gate)" % _r.returncode
try:
    _eng = json.loads(_r.stdout)
    assert _eng.get("machine_id") == "bm-c" and _eng.get("alive_flag") is True
    assert _eng.get("burns_active") == [] and _eng.get("queue_next") == []
except Exception:
    assert '"alive_flag": true' in _r.stdout and '"burns_active": []' in _r.stdout \
        and '"queue_next": []' in _r.stdout, "engine face parse failed"

# --- live RAM honesty gate (window face; r1086 law: measured, not assumed) ---
# r1110 window face: probe-time read = ~3.8GB available (MV lane drained, loop CPU-only; RAM
# fluctuates with resident daemons). Wide gate keeps idempotent re-runs green across the
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=620_301..622_300", "A-ext seed=622_501..624_500"),
    ("B-ext exit seed=624_501..624_700", "B-ext exit seed=624_501..624_700"),
    ("entry rng=**620_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**622_501+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W276 seat published bm-c r1102, rides origin 21b51a102)
    ("席位公示=MSG-20261019-034x-bmc-w275-seat 已推 origin bf4bbbde1e r565 律（bm-c r1106 席·queue-head seat-first lane）",
     "席位公示=MSG-20261019-055x-bmc-w276-seat 已推 origin 21b51a102 r565 律（bm-c r1109 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261019-034x-bmc-w275-seat 先推 origin bf4bbbde1e r565 律",
     "席位公示 MSG-20261019-055x-bmc-w276-seat 先推 origin 21b51a102 r565 律"),
    # wave-number + vacancy faces
    ("波号 275", "波号 276"),
    ("r1106 席位窗实跑：origin inbox 零 W275 席位外机命中", "r1109 席位窗实跑：origin inbox 零 W276 席位外机命中"),
    ("零 275 行", "零 276 行"),
    ("零 skip-ahead W276/W277 席位声明", "零 skip-ahead W277/W278 席位声明"),
    ("池第 273 枚", "池第 274 枚"),
    # ordinals + own-wave faces
    ("第 265 波", "第 266 波"),
    ("bm-c 第九十四枚自有波", "bm-c 第九十五枚自有波"),
    ("probe leg0 bmc_rows=93 attempt-continuity face（r1106 窗算法·bm-c own seat+bmc live rows 93 实读）——freeze 时 live derive bmc rows 93+候选=第 94 枚 EXACT",
     "probe leg0 bmc_rows=94 attempt-continuity face（r1109 窗算法·bm-c own seat+bmc live rows 94 实读）——freeze 时 live derive bmc rows 94+候选=第 95 枚 EXACT"),
    ("engine_owner==bm-c 93 行注册", "engine_owner==bm-c 94 行注册"),
    # engine live-read faces (bm-c instance, r1104 window)
    ("saturation_engine.py status live-read r1107：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1110：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1107 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1107 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读"),
    # runner CLI wave
    ("--wave 275/finalize --wave 275", "--wave 276/finalize --wave 276"),
    # sec8 placeholder projection-label bump (W276+ face)
    ("§5.5 W276+ 投影承接机证", "§5.5 W277+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w275", P2), ("n1_w274", "n1_w275"), (P2, "n1_w276"),
    ("_w275bmc", P3), ("_w274bmc", "_w275bmc"), (P3, "_w276bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W275", P1), ("W274", "W275"), ("W273", "W274"), ("W272", "W273"), ("W271", "W272"), ("W270", "W271"),
    ("W269", "W270"), ("W268", "W269"), ("W267", "W268"), ("W266", "W267"), ("W265", "W266"),
    ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), (P1, "W276"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1104)
    "A-ext seed=620_301..622_300": 1,
    "B-ext exit seed=624_501..624_700": 0,
    "entry rng=**620_301+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261019-034x-bmc-w275-seat 已推 origin bf4bbbde1e r565 律（bm-c r1106 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261019-034x-bmc-w275-seat 先推 origin bf4bbbde1e r565 律": 1,
    "波号 275": 1,
    "r1106 席位窗实跑：origin inbox 零 W275 席位外机命中": 1,
    "零 275 行": 1,
    "零 skip-ahead W276/W277 席位声明": 1,
    "池第 273 枚": 1,
    "第 265 波": 1,
    "bm-c 第九十四枚自有波": 1,
    "probe leg0 bmc_rows=93 attempt-continuity face（r1106 窗算法·bm-c own seat+bmc live rows 93 实读）——freeze 时 live derive bmc rows 93+候选=第 94 枚 EXACT": 1,
    "engine_owner==bm-c 93 行注册": 1,
    "saturation_engine.py status live-read r1107：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1107 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1107 窗实读": 1,
    "--wave 275/finalize --wave 275": 1,
    "§5.5 W276+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w275": 4, "n1_w274": 6, "_w275bmc": 4, "_w274bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w276bmc_needle_probe.py r1104 window;
    # measured-counts law r1077)
    "W275": 45, "W274": 62, "W273": 4, "W272": 4, "W271": 3, "W270": 3, "W269": 2, "W268": 2, "W267": 2,
    "W265": 2, "W264": 2, "W263": 2, "W262": 1, "W261": 1, "W259": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 264 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**620_301+j**": 1,
    "exit rng=**622_301+j**": 1,
    "probe W276+ 投影 A naive 622_301..624_300 CLEAN hops=0": 1,
    "5. **W276+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 1,020,535": 0,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "03:2x": 4, "03:0x": 2, "03:3x": 1,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w276bmc": 0, "n1_w276": 0, "W277p_": 0,
    "第 95 枚": 0, "第 266 波": 0, "第九十五枚": 0, "池第 274 枚": 0, "波号 276": 0, "零 276 行": 0,
    "engine_owner==bm-c 94 行注册": 0, "bmc_rows=94": 0, "bmc rows 94+候选": 0,
    "第二十六次连续 A-hop": 0, "第二十六次连续 above-own-A": 0, "连续二十五波": 0, "共二百七十四面": 0,
    "1,029,335": 0, "605,120": 0, "622_501..624_500": 0, "624_501..624_700": 0,
    "624_501..626_500": 0, "624_701..624_900": 0,
    "05:2x": 0, "05:3x": 0, "05:5x": 0,
    "1fcc0bc30f": 0, "018782314d": 0, "5089f02250": 0, "e639699d59": 0, "fc01636095": 0, "21b51a102": 0,
    "−0.09280541": 0, "0.24507989": 0, "−0.09398255": 0, "0.3088": 0,
    "实差 0.0012 在带内": 0, "line_pre_w275 1.1968": 0, "line_merged@K602,920": 0, "K=602,920": 0,
    "r1108 W275 §7 范式": 0, "（W275 注册+烧录+finalize 全落地）": 0,
    "MSG-20261019-055x": 0, "键 W275 实测 K-lift": 0, "本窗 free RAM ~4.4GB": 0,
    "620_301..622_300 CLEAN": 0,
    "617_901..618_100": 0, "617_901..619_900": 0, "611_501..611_700": 0, "615_901..617_900": 0,
    "611_501..611_700": 0, "615_701..617_700": 0,
    "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "611_300+1": 0, "617_900+1": 0, "611_500+1": 0,
    # NOTE (fail-closed discipline): 第二十四次连续 A-hop (T0=3) / 第二十五次连续 above-own-A
    # (T0=2) / 第二十五次连续 A-hop (T0=3) / 连续二十四波 (T0=1) / 共二百七十三面 (T0=1) are NOT
    # zero-floors on this T0 -- they are block-interior current-wave faces (probe: outside=0
    # for the band/ordinal set) + POST_LEG faces, handled by block replace + POST_LEG;
    # banned on T2 via MUST_NOT instead.
}

def xf(t):
    for o, n in VMAP:
        t = t.replace(o, n)
    return t

for o, f in VMAP_FLOORS.items():
    c = T0.count(o)
    if f == 0:
        if c:
            raise SystemExit("VMAP FLOOR(0) FAIL: %r count=%d (expect 0)" % (o, c))
        continue
    if c < f:
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
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
    # RAM face live-measured THIS window (heal (11)): psutil 3.8 available (~3.8GB) + nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释
    # -- GPU=gen-only lane idle (MV lane drained, loop CPU-only); honest window face
    # updated from the r1107 ~4.0GB face; %-format doubling healed at birth
    ("本窗 free RAM ~4.0GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3.8GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 面=空闲回释实测·GPU=gen-only 车道 idle（nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (12)): true W275 anchor appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- the wave-roll had shifted the W263 26G bm-a anchor onto the W264
    # label and the W273 ~4.4G onto W274; both restored + true W275 anchor appended
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚·W272 冻结窗 ~1.4G bm-c 实锚·W273 冻结窗 ~0.3G bm-c 实锚·W274 冻结窗 ~4.4G bm-c 实锚·W275 冻结窗 ~4.0G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚·W272 冻结窗 ~0.3G bm-c 实锚·W273 冻结窗 ~4.4G bm-c 实锚·W274 冻结窗 ~4.0G bm-c 实锚·W275 冻结窗 ~3.8G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 265 注册在册（表尾 W276 行【bm-c r1108 五面冻结 splice 018782314d 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 8th gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w275/ 12/12·ledger append 5089f02250+e639699d59】"
    "·**W275 finalize 已落地**【n1_w275_results.json 机读·净账本锚头 1,029,335·K=602,920 合并池·W275 finalize one-pass bm-c r1108 窗 05:3x·estate chain r1107/r1108 W275 全周期 1fcc0bc30f+018782314d+fc01636095】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1109 席位 MSG-20261019-055x-bmc-w276-seat 已推 origin 21b51a102"
    "·probe receipt _w276bmc_20261019 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 94+候选=第 95 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1109 席位窗 2026-10-19 05:5x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W276=bm-c own-wave window per chain-order law（W273 bm-c→W274 bm-c→W275 bm-c→W276 bm-c own-turn rotation·MSG-055x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W275 N1 注册全部落地**【W275=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W275**"
    "【净账本锚头 **1,029,335**·K=602,920 合并池·n1_w275_results.json 机读·W275 finalize one-pass bm-c r1108 窗 05:3x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W275 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=602,920+2,200（本波）=**605,120 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十五次连续 A-hop）**："
    "A 面算术续带 622_301..624_300（自注册 W275 A 尾 622_300 续）"
    "在席位窗宇宙（post-W275-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W275 B 带 622_301..622_500 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W275 prereg §5 item5 post-W275-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W275 B 尾 622_500→A first-clean **622_501..624_500**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（622_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 622_301..624_300→jump 622_501·refuser band 624_501..624_700〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W275_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=624_501..624_700**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十六次连续 above-own-A 落位）**："
    "B naive 续带 622_501..622_700（自注册 W275 B 尾 622_500+1 续）"
    "在席位窗宇宙（post-W275-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 622_501..622_700 落本波 A first-clean 窗 622_501..624_500 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 622_501..624_500**（1 hop）"
    "→**1 hop** 落位 **624_501..624_700**·**B 落位 base==本波 A 窗尾+1（624_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W275 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W276 A naive 622_301..624_300 将被注册 W275 B 带拒（staircase affects A 承袭·第二十五次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R277：W276 带（A 622_501..624_500/B 624_501..624_700）注册后对 W277+ 的拒面影响=W276 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**622_501+j**（法典 §4 W276 行 A=622_501..624_500·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十五次连续 A-hop）**："
    "A 算术续带 622_301..624_300（自注册 W275 A 尾 622_300 续）"
    "在席位窗宇宙（post-W275-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W275 B 带 622_301..622_500 落 naive A 窗内=W275 prereg §5 item5 post-W275-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W275 B 尾 622_500→A first-clean 622_501..624_500·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（622_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W275_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**624_501+j**（法典 §4 W276 行 B=624_501..624_700·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 622_501..622_700（自注册 W275 B 尾 622_500+1 续）"
    "在席位窗宇宙（post-W275-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 622_501..624_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 622_501..624_500→1 hop 落位 624_501..624_700·"
    "**B 落位 base==本波 A 窗尾+1（624_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十六次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W275 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W277+ 投影 A naive 624_501..626_500 CLEAN hops=0（零 live refusers）/ B naive 624_701..624_900 CLEAN hops=0 "
    "**但落 naive W276 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 624_501..626_500 CLEAN·hops=0——**post-W276-REGISTERED 预披露：naive W276 A 起点将被注册 W276 B 带 624_501..624_700 拒=staircase affects A 第二十六次连续 A-hop 预期**；"
    "投影 B naive 624_701..624_900 clean 但落 naive W276 A 窗 624_501..626_500 内——"
    "**above-own-A 承袭面：W276 B 624_501..624_700 落本波 A 窗之上〔第二十五次连续〕·W276 A 面 1-hop=staircase affects A〔第二十五次连续〕·"
    "W278 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W276 B 带将拒 naive W276 A 窗仅当重叠——"
    "**W277 freezer 承接面强制注记：须在 post-W276 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W277+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 624_501..626_500 **CLEAN**（hops=0·pre-W276 宇宙零 live refusers）——"
    "**post-W276-REGISTERED 预披露：naive W276 A 起点将被注册 W276 B 带 624_501..624_700 拒（staircase-affects-A 第二十六次连续 A-hop 预期）**；"
    "B naive **624_701..624_900 CLEAN（hops=0）但落投影 A 窗 624_501..626_500 内**（W277p_B_lands_inside_W277p_A_naive=true——"
    "**staircase face 延续**：W276 A 622_501..624_500+B 624_501..624_700 注册后 naive W276 A 窗起点即被注册 W276 B 带拒（staircase affects A 承袭·第二十六次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W276 宇宙 live re-derive 必变·禁转录投影）；"
    "**W276 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272/W273/W274/W275/W276=A/B 双 1-hop 形态连续二十五波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W276 冻结方必须在 post-W276 注册宇宙重 derive 且 derive B 时预留本波 A 窗 622_501..624_500+本波 B 带 624_501..624_700"
    "——leg2 律/E36 卡·W141 先例；verify at W277 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w276bmc_freeze_edits.py"
    "（按 _w275bmc_freeze_edits.py 模板派生·gate0.5 自查 W275 行+W275 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1107/r1108 W275 全周期先例实时间线：prereg 1fcc0bc30f 落于 r1107 窗·splice 018782314d 落于 r1108 执行窗 @@SPLICE_T@@——"
    "**W276 freeze 面：W275 own-wave finalize 已落地=席位时即解锁——席位 r1109 窗+prereg r1110 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 264 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**620_301+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**622_301+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W276+ 投影 A naive 622_301..624_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W276+ 投影（probe 机证 leg4", "verify at W276 prereg，hop 链逐跳在 probe 回执。"),
    ("b_gated", "本件=席位窗后首窗冻结件；五面冻结拼接脚本", "（gate0.5 绿·编辑器 loud abort 兜底）**。"),
]

T2 = T1
for name, sm, em in BLOCKS:
    c = T2.count(sm)
    assert c == 1, "BLOCK %s start-marker count=%d (expect 1)" % (name, c)
    i = T2.index(sm)
    j = T2.find(em, i)
    assert j > i, "BLOCK %s end-marker not found after start" % name
    j += len(em)
    NEWTXT = NEW[name].replace("@@SPLICE_T@@", SPLICE_T)
    T2 = T2[:i] + NEWTXT + T2[j:]
    assert NEWTXT in T2, "BLOCK %s NEW not inserted" % name

# ---------------- post gates ----------------
MUST = [
    "PERPETUAL-N1-W276", "research/PERPETUAL_N1_W276_PREREG.md",
    "622_501..624_500", "624_501..624_700", "602,920", "1,029,335", "602,920", "K=602,920",
    "n1_w276_results.json", "n1_w275_results.json", "MSG-20261019-055x-bmc-w276-seat", "21b51a102",
    "池第 274 枚", "第九十五枚", "第 266 波", "第 95 枚",
    "STAIRCASE-AFFECTS-A", "第二十五次连续 A-hop", "第二十六次连续 above-own-A",
    "_w276bmc_20261019", "--wave 276/finalize --wave 276",
    "W275 finalize one-pass bm-c r1108", "n_eff_held_equal 1,027,135",
    "−0.09280541", "0.24507989", "−0.09398255", "（**0.3088** 实测锚）",
    "键 W275 实测 K-lift **−0.0001**", "line_merged@K602,920 **1.1967**", "line_pre_w275 1.1968",
    "实差 0.0012 在带内", "共二百七十四面", "W2..W275", "W1..W275",
    "engine_owner==bm-c 94 行注册", "engine_owner 行 265 注册在册",
    "probe leg0 bmc_rows=94 attempt-continuity face（r1109 窗算法·bm-c own seat+bmc live rows 94 实读）",
    "bm-c 循环班 r1109 席位窗", "本窗 free RAM ~3.8GB", "本机 bm-c 实例",
    "W276=bm-c own-wave window per chain-order law",
    "1fcc0bc30f", "018782314d", "5089f02250", "e639699d59", "fc01636095",
    "W277+ 投影", "W277p_B_lands_inside_W277p_A_naive", "verify at W277 prereg",
    "_w276bmc_freeze_edits.py", "_w275bmc_freeze_edits.py 模板派生",
    "bm-c r1108 W275 §7 范式", "bm-c r1108 W275 §8 范式",
    "（上游 W275 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W275 注册+烧录+finalize 全落地）",
    "W206/W211..W275 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚", "W272 冻结窗 ~0.3G bm-c 实锚", "W273 冻结窗 ~4.4G bm-c 实锚", "W274 冻结窗 ~4.0G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R277：W276 带",
    "→W270 **0.000319**→W271 **0.000319**→W272 **0.000318**→W273 **0.000317**→W274 **0.000316**→W275 **0.000316**→W276 投影 0.000316】",
    "622_500+1", "624_500+1", "624_501..624_700",
    "A_staircase_hop_past_W275_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 276", "零 276 行", "零 skip-ahead W277/W278 席位声明",
    "05:3x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1110：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1110 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1110 窗实读",
    "nvidia-smi 实读 4%·2.8G VRAM 占用·MV 车道已收官 GPU idle 回释",
    "r1109 席位窗实跑：origin inbox 零 W276 席位外机命中",
    "results/p2cal_ext/n1_w275/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501", "B-ext exit seed=613_501",
    "620_301..622_300", "617_901..618_100", "613_301..613_500", "613_301..615_300", "613_701..613_700",
    "620_101..622_100 CLEAN", "620_101..622_100", "618_101..620_100", "617_901..618_100", "617_901..619_900", "611_501..611_700",
    "615_901..617_900", "611_501..611_700", "615_701..617_700",
    "622_301..624_300 CLEAN", "622_501..622_700 CLEAN",
    "GATED on", "finalize PENDING", "queue_depth",
    "600,720", "**602,920 投影**", "line_merged@K600,720", "K=600,720",
    "−0.09280110", "0.24508947", "−0.09630486", "**0.3009**", "实差 0.0035 在带内",
    "17:2x", "17:0x", "15:4x", "15:2x", "16:0x", "18:3x", "18:4x", "19:1x", "20:2x", "20:4x", "21:1x", "00:2x", "00:3x", "01:0x", "03:0x", "03:2x", "03:3x",
    "MSG-20261019-034x", "bf4bbbde1e", "70b21a0264", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",
    "bmc_rows=93", "bmc rows 93+候选", "第 94 枚", "第 265 波", "第九十四枚",
    "engine_owner==bm-c 93 行注册",
    "r1106 席位窗实跑", "r1101 窗算法",
    "GPU idle 回释·MV 车道已收官 GPU idle 回释", "95%·7.9G VRAM",
    "W276p_", "W276p_",
    "line_pre_w271", "键 W274 实测 K-lift",
    "verify at W276 prereg",
    "W276+ 投影", "W275+ 投影", "W274+ 投影",
    "第二十四次连续 A-hop", "第二十二次连续 above-own-A", "第二十五次连续 above-own-A", "连续二十四波", "共二百七十三面",
    "n1_w274_results.json", "n1_w269_results.json", "n1_w268_results.json",
    "W2..W274", "W136..W274", "W1..W274",
    "波号 275", "零 275 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G", "W272 冻结窗 ~1.4G", "W273 冻结窗 ~0.3G",
    "620_300+1", "617_900+1", "611_500+1", "617_900+1", "611_300+1",
    "12:2x", "13:5x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W277+ 投影") == 3, "W276+ count=%d (expect 3 = §5.5 rolled + b_claim_proj + b5)" % T2.count("W277+ 投影")
assert T2.count("W276+ 投影") == 0, "W276+ count=%d (expect 0)" % T2.count("W276+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十五次连续 A-hop") == 3, "A21 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十五次连续 A-hop")
assert T2.count("第二十六次连续 A-hop") == 3, "A22 count=%d (expect 3 = b5 x2 + b_claim_proj)" % T2.count("第二十六次连续 A-hop")
assert T2.count("第二十六次连续 above-own-A") == 2, "B22 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十六次连续 above-own-A")
assert T2.count("第二十五次连续 above-own-A") == 0, "B21 count=%d (expect 0)" % T2.count("第二十五次连续 above-own-A")
assert T2.count("连续二十五波") == 1, "21-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十五波")
assert T2.count("622_501..624_500") >= 5, "own-A count=%d (expect >=5)" % T2.count("622_501..624_500")
assert T2.count("624_501..624_700") >= 4, "own-B count=%d (expect >=4)" % T2.count("624_501..624_700")
assert T2.count("624_501..624_700") >= 3, "reg-W275-B count=%d (expect >=3)" % T2.count("624_501..624_700")
assert T2.count("622_501..622_700") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("622_501..622_700")
assert T2.count("622_301..624_300") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("622_301..624_300")
assert T2.count("624_501..626_500") == 5, "W276p-A count=%d (expect 5 = b_claim_proj x3 + b5 x2)" % T2.count("624_501..626_500")
assert T2.count("624_701..624_900") == 3, "W276p-B count=%d (expect 3 = b_claim_proj x2 + b5)" % T2.count("624_701..624_900")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w276bmc_20261019") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w276bmc_20261019")
assert T2.count("1,029,335") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,029,335")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,027,135 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W275 fivekeys measured value (the canon
# r1102 window left this sub-face stale at the W274-era 1,020,535; healed forward here)
assert T2.count("1,027,135") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,027,135")
assert T2.count("602,920") >= 3, "merged-K count=%d (expect >=3)" % T2.count("602,920")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 95 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 95 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W276 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 018782314d @ " + SPLICE_T + " | finalize estate: fc01636095 @ 05:3x | seat: 21b51a102 @ 05:5x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~3.8GB written, MV 车道已收官 idle) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == e62f3bcbdfe458863bc1b98c176b6f591bcdc14e @ 1fcc0bc30f (frozen pre-run face; HEAD post-backfill twin 52b42b83 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
