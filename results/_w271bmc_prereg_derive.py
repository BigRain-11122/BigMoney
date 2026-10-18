# -*- coding: utf-8 -*-
# r1096 bm-c: W271 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w270bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W270 prereg AT THE FREEZE COMMIT 3bb8b9308e (git
# 3bb8b9308e:research/PERPETUAL_N1_W270_PREREG.md, 23,259 bytes -- the frozen pre-run face; sec7/8
# placeholders intact). Extracted to results/_w271bmc_w270_frozen_face.txt THIS window via python
# subprocess raw bytes (PS Out-File pipeline = GBK re-encode + newline-eat corruption, discarded
# same-window and re-extracted byte-clean); byte-verified: disk==blob sha1
# 626148d08dbccddb91c83373c679b416951eb7b9, sha256_16 3aa0b98239369608 (== r1094 closeout record).
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin 92f167f2c8823e2bb7b24be03f70b421934546be =
# the CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1095 W270 cycle
# (estate e4b015cbb). Deriving from the backfilled face would fabricate W271 sec.7/8 from W270
# measured numbers -- the r1049/r1052 precedent requires the 3bb8b9308e frozen pre-run face.
# W271 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w271bmc_20261018_probe_receipt.json (bm-c r1095 window
#     authored+run live, seat rides origin 87d2697cd per r565 early-visibility law,
#     MSG-20261018-175x-bmc-w271-seat landed on origin [seat commit ts 17:27:39 = the machine-
#     measured seat-window stamp 17:2x; the MSG filename label "175x" is the r1095 authored
#     label, referenced verbatim]; zero foreign W271 seat claims; zero W272/W273 skip-claims).
#     STAIRCASE CONTINUES: A naive 611_301..613_300 REFUSED at start (registered W270 B band
#     611_301..611_500 sits INSIDE the naive A window) -> A first-clean 611_501..613_500 hops=1
#     (TWENTIETH consecutive A-hop, W270 prereg sec.5 item5 post-W270-REGISTERED pre-disclosure
#     confirmed live per r587, ZERO divergence) / B naive 611_501..611_700 lands INSIDE the
#     own-wave W271 A first-clean window 611_501..613_500 (own-A reservation cascade) -> hop
#     past own-A tail 613_500 -> 613_501..613_700 hops=1 (TWENTY-FIRST consecutive above-own-A
#     landing); seed_admit FREE x2 (A base=611501 span=2000 / B base=613501 span=200);
#     leg0 rows=268 owner_rows=260 bmc_rows=89 ordinal=261; leg2 conflicts=0; leg3
#     origin_vacancy=true; W272p projection: A naive 613_501..615_500 CLEAN hops=0 / B naive
#     613_701..613_900 CLEAN hops=0 but lands inside W272p A naive (21st A-hop expected
#     post-register).
#   - upstream W270 finalize LANDED (bm-c r1095 window one-pass, n1_w270_results.json landed via
#     e4b015cbb 17:21:45, fivekeys 6/6 receipt results/_r1095bmc_w270_fivekeys.json + sec.7/8
#     backfilled): merged K=591,920 / ledger 1,018,335 EXACT (1,016,135+2,200) / merged mu
#     -0.09272692103662657 (8dp -0.09272692) / sigma 0.24507005071368662 (8dp 0.24507005) /
#     se_mu@K591,920 0.000319 / W270-only mu -0.09170727272727272 (8dp -0.09170727) / A p95
#     0.3268 / K-lift 0.0000 held-flat / n_eff_held 1,016,135 / line_pre_w270 1.1962 /
#     line_merged@591,920 1.1962 / key1 gap 0.001019648309353846 (4dp 0.0010) in-band;
#     splice 1c814343e 17:06:00 (r1095 window, CLEAN-AT-BIRTH 3rd gen, zero surgical heals,
#     segment-scoped setwave presence gates _set_wave(270):1/(269):0/(268):0); engine self-burn
#     12/12 batched ledger appends 6c1aee751d+ae98b97a10; sixgate 33rd consecutive PRE-FINALIZE
#     ALL PASS. ANCHOR LAW: prereg prose carries 8dp rounded narration faces; ALL gates
#     machine-verify against the full-precision fivekeys/results jsons (r1093 CODELY pit entry;
#     live-read governs r587).
# Needle-count pre-flight evidence: results/_w271bmc_needle_probe.py + results/_w271bmc_needle_probe.json
# (MEASURED live on T0 + T1 roll-simulation THIS window; floors below match every measured count;
# r1077 measured-counts law). Probe verdict: 8/8 block markers count==1 spans valid; placeholders
# zero-residual; ALL old-band instances (609_301..611_300 / 611_301..611_500 / 609_101..609_300 /
# 609_101..611_100 / 609_301..609_500) classified block-interior (outside=0) -> discarded by
# block replace; 607_101..609_100 / 606_901..608_900 family absent two generations; low-W faces
# W256..W251 all block-interior (b5 staircase list) -- only static anchors W244/W247 survive
# outside blocks un-rolled by design.
# Same-window needle heals disclosed (all one-generation shift faces, r1090/r1092 precedent family):
# (1) finalize-window stamp roll: W270 finalize one-pass landed 17:2x (e4b015cbb 17:21:45); T0
#     carries the W269-era 15:4x stamps x4 (measured: 2 block-interior copies discarded later +
#     2 live non-block sec.5 preamble faces) -> POST_LEG x4.
# (2) sec.5 item1 measured keys -> W270 actuals (n1_w270_results + fivekeys machine values):
#     merged mu -0.09272692 / K=591,920 / W270-only -0.09170727 (all full-precision
#     machine-verified in-gate).
# (3) sec.5 item1 diff face: W270-only vs merged TRUE diff = 0.0010 @4dp (measured
#     0.001019648309353846 full) -- the W269-era 0.0019 face is stale, rewritten honestly
#     (0.0010 remains in-band |d|<0.02).
# (4) sec.5 item2 sigma key 0.24506175 -> 0.24507005 (W270 merged-pool measured).
# (5) sec.5 item3 p95 anchor 0.3158 -> 0.3268 (W270 A-band fivekeys measured).
# (6) sec.5 item4 K-lift chain: K-lift +0.0000 held-flat (W270 fivekeys key4) + line_merged@K591,920
#     1.1962 + lowercase line_pre_w269 -> line_pre_w270 1.1962 (lowercase NOT rolled by the
#     W-roll, case-sensitive; r1090 heal (4) family) + n_eff_held_equal 996,335 -> 1,016,135.
# (7) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries W267
#     0.000321 (FALSE -- true W267 measured 0.000320) / W269 0.000320 (FALSE -- true W269
#     measured 0.000319) -> POST_LEG rewrites the tail with true history W266 0.000321 / W267
#     0.000320 / W268 0.000320 / W269 0.000319 / W270 0.000319 (r1095 fivekeys key5 held-flat)
#     and appends the W271 projection 0.000319.
# (8) sec.4 merged-pool anchor face: W1..W270 589,720 -> 591,920 (W270 finalize landed).
# (9) sec.7/8 backfill paradigm rows: bm-c r1093 W269 -> bm-c r1095 W270 (cycle owner + wave roll).
# (10) RAM face live-measured THIS window: psutil 3.32GB available (~3.3GB, probe-time read) +
#     nvidia-smi 95% util / 8046MiB (~7.9G) VRAM occupied -- MV PACK-A i2v GPU burn IN FLIGHT
#     (CEO weekend production order; legal occupant untouchable); the r1094 ~2.1GB face is stale.
# (11) low-RAM precedent ledger append: W270 freeze-window ~3.3G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W269 ~2.1G onto W270 -- both restored + true W270
#     anchor appended).
# (12) seat/provenance legs: MSG-20261018-1605-bmc-w270-seat/9f480646f4/r1094 ->
#     MSG-20261018-175x-bmc-w271-seat/87d2697cd/r1095 (two live faces + block NEWs).
# (13) engine live-read faces r1094 -> r1096 (three live faces, this derive window's fresh read:
#     alive_flag=true, burns_active=[], queue_next=[], heartbeat 56s fresh).
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w271bmc_w270_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W271_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "626148d08dbccddb91c83373c679b416951eb7b9"   # freeze-commit face @ 3bb8b9308e
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "3bb8b9308e:research/PERPETUAL_N1_W270_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W270_PREREG.md"])
assert _hb == "92f167f2c8823e2bb7b24be03f70b421934546be", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23259, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "3aa0b98239369608", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("3bb8b9308e", "1c814343e", "e4b015cbb", "6c1aee751d", "ae98b97a10", "87d2697cd"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "1c814343e"])    # 2026-10-18 17:06:00 +0800
_m = re.match(r"2026-10-18 17:(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "17:%sx" % _m.group(1)[0]   # 17:0x
_fz = git_out(["show", "-s", "--format=%ci", "e4b015cbb"])    # 2026-10-18 17:21:45 +0800
assert _fz.startswith("2026-10-18 17:2"), "finalize estate ts unexpected: %r" % _fz
_st = git_out(["show", "-s", "--format=%ci", "87d2697cd"])   # 2026-10-18 17:27:39 +0800
assert _st.startswith("2026-10-18 17:2"), "seat commit ts unexpected: %r" % _st
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w270_results.json"])
assert _fin_log == "e4b015cbbd", "W270 finalize product landed by unexpected commit: %s" % _fin_log
_seat_log = git_out(["log", "-1", "--format=%h", "--", "fleet/inbox/MSG-20261018-175x-bmc-w271-seat.md"])
assert _seat_log == "87d2697cdc", "W271 seat MSG landed by unexpected commit: %s" % _seat_log

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live; FULL-PRECISION law) ---
with open(os.path.join(REPO, "results", "_r1095bmc_w270_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert fk["merged"]["k"] == 591920, "K drift: %r" % fk["merged"]["k"]
assert round(fk["merged"]["mu"], 8) == -0.09272692, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24507005, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k591920"], 6) == 0.000319, "se_mu drift: %r" % fk["merged"]["se_mu_k591920"]
assert round(fk["w270_only"]["mu"], 8) == -0.09170727, "w270-only mu drift: %r" % fk["w270_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3268, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == 0.0000, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1016135, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w270"], 4) == 1.1962, "line_pre drift: %r" % fk["skill_line"]["line_pre_w270"]
assert round(fk["skill_line"]["line_merged_591920"], 4) == 1.1962, "line_merged drift: %r" % fk["skill_line"]["line_merged_591920"]
assert fk["ledger_identity"]["total"] == 1018335 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w270_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0010 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w270_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1016135
assert round(res["skill_line_v2_k_lift"]["line_pre_w270"], 4) == 1.1962
assert round(res["skill_line_v2_k_lift"]["line_merged_591920"], 4) == 1.1962
assert round(res["null_pool_cumulative"]["se_mu_at_k591920"], 6) == 0.000319, "W270 se_mu chain verify"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w269_results.json"), encoding="utf-8") as f:
    res9 = json.load(f)
assert round(res9["null_pool_cumulative"]["se_mu_at_k589720"], 6) == 0.000319, "W269 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w271bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [611501, 613500] and pr["bands"]["B"] == [613501, 613700]
l1 = pr["legs"]["leg1"]
assert l1["hops_A"] == 1 and l1["hops_B"] == 1
assert l1["A_hop_chain"] == [{"hop": 1, "window": [611301, 613300], "jump_to": 611501,
                              "refuser_pts": [], "refuser_bands": [[611301, 611500]]}]
assert l1["B_hop_chain"] == [{"hop": 1, "window": [611501, 611700], "jump_to": 613501,
                              "refuser_pts": [], "refuser_bands": [[611501, 613500]]}]
assert l1["B_naive"] == [611501, 611700] and l1["B_naive_refused_at_start"] is True
_ra = l1["relation_asserts"]
assert _ra["A_clean_at_naive_start"] is False and _ra["A_staircase_hop_past_W270_B"] is True
assert _ra["A_base_ge_priorB_tail_plus1"] is True and _ra["B_base_above_W270_tail"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["B_lands_above_own_A"] is True
assert _ra["AB_mutual_exclusion"] is True
assert _ra["W268_W269_W270_bands_respected_A"] is True and _ra["W268_W269_W270_bands_respected_B"] is True
_l0 = pr["legs"]["leg0"]
assert _l0["rows"] == 268 and _l0["owner_rows"] == 260 and _l0["bmc_rows"] == 89
assert _l0["ordinal"] == 261 and _l0["w270_finalize_landed"] is True
assert _l0["w270_finalize_anchors"]["ledger_total"] == 1018335
assert _l0["w270_finalize_anchors"]["merged_n"] == 591920
assert round(_l0["w270_finalize_anchors"]["skill_line_delta_k_lift"], 4) == 0.0000
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
_sa = pr["legs"]["leg2"]["seed_admit_gate"]
assert any("base=611501 span=2000" in s and "FREE" in s for s in _sa), "seed admit A face: %r" % _sa
assert any("base=613501 span=200" in s and "FREE" in s for s in _sa), "seed admit B face: %r" % _sa
assert pr["legs"]["leg4"]["W272p_A_naive"] == "613501..615500"
assert pr["legs"]["leg4"]["W272p_B_naive"] == "613701..613900"
assert pr["legs"]["leg4"]["W272p_B_lands_inside_W272p_A_naive"] is True

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
# r1096 window face: probe-time read = 3.32GB available (MV PACK-A i2v GPU-lane burn in
# flight, CEO weekend production order = legal occupant, untouchable; RAM fluctuates across
# the burn cycle). Wide gate keeps idempotent re-runs green across the burn-cycle
# fluctuation (r1052 law); below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 6.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=609_301..611_300", "A-ext seed=611_501..613_500"),
    ("B-ext exit seed=611_301..611_500", "B-ext exit seed=613_501..613_700"),
    ("entry rng=**609_301+j**（与 A[j] 同源配对语义逐字", "entry rng=**611_501+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W271 seat published bm-c r1095, rides origin 87d2697cd)
    ("席位公示=MSG-20261018-1605-bmc-w270-seat 已推 origin 9f480646f4 r565 律（bm-c r1094 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc r565 律（bm-c r1095 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-1605-bmc-w270-seat 先推 origin 9f480646f4 r565 律",
     "席位公示 MSG-20261018-175x-bmc-w271-seat 先推 origin 87d2697cdc r565 律"),
    # wave-number + vacancy faces
    ("波号 270", "波号 271"),
    ("r1094 席位窗实跑：origin inbox 零 W270 席位外机命中", "r1095 席位窗实跑：origin inbox 零 W271 席位外机命中"),
    ("零 270 行", "零 271 行"),
    ("零 skip-ahead W271/W272 席位声明", "零 skip-ahead W272/W273 席位声明"),
    ("池第 268 枚", "池第 269 枚"),
    # ordinals + own-wave faces
    ("第 260 波", "第 261 波"),
    ("bm-c 第八十九枚自有波", "bm-c 第九十枚自有波"),
    ("probe leg0 bmc_rows=88 attempt-continuity face（r1094 窗算法·bm-c own seat+bmc live rows 88 实读）——freeze 时 live derive bmc rows 88+候选=第 89 枚 EXACT",
     "probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）——freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT"),
    ("engine_owner==bm-c 88 行注册", "engine_owner==bm-c 89 行注册"),
    # engine live-read faces (bm-c instance, r1096 window)
    ("saturation_engine.py status live-read r1094：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1094 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1094 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读"),
    # runner CLI wave
    ("--wave 270/finalize --wave 270", "--wave 271/finalize --wave 271"),
    # sec8 placeholder projection-label bump (W272+ face)
    ("§5.5 W271+ 投影承接机证", "§5.5 W272+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w270", P2), ("n1_w269", "n1_w270"), (P2, "n1_w271"),
    ("_w270bmc", P3), ("_w269bmc", "_w270bmc"), (P3, "_w271bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W270", P1), ("W269", "W270"), ("W268", "W269"), ("W267", "W268"), ("W266", "W267"), ("W265", "W266"),
    ("W264", "W265"), ("W263", "W264"), ("W262", "W263"), ("W261", "W262"), ("W260", "W261"),
    ("W259", "W260"), ("W258", "W259"), ("W257", "W258"), (P1, "W271"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle probe r1096)
    "A-ext seed=609_301..611_300": 1,
    "B-ext exit seed=611_301..611_500": 1,
    "entry rng=**609_301+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261018-1605-bmc-w270-seat 已推 origin 9f480646f4 r565 律（bm-c r1094 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261018-1605-bmc-w270-seat 先推 origin 9f480646f4 r565 律": 1,
    "波号 270": 1,
    "r1094 席位窗实跑：origin inbox 零 W270 席位外机命中": 1,
    "零 270 行": 1,
    "零 skip-ahead W271/W272 席位声明": 1,
    "池第 268 枚": 1,
    "第 260 波": 1,
    "bm-c 第八十九枚自有波": 1,
    "probe leg0 bmc_rows=88 attempt-continuity face（r1094 窗算法·bm-c own seat+bmc live rows 88 实读）——freeze 时 live derive bmc rows 88+候选=第 89 枚 EXACT": 1,
    "engine_owner==bm-c 88 行注册": 1,
    "saturation_engine.py status live-read r1094：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1094 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1094 窗实读": 1,
    "--wave 270/finalize --wave 270": 1,
    "§5.5 W271+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w270": 4, "n1_w269": 6, "_w270bmc": 4, "_w269bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w271bmc_needle_probe.py r1096 window;
    # measured-counts law r1077)
    "W270": 34, "W269": 61, "W268": 4, "W267": 4, "W266": 3, "W265": 2, "W264": 2, "W263": 2,
    "W262": 1, "W261": 1, "W260": 1, "W259": 1, "W258": 1, "W257": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 259 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**609_301+j**": 1,
    "exit rng=**611_301+j**": 1,
    "probe W271+ 投影 A naive 611_301..613_300 CLEAN hops=0": 1,
    "5. **W271+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 996,335": 1,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    "（占位·finalize one-pass 后回填": 1,
    "（占位·finalize 同窗回填": 1,
    "15:4x": 4, "15:2x": 2, "16:0x": 1,
    # zero-floors (absence assertions on T0; needle probe measured all == 0)
    "waits-upstream ARMED": 0, "GATED on": 0, "finalize PENDING": 0, "queue_depth": 0,
    "_w271bmc": 0, "n1_w271": 0, "W272p_": 0,
    "第 90 枚": 0, "第 261 波": 0, "第九十枚": 0, "池第 269 枚": 0, "波号 271": 0, "零 271 行": 0,
    "engine_owner==bm-c 89 行注册": 0, "bmc_rows=89": 0,
    "第二十一次连续 A-hop": 0, "第二十一次连续 above-own-A": 0, "连续二十波": 0, "共二百六十九面": 0,
    "1,018,335": 0, "594,120": 0, "611_501..613_500": 0, "613_501..613_700": 0,
    "613_501..615_500": 0, "613_701..613_900": 0,
    "17:0x": 0, "17:2x": 0,
    "3bb8b9308e": 0, "1c814343e": 0, "6c1aee751d": 0, "ae98b97a10": 0, "e4b015cbb": 0, "87d2697cd": 0,
    "−0.09272692": 0, "0.24507005": 0, "−0.09170727": 0, "0.3268": 0,
    "实差 0.0010 在带内": 0, "line_pre_w270 1.1962": 0, "line_merged@K591,920": 0, "K=591,920": 0,
    "r1095 W270 §7 范式": 0, "（W270 注册+烧录+finalize 全落地）": 0,
    "MSG-20261018-175x": 0, "bmc rows 89+候选": 0,
    "键 W270 实测 K-lift": 0, "607_101..609_100": 0, "12:2x": 0, "13:5x": 0, "14:0x": 0,
    "609_100+1": 0,
    # NOTE (fail-closed discipline): 第十九次连续 A-hop (T0=3) / 第二十次连续 above-own-A
    # (T0=2) / 第二十次连续 A-hop (T0=3) / 连续十九波 (T0=1) / 共二百六十八面 (T0=1) are NOT
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
    # finalize-window stamp roll (heal (1)): W270 finalize one-pass landed 17:2x (e4b015cbb
    # 17:21:45); T1 carries the W269-era 15:4x stamps x4 (measured: 2 block-interior copies
    # discarded later + 2 live non-block sec.5 preamble faces)
    ("15:4x", "17:2x", 4),
    # sec.5 item1 measured keys -> W270 actuals (n1_w270_results + fivekeys machine values)
    ("（W270 实测键 **−0.09273072**·K=589,720 合并池·W270-only 实测 **−0.09084568**）",
     "（W270 实测键 **−0.09272692**·K=591,920 合并池·W270-only 实测 **−0.09170727**）", 1),
    ("W2..W270 共二百六十八面实测 mu 稳定先例", "W2..W270 共二百六十九面实测 mu 稳定先例", 1),
    # sec.5 item1 diff face (heal (3)): TRUE W270 diff = 0.0010 @4dp (measured
    # 0.001019648309353846 full), in-band
    ("W270-only vs merged 实差 0.0019 在带内", "W270-only vs merged 实差 0.0010 在带内", 1),
    # sec.5 item2 sigma key (heal (4))
    ("键 **0.24506175**=W270 合并池实测", "键 **0.24507005**=W270 合并池实测", 1),
    # sec.5 item3 p95 anchor (heal (5))
    ("与 W270 A 档 p95（**0.3158** 实测锚）", "与 W270 A 档 p95（**0.3268** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (6): lowercase line_pre_w269 NOT rolled by the
    # W-roll; true W270 anchors K-lift +0.0000 held-flat + line_merged@K591,920 1.1962 +
    # line_pre_w270 1.1962 + n_eff_held 1,016,135)
    ("键 W270 实测 K-lift **+0.0001**·line_merged@K589,720 **1.1961**·line_pre_w269 1.196·n_eff_held_equal 996,335",
     "键 W270 实测 K-lift **+0.0000**·line_merged@K591,920 **1.1962**·line_pre_w270 1.1962·n_eff_held_equal 1,016,135", 1),
    # se_mu chain true-history correction (heal (7); r1095 fivekeys key5 measured W270=0.000319
    # held-flat, W269=0.000319)
    ("→W267 **0.000321**→W268 **0.000320**→W269 **0.000320**→W270 **0.000319**→W271 投影 0.000319】",
     "→W266 **0.000321**→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 投影 0.000319】", 1),
    # sec.4 merged-pool anchor face (heal (8): W270 finalize landed)
    ("W1..W270 已落账 589,720 实测", "W1..W270 已落账 591,920 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W270 cycle (heal (9): bm-c r1095)
    ("bm-c r1093 W270 §7 范式", "bm-c r1095 W270 §7 范式", 1),
    ("bm-c r1093 W270 §8 范式", "bm-c r1095 W270 §8 范式", 1),
    # RAM face live-measured THIS window (heal (10)): psutil 3.32GB available (~3.3GB) +
    # nvidia-smi 95% util / 8046MiB (~7.9G) VRAM occupied -- MV PACK-A i2v GPU burn IN FLIGHT
    # (CEO weekend production order, legal occupant untouchable); honest window face updated
    # from the r1094 ~2.1GB face
    ("本窗 free RAM ~2.1GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 98%·7.8G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~3.3GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 挤占=MV PACK-A GPU 道烧批窗实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 95%·7.9G VRAM 占用·MV PACK-A i2v wave-1 烧批在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (11)): W270 anchor ~3.3G bm-c appended (chain
    # convention: label = just-completed wave, value = live measure at THIS derive window;
    # ram-squeeze face) -- the wave-roll had shifted the W263 26G bm-a anchor onto the W264
    # label and the W269 ~2.1G onto W270; both restored + true W270 anchor appended
    ("W244 冻结窗 41.9G bm-a 实锚·W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚·W268 冻结窗 ~0.1G bm-c 实锚·W269 冻结窗 ~1.4G bm-c 实锚·W270 冻结窗 ~2.1G bm-c 实锚）",
     "W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚·W268 冻结窗 ~1.4G bm-c 实锚·W269 冻结窗 ~2.1G bm-c 实锚·W270 冻结窗 ~3.3G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 260 注册在册（表尾 W271 行【bm-c r1095 五面冻结 splice 1c814343ed 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·CLEAN-AT-BIRTH 3rd gen）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w270/ 12/12·ledger append 6c1aee751d+ae98b97a10】"
    "·**W270 finalize 已落地**【n1_w270_results.json 机读·净账本锚头 1,018,335·K=591,920 合并池·W270 finalize one-pass bm-c r1095 窗 17:2x·estate chain r1094/r1095 3bb8b9308e+1c814343ed+e4b015cbbd】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1095 席位 MSG-20261018-175x-bmc-w271-seat 已推 origin 87d2697cdc"
    "·probe receipt _w271bmc_20261018 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 89+候选=第 90 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1095 席位窗 2026-10-18 17:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W271=bm-c own-wave window per chain-order law（W268 bm-c→W269 bm-c→W270 bm-c→W271 bm-c own-turn rotation·MSG-175x owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W270 N1 注册全部落地**【W270=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W270**"
    "【净账本锚头 **1,018,335**·K=591,920 合并池·n1_w270_results.json 机读·W270 finalize one-pass bm-c r1095 窗 17:2x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W270 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=591,920+2,200（本波）=**594,120 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十次连续 A-hop）**："
    "A 面算术续带 611_301..613_300（自注册 W270 A 尾 611_300 续）"
    "在席位窗宇宙（post-W270-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W270 B 带 611_301..611_500 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W270 prereg §5 item5 post-W270-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W270 B 尾 611_500→A first-clean **611_501..613_500**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（611_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 611_301..613_300→jump 611_501·refuser band 611_301..611_500〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W270_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=613_501..613_700**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第二十一次连续 above-own-A 落位）**："
    "B naive 续带 611_501..611_700（自注册 W270 B 尾 611_500+1 续）"
    "在席位窗宇宙（post-W270-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 611_501..611_700 落本波 A first-clean 窗 611_501..613_500 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 611_501..613_500**（1 hop）"
    "→**1 hop** 落位 **613_501..613_700**·**B 落位 base==本波 A 窗尾+1（613_500+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W270 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W271 A naive 611_301..613_300 将被注册 W270 B 带拒（staircase affects A 承袭·第二十次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R272：W271 带（A 611_501..613_500/B 613_501..613_700）注册后对 W272+ 的拒面影响=W271 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**611_501+j**（法典 §4 W271 行 A=611_501..613_500·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第二十次连续 A-hop）**："
    "A 算术续带 611_301..613_300（自注册 W270 A 尾 611_300 续）"
    "在席位窗宇宙（post-W270-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W270 B 带 611_301..611_500 落 naive A 窗内=W270 prereg §5 item5 post-W270-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W270 B 尾 611_500→A first-clean 611_501..613_500·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（611_500+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W270_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**613_501+j**（法典 §4 W271 行 B=613_501..613_700·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 611_501..611_700（自注册 W270 B 尾 611_500+1 续）"
    "在席位窗宇宙（post-W270-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 611_501..613_500 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 611_501..613_500→1 hop 落位 613_501..613_700·"
    "**B 落位 base==本波 A 窗尾+1（613_500+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第二十一次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W270 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W272+ 投影 A naive 613_501..615_500 CLEAN hops=0（零 live refusers）/ B naive 613_701..613_900 CLEAN hops=0 "
    "**但落 naive W272 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 613_501..615_500 CLEAN·hops=0——**post-W271-REGISTERED 预披露：naive W272 A 起点将被注册 W271 B 带 613_501..613_700 拒=staircase affects A 第二十一次连续 A-hop 预期**；"
    "投影 B naive 613_701..613_900 clean 但落 naive W272 A 窗 613_501..615_500 内——"
    "**above-own-A 承袭面：W271 B 613_501..613_700 落本波 A 窗之上〔第二十一次连续〕·W272 A 面 1-hop=staircase affects A〔第二十一次连续〕·"
    "W273 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W271 B 带将拒 naive W272 A 窗仅当重叠——"
    "**W273 freezer 承接面强制注记：须在 post-W272 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W272+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 613_501..615_500 **CLEAN**（hops=0·pre-W271 宇宙零 live refusers）——"
    "**post-W271-REGISTERED 预披露：naive W272 A 起点将被注册 W271 B 带 613_501..613_700 拒（staircase-affects-A 第二十一次连续 A-hop 预期）**；"
    "B naive **613_701..613_900 CLEAN（hops=0）但落投影 A 窗 613_501..615_500 内**（W272p_B_lands_inside_W272p_A_naive=true——"
    "**staircase face 延续**：W271 A 611_501..613_500+B 613_501..613_700 注册后 naive W272 A 窗起点即被注册 W271 B 带拒（staircase affects A 承袭·第二十一次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W271 宇宙 live re-derive 必变·禁转录投影）；"
    "**W272 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268/W269/W270/W271=A/B 双 1-hop 形态连续二十波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W272 冻结方必须在 post-W271 注册宇宙重 derive 且 derive B 时预留本波 A 窗 611_501..613_500+本波 B 带 613_501..613_700"
    "——leg2 律/E36 卡·W141 先例；verify at W272 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w271bmc_freeze_edits.py"
    "（按 _w270bmc_freeze_edits.py 模板派生·gate0.5 自查 W270 行+W270 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1094/r1095 W270 先例实时间线：prereg 3bb8b9308e 落于 r1094 窗·splice 1c814343ed 落于 r1095 执行窗 @@SPLICE_T@@——"
    "**W271 freeze 面：W270 own-wave finalize 已落地=席位时即解锁——席位 r1095 窗+prereg r1096 窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 259 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**609_301+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**611_301+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W271+ 投影 A naive 611_301..613_300 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W271+ 投影（probe 机证 leg4", "verify at W271 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W271", "research/PERPETUAL_N1_W271_PREREG.md",
    "611_501..613_500", "613_501..613_700", "594,120", "1,018,335", "591,920", "K=591,920",
    "n1_w271_results.json", "n1_w270_results.json", "MSG-20261018-175x-bmc-w271-seat", "87d2697cdc",
    "池第 269 枚", "第九十枚", "第 261 波", "第 90 枚",
    "STAIRCASE-AFFECTS-A", "第二十次连续 A-hop", "第二十一次连续 above-own-A",
    "_w271bmc_20261018", "--wave 271/finalize --wave 271",
    "W270 finalize one-pass bm-c r1095", "n_eff_held_equal 1,016,135",
    "−0.09272692", "0.24507005", "−0.09170727", "（**0.3268** 实测锚）",
    "键 W270 实测 K-lift **+0.0000**", "line_merged@K591,920 **1.1962**", "line_pre_w270 1.1962",
    "实差 0.0010 在带内", "共二百六十九面", "W2..W270", "W1..W270",
    "engine_owner==bm-c 89 行注册", "engine_owner 行 260 注册在册",
    "probe leg0 bmc_rows=89 attempt-continuity face（r1095 窗算法·bm-c own seat+bmc live rows 89 实读）",
    "bm-c 循环班 r1095 席位窗", "本窗 free RAM ~3.3GB", "本机 bm-c 实例",
    "W271=bm-c own-wave window per chain-order law",
    "3bb8b9308e", "1c814343ed", "6c1aee751d", "ae98b97a10", "e4b015cbbd",
    "W272+ 投影", "W272p_B_lands_inside_W272p_A_naive", "verify at W272 prereg",
    "_w271bmc_freeze_edits.py", "_w270bmc_freeze_edits.py 模板派生",
    "bm-c r1095 W270 §7 范式", "bm-c r1095 W270 §8 范式",
    "（上游 W270 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "（W270 注册+烧录+finalize 全落地）",
    "W206/W211..W270 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "W268 冻结窗 ~1.4G bm-c 实锚", "W269 冻结窗 ~2.1G bm-c 实锚", "W270 冻结窗 ~3.3G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R272：W271 带",
    "→W266 **0.000321**→W267 **0.000320**→W268 **0.000320**→W269 **0.000319**→W270 **0.000319**→W271 投影 0.000319】",
    "611_500+1", "613_500+1", "611_301..611_500",
    "A_staircase_hop_past_W270_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 271", "零 271 行", "零 skip-ahead W272/W273 席位声明",
    "17:2x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1096：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1096 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1096 窗实读",
    "MV PACK-A i2v wave-1 烧批在飞",
    "r1095 席位窗实跑：origin inbox 零 W271 席位外机命中",
    "results/p2cal_ext/n1_w270/ 12/12",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=609_301", "B-ext exit seed=611_301",
    "609_301..611_300", "609_101..609_300", "609_101..611_100", "609_301..609_500",
    "611_301..613_300 CLEAN", "607_101..609_100", "607_101..607_300", "606_901..608_900",
    "GATED on", "finalize PENDING", "queue_depth",
    "589,720", "**591,920 投影**", "line_merged@K589,720", "K=589,720",
    "−0.09273072", "0.24506175", "−0.09084568", "**0.3158**", "实差 0.0019 在带内",
    "15:4x", "15:2x", "16:0x",
    "MSG-20261018-1605", "9f480646f4", "67fe12710c", "440b07c94b", "32cbe26a1c", "f59af28e77", "4eb8ec87cc",
    "bmc_rows=88", "bmc rows 88+候选", "第 89 枚", "第 260 波", "第八十九枚",
    "engine_owner==bm-c 88 行注册",
    "r1094 席位窗实跑", "r1094 窗算法",
    "本窗 free RAM ~2.1GB", "98%·7.8G VRAM",
    "W270p_", "W271p_",
    "line_pre_w269", "键 W269 实测 K-lift",
    "verify at W271 prereg",
    "W271+ 投影", "W270+ 投影", "W269+ 投影",
    "第十九次连续 A-hop", "第二十次连续 above-own-A", "连续十九波", "共二百六十八面",
    "n1_w269_results.json", "n1_w268_results.json",
    "W2..W269", "W136..W269", "W1..W269",
    "波号 270", "零 270 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G", "W267 冻结窗 ~5G",
    "W268 冻结窗 ~0.1G", "W269 冻结窗 ~1.4G", "W270 冻结窗 ~2.1G",
    "609_300+1", "611_300+1", "609_100+1",
    "12:2x", "13:5x", "14:0x",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W272+ 投影") == 3, "W272+ count=%d (expect 3 = §5.5 rolled + b5 + b6)" % T2.count("W272+ 投影")
assert T2.count("W271+ 投影") == 0, "W271+ count=%d (expect 0)" % T2.count("W271+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第二十次连续 A-hop") == 3, "A20 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第二十次连续 A-hop")
assert T2.count("第二十一次连续 A-hop") == 3, "A21 count=%d (expect 3 = b5 x2 + b6)" % T2.count("第二十一次连续 A-hop")
assert T2.count("第二十一次连续 above-own-A") == 2, "B21 count=%d (expect 2 = b_band + b3_b)" % T2.count("第二十一次连续 above-own-A")
assert T2.count("第二十次连续 above-own-A") == 0, "B20 count=%d (expect 0)" % T2.count("第二十次连续 above-own-A")
assert T2.count("连续二十波") == 1, "20-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续二十波")
assert T2.count("611_501..613_500") >= 5, "own-A count=%d (expect >=5)" % T2.count("611_501..613_500")
assert T2.count("613_501..613_700") >= 4, "own-B count=%d (expect >=4)" % T2.count("613_501..613_700")
assert T2.count("611_301..611_500") >= 3, "reg-W270-B count=%d (expect >=3)" % T2.count("611_301..611_500")
assert T2.count("611_501..611_700") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("611_501..611_700")
assert T2.count("611_301..613_300") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("611_301..613_300")
assert T2.count("613_501..615_500") == 5, "W272p-A count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("613_501..615_500")
assert T2.count("613_701..613_900") == 3, "W272p-B count=%d (expect 3 = b6 x2 + b5)" % T2.count("613_701..613_900")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w271bmc_20261018") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w271bmc_20261018")
assert T2.count("1,018,335") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,018,335")
# n_eff_held face honest update (r1093 full-precision law): the ONLY 1,016,135 in the output
# is the sec.5 item4 n_eff_held_equal anchor = the W270 fivekeys measured value (the canon
# r1094 window left this sub-face stale at the W260-era 996,335; healed forward here)
assert T2.count("1,016,135") == 1, "n_eff_held count=%d (expect 1 = sec.5 item4 honest anchor only)" % T2.count("1,016,135")
assert T2.count("591,920") >= 3, "merged-K count=%d (expect >=3)" % T2.count("591,920")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")
assert T2.count("第 90 枚") == 2, "own-ordinal count=%d (expect 2 = leg + b_title)" % T2.count("第 90 枚")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W271 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 1c814343e @ " + SPLICE_T + " | finalize estate: e4b015cbb @ 17:2x | seat: 87d2697cd @ 17:2x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~3.3GB written, MV PACK-A burn window) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == 626148d08dbccddb91c83373c679b416951eb7b9 @ 3bb8b9308e (frozen pre-run face; HEAD post-backfill twin 92f167f2 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
