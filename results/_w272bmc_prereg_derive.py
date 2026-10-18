# -*- coding: utf-8 -*-
# r1099 bm-c: W272 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w271bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W271 prereg AT THE FREEZE COMMIT f75b18c862 (git
# f75b18c862:research/PERPETUAL_N1_W271_PREREG.md, 23,336 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w272bmc_w271_frozen_face.txt by the r1098 prep window
# via python subprocess raw bytes; byte-verified: disk==blob sha256_16 f8b4a755d81bfbe5.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin e204ebdd512eb4a27a2e76ff5040399357b9d154
# (27,175 bytes) = the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1097
# W271 cycle (estate e0a21b817d). Deriving from the backfilled face would fabricate W272 sec.7/8
# from W271 measured numbers -- the r1049/r1052 precedent requires the f75b18c862 frozen pre-run
# face. W272 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w272bmc_20261018_probe_receipt.json (bm-c r1098 window
#     authored+run live, seat rides origin f608ff1cee per r565 early-visibility law,
#     MSG-20261018-191x-bmc-w272-seat landed on origin; zero foreign W272 seat claims; zero
#     W273/W274 skip-claims). STAIRCASE CONTINUES: A naive 613_501..615_500 REFUSED at start
#     (registered W271 B band 613_501..613_700 sits INSIDE the naive A window) -> A first-clean
#     613_701..615_700 hops=1 (TWENTY-FIRST consecutive A-hop, W271 prereg sec.5 item5
#     post-W271-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) /
#     B naive 613_701..613_900 lands INSIDE the own-wave W272 A first-clean window 613_701..615_700
#     (own-A reservation cascade) -> hop past own-A tail 615_700 -> 615_701..615_900 hops=1
#     (TWENTY-SECOND consecutive above-own-A landing); seed_admit FREE x2 (A base=613701 span=2000 /
#     B base=615701 span=200); leg0 rows=269 owner_rows=261 bmc_rows=90 ordinal=262; leg2
#     conflicts=0; leg3 origin_vacancy=true; W273p projection: A naive 615_701..617_700 CLEAN
#     hops=0 / B naive 615_901..616_100 CLEAN hops=0 but lands inside W273p A naive.
#   - upstream W271 finalize LANDED (bm-c r1097 window one-pass, n1_w271_results.json landed via
#     e0a21b817d 18:46:31, fivekeys 6/6 receipt results/_r1097bmc_w271_fivekeys.json + sec.7/8
#     backfilled): merged K=594,120 / ledger 1,020,535 EXACT (1,018,335+2,200) / merged mu
#     -0.09276411835992728 (8dp -0.09276412) / sigma 0.24509039950538597 (8dp 0.24509040) /
#     se_mu@K594,120 0.000318 (narrowed from 0.000319) / W271-only mu -0.10277222727272727
#     (8dp -0.10277223) / A p95 0.3042 / K-lift +0.0001 / n_eff_held 1,018,335 / line_pre_w271
#     1.1963 / line_merged@594,120 1.1964 / key1 only-vs-merged gap 0.01000810891279999 (4dp 0.0100)
#     in-band; splice 7dd091eef1 18:33:39 (r1097 window, CLEAN-AT-BIRTH 4th gen); engine self-burn
#     12/12 batched ledger appends a035552321+037445477b; sixgate 34th consecutive PRE-FINALIZE ALL
#     PASS. ANCHOR LAW: prereg prose carries 8dp rounded narration faces; ALL gates machine-verify
#     against the full-precision fivekeys/results jsons (r1093 CODELY pit entry; live-read governs
#     r587).
# Needle-count pre-flight evidence: results/_w272bmc_needle_probe.py + results/_w272bmc_needle_probe.json
# (MEASURED live on T0 + T1 roll-simulation THIS window; floors below match every measured count;
# r1077 measured-counts law). Probe verdict: 8/8 block markers count==1 spans valid; placeholders
# zero-residual; ALL old-band instances (611_501..613_500 / 613_501..613_700 / 611_301..611_500 /
# 611_301..613_300 / 613_501..615_500 / 613_701..613_900) classified block-interior (outside=0)
# -> discarded by block replace; 609_101..609_300 family absent; static anchors W244/W247 survive
# outside blocks un-rolled by design; T0 stamps 17:2x=5 / 17:0x=2 (3+2 block-interior, 2 live).
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092/r1096 family):
# (1) finalize-window stamp roll: W271 finalize one-pass landed 18:4x (e0a21b817d 18:46:31); T0
#     carries the W270-era 17:2x stamps x5 (measured: 3 block-interior copies discarded by block
#     replace + 2 live sec.5 preamble faces) -> POST_LEG x5.
# (2) sec.5 item1 measured keys -> W271 actuals (n1_w271_results + fivekeys machine values):
#     merged mu -0.09276412 / K=594,120 / W271-only -0.10277223 (all full-precision
#     machine-verified in-gate).
# (3) sec.5 item1 diff face: W271-only vs merged TRUE diff = 0.0100 @4dp (measured
#     0.01000810891279999 full) in-band |d|<0.02.
# (4) sec.5 item2 sigma key 0.24507005 -> 0.24509040 (W271 merged-pool measured).
# (5) sec.5 item3 p95 anchor 0.3268 -> 0.3042 (W271 A-band fivekeys measured).
# (6) sec.5 item4 K-lift chain: K-lift +0.0001 (W271 fivekeys key4) + line_merged@K594,120 1.1964
#     + lowercase line_pre_w270 -> line_pre_w271 1.1963 (lowercase NOT rolled by the W-roll,
#     case-sensitive; r1096 heal (6) family) + n_eff_held_equal 1,016,135 -> 1,018,335.
# (7) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries W271
#     0.000319 (FALSE -- true W271 measured 0.000318) -> POST_LEG rewrites the tail with true
#     history W266 0.000321 / W267 0.000320 / W268 0.000320 / W269 0.000319 / W270 0.000319 /
#     W271 0.000318 and appends the W272 projection 0.000318.
# (8) sec.4 merged-pool anchor face: W1..W270 591,920 -> W1..W271 594,120 (W271 finalize landed).
# (9) sec.7/8 backfill paradigm rows: bm-c r1095 W270 -> bm-c r1097 W271 (cycle owner + wave roll).
# (10) RAM face live-measured THIS window: psutil 1.38GB available (~1.4GB, probe-time read) +
#     nvidia-smi 100% util / 15,538MiB (~15.2G) VRAM occupied -- MV PACK-A i2v GPU burn IN FLIGHT
#     (CEO weekend production order; legal occupant untouchable); the r1096 ~3.3GB face is stale.
# (11) low-RAM precedent ledger append: W271 freeze-window ~1.4G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W270 ~3.3G onto W271 -- both restored + true W271
#     anchor appended).
# (12) seat/provenance legs: MSG-20261018-175x-bmc-w271-seat/87d2697cdc/r1095 ->
#     MSG-20261018-191x-bmc-w272-seat/f608ff1cee/r1098 (two live faces + block NEWs).
# (13) engine live-read faces r1096 -> r1099 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat fresh).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w272bmc_w271_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W272_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "a5aad2251d04d082c031b61d67dc3d5b0f39b06f"   # freeze-commit face @ f75b18c862
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "f75b18c862:research/PERPETUAL_N1_W271_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W271_PREREG.md"])
assert _hb == "e204ebdd512eb4a27a2e76ff5040399357b9d154", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23336, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "f8b4a755d81bfbe5", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("f75b18c862", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d", "f608ff1cee"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "7dd091eef1"])    # 2026-10-18 18:33:39 +0800
_m = re.match(r"2026-10-18 18:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "18:%sx" % _m.group(1)[0]   # 18:3x
_fz = git_out(["show", "-s", "--format=%ci", "e0a21b817d"])    # 2026-10-18 18:46:31 +0800
assert _fz.startswith("2026-10-18 18:4"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "f608ff1cee"])   # 2026-10-18 19:10:53 +0800
assert _st.startswith("2026-10-18 19:1"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w271_results.json"])
assert _fin_log == "e0a21b817d", "W271 finalize product landed by unexpected commit: %s" % _fin_log
_seat_log = git_out(["log", "-1", "--format=%h", "--", "fleet/inbox/MSG-20261018-191x-bmc-w272-seat.md"])
assert _seat_log == "f608ff1cee", "W272 seat MSG landed by unexpected commit: %s" % _seat_log

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1097bmc_w271_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 594120, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09276412, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24509040, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k594120"], 6) == 0.000318, "se_mu drift: %r" % fk["merged"]["se_mu_k594120"]
assert round(fk["w271_only"]["mu"], 8) == -0.10277223, "w271-only mu drift: %r" % fk["w271_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3042, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1018335, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w271"], 4) == 1.1963, "line_pre drift: %r" % fk["skill_line"]["line_pre_w271"]
assert round(fk["skill_line"]["line_merged_594120"], 4) == 1.1964, "line_merged drift: %r" % fk["skill_line"]["line_merged_594120"]
assert fk["ledger_identity"]["total"] == 1020535 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w271_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.01 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w271_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1018335
assert round(res["skill_line_v2_k_lift"]["line_pre_w271"], 4) == 1.1963
assert round(res["skill_line_v2_k_lift"]["line_merged_594120"], 4) == 1.1964
assert round(res["null_pool_cumulative"]["se_mu_at_k594120"], 6) == 0.000318, "W271 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w270_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k591920"], 6) == 0.000319, "W270 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w272bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [613701, 615700] and pr["bands"]["B"] == [615701, 615900]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [613501, 615500], "jump_to": 613701,
                              "refuser_pts": [], "refuser_bands": [[613501, 613700]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [613701, 613900], "jump_to": 615701,
                              "refuser_pts": [], "refuser_bands": [[613701, 615700]]}]
