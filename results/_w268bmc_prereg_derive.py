# -*- coding: utf-8 -*-
# r1090 bm-c: W268 prereg derive (count-asserted ordered transform + marker-extracted block replaces).
# Canon-clone of _w267bmc_prereg_derive.py per age() machine-needle law (shift-map one generation).
# Source = committed frozen W267 prereg AT THE FREEZE COMMIT df55e3fab9 (git df55e3fab9:research/PERPETUAL_N1_W267_PREREG.md,
# 23,008 bytes -- the frozen pre-run face; sec7/8 placeholders intact). Extracted to
# results/_w268bmc_w267_frozen_face.txt THIS window (r1090); byte-verified:
# disk==blob sha1 a345554542439271a8888fbb27f29b1cde98037d, sha256_16 0918b8990154a23b.
# TEMPLATE-FACE DISCLOSURE (r1052/r1049 law): HEAD twin cd2a8478567e1db0300d22304d872e807207466d = the
# CURRENT HEAD face = the POST-CYCLE face with sec.7/8 BACKFILLED by the r1089 W267 cycle (fivekeys+backfill
# closeout b9ad2f1119). Deriving from the backfilled face would fabricate W268 sec.7/8 from W267's measured
# numbers -- the r1049/r1052 precedent requires the df55e3fab9 frozen pre-run face.
# W268 facts (all machine-derived, never transcribed):
#   - seat probe ADMIT receipt results/_w268bmc_20261018_probe_receipt.json (bm-c r1089 window authored+run
#     live, seat rides origin b9ad2f1119 per r565 early-visibility law, MSG-20261018-1229-bmc-w268-seat
#     landed on origin; zero foreign W268 seat claims). STAIRCASE CONTINUES: A naive 604_701..606_700
#     REFUSED at start (registered W267 B band 604_701..604_900 sits INSIDE the naive A window) -> A
#     first-clean 604_901..606_900 hops=1 (SEVENTEENTH consecutive A-hop, W267 prereg sec.5 item5
#     post-W267-REGISTERED pre-disclosure confirmed live per r587, ZERO divergence) / B naive
#     604_901..605_100 REFUSED at start (lands INSIDE the own-wave W268 A first-clean window
#     604_901..606_900) -> own-A reservation cascade hop past 606_900 -> 606_901..607_100 hops=1
#     (EIGHTEENTH consecutive above-own-A landing); seed_admit FREE x2 (A base=604901 span=2000 /
#     B base=606901 span=200); leg0 rows=265 owner_rows=257 bmc_rows=86 ordinal=258; leg2 conflicts=0;
#     leg3 origin_vacancy=true; W269p projection: A naive 606_901..608_900 CLEAN hops=0 / B naive
#     607_101..607_300 CLEAN hops=0 but lands inside W269p A naive (18th A-hop expected post-register).
#   - upstream W267 finalize LANDED (bm-c r1089 window one-pass, n1_w267_results.json landed via
#     b9ad2f1119 12:29:57, fivekeys 6/6 receipt results/_r1089bmc_w267_fivekeys.json + sec.7/8 backfilled):
#     merged K=585,320 / ledger 1,011,735 EXACT (1,009,535+2,200) / merged mu -0.09273843 (8dp) /
#     sigma 0.24505587 (8dp) / se_mu@K585,320 0.000320 / W267-only mu -0.09269745 (8dp) / A p95 0.3058 /
#     K-lift -0.0001 (first negative micro-move) / n_eff_held 1,009,535 / line_pre_w267 1.1959 /
#     line_merged@585,320 1.1958 / key1 gap 4.097e-05 (4dp 0.0000) in-band; splice 7b9e9377 11:44:20
#     (r1088 window, setwave root-cure landed; engine self-burn 12/12 batched ledger appends
#     99166404f2+eb5c74dbf7); sixgate 30th PRE-FINALIZE ALL PASS.
# Needle-count pre-flight evidence: results/_w268bmc_facts_probe.py + results/_w268bmc_facts_probe.json
# (MEASURED live on T0 + T1 roll-simulation THIS window; floors below match every measured count;
# r1077 measured-counts law). T1-sim residuals verified: P1/P2/P3 leftovers 0, W268+ count 2 (both
# block-interior, discarded), R268 count 1 (block-interior, discarded).
# Same-window needle heals disclosed:
# (1) NO date-roll heal needed this generation: the W267 seat-probe receipt and the W268 seat-probe
#     receipt are BOTH dated 20261018 -- the _w267bmc->_w268bmc roll lands the correct date directly.
# (2) RAM face live-measured THIS window: psutil 0.11-0.14GB available (~0.1GB, RAM-critical
#     triple-read 13:05) + nvidia-smi 100% util / 15.6G VRAM occupied -- MV PACK-A i2v wave-1 GPU
#     burn IN FLIGHT (CEO weekend production order; top RAM consumer = GPU-lane python.exe 4550MB,
#     legal occupant untouchable); low-RAM honest face updated from the r1087 ~5GB idle face.
# (3) se_mu chain true-history correction (r1059 canon-embed advice): post-roll form carries
#     W264 0.000323 (FALSE -- true W264 measured 0.000322) -> POST_LEG rewrites the tail with true
#     history W264 0.000322 / W265 0.000321 / W266 0.000321 / W267 0.000320 (measured per fivekeys
#     key5 se_mu_narrowing 0.000320) and appends the W268 projection 0.000320.
# (4) K-lift POST_LEG: post-roll form carries "键 W267 实测 K-lift **0.0001**·line_merged@K583,120
#     **1.1958**·line_pre_w266 1.1957" (lowercase line_pre_w266 NOT rolled by the W-roll --
#     case-sensitive) -- corrected to the true W267 anchors K-lift **−0.0001** (first negative
#     micro-move since W258)·line_merged@K585,320 **1.1958**·line_pre_w267 **1.1959**.
# (5) low-RAM precedent ledger append: W267 freeze-window ~1.5G bm-c anchor appended via POST_LEG
#     (chain precedent every-wave append, b6_ram paradigm; the wave-roll had shifted the W263 26G
#     bm-a anchor onto the W264 label and the W264 7G onto W265 -- both restored + true W267 anchor
#     appended).
# (6) n_eff_held_equal 996,335 carried verbatim per W264/W265/W266/W267 derive precedent (static
#     precedent-chain face; the live n_eff anchors are machine-verified from receipts in the
#     gates below).
# (7) finalize-window stamp roll: W267 finalize one-pass landed 12:2x (n1_w267_results.json via
#     b9ad2f1119 12:29:57); T1 carries the W266-era 10:2x stamps x5 (measured; two block-interior
#     copies discarded by block replacement + the L44 live faces) -> POST_LEG rolls all to 12:2x.
# (8) b6 ordinal heal (defect caught at the derive birth station, CEO defect-birthplace law): the
#     W267 face's b6 short-form bracket "W268 A 面 1-hop=staircase affects A〔第十六次连续〕" carried
#     a latent ordinal defect (live W268 probe = SEVENTEENTH A-hop); the block replacement discards
#     the defective face and THIS derive writes the live-verified pairing W268 A=第十七次 /
#     W268 B=第十八次 per the W268 probe receipt.
import io, os, sys, subprocess, hashlib, re, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w268bmc_w267_frozen_face.txt")
OUT = os.path.join(REPO, "research", "PERPETUAL_N1_W268_PREREG.md")
GIT = "C:/Program Files/Git/cmd/git.exe"

def git_out(args):
    r = subprocess.run([GIT] + args, capture_output=True, cwd=REPO)
    if r.returncode != 0:
        raise SystemExit("git fail %r: %s" % (args, r.stderr.decode("utf-8", "replace")))
    return r.stdout.decode("utf-8", "replace").strip()

# --- source byte-identity gates ---
_blob_expect = "a345554542439271a8888fbb27f29b1cde98037d"   # freeze-commit face @ df55e3fab9
_ho = git_out(["hash-object", SRC])
assert _ho == _blob_expect, "SRC blob mismatch: got %s expect %s" % (_ho, _blob_expect)
_fc = git_out(["rev-parse", "df55e3fab9:research/PERPETUAL_N1_W267_PREREG.md"])
assert _fc == _blob_expect, "freeze-commit blob mismatch: %s" % _fc
_hb = git_out(["rev-parse", "HEAD:research/PERPETUAL_N1_W267_PREREG.md"])
assert _hb == "cd2a8478567e1db0300d22304d872e807207466d", "HEAD tpl twin face drifted: %s" % _hb

T0 = io.open(SRC, encoding="utf-8", newline="").read()
assert len(T0.encode("utf-8")) == 23008, "SRC size drift: %d" % len(T0.encode("utf-8"))
assert hashlib.sha256(T0.encode("utf-8")).hexdigest()[:16] == "0918b8990154a23b", "SRC sha mismatch"

# --- chain-fact existence gates (zero transcription) ---
for sha in ("df55e3fab9", "7b9e9377", "b9ad2f1119", "99166404f2", "eb5c74dbf7"):
    git_out(["cat-file", "-e", sha + "^{commit}"])
_ci = git_out(["show", "-s", "--format=%ci", "7b9e9377"])    # 2026-10-18 11:44:20 +0800
_m = re.match(r"2026-10-18 (1[12]):(\d{2})", _ci)
assert _m, "splice commit ts unexpected: %r" % _ci
SPLICE_T = "%s:%sx" % (_m.group(1), _m.group(2)[0])           # 11:4x
_fz = git_out(["show", "-s", "--format=%ci", "b9ad2f1119"])   # 2026-10-18 12:29:57 +0800
assert _fz.startswith("2026-10-18 12:2"), "finalize commit ts unexpected: %r" % _fz
_fin_log = git_out(["log", "-1", "--format=%h", "--", "results/perpetual_faces/n1_w267_results.json"])
assert _fin_log == "b9ad2f1119", "W267 finalize product landed by unexpected commit: %s" % _fin_log

# --- finalize-anchor machine-verify gates (fivekeys receipt + results json, live) ---
with open(os.path.join(REPO, "results", "_r1089bmc_w267_fivekeys.json"), encoding="utf-8") as f:
    fk = json.load(f)
assert round(fk["merged"]["mu"], 8) == -0.09273843, "merged mu drift: %r" % fk["merged"]["mu"]
assert round(fk["merged"]["sigma"], 8) == 0.24505587, "sigma drift: %r" % fk["merged"]["sigma"]
assert round(fk["merged"]["se_mu_k585320"], 6) == 0.00032, "se_mu drift: %r" % fk["merged"]["se_mu_k585320"]
assert round(fk["w267_only"]["mu"], 8) == -0.09269745, "w267-only mu drift: %r" % fk["w267_only"]["mu"]
assert round(fk["a_band"]["full_sharpe_p95"], 4) == 0.3058, "p95 drift: %r" % fk["a_band"]["full_sharpe_p95"]
assert round(fk["skill_line"]["k_lift_delta"], 4) == -0.0001, "k-lift drift: %r" % fk["skill_line"]["k_lift_delta"]
assert fk["skill_line"]["n_eff_held"] == 1009535, "n_eff_held drift: %r" % fk["skill_line"]["n_eff_held"]
assert round(fk["skill_line"]["line_pre_w267"], 4) == 1.1959, "line_pre drift: %r" % fk["skill_line"]["line_pre_w267"]
assert round(fk["skill_line"]["line_merged_585320"], 4) == 1.1958, "line_merged drift: %r" % fk["skill_line"]["line_merged_585320"]
assert fk["merged"]["k"] == 585320, "K drift: %r" % fk["merged"]["k"]
assert fk["ledger_identity"]["total"] == 1011735 and fk["ledger_identity"]["exact"], "ledger identity drift"
_k1 = [c for c in fk["checks"] if c["name"] == "key1_w267_vs_merged_mu_gap"][0]
assert round(_k1["value"], 4) == 0.0 and _k1["pass"], "key1 gap drift: %r" % _k1["value"]
assert fk["all_pass"] is True, "fivekeys not all_pass"
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w267_results.json"), encoding="utf-8") as f:
    res = json.load(f)
assert res["skill_line_v2_k_lift"]["n_eff_held_equal"] == 1009535
assert round(res["skill_line_v2_k_lift"]["line_pre_w267"], 4) == 1.1959
assert round(res["skill_line_v2_k_lift"]["line_merged_585320"], 4) == 1.1958
assert round(res["null_pool_cumulative"]["se_mu_at_k585320"], 6) == 0.00032
with open(os.path.join(REPO, "results", "perpetual_faces", "n1_w266_results.json"), encoding="utf-8") as f:
    res6 = json.load(f)