assert l1["B_naive"] == [613701, 613900] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W271_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W271_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W269_W270_W271_bands_respected_A"] is True and _ra["W269_W270_W271_bands_respected_B"] is True  # r1100 heal: labels rolled one triple forward (seat-time clone stale-label defect; receipt healed in-kind, git f608ff1cee preserves the seat-time original)
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 269 and _l0["owner_rows"] == 261 and _l0["bmc_rows"] == 90
assert _l0["ordinal"] == 262 and _l0["w271_finalize_landed"] is True
assert _l0["w271_finalize_anchors"]["ledger_total"] == 1020535
assert _l0["w271_finalize_anchors"]["merged_n"] == 594120
assert round(_l0["w271_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=613701 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=615701 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W273p_A_naive"] == "615701..617700"
assert pr["legs"]["leg4"]["W273p_B_naive"] == "615901..616100"
assert pr["legs"]["leg4"]["W273p_B_lands_inside_W273p_A_naive"] is True

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
# r1099 window face: probe-time read = 1.38GB available (MV PACK-A i2v GPU-lane burn in
# flight, CEO weekend production order = legal occupant, untouchable; RAM fluctuates across
# the burn cycle). Wide gate keeps idempotent re-runs green across the burn-cycle
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=611_501..613_500", "A-ext seed=613_701..615_700"),
    ("B-ext exit seed=613_501..613_700", "B-ext exit seed=615_701..615_900"),
    ("entry rng=**611_501+j**（与 A[j] 同源配对语义逐字", "entry rng=**613_701+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W272 seat published bm-c r1098, rides origin f608ff1cee)
    ("席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc r565 律（bm-c r1095 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-191x-bmc-w272-seat 已推 origin f608ff1cee r565 律（bm-c r1098 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cdc r565 律",
     "席位公示 MSG-20261018-191x-bmc-w272-seat 先推 origin f608ff1cee r565 律"),
    # wave-number + vacancy faces
    ("波号 271", "波号 272"),
    ("r1095 席位窗实跑：origin inbox 零 W271 席位外机命中", "r1098 席位窗实跑：origin inbox 零 W272 席位外机命中"),
    ("零 271 行", "零 272 行"),
    ("零 skip-ahead W272/W273 席位声明", "零 skip-ahead W273/W274 席位声明"),
    ("池第 269 枚", "池第 270 枚"),
    # ordinals + own-wave faces
    ("第 261 波", "第 262 波"),
    ("bm-c 第九十枚自有波", "bm-c 第九十一枚自有波"),
    ("probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT",
     "probe leg0 bmc_rows=90 attempt-continuity face（r1098 窗算法·bm-c own seat+bmc live rows 90 实读）——freeze 时 live derive bmc rows 90+候选=第 91 枚 EXACT"),
    ("engine_owner==bm-c 89 行注册", "engine_owner==bm-c 90 行注册"),
    # engine live-read faces (bm-c instance, r1099 window)
    ("saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1099：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1099 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1099 窗实读"),
    # runner CLI wave
    ("--wave 271/finalize --wave 271", "--wave 272/finalize --wave 272"),
    # sec8 placeholder projection-label bump (W273+ face)
    ("§5.5 W272+ 投影承接机证", "§5.5 W273+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w271", P2), ("n1_w270", "n1_w271"), (P2, "n1_w272"),
    ("_w271bmc", P3), ("_w270bmc", "_w271bmc"), (P3, "_w272bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W271", P1), ("W270", "W271"), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"), ("W266", "W267"),
    ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"),
    ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), (P1, "W272"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1099)
    "A-ext seed=611_501..613_500": 1,
    "B-ext exit seed=613_501..613_700": 1,
    "entry rng=**611_501+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc r565 律（bm-c r1095 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cdc r565 律": 1,
    "波号 271": 1,
    "r1095 席位窗实跑：origin inbox 零 W271 席位外机命中": 1,
    "零 271 行": 1,
    "零 skip-ahead W272/W273 席位声明": 1,
    "池第 269 枚": 1,
    "第 261 波": 1,
    "bm-c 第九十枚自有波": 1,
    "probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT": 1,
    "engine_owner==bm-c 89 行注册": 1,
    "saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读": 1,
    "--wave 271/finalize --wave 271": 1,
    "§5.5 W272+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w271": 4, "n1_w270": 6, "_w271bmc": 4, "_w270bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w272bmc_needle_probe.py r1099 window;
    # measured-counts law r1077)
    "W271": 34, "W270": 61, "W269": 4, "W268": 4, "W267": 3, "W266": 3, "W265": 2, "W264": 2, "W263": 2,
    "W262": 1, "W261": 1, "W260": 1, "W259": 1, "W258": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 260 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**611_501+j**": 1,
    "exit rng=**613_501+j**": 1,
    "probe W272+ 投影 A naive 613_501..615_500 CLEAN hops=0": 1,
    "5. **W272+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 1,016,135": 1,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "17:2x": 5, "17:0x": 2,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w272bmc": 0, "n1_w272": 0, "W273p_": 0,
    "第 91 枚": 0, "第 262 波": 0, "第九十一枚": 0, "池第 270 枚": 0, "波号 272": 0, "零 272 行": 0,
    "engine_owner==bm-c 90 行注册": 0, "bmc_rows=90": 0, "bmc rows 90+候选": 0,
    "第二十二次连续 A-hop": 0, "第二十二次连续 above-own-A": 0, "连续二十一波": 0, "共二百七十面": 0,
    "1,020,535": 0, "596,320": 0, "613_701..615_700": 0, "615_701..615_900": 0,
    "615_701..617_700": 0, "615_901..616_100": 0,
    "18:3x": 0, "18:4x": 0, "19:1x": 0,
    "f75b18c862": 0, "7dd091eef1": 0, "a035552321": 0, "037445477b": 0, "e0a21b817d": 0, "f608ff1cee": 0,
    "−0.09276412": 0, "0.24509040": 0, "−0.10277223": 0, "0.3042": 0,
    "实差 0.0100 在带内": 0, "line_pre_w271 1.1963": 0, "line_merged@K594,120": 0, "K=594,120": 0,
    "r1097 W271 §7 范式": 0, "（W271 注册+烧录+finalize 全落地）": 0,
    "MSG-20261018-191x": 0, "键 W271 实测 K-lift": 0, "本窗 free RAM ~1.4GB": 0,
    "611_501..613_500 CLEAN": 0,
    "609_101..609_300": 0, "609_101..611_100": 0, "609_301..609_500": 0, "607_101..609_100": 0,
    "607_101..607_300": 0, "606_901..608_900": 0,
    "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "609_100+1": 0, "611_300+1": 0, "609_300+1": 0,
    # NOTE (fail-closed discipline): 第二十次连续 A-hop (T0=3) / 第二十一次连续 above-own-A
    # (T0=2) / 第二十一次连续 A-hop (T0=3) / 连续二十波 (T0=1) / 共二百六十九面 (T0=1) are NOT
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
        raise SystemExit("VMAP FLOOR FAIL: %r count=%d floor=%d" % (o, c))

T1 = xf(T0)

# ---------------- post-roll correction legs (needles exist only in T1 after the rolls) ----------------
VMAP_POST_LEGS = [
    # finalize-window stamp roll (heal (1)): W271 finalize one-pass landed 18:4x (e0a21b817d
    # 18:46:31); T1 carries the W270-era 17:2x stamps x5 (measured: 3 block-interior copies
    # discarded by block replace + 2 live sec.5 preamble faces)
    ("17:2x", "18:4x", 5),
    # sec.5 item1 measured keys -> W271 actuals (n1_w271_results + fivekeys machine values)
    ("（W271 实测键 **−0.09272692**·K=591,920 合并池·W271-only 实测 **−0.09170727**）",
     "（W271 实测键 **−0.09276412**·K=594,120 合并池·W271-only 实测 **−0.10277223**）", 1),
    ("W2..W271 共二百六十九面实测 mu 稳定先例", "W2..W271 共二百七十面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (3)): TRUE W271 diff = 0.0100 @4dp (measured
    # 0.01000810891279999 full), in-band
    ("W271-only vs merged 实差 0.0010 在带内", "W271-only vs merged 实差 0.0100 在带内", 1),
    # sec.5 item2 sigma key (heal (4))
    ("键 **0.24507005**=W271 合并池实测", "键 **0.24509040**=W271 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (5))
    ("与 W271 A 档 p95（**0.3268** 实测锚）", "与 W271 A 档 p95（**0.3042** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (6): lowercase line_pre_w270 NOT rolled by the
    # W-roll; true W271 anchors K-lift +0.0001 + line_merged@K594,120 1.1964 +
    # line_pre_w271 1.1963 + n_eff_held 1,018,335)
    ("键 W271 实测 K-lift **+0.0000**·line_merged@K591,920 **1.1962**·line_pre_w270 1.1962·n_eff_held_equal 1,016,135",
     "键 W271 实测 K-lift **+0.0001**·line_merged@K594,120 **1.1964**·line_pre_w271 1.1963·n_eff_held_equal 1,018,335", 1),
    # se_mu chain true-history correction (heal (7); r1097 fivekeys key5 measured W271=0.000318
    # narrowed from W270 0.000319)
    ("→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 **0.000319**→W272 投影 0.000319】",
     "→W266 **0.000321**→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 投影 0.000318】", 1),
    # sec.4 merged-pool anchor face (heal (8): W271 finalize landed)
    ("W1..W271 已落账 591,920 实测", "W1..W271 已落账 594,120 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W271 cycle (heal (9): bm-c r1097)
    ("bm-c r1095 W271 §7 范式", "bm-c r1097 W271 §7 范式", 1),
    ("bm-c r1095 W271 §8 范式", "bm-c r1097 W271 §8 范式", 1),
    # RAM face live-measured THIS window (heal (10)): psutil 1.38GB available (~1.4GB) +
    # nvidia-smi 100% util / 15,538MiB (~15.2G) VRAM occupied -- MV PACK-A i2v GPU burn IN FLIGHT
    # (CEO weekend production order, legal occupant untouchable); honest window face updated
    # from the r1096 ~3.3GB face
    ("本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 95%·7.9G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~1.4GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.2G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (11)): W271 anchor ~1.4G bm-c appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- the wave-roll had shifted the W263 26G bm-a anchor onto the W264
    # label and the W270 ~3.3G onto W271; both restored + true W271 anchor appended
    ("W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚·W271 冻结窗 ~3.3G bm-c 实锚）",
     "W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚·W271 冻结窗 ~1.4G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 261 注册在册（表尾 W272 行【bm-c r1097 五面冻结 splice 7dd091eef1 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 4th gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w271/ 12/12·ledger append a035552321+037445477b】"
    "·**W271 finalize 已落地**【n1_w271_results.json 机读·净账本锚头 1,020,535·K=594,120 合并池·W271 finalize one-pass bm-c r1097 窗 18:4x·estate chain r1096/r1097 f75b18c862+7dd091eef1+e0a21b817d】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1098 席位 MSG-20261018-191x-bmc-w272-seat 已推 origin f608ff1cee"
    "·probe receipt _w272bmc_20261018 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 90+候选=第 91 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1098 席位窗 2026-10-18 19:1x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W272=bm-c own-wave window per chain-order law（W269 bm-c→W270 bm-c→W271 bm-c→W272 bm-c own-turn rotation·MSG-191x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W271 N1 注册全部落地**【W271=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W271**"
    "【净账本锚头 **1,020,535**·K=594,120 合并池·n1_w271_results.json 机读·W271 finalize one-pass bm-c r1097 窗 18:4x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W271 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=594,120+2,200（本波）=**596,320 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十一次连续 A-hop）**："
    "A 面算术续带 613_501..615_500（自注册 W271 A 尾 613_500 续）"
    "在席位窗宇宙（post-W271-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W271 B 带 613_501..613_700 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W271 prereg §5 item5 post-W271-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W271 B 尾 613_700→A first-clean **613_701..615_700**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（613_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 613_501..615_500→jump 613_701·refuser band 613_501..613_700〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W271_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=615_701..615_900**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十二次连续 above-own-A 落位）**："
    "B naive 续带 613_701..613_900（自注册 W271 B 尾 613_700+1 续）"
    "在席位窗宇宙（post-W271-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 613_701..613_900 落本波 A first-clean 窗 613_701..615_700 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 613_701..615_700**（1 hop）"
    "→**1 hop** 落位 **615_701..615_900**·**B 落位 base==本波 A 窗尾+1（615_700+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W271 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W272 A naive 613_501..615_500 将被注册 W271 B 带拒（staircase affects A 承袭·第二十一次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R273：W272 带（A 613_701..615_700/B 615_701..615_900）注册后对 W273+ 的拒面影响=W272 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**613_701+j**（法典 §4 W272 行 A=613_701..615_700·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十一次连续 A-hop）**："
    "A 算术续带 613_501..615_500（自注册 W271 A 尾 613_500 续）"
    "在席位窗宇宙（post-W271-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W271 B 带 613_501..613_700 落 naive A 窗内=W271 prereg §5 item5 post-W271-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W271 B 尾 613_700→A first-clean 613_701..615_700·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（613_700+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W271_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**615_701+j**（法典 §4 W272 行 B=615_701..615_900·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 613_701..613_900（自注册 W271 B 尾 613_700+1 续）"
    "在席位窗宇宙（post-W271-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 613_701..615_700 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 613_701..615_700→1 hop 落位 615_701..615_900·"
    "**B 落位 base==本波 A 窗尾+1（615_700+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十二次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W271 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W273+ 投影 A naive 615_701..617_700 CLEAN hops=0（零 live refusers）/ B naive 615_901..616_100 CLEAN hops=0 "
    "**但落 naive W273 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 615_701..617_700 CLEAN·hops=0——**post-W272-REGISTERED 预披露：naive W273 A 起点将被注册 W272 B 带 615_701..615_900 拒=staircase affects A 第二十二次连续 A-hop 预期**；"
    "投影 B naive 615_901..616_100 clean 但落 naive W273 A 窗 615_701..617_700 内——"
    "**above-own-A 承袭面：W272 B 615_701..615_900 落本波 A 窗之上〔第二十二次连续〕·W273 A 面 1-hop=staircase affects A〔第二十二次连续〕·"
    "W274 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W272 B 带将拒 naive W273 A 窗仅当重叠——"
    "**W274 freezer 承接面强制注记：须在 post-W273 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W273+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 615_701..617_700 **CLEAN**（hops=0·pre-W272 宇宙零 live refusers）——"
    "**post-W272-REGISTERED 预披露：naive W273 A 起点将被注册 W272 B 带 615_701..615_900 拒（staircase-affects-A 第二十二次连续 A-hop 预期）**；"
    "B naive **615_901..616_100 CLEAN（hops=0）但落投影 A 窗 615_701..617_700 内**（W273p_B_lands_inside_W273p_A_naive=true——"
    "**staircase face 延续**：W272 A 613_701..615_700+B 615_701..615_900 注册后 naive W273 A 窗起点即被注册 W272 B 带拒（staircase affects A 承袭·第二十二次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W272 宇宙 live re-derive 必变·禁转录投影）；"
    "**W273 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271/W272=A/B 双 1-hop 形态连续二十一波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W273 冻结方必须在 post-W272 注册宇宙重 derive 且 derive B 时预留本波 A 窗 613_701..615_700+本波 B 带 615_701..615_900"
    "——leg2 律/E36 卡·W141 先例；verify at W273 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w272bmc_freeze_edits.py"
    "（按 _w271bmc_freeze_edits.py 模板派生·gate0.5 自查 W271 行+W271 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1096/r1097 W271 先例实时间线：prereg f75b18c862 落于 r1096 窗·splice 7dd091eef1 落于 r1097 执行窗 @@SPLICE_T@@——"
    "**W272 freeze 面：W271 own-wave finalize 已落地=席位时即解锁——席位 r1098 窗+prereg r1099 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 260 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**611_501+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**613_501+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W272+ 投影 A naive 613_501..615_500 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W272+ 投影（probe 机证 leg4", "verify at W272 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W272", "research/PERPETUAL_N1_W272_PREREG.md",
    "613_701..615_700", "615_701..615_900", "596,320", "1,020,535", "594,120", "K=594,120",
    "n1_w272_results.json", "n1_w271_results.json", "MSG-20261018-191x-bmc-w272-seat", "f608ff1cee",
    "池第 270 枚", "第九十一枚", "第 262 波", "第 91 枚",
    "STAIRCASE-AFFECTS-A", "第二十一次连续 A-hop", "第二十二次连续 above-own-A",
    "_w272bmc_20261018", "--wave 272/finalize --wave 272",
    "W271 finalize one-pass bm-c r1097", "n_eff_held_equal 1,018,335",
    "−0.09276412", "0.24509040", "−0.10277223", "（**0.3042** 实测锚）",
    "键 W271 实测 K-lift **+0.0001**", "line_merged@K594,120 **1.1964**", "line_pre_w271 1.1963",
    "实差 0.0100 在带内", "共二百七十面", "W2..W271", "W1..W271",
    "engine_owner==bm-c 90 行注册", "engine_owner 行 261 注册在册",
    "probe leg0 bmc_rows=90 attempt-continuity face（r1098 窗算法·bm-c own seat+bmc live rows 90 实读）",
    "bm-c 循环班 r1098 席位窗", "本窗 free RAM ~1.4GB", "本机 bm-c 实例",
    "W272=bm-c own-wave window per chain-order law",
    "f75b18c862", "7dd091eef1", "a035552321", "037445477b", "e0a21b817d",
    "W273+ 投影", "W273p_B_lands_inside_W273p_A_naive", "verify at W273 prereg",
    "_w272bmc_freeze_edits.py", "_w271bmc_freeze_edits.py 模板派生",
    "bm-c r1097 W271 §7 范式", "bm-c r1097 W271 §8 范式",
    "（上游 W271 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W271 注册+烧录+finalize 全落地）",
    "W206/W211..W271 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "W271 冻结窗 ~1.4G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R273：W272 带",
    "→W266 **0.000321**→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 **0.000318**→W272 投影 0.000318】",
    "613_700+1", "615_700+1", "613_501..613_700",
    "A_staircase_hop_past_W271_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 272", "零 272 行", "零 skip-ahead W273/W274 席位声明",
    "18:4x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1099：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1099 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1099 窗实读",
    "MV PACK-A i2v wave-1 烧批在飞",
    "r1098 席位窗实跑：origin inbox 零 W272 席位外机命中",
    "results/p2cal_ext/n1_w271/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=611_501", "B-ext exit seed=613_501",
    "611_501..613_500", "611_301..611_500", "611_101..611_300", "611_101..613_100", "611_501..611_500",
    "611_301..613_300 CLEAN", "611_301..613_300", "609_301..611_300", "609_101..609_300", "609_101..611_100", "609_301..609_500",
    "607_101..609_100", "607_101..607_300", "606_901..608_900",
    "613_501..615_500 CLEAN", "613_701..613_900 CLEAN",
    "GATED on", "finalize PENDING", "queue_depth",
    "591,920", "**594,120 投影**", "line_merged@K591,920", "K=591,920",
    "−0.09272692", "0.24507005", "−0.09170727", "**0.3268**", "实差 0.0010 在带内",
    "17:2x", "17:0x", "15:4x", "15:2x", "16:0x",
    "MSG-20261018-175x", "87d2697cdc", "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbb",
    "bmc_rows=89", "bmc rows 89+候选", "第 90 枚", "第 261 波", "第九十枚",
    "engine_owner==bm-c 89 行注册",
    "r1095 席位窗实跑", "r1095 窗算法",
    "本窗 free RAM ~3.3GB", "95%·7.9G VRAM",
    "W272p_", "W271p_",
    "line_pre_w270", "键 W270 实测 K-lift",
    "verify at W272 prereg",
    "W272+ 投影", "W271+ 投影", "W270+ 投影",
    "第二十次连续 A-hop", "第二十次连续 above-own-A", "第二十一次连续 above-own-A", "连续二十波", "共二百六十九面",
    "n1_w270_results.json", "n1_w269_results.json", "n1_w268_results.json",
    "W2..W270", "W136..W270", "W1..W270",
    "波号 271", "零 271 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G", "W271 冻结窗 ~3.3G",
    "611_500+1", "613_500+1", "609_300+1", "611_300+1", "609_100+1",
    "12:2x", "13:5x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W273+ 投影") == 3, "W273+ count=%d (expect 3 = §5.5 rolled + b_claim_proj + b5)" % T2.count("W273+ 投影")
assert T2.count("W272+ 投影") == 0, "W272+ count=%d (expect 0)" % T2.count("W272+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十一次连续 A-hop") == 3, "A21 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十一次连续 A-hop")
assert T2.count("第二十二次连续 A-hop") == 3, "A22 count=%d (expect 3 = b5 x2 + b_claim_proj)" % T2.count("第二十二次连续 A-hop")
assert T2.count("第二十二次连续 above-own-A") == 2, "B22 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十二次连续 above-own-A")
assert T2.count("第二十一次连续 above-own-A") == 0, "B21 count=%d (expect 0)" % T2.count("第二十一次连续 above-own-A")
assert T2.count("连续二十一波") == 1, "21-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十一波")
assert T2.count("613_701..615_700") >= 5, "own-A count=%d (expect >=5)" % T2.count("613_701..615_700")
assert T2.count("615_701..615_900") >= 4, "own-B count=%d (expect >=4)" % T2.count("615_701..615_900")
assert T2.count("613_501..613_700") >= 3, "reg-W271-B count=%d (expect >=3)" % T2.count("613_501..613_700")
assert T2.count("613_701..613_900") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("613_701..613_900")
assert T2.count("613_501..615_500") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("613_501..615_500")
assert T2.count("615_701..617_700") == 5, "W273p-A count=%d (expect 5 = b_claim_proj x3 + b5 x2)" % T2.count("615_701..617_700")
assert T2.count("615_901..616_100") == 3, "W273p-B count=%d (expect 3 = b_claim_proj x2 + b5)" % T2.count("615_901..616_100")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w272bmc_20261018") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w272bmc_20261018")
assert T2.count("1,020,535") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,020,535")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,018,335 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W271 fivekeys measured value (the canon
# r1096 window left this sub-face stale at the W270-era 1,016,135; healed forward here)
assert T2.count("1,018,335") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,018,335")
assert T2.count("594,120") >= 3, "merged-K count=%d (expect >=3)" % T2.count("594,120")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 91 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 91 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W272 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 7dd091eef1 @ " + SPLICE_T + " | finalize estate: e0a21b817d @ 18:4x | seat: f608ff1cee @ 19:1x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~1.4GB written, MV PACK-A burn window) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == a5aad2251d04d082c031b61d67dc3d5b0f39b06f @ f75b18c862 (frozen pre-run face; HEAD post-backfill twin e204ebdd disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