assert round(res6["null_pool_cumulative"]["se_mu_at_k583120"], 6) == 0.000321, "W266 se_mu chain verify"
with open(os.path.join(REPO, "results", "_w268bmc_20261018_probe_receipt.json"), encoding="utf-8") as f:
    pr = json.load(f)
assert pr["verdict"] == "ADMIT"
assert pr["bands"]["A"] == [604901, 606900] and pr["bands"]["B"] == [606901, 607100]
assert pr["legs"]["leg1"]["hops_A"] == 1 and pr["legs"]["leg1"]["hops_B"] == 1
assert pr["legs"]["leg1"]["A_hop_chain"] == [{"hop": 1, "window": [604701, 606700], "jump_to": 604901,
                                             "refuser_pts": [], "refuser_bands": [[604701, 604900]]}]
assert pr["legs"]["leg1"]["B_hop_chain"] == [{"hop": 1, "window": [604901, 605100], "jump_to": 606901,
                                             "refuser_pts": [], "refuser_bands": [[604901, 606900]]}]
_ra = pr["legs"]["leg1"]["relation_asserts"]
assert _ra["A_staircase_hop_past_W267_B"] is True and _ra["B_lands_above_own_A"] is True
assert _ra["B_hop_lands_inside_A"] is False and _ra["AB_mutual_exclusion"] is True
assert pr["legs"]["leg0"]["rows"] == 265 and pr["legs"]["leg0"]["owner_rows"] == 257
assert pr["legs"]["leg0"]["bmc_rows"] == 86 and pr["legs"]["leg0"]["ordinal"] == 258
assert pr["legs"]["leg0"]["w267_finalize_anchors"]["ledger_total"] == 1011735
assert pr["legs"]["leg0"]["w267_finalize_anchors"]["merged_n"] == 585320
assert round(pr["legs"]["leg0"]["w267_finalize_anchors"]["skill_line_delta_k_lift"], 4) == -0.0001
assert pr["legs"]["leg2"]["conflicts"] == 0 and pr["legs"]["leg3"]["origin_vacancy"] is True
assert pr["legs"]["leg4"]["W269p_A_naive"] == "606901..608900"
assert pr["legs"]["leg4"]["W269p_B_naive"] == "607101..607300"
assert pr["legs"]["leg4"]["W269p_B_lands_inside_W269p_A_naive"] is True

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
# r1090 window face: triple-read 13:05 = 0.11/0.12/0.14 GB available (RAM-critical squeeze from the
# MV PACK-A i2v GPU-lane python.exe 4550MB; CEO weekend production order = legal occupant, untouchable).
# Wide gate keeps idempotent re-runs green across the burn-cycle fluctuation (r1052 byte-identity law);
# below 0.05GB = machine near death = fail-closed correct.
import psutil
_ram_free = psutil.virtual_memory().available / (1024 ** 3)
assert 0.05 <= _ram_free <= 3.0, "RAM face out of honest window: %.2f" % _ram_free

P1, P2, P3 = "\x01W\x01", "\x01N\x01", "\x01B\x01"

VMAP = [
    # ---- explicit wave-free legs BEFORE the wave rolls (compound needles first) ----
    ("A-ext seed=602_701..604_700", "A-ext seed=604_901..606_900"),
    ("B-ext exit seed=604_701..604_900", "B-ext exit seed=606_901..607_100"),
    ("entry rng=**602_701+j**（与 A[j] 同源配对语义逐字", "entry rng=**604_901+j**（与 A[j] 同源配对语义逐字"),
    # seat/provenance faces (W268 seat published bm-c r1089, rides origin b9ad2f1119)
    ("席位公示=MSG-20261018-1025-bmc-w267-seat 已推 origin 942ebd5885 r565 律（bm-c r1086 席·queue-head seat-first lane）",
     "席位公示=MSG-20261018-1229-bmc-w268-seat 已推 origin b9ad2f1119 r565 律（bm-c r1089 席·queue-head seat-first lane）"),
    ("席位公示 MSG-20261018-1025-bmc-w267-seat 先推 origin 942ebd5885 r565 律",
     "席位公示 MSG-20261018-1229-bmc-w268-seat 先推 origin b9ad2f1119 r565 律"),
    # wave-number + vacancy faces
    ("波号 267", "波号 268"),
    ("r1086 席位窗实跑：origin inbox 零 W267 席位外机命中", "r1089 席位窗实跑：origin inbox 零 W268 席位外机命中"),
    ("零 267 行", "零 268 行"),
    ("零 skip-ahead W268/W269 席位声明", "零 skip-ahead W269/W270 席位声明"),
    ("池第 265 枚", "池第 266 枚"),
    # ordinals + own-wave faces
    ("第 257 波", "第 258 波"),
    ("bm-c 第八十六枚自有波", "bm-c 第八十七枚自有波"),
    ("probe leg0 bmc_rows=85 attempt-continuity face（r1086 窗算法·bm-c own seat+bmc live rows 85 实读）——freeze 时 live derive bmc rows 85+候选=第 86 枚 EXACT",
     "probe leg0 bmc_rows=86 attempt-continuity face（r1089 窗算法·bm-c own seat+bmc live rows 86 实读）——freeze 时 live derive bmc rows 86+候选=第 87 枚 EXACT"),
    ("engine_owner==bm-c 85 行注册", "engine_owner==bm-c 86 行注册"),
    # engine live-read faces (bm-c instance, r1090 window)
    ("saturation_engine.py status live-read r1087：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
     "saturation_engine.py status live-read r1090：burns_active=[] queue_next=[] 实读·heartbeat 新鲜"),
    ("本机 bm-c 实例·heartbeat 新鲜实读 r1087 窗·队列空转 idle",
     "本机 bm-c 实例·heartbeat 新鲜实读 r1090 窗·队列空转 idle"),
    ("引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1087 窗实读",
     "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1090 窗实读"),
    # runner CLI wave
    ("--wave 267/finalize --wave 267", "--wave 268/finalize --wave 268"),
    # sec8 placeholder projection-label bump (W269+ face)
    ("§5.5 W268+ 投影承接机证", "§5.5 W269+ 投影承接机证"),
    # ---- lowercase chained rolls (result/script faces) ----
    ("n1_w267", P2), ("n1_w266", "n1_w267"), (P2, "n1_w268"),
    ("_w267bmc", P3), ("_w266bmc", "_w267bmc"), (P3, "_w268bmc"),
    # ---- wave-number roll (chained placeholders) ----
    ("W267", P1), ("W266", "W267"), ("W265", "W266"), ("W264", "W265"), ("W263", "W264"), ("W262", "W263"),
    ("W261", "W262"), ("W260", "W261"), ("W259", "W260"), ("W258", "W259"), ("W257", "W258"),
    ("W256", "W257"), ("W255", "W256"), (P1, "W268"),
]

VMAP_FLOORS = {
    # explicit legs (all measured == 1 on T0, needle facts-probe r1090)
    "A-ext seed=602_701..604_700": 1,
    "B-ext exit seed=604_701..604_900": 1,
    "entry rng=**602_701+j**（与 A[j] 同源配对语义逐字": 1,
    "席位公示=MSG-20261018-1025-bmc-w267-seat 已推 origin 942ebd5885 r565 律（bm-c r1086 席·queue-head seat-first lane）": 1,
    "席位公示 MSG-20261018-1025-bmc-w267-seat 先推 origin 942ebd5885 r565 律": 1,
    "波号 267": 1,
    "r1086 席位窗实跑：origin inbox 零 W267 席位外机命中": 1,
    "零 267 行": 1,
    "零 skip-ahead W268/W269 席位声明": 1,
    "池第 265 枚": 1,
    "第 257 波": 1,
    "bm-c 第八十六枚自有波": 1,
    "probe leg0 bmc_rows=85 attempt-continuity face（r1086 窗算法·bm-c own seat+bmc live rows 85 实读）——freeze 时 live derive bmc rows 85+候选=第 86 枚 EXACT": 1,
    "engine_owner==bm-c 85 行注册": 1,
    "saturation_engine.py status live-read r1087：burns_active=[] queue_next=[] 实读·heartbeat 新鲜": 1,
    "本机 bm-c 实例·heartbeat 新鲜实读 r1087 窗·队列空转 idle": 1,
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1087 窗实读": 1,
    "--wave 267/finalize --wave 267": 1,
    "§5.5 W268+ 投影承接机证": 1,
    # lowercase rolls (measured on T0)
    "n1_w267": 4, "n1_w266": 6, "_w267bmc": 4, "_w266bmc": 1,
    # wave rolls (MEASURED live on T0, results/_w268bmc_facts_probe.py r1090 window;
    # measured-counts law r1077: W263 raw 3 and W264 raw 4 this generation)
    "W267": 35, "W266": 62, "W265": 4, "W264": 4, "W263": 3, "W262": 1, "W261": 1, "W260": 1,
    "W259": 1, "W258": 1, "W257": 1, "W256": 1, "W255": 1,
    # block-marker stability floors (raw template face; measured on T0)
    "engine_owner 行 256 注册在册（表尾": 1,
    "prev=**届时空窗活链头 derive 禁手抄**": 1,
    "（**A 面=STAIRCASE-AFFECTS-A": 1,
    "entry rng seed=**602_701+j**": 1,
    "exit rng=**604_701+j**": 1,
    "probe W268+ 投影 A naive 604_701..606_700 CLEAN hops=0": 1,
    "5. **W268+ 投影（probe 机证 leg4": 1,
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本": 1,
    "（gate0.5 绿·编辑器 loud abort 兜底）**。": 1,
    "owner per chain-order law）**】】）": 1,
    "verify at W268 prereg，hop 链逐跳在 probe 回执。": 1,
    "（见 §5 item5）。": 1,
    "seed_admit_gate rc0 双带 FREE": 1,
    "n_eff_held_equal 996,335": 1,
    "注册+烧录+finalize 全落地": 2,
    "席位时即解锁": 2,
    # zero-floors (absence assertions on T0; facts-probe r1090 measured all == 0)
    "waits-upstream ARMED": 0,
    "1,011,735": 0, "587,520": 0, "604_901..606_900": 0, "606_901..607_100": 0,
    "−0.09273843": 0, "0.24505587": 0, "−0.09269745": 0, "0.3058": 0, "12:2x": 0,
    "MSG-20261018-1229": 0, "b9ad2f1119": 0, "_w268bmc": 0, "n1_w268": 0, "W270": 0,
    "第 87 枚": 0, "第 258 波": 0, "第八十七枚": 0, "池第 266 枚": 0, "波号 268": 0, "零 268 行": 0,
    "engine_owner==bm-c 86 行注册": 0, "606_901..608_900": 0, "607_101..607_300": 0,
    "第十八次连续 A-hop": 0, "第十八次连续 above-own-A": 0, "GATED on": 0, "finalize PENDING": 0,
    "07:0x": 0, "19:2x": 0, "让路态": 0, "queue_depth": 0,
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
    # finalize-window stamp roll (heal (7)): W267 finalize one-pass landed 12:2x (b9ad2f1119 12:29:57);
    # T1 carries the W266-era 10:2x stamps x5 (measured; 2 block-interior copies discarded later)
    ("10:2x", "12:2x", 5),
    # sec.5 item1 measured keys -> W267 actuals (n1_w267_results + fivekeys machine values)
    ("（W267 实测键 **−0.09273858**·K=583,120 合并池·W267-only 实测 **−0.09878527**）",
     "（W267 实测键 **−0.09273843**·K=585,320 合并池·W267-only 实测 **−0.09269745**）", 1),
    ("W2..W267 共二百六十五面实测 mu 稳定先例", "W2..W267 共二百六十六面实测 mu 稳定先例", 1),
    ("W267-only vs merged 实差 0.0060 在带内", "W267-only vs merged 实差 0.0000 在带内", 1),
    # sec.5 item2 sigma key
    ("键 **0.24507392**=W267 合并池实测", "键 **0.24505587**=W267 合并池实测", 1),
    # sec.5 item3 p95 anchor
    ("与 W267 A 档 p95（**0.3268** 实测锚）", "与 W267 A 档 p95（**0.3058** 实测锚）", 1),
    # sec.5 item4 K-lift chain + line faces (heal (4): lowercase line_pre_w266 NOT rolled by the
    # W-roll; true W267 anchors K-lift −0.0001 + line_merged@K585,320 1.1958 + line_pre_w267 1.1959)
    ("键 W267 实测 K-lift **0.0001**·line_merged@K583,120 **1.1958**·line_pre_w266 1.1957·n_eff_held_equal 996,335",
     "键 W267 实测 K-lift **−0.0001**·line_merged@K585,320 **1.1958**·line_pre_w267 1.1959·n_eff_held_equal 996,335", 1),
    ("→W264 **0.000323**→W265 **0.000322**→W266 **0.000321**→W267 **0.000321**→W268 投影 0.000321】",
     "→W264 **0.000322**→W265 **0.000321**→W266 **0.000321**→W267 **0.000320**→W268 投影 0.000320】", 1),
    # sec.4 merged-pool anchor face (W267 finalize landed)
    ("W1..W267 已落账 583,120 实测", "W1..W267 已落账 585,320 实测", 1),
    # sec.7/8 backfill paradigm rows -> the W267 cycle (bm-c r1089)
    ("bm-c r1086 W267 §7 范式", "bm-c r1089 W267 §7 范式", 1),
    ("bm-c r1086 W267 §8 范式", "bm-c r1089 W267 §8 范式", 1),
    # RAM face live-measured THIS window (heal (2)): psutil 0.11-0.14GB available (~0.1GB, RAM-critical
    # squeeze from the MV PACK-A i2v GPU-lane python.exe 4550MB -- CEO weekend production order, legal
    # occupant untouchable) + nvidia-smi 100% / 15.6G VRAM occupied -- GPU burn IN FLIGHT; honest
    # ram-critical window face updated from the r1087 idle ~5GB face
    ("本窗 free RAM ~5GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·GPU=gen-only 车道空窗（nvidia-smi 实读 6%·3.4G VRAM 常驻·零在飞烧批）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）",
     "本窗 free RAM ~0.1GB（bm-c 底盘常驻·24G 物理内存机·CEO 周末用机态·RAM 临界挤占=GPU 道主进程 python 4.5G 实测·GPU=gen-only 车道满载烧批在飞（nvidia-smi 实读 100%·15.6G VRAM 占用·MV PACK-A i2v wave-1 在飞）·LLM 态已退役 gen 专用车道·引擎队列空转·CPU 车道独立如实注记）", 1),
    # low-RAM precedent ledger append (heal (5)): W267 anchor ~0.1G bm-c appended (chain convention:
    # label = just-completed wave, value = live measure at THIS derive window; ram-critical face)
    # (the wave-roll had shifted the W263 26G bm-a anchor onto the W264 label and the W264 7G onto
    # W265 -- restore both + append the true W267 anchor)
    ("·W244 冻结窗 41.9G bm-a 实锚·W264 冻结窗 26G bm-a 实锚·W265 冻结窗 7G bm-c 实锚·W266 冻结窗 3G bm-c 实锚·W267 冻结窗 ~5G bm-c 实锚）",
     "·W244 冻结窗 41.9G bm-a 实锚·W263 冻结窗 26G bm-a 实锚·W264 冻结窗 7G bm-c 实锚·W265 冻结窗 3G bm-c 实锚·W266 冻结窗 ~5G bm-c 实锚·W267 冻结窗 ~0.1G bm-c 实锚）", 1),
]

for o, n, f in VMAP_POST_LEGS:
    c = T1.count(o)
    if c < f:
        raise SystemExit("VMAP POST FLOOR FAIL: %r count=%d floor=%d" % (o, c, f))
    T1 = T1.replace(o, n)

# ---------------- block replacements (needles marker-matched on T1; NEW = final) ----------------
NEW = {}

NEW["b_title"] = (
    "engine_owner 行 257 注册在册（表尾 W267 行【bm-c r1089 五面冻结 splice 7b9e9377 落地 @@SPLICE_T@@·selftest ALL-PASS（setwave root-cure 出生站拦截就位·r1076 家族病根终结）】"
    "+引擎自燃 12/12 分片已落【results/p2cal_ext/n1_w267/ 12/12·ledger append 99166404f2+eb5c74dbf7】"
    "·**W267 finalize 已落地**【n1_w267_results.json 机读·净账本锚头 1,011,735·K=585,320 合并池·W267 finalize one-pass bm-c r1089 窗 12:2x·estate chain r1088/r1089 7b9e9377+b9ad2f1119】）"
    "+本候选=bm-c 自有席自有波【live-derive face：席面 own-seat face（bm-c r1089 席位 MSG-20261018-1229-bmc-w268-seat 已推 origin b9ad2f1119"
    "·probe receipt _w268bmc_20261018 机证·bands ADMIT verbatim·queue-head seat-first lane）"
    "→freeze 时 live derive bmc rows 86+候选=第 87 枚 EXACT·以 freeze 时 live derive 为准 r587/r359】"
    "【bm-c 循环班 r1089 席位窗 2026-10-18 12:2x·CEO 填载令 standing+2026-10-10 ~23:1x RE-ISSUE+O-20261013-2215 CPU 常开令"
    "·**W268=bm-c own-wave window per chain-order law（W265 bm-c→W266 bm-c→W267 bm-c→W268 bm-c own-turn rotation·MSG-1229 owner per chain-order law）**】】）"
)

NEW["b_prev"] = (
    "prev=**届时空窗活链头 derive 禁手抄**——起稿窗实况（**锚滚链面 r576/r590 律**）："
    "**W1..W267 N1 注册全部落地**【W267=注册+12/12 分片已烧·**finalize 已落地**——最新已 finalize 锚=**W267**"
    "【净账本锚头 **1,011,735**·K=585,320 合并池·n1_w267_results.json 机读·W267 finalize one-pass bm-c r1089 窗 12:2x】】；"
    "**零在飞上游席——「零在飞上游链前」断言适用且干净前置成立**（上游 W267 席位已闭链=注册+烧录+finalize 全落地·零在飞）；"
    "finalize 键序前置=届时按 registry 键 derive 复核 FAIL-CLOSED r307 两态例恒在；"
    "累计 null 池=585,320+2,200（本波）=**587,520 投影**（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"
)

NEW["b_band"] = (
    "（**A 面=STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十七次连续 A-hop）**："
    "A 面算术续带 604_701..606_700（自注册 W267 A 尾 604_700 续）"
    "在席位窗宇宙（post-W267-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W267 B 带 604_701..604_900 落 naive A 窗内=staircase re-emergence affects A 承袭"
    "·W267 prereg §5 item5 post-W267-REGISTERED pre-disclosure 兑现 r587 如实披露）"
    "→walk 越注册 W267 B 尾 604_900→A first-clean **604_901..606_900**·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（604_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim leg1 机证〔window 604_701..606_700→jump 604_901·refuser band 604_701..604_900〕"
    "·A_clean_at_naive_start=false·A_staircase_hop_past_W267_B=true"
    "·A base>=registered prior-wave B tail+1 floor relation）·非转录 r587 前向单调断言在走册；"
    "**B-ext exit seed=606_901..607_100**（**B 面=1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态（第十八次连续 above-own-A 落位）**："
    "B naive 续带 604_901..605_100（自注册 W267 B 尾 604_900+1 续）"
    "在席位窗宇宙（post-W267-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗 604_901..605_100 落本波 A first-clean 窗 604_901..606_900 内"
    "=own-A reservation cascade standard leg 强制·probe leg1 B_semantics 机证·B_naive_refused_at_start=true）"
    "——**own-A reservation standard leg 越本波 A 窗 604_901..606_900**（1 hop）"
    "→**1 hop** 落位 **606_901..607_100**·**B 落位 base==本波 A 窗尾+1（606_900+1）EXACT 机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执 leg1 机证"
    "·非转录 r587·AB 同窗互斥面 leg2 律在场）；"
    "**W267 prereg §5 item5 投影承接面注记兑现+落位一致如面**："
    "投影预言 W268 A naive 604_701..606_700 将被注册 W267 B 带拒（staircase affects A 承袭·第十七次连续 A-hop）"
    "与 B own-A reservation cascade 上移——本窗 live re-derive 与投影完全一致（零分歧如实注记·禁转录投影 r587 面在场）。"
    "R269：W268 带（A 604_901..606_900/B 606_901..607_100）注册后对 W269+ 的拒面影响=W268 冻结方 leg4 前瞻已机证（见 §5 item5）。"
)

NEW["b3_a"] = (
    "entry rng seed=**604_901+j**（法典 §4 W268 行 A=604_901..606_900·"
    "**STAIRCASE-AFFECTS-A·1-HOP WALK 形态（W239 staircase era 后第十七次连续 A-hop）**："
    "A 算术续带 604_701..606_700（自注册 W267 A 尾 604_700 续）"
    "在席位窗宇宙（post-W267-REGISTERED 终态注册）起点即 REFUSED"
    "（注册 W267 B 带 604_701..604_900 落 naive A 窗内=W267 prereg §5 item5 post-W267-REGISTERED pre-disclosure 兑现·r587 承袭披露）"
    "→walk 越注册 W267 B 尾 604_900→A first-clean 604_901..606_900·**hops=1**·"
    "**A 落位 base==注册前波 B 尾+1（604_900+1）机检关系**"
    "（A_hop_chain 1 跳 verbatim probe leg1 机证·A_clean_at_naive_start=false·A_staircase_hop_past_W267_B=true）"
    "·非转录 r587·ADMIT 回执在场）；p=`BASELINE_P"
)

NEW["b3_b"] = (
    "exit rng=**606_901+j**（法典 §4 W268 行 B=606_901..607_100·"
    "**1-HOP own-A RESERVATION CASCADE·落位高于本波 A 窗形态**："
    "B naive 续带 604_901..605_100（自注册 W267 B 尾 604_900+1 续）"
    "在席位窗宇宙（post-W267-REGISTERED 终态注册）起点即 REFUSED"
    "（naive B 窗落本波 A first-clean 窗 604_901..606_900 内=own-A reservation cascade standard leg·probe leg1 B_semantics 机证）"
    "→own-A reservation 越本波 A 窗 604_901..606_900→1 hop 落位 606_901..607_100·"
    "**B 落位 base==本波 A 窗尾+1（606_900+1）机检关系**"
    "（B_hop lands-inside-A=false·B_lands_above_own_A=true·B_hop_chain 1 跳 verbatim 在 probe 回执"
    "·第十八次连续 above-own-A 落位如实注记）"
    "·非转录 r587·与 W267 prereg §5 item5 投影承接面注记兑现+落位零分歧披露收敛·ADMIT 回执在场）；p_exit=`P_EXIT=0.05`"
)

NEW["b_claim_proj"] = (
    "probe W269+ 投影 A naive 606_901..608_900 CLEAN hops=0（零 live refusers）/ B naive 607_101..607_300 CLEAN hops=0 "
    "**但落 naive W269 A 窗内**→own-A reservation cascade 下 staircase 级联上移 **staircase face 延续 live re-derive governs 预披露**"
    "（投影 A naive 606_901..608_900 CLEAN·hops=0——**post-W268-REGISTERED 预披露：naive W269 A 起点将被注册 W268 B 带 606_901..607_100 拒=staircase affects A 第十八次连续 A-hop 预期**；"
    "投影 B naive 607_101..607_300 clean 但落 naive W269 A 窗 606_901..608_900 内——"
    "**above-own-A 承袭面：W268 B 606_901..607_100 落本波 A 窗之上〔第十八次连续〕·W269 A 面 1-hop=staircase affects A〔第十八次连续〕·"
    "W270 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace·注册 W268 B 带将拒 naive W269 A 窗仅当重叠——"
    "**W270 freezer 承接面强制注记：须在 post-W269 宇宙重 derive 且 derive B 时预留本波 A 窗·W141 先例·never transcribe r587**）"
)

NEW["b5_projection"] = (
    "5. **W269+ 投影（probe 机证 leg4·下波冻结方复核非转抄 r587 律）**：A naive first-clean 606_901..608_900 **CLEAN**（hops=0·pre-W268 宇宙零 live refusers）——"
    "**post-W268-REGISTERED 预披露：naive W269 A 起点将被注册 W268 B 带 606_901..607_100 拒（staircase-affects-A 第十八次连续 A-hop 预期）**；"
    "B naive **607_101..607_300 CLEAN（hops=0）但落投影 A 窗 606_901..608_900 内**（W269p_B_lands_inside_W269p_A_naive=true——"
    "**staircase face 延续**：W268 A 604_901..606_900+B 606_901..607_100 注册后 naive W269 A 窗起点即被注册 W268 B 带拒（staircase affects A 承袭·第十八次连续 A-hop 预期）"
    "→A first-clean 将上移·B own-A reservation cascade 落位相应上移——post-W268 宇宙 live re-derive 必变·禁转录投影）；"
    "**W269 冻结方禁假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 恒等·须重读 live trace**"
    "（W251 起 staircase affects A·W252/W253/W254/W255/W256/W257/W258/W259/W260/W261/W262/W263/W264/W265/W266/W267/W268=A/B 双 1-hop 形态连续十七波如实注记·seed-gap face 已于 W252 终结=A 首跳如实注记）"
    "——W269 冻结方必须在 post-W268 注册宇宙重 derive 且 derive B 时预留本波 A 窗 604_901..606_900+本波 B 带 606_901..607_100"
    "——leg2 律/E36 卡·W141 先例；verify at W269 prereg，hop 链逐跳在 probe 回执。"
)

NEW["b_gated"] = (
    "本件=席位窗后首窗冻结件；五面冻结拼接脚本 results/_w268bmc_freeze_edits.py"
    "（按 _w267bmc_freeze_edits.py 模板派生·gate0.5 自查 W267 行+W267 finalize 件在场=已绿·未落即 loud abort 兜底）"
    "=**splice 执行窗派生落地（r1088/r1089 W267 先例实时间线：prereg df55e3fab9 落于 r1087 窗·splice 7b9e9377 落于 r1088 执行窗 @@SPLICE_T@@——"
    "**W268 freeze 面：W267 own-wave finalize 已落地=席位时即解锁——席位+prereg 本窗落地 per seat-first law O-20261010-2350 §2·"
    "splice 执行窗开门（gate0.5 绿·编辑器 loud abort 兜底）**。"
)

# marker pairs: (block, start_marker, end_marker) -- needles matched on T1 (post-roll faces)
BLOCKS = [
    ("b_title", "engine_owner 行 256 注册在册（表尾", "owner per chain-order law）**】】）"),
    ("b_prev", "prev=**届时空窗活链头 derive 禁手抄**", "（机械算·投影面仅披露·finalize 运行时按 registry 键 derive 免疫）。"),
    ("b_band", "（**A 面=STAIRCASE-AFFECTS-A", "（见 §5 item5）。"),
    ("b3_a", "entry rng seed=**602_701+j**", "；p=`BASELINE_P"),
    ("b3_b", "exit rng=**604_701+j**", "；p_exit=`P_EXIT=0.05`"),
    ("b_claim_proj", "probe W268+ 投影 A naive 604_701..606_700 CLEAN hops=0", "never transcribe r587**）"),
    ("b5_projection", "5. **W268+ 投影（probe 机证 leg4", "verify at W268 prereg，hop 链逐跳在 probe 回执。"),
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
    "PERPETUAL-N1-W268", "research/PERPETUAL_N1_W268_PREREG.md",
    "604_901..606_900", "606_901..607_100", "587,520", "1,011,735", "585,320",
    "n1_w268_results.json", "MSG-20261018-1229-bmc-w268-seat", "b9ad2f1119",
    "池第 266 枚", "第八十七枚", "第 258 波", "第 87 枚",
    "STAIRCASE-AFFECTS-A", "第十七次连续 A-hop", "第十八次连续 above-own-A",
    "_w268bmc_20261018", "--wave 268/finalize --wave 268",
    "W267 finalize one-pass bm-c r1089", "n_eff_held_equal 996,335",
    "−0.09273843", "0.24505587", "−0.09269745", "（**0.3058** 实测锚）",
    "键 W267 实测 K-lift **−0.0001**", "line_merged@K585,320 **1.1958**", "line_pre_w267 1.1959",
    "实差 0.0000 在带内", "共二百六十六面", "W2..W267",
    "engine_owner==bm-c 86 行注册", "engine_owner 行 257 注册在册",
    "probe leg0 bmc_rows=86 attempt-continuity face（r1089 窗算法·bm-c own seat+bmc live rows 86 实读）",
    "bm-c 循环班 r1089 席位窗", "本窗 free RAM ~0.1GB", "本机 bm-c 实例",
    "W268=bm-c own-wave window per chain-order law",
    "df55e3fab9", "7b9e9377", "99166404f2", "eb5c74dbf7",
    "W269+ 投影", "W269p_B_lands_inside_W269p_A_naive", "verify at W269 prereg",
    "_w268bmc_freeze_edits.py", "_w267bmc_freeze_edits.py 模板派生",
    "bm-c r1089 W267 §7 范式", "bm-c r1089 W267 §8 范式",
    "（上游 W267 席位已闭链=注册+烧录+finalize 全落地·零在飞）",
    "W206/W211..W267 低 RAM 实烧先例", "W263 冻结窗 26G bm-a 实锚", "W264 冻结窗 7G bm-c 实锚",
    "W265 冻结窗 3G bm-c 实锚", "W266 冻结窗 ~5G bm-c 实锚", "W267 冻结窗 ~0.1G bm-c 实锚",
    "席位时即解锁", "（见 §5 item5）。", "R269：W268 带",
    "→W264 **0.000322**→W265 **0.000321**→W266 **0.000321**→W267 **0.000320**→W268 投影 0.000320】",
    "604_900+1", "606_900+1",
    "A_staircase_hop_past_W267_B=true", "B_lands_above_own_A=true",
    "seed_admit_gate rc0 双带 FREE",
    "波号 268", "零 268 行", "零 skip-ahead W269/W270 席位声明",
    "（W267 注册+烧录+finalize 全落地）",
    "12:2x", "（占位·finalize one-pass 后回填",
    "saturation_engine.py status live-read r1090：burns_active=[] queue_next=[] 实读·heartbeat 新鲜",
    "本机 bm-c 实例·heartbeat 新鲜实读 r1090 窗·队列空转 idle",
    "引擎实况注记（本机 bm-c 实例 heartbeat 新鲜 r1090 窗实读",
    "MV PACK-A i2v wave-1 在飞",
]
for s in MUST:
    assert s in T2, "MUST-HAVE missing: %r" % s

MUST_NOT = [
    "A-ext seed=602_701", "B-ext exit seed=604_701",
    "602_701..604_700", "604_701..606_700 CLEAN", "602_501..604_500",
    "GATED on", "finalize PENDING", "pending 投影 derive",
    "583,120", "1,009,535", "**585,320 投影**", "line_merged@K583,120",
    "−0.09273858", "0.24507392", "−0.09878527", "**0.3268**", "实差 0.0060 在带内",
    "07:0x", "19:2x", "10:2x", "queue_depth",
    "MSG-20261018-1025", "942ebd5885", "595433d63c", "dc71ecc3f9", "007ec5e713",
    "bc7cab9893", "18f6ffe931",
    "bmc_rows=85", "bmc rows 85+候选", "第 86 枚", "第 257 波", "第八十六枚",
    "engine_owner==bm-c 85 行注册",
    "r1086 席", "r1086 席位窗实跑", "r1086 窗算法",
    "本窗 free RAM ~5GB", "让路态", "6%·3.4G VRAM",
    "W268p_", "W267p_", "W266p_",
    "line_pre_w266", "键 W266 实测 K-lift", "键 W265 实测 K-lift",
    "verify at W268 prereg",
    "W268+ 投影", "W267+ 投影",
    "第十六次连续 A-hop", "第十七次连续 above-own-A", "连续十六波", "共二百六十五面",
    "_w266bmc_freeze_edits_TOL.py",
    "n1_w266_results.json", "n1_w265_results.json",
    "W2..W266", "W136..W266",
    "波号 267", "零 267 行",
    "W264 冻结窗 26G", "W265 冻结窗 7G", "W266 冻结窗 3G",
]
for s in MUST_NOT:
    assert s not in T2, "MUST-NOT-HAVE present: %r (count=%d)" % (s, T2.count(s))

# pinned count gates
assert T2.count("W269+ 投影") == 3, "W269+ count=%d (expect 3 = §5.5 rolled + b5 + b6 claim)" % T2.count("W269+ 投影")
assert T2.count("W268+ 投影") == 0, "W268+ count=%d (expect 0)" % T2.count("W268+ 投影")
assert T2.count("hops=1") == 2, "hops=1 count=%d (expect 2)" % T2.count("hops=1")
assert T2.count("hops=0") == 5, "hops=0 count=%d (expect 5)" % T2.count("hops=0")
assert T2.count("第十七次连续 A-hop") == 3, "A17 count=%d (expect 3 = b_band x2 + b3_a)" % T2.count("第十七次连续 A-hop")
assert T2.count("第十八次连续 A-hop") == 3, "A18 count=%d (expect 3 = b5 x2 + b6)" % T2.count("第十八次连续 A-hop")
assert T2.count("第十八次连续 above-own-A") == 2, "B18 count=%d (expect 2 = b_band + b3_b)" % T2.count("第十八次连续 above-own-A")
assert T2.count("第十七次连续 above-own-A") == 0, "B17 count=%d (expect 0)" % T2.count("第十七次连续 above-own-A")
assert T2.count("连续十七波") == 1, "17-wave count=%d (expect 1 = b5 NEW)" % T2.count("连续十七波")
assert T2.count("604_901..606_900") >= 5, "own-A count=%d (expect >=5)" % T2.count("604_901..606_900")
assert T2.count("606_901..607_100") >= 4, "own-B count=%d (expect >=4)" % T2.count("606_901..607_100")
assert T2.count("604_701..604_900") >= 3, "reg-W267-B count=%d (expect >=3)" % T2.count("604_701..604_900")
assert T2.count("604_901..605_100") == 3, "B-naive count=%d (expect 3 = b_band x2 + b3_b)" % T2.count("604_901..605_100")
assert T2.count("604_701..606_700") == 4, "A-naive count=%d (expect 4 = b_band x3 + b3_a)" % T2.count("604_701..606_700")
assert T2.count("606_901..608_900") == 5, "W269p-A count=%d (expect 5 = b6 x3 + b5 x2)" % T2.count("606_901..608_900")
assert T2.count("607_101..607_300") == 3, "W269p-B count=%d (expect 3 = b6 x2 + b5)" % T2.count("607_101..607_300")
assert T2.count("席位时即解锁") == 2, "unlock count=%d (expect 2)" % T2.count("席位时即解锁")
assert T2.count("_w268bmc_20261018") == 3, "probe-receipt count=%d (expect 3 = 2 non-block + b_title)" % T2.count("_w268bmc_20261018")
assert T2.count("1,011,735") == 2, "ledger count=%d (expect 2 = b_title + b_prev)" % T2.count("1,011,735")
assert T2.count("585,320") >= 3, "merged-K count=%d (expect >=3)" % T2.count("585,320")
assert T2.count("（占位·finalize one-pass 后回填") == 1, "sec7 placeholder count=%d (expect 1)" % T2.count("（占位·finalize one-pass 后回填")
assert T2.count("（占位·finalize 同窗回填") == 1, "sec8 placeholder count=%d (expect 1)" % T2.count("（占位·finalize 同窗回填")

# residue scan: all X_Y..X_Y windows well-formed
for m in re.finditer(r"(\d{3}_\d{3})\.\.(\d{3}_\d{3})", T2):
    lo = int(m.group(1).replace("_", "")); hi = int(m.group(2).replace("_", ""))
    assert lo <= hi, "malformed window %s" % m.group(0)

io.open(OUT, "w", encoding="utf-8", newline="").write(T2)
print("W268 PREREG DERIVE OK -> %s (%d bytes, %d lines)" % (OUT, len(T2.encode("utf-8")), T2.count("\n") + 1))
print("splice commit face: 7b9e9377 @ " + SPLICE_T + " | finalize: b9ad2f1119 @ 12:2x")
print("blocks replaced: %s" % ", ".join(n for n, _, _ in BLOCKS))
print("vmap legs: %d floors: %d post-legs: %d MUST: %d MUST_NOT: %d" % (
    len(VMAP), len(VMAP_FLOORS), len(VMAP_POST_LEGS), len(MUST), len(MUST_NOT)))
print("live RAM face: %.2f GB available (~0.1GB written, ram-critical MV squeeze) | engine: alive burns=[] queue=[]" % _ram_free)
print("src blob-verified == a345554542439271a8888fbb27f29b1cde98037d @ df55e3fab9 (frozen pre-run face; HEAD post-backfill twin cd2a8478 disclosed, NOT used)")
print("out sha256_16: %s" % hashlib.sha256(T2.encode("utf-8")).hexdigest()[:16])
